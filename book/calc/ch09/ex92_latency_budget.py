"""Worked example 9.2: latency targets of 东数西算 as fiber route length, and
what a hub-to-cluster link implies in spans, amplifier sites and regenerators.

Group delay per unit length is n_g/c (Chapter 1, Sections 1.2 and 1.7), with
n_g the effective group index of SMF-28 Ultra at 1550 nm (datasheet).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import ch09lib as cl

r = Results()
c = cl.c_light()
NG = "ch01.fiber.smf28ultra_group_index_1550"
ng = L(NG)
us_per_km = ng / c * 1e3 * 1e6          # µs per km
km_per_ms = c / ng * 1e-3 / 1e3         # km per ms
r.emit("ng", ng, "", 5, [NG])
r.emit("us_per_km", us_per_km, "µs/km", 4, [NG, "ch01.const.speed_of_light_c"])
r.emit("km_per_ms", km_per_ms, "km/ms", 4, [NG, "ch01.const.speed_of_light_c"])

# --- policy targets as one-way fiber lengths ---------------------------------
T20 = "ch09.dsxs.cluster_latency_20ms"
T10 = "ch09.dsxs.edge_latency_10ms"
TC = "ch09.dsxs.latency_circles_1_5_20"
t1, t5, t20c = (float(v) for v in cl.rec(TC)["value"])
assert t20c == L(T20)
r.emit("L_1ms", t1 * km_per_ms, "km", 3, [TC, NG])
r.emit("L_5ms", t5 * km_per_ms, "km", 3, [TC, NG])
r.emit("L_10ms", L(T10) * km_per_ms, "km", 3, [T10, NG])
r.emit("L_20ms", L(T20) * km_per_ms, "km", 3, [T20, NG])
r.emit("rtt_20ms_oneway", 2 * L(T20), "ms", 2, [T20])
# If the 1/5/20 ms circles of 1779号 were round-trip, the reach halves:
r.emit("L_20ms_if_rtt", L(T20) / 2 * km_per_ms, "km", 3, [TC, NG])
r.emit("L_1ms_if_rtt", t1 / 2 * km_per_ms, "km", 3, [TC, NG])
r.emit("L_5ms_if_rtt", t5 / 2 * km_per_ms, "km", 3, [TC, NG])

# --- the 1.5x theoretical-latency rule ----------------------------------------
TH = "ch09.dsxs.latency_1p5x_theory"
k = L(TH)
# ASSUMPTION: theoretical latency = n_g * (great-circle distance) / c, i.e. the same
# fiber on a geodesic path, so the rule caps the route-to-geodesic ratio at k.
r.emit("k_theory", k, "", 2, [TH])
r.emit("geo_max_20ms", L(T20) * km_per_ms / k, "km", 3, [T20, TH, NG])

# --- Ningbo to Gui'an field link (CMRI 2023) ----------------------------------
FT = "ch09.l400.field_5616km"
FL = "ch09.l400.field_5616km_latency"
L_loop = L(FT)
L_ow = float(cl.cond(FT, "one_way_link_km"))
ns_ow = float(cl.cond(FT, "spans_one_way"))
assert abs(2 * L_ow - L_loop) < 1e-9
tau_meas = L(FL)                       # ms, loop
tau_pred = L_loop * us_per_km / 1e3    # ms, loop
ng_impl = tau_meas * 1e-3 * c / (L_loop * 1e3)
r.emit("ng_oneway_km", L_ow, "km", 4, [FT])
r.emit("ng_spans_ow", ns_ow, "", 2, [FT])
r.emit("ng_avg_span", L_ow / ns_ow, "km", 3, [FT])
r.emit("ng_ila_ow", ns_ow - 1, "", 2, [FT])
r.emit("ng_tau_pred_loop", tau_pred, "ms", 4, [FT, NG])
r.emit("ng_tau_meas_loop", tau_meas, "ms", 5, [FL])
r.emit("ng_tau_meas_ow", tau_meas / 2, "ms", 4, [FL])
r.emit("ng_tau_pred_ow", tau_pred / 2, "ms", 4, [FT, NG])
r.emit("ng_implied", ng_impl, "", 5, [FT, FL])
r.emit("ng_impl_dev_pct", 100 * (ng_impl / ng - 1), "%", 2, [FT, FL, NG])
r.emit("ng_dtau_us", (tau_pred - tau_meas) * 1e3, "µs", 2, [FT, FL, NG])
r.emit("ng_dtau_km", (tau_pred - tau_meas) * km_per_ms, "km", 2, [FT, FL, NG])
r.emit("ng_ow_frac_20", 100 * (tau_meas / 2) / L(T20), "%", 2, [FL, T20])
assert abs(ng_impl / ng - 1) < 0.01, "implied group index far from datasheet"

# --- Beijing to Inner Mongolia first commercial link ---------------------------
FL1 = "ch09.l400.cmcc_first_link_2024"
L1 = L(FL1)
oa1 = float(cl.cond(FL1, "oa_sites"))
r.emit("bj_km", L1, "km", 3, [FL1])
r.emit("bj_spans", oa1 + 1, "", 2, [FL1])
r.emit("bj_avg_span", L1 / (oa1 + 1), "km", 3, [FL1])
r.emit("bj_tau_ow", L1 * us_per_km / 1e3, "ms", 3, [FL1, NG])
assert L1 * us_per_km / 1e3 < t5

# --- What a 20 ms one-way budget implies ---------------------------------------
Lmax = L(T20) * km_per_ms
# ASSUMPTION: no latency reserved for terminal equipment (DSP, FEC, framing and
# switching); the result is an upper bound on route length.
# ASSUMPTION A: 80 km spans (Section 9.3 reference span); ASSUMPTION B: the mean
# span of the Ningbo-Gui'an field route.
SPAN_A = 80.0
spans_a = math.ceil(Lmax / SPAN_A)
spans_b = math.ceil(Lmax / (L_ow / ns_ow))
r.emit("span_a", SPAN_A, "km", 2)
r.emit("bud_spans_a", spans_a, "", 2, [T20, NG])
r.emit("bud_ila_a", spans_a - 1, "", 2, [T20, NG])
r.emit("bud_spans_b", spans_b, "", 2, [T20, NG, FT])
r.emit("bud_ila_b", spans_b - 1, "", 2, [T20, NG, FT])

R1500 = "ch09.l400.reach_1500_g652d_edfa"
R2502 = "ch09.l400.ecoc2023_reach_2502"
RPCS = "ch09.l400.pcs16qam_b2b_17p5"
reach_pcs = float(cl.cond(RPCS, "p2p_reach_km"))


def regens(length, reach):
    """Number of intermediate O-E-O regenerators: segments - 1."""
    return math.ceil(length / reach) - 1


r.emit("reach_1500", L(R1500), "km", 4, [R1500])
r.emit("reach_2502", L(R2502), "km", 4, [R2502])
r.emit("reach_pcs", reach_pcs, "km", 4, [RPCS])
r.emit("reg_1500", regens(Lmax, L(R1500)), "", 1, [R1500, T20, NG])
r.emit("reg_2502", regens(Lmax, L(R2502)), "", 1, [R2502, T20, NG])
r.emit("reg_5616", regens(Lmax, L_loop), "", 1, [FT, T20, NG])
r.emit("reg_pcs", regens(Lmax, reach_pcs), "", 1, [RPCS, T20, NG])
r.emit("reg_ng_pcs", regens(L_ow, reach_pcs), "", 1, [RPCS, FT])
r.emit("reg_ng_1500", regens(L_ow, L(R1500)), "", 1, [R1500, FT])
r.emit("reg_ng_2502", regens(L_ow, L(R2502)), "", 1, [R2502, FT])
assert regens(Lmax, L(R1500)) == 2 and regens(Lmax, L(R2502)) == 1

# --- Verizon round-trip SLA on the same scale (used again in 9.6) ---------------
VZ = "ch09.cmp.us_verizon_na_latency"
rtt = L(VZ)
lo, hi = cl.rec(VZ)["conditions"]["measured_range_ms"]
r.emit("vz_rtt", rtt, "ms", 2, [VZ])
r.emit("vz_oneway", rtt / 2, "ms", 3, [VZ])
r.emit("vz_L", rtt / 2 * km_per_ms, "km", 3, [VZ, NG])
r.emit("vz_meas_lo", lo, "ms", 3, [VZ])
r.emit("vz_meas_hi", hi, "ms", 3, [VZ])
r.emit("vz_L_lo", lo / 2 * km_per_ms, "km", 3, [VZ, NG])
r.emit("vz_L_hi", hi / 2 * km_per_ms, "km", 3, [VZ, NG])

# --- figure: one-way latency versus fiber length --------------------------------
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.2))
xs = [0, 5000]
ax.plot(xs, [x * us_per_km / 1e3 for x in xs], color=cl.COLORS[0], label="one-way, $n_g$ of SMF-28 Ultra")
ax.plot(xs, [2 * x * us_per_km / 1e3 for x in xs], color=cl.COLORS[1], ls="--", label="round trip")
for t, lab in ((t1, "1 ms"), (t5, "5 ms"), (L(T10), "10 ms (edge, one-way)"), (L(T20), "20 ms (cluster, one-way)")):
    ax.axhline(t, color=cl.GRAY, lw=0.8, ls=":")
    ax.text(4950, t + 0.4, lab, ha="right", va="bottom", fontsize=9)
ax.plot([L_ow], [tau_meas / 2], "o", color=cl.COLORS[2], ms=7, label="Ningbo–Gui'an, measured (loop / 2)")
ax.plot([L1], [L1 * us_per_km / 1e3], "s", color=cl.COLORS[3], ms=7, label="Beijing–Inner Mongolia, computed")
ax.plot([rtt / 2 * km_per_ms], [rtt], "D", color=cl.COLORS[4], ms=7, label="Verizon NA SLA (round trip)")
ax.set_xlabel("fiber route length (km)")
ax.set_ylabel("latency (ms)")
ax.set_xlim(0, 5000)
ax.set_ylim(0, 50)
ax.legend(loc="upper left", fontsize=9)
cl.savefig(fig, "latency_vs_length")
r.save()
