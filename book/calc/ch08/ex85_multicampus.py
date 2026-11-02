"""Section 8.5 worked example (a MODEL, not a disclosed design): WAN bandwidth for
gradient synchronization of data-parallel training across S campuses.

Each campus holds a full model replica (tensor/pipeline parallelism stay inside).
Hierarchical all-reduce: reduce-scatter inside each campus, an all-reduce of the
gradient across the S campuses over the WAN, all-gather inside. Treating each
campus as one process with aggregate WAN bandwidth B_W, the bandwidth-optimal
lower bound (Patarasuk and Yuan; Chapter 5) gives the bytes each campus must send:
    D = 2 (S-1)/S * X s_item
and with the Hockney cost per message (alpha_c = one-way propagation delay):
    T_sync = 2 (S-1) alpha_c + D / B_W.
Requirement: T_sync <= f T_step  ->  B_W >= D / (f T_step - 2 (S-1) alpha_c).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch08lib as cl

r = Results()
# ---------- ASSUMPTIONS (none is a sourced fact)
P_PARAM = 405e9     # ASSUMPTION: dense model with the parameter count in the name 'Llama 3 405B'
S_ITEM = 2          # ASSUMPTION: gradients exchanged in 16-bit format (bytes per parameter)
T_STEP = 10.0       # ASSUMPTION: optimizer step time (s)
F_OVL = 0.5         # ASSUMPTION: fraction of the step during which WAN sync can overlap compute
D_KM = 1500.0       # ASSUMPTION: fiber route length between two campuses (km)
GPU_PER_CAMPUS = 8000  # ASSUMPTION: half of the Llama 3 405B GPU count on each of two campuses
for name, v, u, d in (("P", P_PARAM / 1e9, "billion parameters", 3), ("s_item", S_ITEM, "bytes", 1),
                      ("T_step", T_STEP, "s", 2), ("f", 100 * F_OVL, "%", 2), ("d_km", D_KM, "km", 2),
                      ("gpu_campus", GPU_PER_CAMPUS, "GPUs", 2)):
    r.emit(name, v, u, d)
assert abs(2 * GPU_PER_CAMPUS - L("ch08.ai.llama3_gpus")) < 1

tkm = cl.us_per_km()
alpha = D_KM * tkm * 1e-6                        # one-way, s
X_bits = P_PARAM * S_ITEM * 8
r.emit("grad_tb", X_bits / 1e12, "Tb", 3)
r.emit("grad_gb", P_PARAM * S_ITEM / 1e9, "GB", 3)
r.emit("alpha_ms", alpha * 1e3, "ms", 3, [cl.NG_ID, cl.C_ID])
r.emit("rtt_ms", 2 * alpha * 1e3, "ms", 3, [cl.NG_ID, cl.C_ID])


def bw_req(S, T=T_STEP, f=F_OVL, comm_factor=1.0):
    D = 2 * (S - 1) / S * X_bits / comm_factor
    budget = f * T - 2 * (S - 1) * alpha
    assert budget > 0
    return D / budget, D


for S in (2, 4, 8):
    b, D = bw_req(S)
    r.emit(f"D_S{S}", D / 1e12, "Tb", 3)
    r.emit(f"bw_S{S}", b / 1e12, "Tb/s", 3, [cl.NG_ID])
    r.emit(f"lat_S{S}_ms", 2 * (S - 1) * alpha * 1e3, "ms", 3, [cl.NG_ID])
bw2, D2 = bw_req(2)
# latency share of the sync budget
r.emit("lat_share_pct", 100 * 2 * alpha / (F_OVL * T_STEP), "%", 2, [cl.NG_ID])
# bandwidth-delay product (bytes in flight over one RTT)
r.emit("bdp_gb", bw2 * 2 * alpha / 8 / 1e9, "GB", 3, [cl.NG_ID])
# Hockney crossover: message size at which latency and bandwidth terms are equal
r.emit("n_half_mb", alpha * bw2 / 8 / 1e6, "MB", 3, [cl.NG_ID])

# Compare with in-campus scale-out bandwidth and with optical units
GL = "ch08.ai.llama3_gpu_link"
inc = GPU_PER_CAMPUS * L(GL) * 1e9
r.emit("campus_scaleout_pbps", inc / 1e15, "Pb/s", 3, [GL])
r.emit("wan_over_campus", inc / bw2, "1", 3, [GL])
R8 = "ch08.radwan.reach_8qam"
assert D_KM < L(R8)
WL = 150e9          # 8QAM rate in the RADWAN reach table that covers D_KM
r.emit("wl_150", math.ceil(bw2 / WL), "wavelengths", 2, [R8])
FP = "ch08.google_optical.fiber_pair_capacity"
r.emit("fp_frac", 100 * bw2 / (L(FP) * 1e12), "%", 2, [FP])
# Low-communication methods (as reported; transfer to this scale is not shown by the sources)
DL, SD = "ch08.ai.diloco_comm_reduction", "ch08.ai.streaming_diloco_bw"
r.emit("bw_diloco_gbps", bw2 / L(DL) / 1e9, "Gb/s", 3, [DL])
r.emit("bw_sdiloco_gbps", bw2 / L(SD) / 1e9, "Gb/s", 3, [SD])
# Fully synchronous, no overlap: step stretch at a given WAN rate
# ASSUMPTION: an 800 Gb/s inter-campus allocation (two 400G-class circuits)
BW_GIVEN = 0.8e12
t_sync = 2 * alpha + D2 / BW_GIVEN
r.emit("bw_given", BW_GIVEN / 1e9, "Gb/s", 2)
r.emit("tsync_given", t_sync, "s", 3, [cl.NG_ID])
r.emit("stretch_pct", 100 * t_sync / T_STEP, "%", 3, [cl.NG_ID])

# Meta multi-building cluster (Chapter 5 records, tier A) for context
r.emit("meta_gpus", L("ch05.ai.meta_129k_h100") / 1e3, "thousand GPUs", 3, ["ch05.ai.meta_129k_h100"])
r.emit("meta_bldgs", cl.cond("ch05.ai.meta_129k_h100", "buildings"), "buildings", 1, ["ch05.ai.meta_129k_h100"])
r.emit("meta_xbldg_lat", float(cl.rec("ch05.ai.meta_latency_hierarchy")["value"][2]), "1", 2, ["ch05.ai.meta_latency_hierarchy"])
r.emit("llama_pods", L("ch08.ai.llama3_cluster", "lo") / L("ch08.ai.llama3_cluster", "hi"), "pods", 2,
       ["ch08.ai.llama3_cluster"])

# Fairwater fiber miles (tier C; contested box): consequences of the two readings
FG, FS = "ch08.ai.fairwater_new_fiber_guthrie", "ch08.ai.fairwater_fiber_source"
inc_mi = L(FG)
g = L(FS, "hi") / 100
r.emit("fw_prior_max", inc_mi / g / 1e3, "thousand mi", 3, [FG, FS])
r.emit("fw_total_max", inc_mi * (1 + g) / g / 1e3, "thousand mi", 3, [FG, FS])
NEW = "ch08.carrier.lumen_2025_new_fiber_vs_route_miles"
fpr = L(NEW, "lo") / L(NEW, "hi")
r.emit("fw_route_equiv", inc_mi / fpr, "route-mi", 2, [FG, NEW])
r.emit("fw_fiber_km", inc_mi * cl.MI_KM / 1e3, "thousand fiber-km", 3, [FG])

# ---------- figure: required WAN bandwidth vs step time
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.4))
T = np.logspace(0, 2, 200)
for S, col in ((2, cl.COLORS[0]), (4, cl.COLORS[1]), (8, cl.COLORS[2])):
    ax.loglog(T, [bw_req(S, t)[0] / 1e12 for t in T], color=col, label=f"S = {S} campuses, synchronous")
ax.loglog(T, [bw_req(2, t, comm_factor=L(DL))[0] / 1e12 for t in T], color=cl.COLORS[3], ls="--",
          label="S = 2, communication / 500 (DiLoCo factor)")
ax.axhline(L(FP), color=cl.GRAY, ls=":", lw=1)
ax.text(1.1, L(FP) * 1.15, "one fiber pair, 2013 coherent DWDM", fontsize=8.5)
ax.axhline(WL / 1e12, color=cl.GRAY, ls=":", lw=1)
ax.text(1.1, WL / 1e12 * 1.15, "one 150 Gb/s wavelength", fontsize=8.5)
ax.set_xlabel("Optimizer step time (s)")
ax.set_ylabel("Required WAN bandwidth per campus (Tb/s)")
ax.set_ylim(1e-3, 50)
ax.legend(fontsize=8.5, loc="lower left")
ax.set_title("Model: 405e9 parameters, 2-byte gradients, 50 % overlap, 1500 km", fontsize=10)
cl.savefig(fig, "multicampus_bw")
r.save()
