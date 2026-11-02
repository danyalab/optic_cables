"""Worked example 5.3: all-reduce cost models and the per-GPU network bandwidth that
hides gradient synchronization under compute.

Part A simulates a ring all-reduce chunk by chunk and checks that every rank sends
2(N-1)/N of the message (Patarasuk and Yuan 2009). Part B evaluates the alpha-beta
(here tau, B) models of Thakur et al. (2005). Part C is the bandwidth budget for a
175B-parameter model on 12,288 GPUs (MegaScale's scale and MFU), with every model
input an explicit ASSUMPTION.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch05lib as cl

r = Results()

# =========================================================== A. ring simulation
def ring_allreduce(data):
    """data: (N, X) array, one row per rank. Returns result rows and bytes sent per rank."""
    n, x = data.shape
    assert x % n == 0
    c = x // n
    buf = data.astype(float).copy()
    sent = np.zeros(n)
    # reduce-scatter: at step s rank i sends chunk (i - s) mod n to rank i+1
    for s in range(n - 1):
        out = [(i, (i - s) % n, buf[i, ((i - s) % n) * c:((i - s) % n + 1) * c].copy()) for i in range(n)]
        for i, ch, payload in out:
            j = (i + 1) % n
            buf[j, ch * c:(ch + 1) * c] += payload
            sent[i] += payload.size
    # all-gather: rank i now owns the full sum of chunk (i + 1) mod n
    for s in range(n - 1):
        out = [(i, (i + 1 - s) % n, buf[i, ((i + 1 - s) % n) * c:((i + 1 - s) % n + 1) * c].copy()) for i in range(n)]
        for i, ch, payload in out:
            j = (i + 1) % n
            buf[j, ch * c:(ch + 1) * c] = payload
            sent[i] += payload.size
    return buf, sent

rng = np.random.default_rng(5)
for n in (2, 4, 7, 8):
    x = n * 6
    d = rng.integers(0, 100, size=(n, x))
    res, sent = ring_allreduce(d)
    assert np.allclose(res, d.sum(axis=0)), "ring all-reduce must produce the sum on every rank"
    assert np.allclose(sent, 2 * (n - 1) / n * x), "each rank sends 2(N-1)/N of the message"
r.emit("sim_ok", 1, "", 1)
assert L("ch05.ai.allreduce_2x_bound") == 2

# =========================================================== B. cost models
TAU = cl.cond("ch05.ai.tencent_nvlink_roce_latency", "roce_us") * 1e-6        # s, RoCE transfer latency
TAU_NVL = cl.cond("ch05.ai.tencent_nvlink_roce_latency", "nvlink_ns") * 1e-9  # s
BW = L("ch05.ai.llama3_400g_per_gpu") * 1e9 / 8                               # B/s per GPU
lat_ins = ["ch05.ai.tencent_nvlink_roce_latency", "ch05.ai.llama3_400g_per_gpu"]
r.emit("tau_us", TAU * 1e6, "µs", 2, lat_ins)
r.emit("tau_nvl_ns", TAU_NVL * 1e9, "ns", 3, lat_ins)
for i, nm in enumerate(("rack", "zone", "bldg")):
    r.emit(f"meta_lat_{nm}", cl.rec("ch05.ai.meta_latency_hierarchy")["value"][i], "", 2, ["ch05.ai.meta_latency_hierarchy"])
r.emit("meta_zone_racks", cl.cond("ch05.ai.meta_zone_4k", "racks"), "racks", 3, ["ch05.ai.meta_zone_4k"])
r.emit("llama_racks", cl.cond("ch05.ai.llama3_pod_3072", "racks"), "racks", 3, ["ch05.ai.llama3_pod_3072"])
r.emit("gpus_per_rack", cl.cond("ch05.ai.llama3_pod_3072", "gpus_per_rack"), "GPUs", 2, ["ch05.ai.llama3_pod_3072"])
r.emit("bw_GBps", BW / 1e9, "GB/s", 3, lat_ins)

N_SEG = L("ch05.ai.hpn_segment_1k")
N_SUM = cl.cond("ch05.ai.nccl_tree_latency_180x", "gpus")
for tag, n in (("seg", N_SEG), ("sum", N_SUM)):
    s_star = n * TAU * BW            # 2(N-1) tau = 2(N-1)/N S/B
    r.emit(f"sstar_{tag}_MB", s_star / 1e6, "MB", 3, lat_ins)
    r.emit(f"ringlat_{tag}_ms", 2 * (n - 1) * TAU * 1e3, "ms", 3, lat_ins)
    r.emit(f"lat_ratio_{tag}", (n - 1) / math.log2(n), "", 3, lat_ins)
    r.emit(f"log2_{tag}", math.log2(n), "", 3, lat_ins)
r.emit("n_sum", N_SUM, "GPUs", 5, ["ch05.ai.nccl_tree_latency_180x"])
r.emit("n_seg", N_SEG, "GPUs", 4, ["ch05.ai.hpn_segment_1k"])
assert (N_SUM - 1) / math.log2(N_SUM) > L("ch05.ai.nccl_tree_latency_180x")

# busbw factor for large N
r.emit("busbw_seg", 2 * (N_SEG - 1) / N_SEG, "", 4, ["ch05.ai.hpn_segment_1k"])

# Hierarchical all-reduce on a rail-optimized fabric: 8 GPUs per node
G = cl.cond("ch05.ai.megascale_nics", "nics_per_server")
assert G == L("ch05.clos.dgx_h100_fabric_def") == 8
BW_NVL = L("ch05.su.nvlink4_900") * 1e9 / 2          # B/s per direction
r.emit("g", G, "GPUs per node", 1, ["ch05.ai.megascale_nics"])
r.emit("nvl_dir_GBps", BW_NVL / 1e9, "GB/s", 3, ["ch05.su.nvlink4_900"])
S_EX = 1e9   # ASSUMPTION: 1 GB message for the hierarchy illustration
n_nodes = int(N_SEG // G)
t_flat = cl.t_ring(N_SEG, S_EX, BW, TAU)
t_h, t_in, t_out = cl.t_hier(n_nodes, G, S_EX, BW_NVL, BW, TAU_NVL, TAU)
r.emit("s_ex_GB", S_EX / 1e9, "GB", 2)
r.emit("t_flat_ms", t_flat * 1e3, "ms", 3, lat_ins)
r.emit("t_hier_ms", t_h * 1e3, "ms", 3, lat_ins + ["ch05.su.nvlink4_900"])
r.emit("t_hier_in_ms", t_in * 1e3, "ms", 3, lat_ins + ["ch05.su.nvlink4_900"])
r.emit("t_hier_out_ms", t_out * 1e3, "ms", 3, lat_ins)
r.emit("hier_speedup", t_flat / t_h, "", 3, lat_ins + ["ch05.su.nvlink4_900"])
r.emit("nic_bytes_flat_GB", 2 * (N_SEG - 1) / N_SEG * S_EX / 1e9, "GB", 3)
r.emit("nic_bytes_hier_GB", 2 * (n_nodes - 1) / n_nodes * S_EX / G / 1e9, "GB", 3)
r.emit("n_nodes", n_nodes, "nodes", 3, ["ch05.ai.hpn_segment_1k"])
assert t_h < t_flat

# =========================================================== C. bandwidth budget
MS = "ch05.ai.megascale_mfu"
N_GPU = cl.cond(MS, "gpus")
P = float(cl.cond(MS, "model").rstrip("B")) * 1e9
U = L(MS) / 100
ins = [MS]
# ASSUMPTIONS (all stated in prose and listed in ch05_needs.md)
F_PEAK = 1.0e15        # FLOP/s per GPU, dense 16-bit peak (round number)
B_GRAD = 2             # bytes per gradient element (16-bit all-reduce)
FLOP_PER_PT = 6        # training FLOPs per parameter per token (forward 2 + backward 4)
PHI = 2 / 3            # fraction of step time during which gradient all-reduce can overlap (backward pass)
TP, PP = 8, 8          # tensor-parallel inside a node, pipeline-parallel stages
H, NL = 12288, 96      # hidden size and layers for a 175B dense transformer
TOK = 2 ** 22          # global batch, tokens per optimizer step
assert abs(12 * NL * H ** 2 / P - 1) < 0.01, "assumed shape must give the stated parameter count"
assert TP == G
D = N_GPU // (TP * PP)
assert D * TP * PP == N_GPU
t_r = TOK / D
T_step = FLOP_PER_PT * P * TOK / (N_GPU * F_PEAK * U)
S_grad = B_GRAD * P / (TP * PP)
B_dp = 2 * (D - 1) / D * S_grad / (PHI * T_step)
B_dp_closed = B_GRAD * F_PEAK * U / (3 * PHI * t_r) * (D - 1) / D
assert abs(B_dp / B_dp_closed - 1) < 1e-12
B_tp = (TP - 1) * B_GRAD * F_PEAK * U / (9 * H)
B_pp = B_GRAD * F_PEAK * U / (36 * H * (NL / PP))
for name, val, unit_, dg in (("n_gpu", N_GPU, "GPUs", 5), ("p_B", P / 1e9, "billion parameters", 3),
                             ("mfu", U * 100, "%", 3), ("fpeak", F_PEAK / 1e15, "PFLOP/s", 2),
                             ("tp", TP, "", 1), ("pp", PP, "", 1), ("dp", D, "", 3), ("h", H, "", 5),
                             ("nl", NL, "layers", 2), ("tok_M", TOK / 1e6, "million tokens", 3),
                             ("t_r", t_r, "tokens", 3), ("phi", PHI, "", 3),
                             ("p_check_B", 12 * NL * H ** 2 / 1e9, "billion parameters", 4)):
    r.emit(name, val, unit_, dg, ins)
r.emit("t_step", T_step, "s", 3, ins)
r.emit("s_grad_GB", S_grad / 1e9, "GB", 3, ins)
r.emit("b_dp_gbps", B_dp * 8 / 1e9, "Gb/s", 3, ins)
r.emit("b_dp_GBps", B_dp / 1e9, "GB/s", 3, ins)
r.emit("b_tp_gbps", B_tp * 8 / 1e9, "Gb/s", 3, ins)
r.emit("b_tp_GBps", B_tp / 1e9, "GB/s", 3, ins)
r.emit("b_pp_gbps", B_pp * 8 / 1e9, "Gb/s", 3, ins)
r.emit("tp_over_dp", B_tp / B_dp, "", 2, ins)
r.emit("dp_over_pp", B_dp / B_pp, "", 3, ins)
# DP ring latency vs bandwidth term at D ranks
r.emit("dp_lat_ms", 2 * (D - 1) * TAU * 1e3, "ms", 3, ins + lat_ins)
# The same Tencent paper gives a RoCE latency twice as large in another section: double tau.
r.emit("dp_lat2_ms", 2 * (D - 1) * 2 * TAU * 1e3, "ms", 3, ins + lat_ins)
r.emit("sstar_seg2_MB", N_SEG * 2 * TAU * BW / 1e6, "MB", 3, lat_ins)
r.emit("dp_bw_s", 2 * (D - 1) / D * S_grad / BW, "s", 3, ins + lat_ins)
# TP over the NIC vs over NVLink: comm time as a fraction of compute time (no overlap)
nic = L("ch05.ai.llama3_400g_per_gpu") * 1e9 / 8
r.emit("tp_frac_nic", B_tp / nic * 100, "%", 3, ins + ["ch05.ai.llama3_400g_per_gpu"])
r.emit("tp_frac_nvl", B_tp / BW_NVL * 100, "%", 2, ins + ["ch05.su.nvlink4_900"])
r.emit("dp_frac_400", B_dp / nic * 100, "%", 2, ins + ["ch05.ai.llama3_400g_per_gpu"])
r.emit("megascale_nic", L("ch05.ai.megascale_nics"), "Gb/s", 3, ["ch05.ai.megascale_nics"])
# Meta cross-zone bandwidth per GPU under 1:7 and 1:2.8
for tag, rid in (("7", "ch05.ai.llama3_oversub_1to7"), ("2p8", "ch05.ai.meta_oversub_2p8")):
    r.emit(f"meta_xz_{tag}", L("ch05.ai.llama3_400g_per_gpu") / L(rid), "Gb/s", 3,
           [rid, "ch05.ai.llama3_400g_per_gpu"])
# Sensitivity: halving tokens per replica doubles B_dp; doubling D at fixed batch does the same
r.emit("b_dp_2x_gbps", 2 * B_dp * 8 / 1e9, "Gb/s", 3, ins)

# =========================================================== figures
plt = cl.setup_mpl()
sizes = np.geomspace(1e3, 1e10, 200)
fig, ax = plt.subplots(figsize=(7.2, 4.4))
for i, (lab, fn) in enumerate((("ring", cl.t_ring), ("Rabenseifner (halving + doubling)", cl.t_rabenseifner),
                               ("recursive doubling", cl.t_recursive_doubling),
                               ("binomial reduce + broadcast", cl.t_binomial_allreduce))):
    ax.plot(sizes, [fn(N_SEG, s, BW, TAU) for s in sizes], color=cl.COLORS[i], label=lab)
ax.plot(sizes, [2 * (N_SEG - 1) / N_SEG * s / BW for s in sizes], color=cl.GRAY, ls=":", lw=1.2,
        label=r"bandwidth bound $2\frac{N-1}{N}S/B$")
ax.axvline(N_SEG * TAU * BW, color=cl.GRAY, lw=0.8, ls="--")
ax.text(N_SEG * TAU * BW * 1.2, 2e-5, r"$S^*=N\tau B$", fontsize=9)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Message size per GPU, $S$ (bytes)")
ax.set_ylabel("All-reduce time (s)")
ax.set_ylim(1e-5, 10)
ax.legend(fontsize=8.5, loc="upper left")
ax.set_title(f"Computed: N = {int(N_SEG)} GPUs, tau = {TAU*1e6:.0f} us, B = {BW/1e9:.0f} GB/s per GPU", fontsize=10)
cl.savefig(fig, "allreduce_time")

fig, ax = plt.subplots(figsize=(7.2, 4.4))
Ds = np.array([2 ** j for j in range(2, 13)], dtype=float)
bdp = [B_GRAD * F_PEAK * U / (3 * PHI * (TOK / d)) * (d - 1) / d * 8 / 1e9 for d in Ds]
ax.plot(Ds, bdp, "o-", color=cl.COLORS[0], ms=4, label="data-parallel all-reduce, fully overlapped")
ax.axhline(B_tp * 8 / 1e9, color=cl.COLORS[1], label="tensor parallel (TP = 8) if it crossed the NIC")
ax.axhline(B_pp * 8 / 1e9, color=cl.COLORS[2], label="pipeline point-to-point (PP = 8)")
for v, lab in ((400, "400G NIC"), (800, "800G NIC")):
    ax.axhline(v, color=cl.GRAY, ls="--", lw=1)
    ax.text(Ds[-1], v * 1.1, lab, fontsize=8.5, ha="right")
ax.plot([D], [B_dp * 8 / 1e9], "*", ms=13, color=cl.COLORS[3], label=f"worked example, D = {D}")
ax.set_xscale("log", base=2); ax.set_yscale("log")
ax.set_xlabel("Data-parallel degree $D$ (global batch fixed)")
ax.set_ylabel("Required per-GPU bandwidth (Gb/s)")
ax.legend(fontsize=8, loc="upper left", bbox_to_anchor=(0.0, 0.93))
ax.set_ylim(1, 2e4)
ax.set_title("Computed from the stated assumptions (175B dense model, MFU from MegaScale)", fontsize=10)
cl.savefig(fig, "bandwidth_budget")

r.save()
