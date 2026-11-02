"""Worked example 5.6: optics count, power and cost share for a 100k-accelerator
scale-out fabric. A transparent model: every input is a ledger value or an
explicit ASSUMPTION; no published total is reproduced because none exists."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch05lib as cl

r = Results()

# ---------------------------------------------------------------- assumptions
N = 100_000            # ASSUMPTION: accelerators (round target; cf. Meta 129k, Tencent >100k claim)
K = 128                # ASSUMPTION: 51.2T switch used as 128 x 400G (ch05.pw.broadcom_51t_128_modules)
assert K * cl.cond("ch05.pw.broadcom_51t_128_modules", "module_rate_G") == 51200
TIERS = cl.tiers_needed(N, K)
assert TIERS == 3
P_NIC400 = L("ch04.pmd.400g_dr4_power_qsfp112")          # NIC-side 400G DR4 module (datasheet max)
P_TWIN800 = L("ch04.pmd.800g_2xdr4_power")                # switch-side twin-port 2x400G module
P_TWIN1600 = L("ch04.pmd.1p6t_dr8_power")                 # switch-side 2x800G module
P_GPU = float(cl.cond("ch05.ai.llama3_cluster_24k", "gpu").split()[1])   # 'H100 700 W'
SIG_META = L("ch05.ai.llama3_oversub_1to7")
BCP = "ch04.pw.broadcom_pluggable_14w_800g"
CPO = L(BCP) / float(cl.cond(BCP, "comparison").split()[1].rstrip("W/800G"))
src = ["ch04.pmd.400g_dr4_power_qsfp112", "ch04.pmd.800g_2xdr4_power", "ch04.pmd.1p6t_dr8_power",
       "ch05.ai.llama3_cluster_24k"]
r.emit("n", N, "accelerators", 6)
r.emit("k", K, "ports", 3, ["ch05.pw.broadcom_51t_128_modules"])
r.emit("tiers", TIERS, "", 1)
r.emit("p_gpu", P_GPU, "W", 3, ["ch05.ai.llama3_cluster_24k"])
r.emit("cpo_ratio", CPO, "", 3, [BCP])

# switch counts for a partially built 3-tier fat tree (full bisection)
leaf = math.ceil(N / (K / 2)); spine = math.ceil(N / (K / 2)); core = math.ceil(N / K)
r.emit("sw_leaf", leaf, "switches", 4); r.emit("sw_core", core, "switches", 3)
r.emit("sw_total", leaf + spine + core, "switches", 4)


def ends(host_optical, sig_top=1.0):
    """Optical port ends per accelerator: (NIC side, switch side)."""
    nic = 1 if host_optical else 0
    sw = (1 if host_optical else 0) + 1 + 1 + 1 / sig_top + 1 / sig_top
    return nic, sw

cases = {
    "a": ("Host link copper, 400G", False, 1.0, 400),
    "b": ("Host link optical, 400G", True, 1.0, 400),
    "c": ("Copper host, 400G, top tier 1:7", False, SIG_META, 400),
    "d": ("Optical host, 800G (two 400G planes)", True, 1.0, 800),
}
watts = {}
for tag, (lab, opt, sig, rate) in cases.items():
    nic, sw = ends(opt, sig)
    if rate == 400:
        p_nic, p_end = P_NIC400, P_TWIN800 / 2
    else:
        # ASSUMPTION: the 800G NIC-side module draws as much as the 800G twin-port module
        p_nic, p_end = P_TWIN800, P_TWIN1600 / 2
    w = nic * p_nic + sw * p_end
    w_cpo = nic * p_nic + sw * p_end / CPO
    mods = nic + sw / 2
    watts[tag] = (lab, nic * p_nic, sw * p_end, sw * p_end / CPO)
    r.emit(f"{tag}_ends", nic + sw, "port ends", 3)
    r.emit(f"{tag}_mods", mods, "modules", 3)
    r.emit(f"{tag}_mods_total", mods * N / 1e3, "thousand modules", 3)
    r.emit(f"{tag}_w", w, "W", 3, src)
    r.emit(f"{tag}_mw", w * N / 1e6, "MW", 3, src)
    r.emit(f"{tag}_w_cpo", w_cpo, "W", 3, src + [BCP])
    r.emit(f"{tag}_share", w / P_GPU * 100, "%", 2, src)
    r.emit(f"{tag}_share_cpo", w_cpo / P_GPU * 100, "%", 2, src + [BCP])
assert ends(True)[0] + ends(True)[1] == 6 and sum(ends(False)) == 4
r.emit("sig_meta", SIG_META, "", 1, ["ch05.ai.llama3_oversub_1to7"])

# TPU v4 comparison: 1.5 optical links per chip = 3 port ends
r.emit("v4_ends", 2 * L("ch05.ocs.tpuv4_6144_links") / L("ch05.ocs.tpuv4_chips"), "port ends", 2,
       ["ch05.ocs.tpuv4_6144_links", "ch05.ocs.tpuv4_chips"])

# tier-C claim for the contested box: six transceivers, 180 W, $6000 per GPU
J = "ch05.pw.jensen_6_xcvr_per_gpu"
r.emit("j_w_each", cl.cond(J, "power_W_per_gpu") / L(J), "W", 2, [J])
r.emit("j_usd_each", cl.cond(J, "cost_usd_per_gpu") / L(J), "USD", 2, [J])
r.emit("j_w_dr8", L(J) * P_TWIN1600, "W", 3, [J, "ch04.pmd.1p6t_dr8_power"])

# cost share as a function of rho = (module price)/(accelerator all-in price), unknown
def share(n_mod, rho):
    return n_mod * rho / (1 + n_mod * rho)

for tag in ("a", "b"):
    m = 1 * (tag == "b") + ends(tag == "b")[1] / 2
    for rho in (0.01, 0.03):
        r.emit(f"{tag}_cost_{int(rho*100)}", share(m, rho) * 100, "%", 2)
r.emit("tpu_cost_cap", L("ch05.ocs.tpuv4_cost_share", "lo"), "%", 1, ["ch05.ocs.tpuv4_cost_share"])
# rho at which case b reaches the TPU v4 cap (5% of GPU + optics), for orientation only
mb = 1 + ends(True)[1] / 2
cap = L("ch05.ocs.tpuv4_cost_share", "lo") / 100
r.emit("rho_at_cap", cap / (1 - cap) / mb * 100, "%", 2, ["ch05.ocs.tpuv4_cost_share"])

# ---------------------------------------------------------------- figure
plt = cl.setup_mpl()
fig, (ax, ax2) = plt.subplots(1, 2, figsize=(9.6, 4.2), gridspec_kw={"width_ratios": [1.25, 1]})
labs = [watts[t][0] for t in cases]
x = np.arange(len(labs))
nic_w = [watts[t][1] for t in cases]; sw_w = [watts[t][2] for t in cases]; cpo_w = [watts[t][3] for t in cases]
ax.bar(x - 0.18, nic_w, 0.34, color=cl.COLORS[0], label="NIC-side module")
ax.bar(x - 0.18, sw_w, 0.34, bottom=nic_w, color=cl.COLORS[1], label="switch-side ports, pluggable")
ax.bar(x + 0.18, nic_w, 0.34, color=cl.COLORS[0])
ax.bar(x + 0.18, cpo_w, 0.34, bottom=nic_w, color=cl.COLORS[2], label="switch-side ports, CPO ratio applied")
ax.set_xticks(x); ax.set_xticklabels([l.replace(", ", ",\n", 1) for l in labs], fontsize=7.5)
ax.set_ylabel("Optics power per accelerator (W)")
ax.legend(fontsize=8, loc="upper left")
ax.set_title("(a) computed power per accelerator", fontsize=10)
rho = np.geomspace(0.002, 0.2, 100)
for i, (tag, m) in enumerate((("copper host link", 2.0), ("optical host link", mb))):
    ax2.plot(rho * 100, share(m, rho) * 100, color=cl.COLORS[i], label=f"{tag}, {m:g} modules")
ax2.axhline(cap * 100, color=cl.GRAY, ls=":", lw=1.2)
ax2.text(0.25, cap * 100 * 1.15, "TPU v4: optics + OCS < 5% of system cost", fontsize=8)
ax2.set_xscale("log"); ax2.set_yscale("log")
ax2.set_xlabel(r"Module price / accelerator price, $\rho$ (%)")
ax2.set_ylabel("Optics share of (accelerator + optics) cost (%)")
ax2.legend(fontsize=8, loc="lower right")
ax2.set_title("(b) cost share versus an unknown price ratio", fontsize=10)
fig.tight_layout()
cl.savefig(fig, "cluster_optics")

r.save()
