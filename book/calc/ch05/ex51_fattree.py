"""Worked example 5.1: folded-Clos (fat-tree) counting.

1. Reproduce Al-Fares et al. (k = 48) and the DGX H100 SuperPOD tables from the
   closed forms N = 2 (k/2)^l, S = (2l - 1)(k/2)^(l-1), links per tier = N.
2. Apply the formulas to a 51.2 Tb/s switch used as 128 x 400G or 64 x 800G.
3. Leaf oversubscription sigma: N(sigma) = N(1) * 2 sigma / (1 + sigma).
4. Clos (1953) crosspoint counts.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch05lib as cl

r = Results()
_emit = r.emit


def emit(name, value, unit, digits=3, inputs=()):
    """Counts above a million are shown in millions; exact counts keep all digits."""
    if value >= 1e6:
        return _emit(name, value / 1e6, "million " + unit, 3, inputs)
    if float(value).is_integer() and unit not in ("Tb/s", "Pb/s", "%", ""):
        digits = max(digits, len(str(int(value))))
    return _emit(name, value, unit, digits, inputs)


r.emit = emit

# ---------------------------------------------------------------- 1. checks
K_AF = cl.cond("ch05.clos.fattree_hosts_k48", "k")
n_af = cl.fattree_hosts(K_AF, 3)
assert n_af == L("ch05.clos.fattree_hosts_k48")
assert (K_AF / 2) ** 2 == L("ch05.clos.fattree_paths_k48")
s_af = cl.fattree_switches(K_AF, 3)
assert s_af == 5 * K_AF ** 2 / 4
r.emit("af_k", K_AF, "ports", 3, ["ch05.clos.fattree_hosts_k48"])
r.emit("af_hosts", n_af, "hosts", 5, ["ch05.clos.fattree_hosts_k48"])
r.emit("af_switches", s_af, "switches", 4, ["ch05.clos.fattree_hosts_k48"])
r.emit("af_core", (K_AF / 2) ** 2, "switches", 3, ["ch05.clos.fattree_hosts_k48"])
r.emit("af_pods", K_AF, "pods", 2, ["ch05.clos.fattree_hosts_k48"])
r.emit("af_sw_links", 2 * n_af, "links", 5, ["ch05.clos.fattree_hosts_k48"])

# DGX H100 SuperPOD: infer the radix from the 56-SU row (512 leaf, 512 spine, 256 core).
DGX = "ch05.clos.dgx_h100_16k_cables"
n_dgx = L(DGX)
assert cl.rec(DGX)["conditions"]["gpus"] == 16384
leaf, spine, core = 512, 512, 256
assert cl.cond(DGX, "switches") == f"{leaf} leaf, {spine} spine, {core} core"
k_dgx = 2 * n_dgx / leaf                      # each leaf has k/2 host ports
assert k_dgx == 64
assert n_dgx / (k_dgx / 2) == spine and n_dgx / k_dgx == core   # same counting as fattree_switches
assert cl.fattree_hosts(k_dgx, 3) >= n_dgx
r.emit("dgx_k", k_dgx, "ports", 2, [DGX])
r.emit("dgx_max3", cl.fattree_hosts(k_dgx, 3), "GPUs", 5, [DGX])
r.emit("dgx_fill", n_dgx / cl.fattree_hosts(k_dgx, 3) * 100, "%", 2, [DGX])
# 4-SU two-tier row: 32 leaf, 16 spine for 1024 GPU ports (1016 used)
SU4 = "ch05.clos.dgx_h100_4su_switches"
lf4, sp4 = L(SU4, "lo"), L(SU4, "hi")
ports4 = lf4 * k_dgx / 2
assert ports4 == 1024 and lf4 * (k_dgx / 2) / k_dgx == sp4
r.emit("dgx4_ports", ports4, "GPU ports", 4, [SU4, DGX])
r.emit("dgx_max2", cl.fattree_hosts(k_dgx, 2), "GPUs", 4, [DGX])

# ---------------------------------------------------------------- 2. 51.2T switch
BC = "ch05.pw.broadcom_51t_128_modules"
n_mod = L(BC)
port_g = cl.cond(BC, "module_rate_G")
cap_t = n_mod * port_g / 1e3                  # Tb/s
assert abs(cap_t - cl.cond("ch05.ai.hpn_segment_1k", "switch_chip_Tbps")) < 1e-9   # same 51.2T class as HPN
r.emit("sw_cap", cap_t, "Tb/s", 3, [BC])
for tag, prate in (("400", 400), ("800", 800)):
    k = cap_t * 1e3 / prate
    r.emit(f"k{tag}", k, "ports", 3, [BC])
    for l in (2, 3):
        n = cl.fattree_hosts(k, l)
        s = cl.fattree_switches(k, l)
        hl, sl = cl.fattree_links(k, l)
        bis = n / 2 * prate * 1e9                # one-direction min-cut capacity
        r.emit(f"k{tag}_l{l}_hosts", n, "hosts", 4, [BC])
        r.emit(f"k{tag}_l{l}_sw", s, "switches", 4, [BC])
        r.emit(f"k{tag}_l{l}_swlinks", sl, "links", 4, [BC])
        # ASSUMPTION (prose): every switch-to-switch link is optical, two transceiver ports per link
        r.emit(f"k{tag}_l{l}_xcvr", 2 * sl, "transceiver ports", 4, [BC])
        r.emit(f"k{tag}_l{l}_xcvr_per_host", 2 * sl / n, "per host", 2, [BC])
        r.emit(f"k{tag}_l{l}_bis", bis / 1e15, "Pb/s", 3, [BC])
        r.emit(f"k{tag}_l{l}_tot", 2 * bis / 1e15, "Pb/s", 3, [BC])
        r.emit(f"k{tag}_l{l}_sw_per_khost", s / n * 1e3, "switches per 1000 hosts", 3, [BC])
    r.emit(f"k{tag}_paths3", (k / 2) ** 2, "paths", 4, [BC])
# switches per host fall as 1/k: check (2l-1)/(k/2)
assert abs(cl.fattree_switches(128, 3) / cl.fattree_hosts(128, 3) - (2 * 3 - 1) / 128) < 1e-12

# Meta 129k-GPU cluster: tiers needed at each radix
META = "ch05.ai.meta_129k_h100"
for tag, k in (("400", 128), ("800", 64)):
    r.emit(f"meta_tiers_k{tag}", cl.tiers_needed(L(META), k), "tiers", 1, [META, BC])
assert cl.tiers_needed(L(META), 64) == 4 and cl.tiers_needed(L(META), 128) == 3

# ---------------------------------------------------------------- 3. oversubscription
OS = "ch05.clos.oversub_5to1_meaning"
sig5 = 5.0
assert abs(100 / sig5 - L(OS)) < 1e-9
for tag, sig in (("lo", L("ch05.clos.oversub_typical_2008", "lo")), ("hi", L("ch05.clos.oversub_typical_2008", "hi"))):
    r.emit(f"os_{tag}", sig, "", 2, ["ch05.clos.oversub_typical_2008"])
    r.emit(f"os_gain_{tag}", 2 * sig / (1 + sig), "", 3, ["ch05.clos.oversub_typical_2008"])
    r.emit(f"os_frac_{tag}", 100 / sig, "%", 3, ["ch05.clos.oversub_typical_2008"])
# ASSUMPTION: illustrative 3:1 leaf oversubscription on the 128 x 400G three-tier fabric
SIG_EX = 3.0
n3 = cl.fattree_hosts(128, 3, SIG_EX)
hl, sl = cl.fattree_links(128, 3, SIG_EX)
r.emit("ex_sigma", SIG_EX, "", 1)
r.emit("ex_sigma_hosts", n3, "hosts", 4, [BC])
r.emit("ex_sigma_xcvr_per_host", 2 * sl / n3, "per host", 3, [BC])
r.emit("ex_sigma_sw", cl.fattree_switches(128, 3, SIG_EX), "switches", 4, [BC])
assert abs(n3 / cl.fattree_hosts(128, 3) - 1.5) < 1e-12

# Alibaba HPN dual-plane bound: each NIC port is 200G, so a 51.2T chip has radix 256 per plane
HPN = "ch05.ai.hpn_segment_1k"
nic = cl.cond("ch05.ai.hpn_host_3p2t", "nic")          # '2x200G'
p_hpn = float(nic.split("x")[1].rstrip("G"))
k_hpn = cl.cond(HPN, "switch_chip_Tbps") * 1e3 / p_hpn
r.emit("hpn_k", k_hpn, "ports", 3, [HPN, "ch05.ai.hpn_host_3p2t"])
r.emit("hpn_bound2", cl.fattree_hosts(k_hpn, 2), "GPUs", 4, [HPN])
r.emit("hpn_bound2_400", cl.fattree_hosts(128, 2), "GPUs", 4, [HPN])
assert cl.fattree_hosts(k_hpn, 2) > L("ch05.ai.hpn_pod_15k") > cl.fattree_hosts(128, 2)
r.emit("hpn_gpu_per_tor", L(HPN) / cl.cond(HPN, "tors_per_segment"), "GPUs per ToR", 3, [HPN])

# MegaScale: Tomahawk 4, 64 x 400G, 1:1 at every layer
MS = "ch05.ai.megascale_tor_split"
k_ms = 64
assert abs(L(MS) * 1e3 / 400 - k_ms) < 1e-9
r.emit("ms_k", k_ms, "ports", 2, [MS])
r.emit("ms_max3", cl.fattree_hosts(k_ms, 3), "400G ports", 5, [MS])

# ---------------------------------------------------------------- 4. Clos 1953
for N, rid in ((36, "ch05.clos.clos_n36_crosspoints"), (1000, "ch05.clos.clos_n1000_crosspoints")):
    c3 = 6 * N ** 1.5 - 3 * N
    assert abs(c3 - L(rid)) < 1.0, (c3, L(rid))
    r.emit(f"clos_c3_{N}", c3, "crosspoints", 6, [rid])
    r.emit(f"clos_sq_{N}", N ** 2, "crosspoints", 7, [rid])
    r.emit(f"clos_ratio_{N}", c3 / N ** 2 * 100, "%", 3, [rid])
r.emit("clos_m36", 2 * 6 - 1, "middle switches", 2, ["ch05.clos.clos_n36_crosspoints"])

# ---------------------------------------------------------------- figure
plt = cl.setup_mpl()
ks = np.arange(16, 260, 2)
fig, ax = plt.subplots(figsize=(7.2, 4.4))
for i, l in enumerate((2, 3, 4)):
    ax.plot(ks, [cl.fattree_hosts(k, l) for k in ks], color=cl.COLORS[i], label=f"{l} tiers, $N=2(k/2)^{{{l}}}$")
ax.plot(ks, [cl.fattree_hosts(k, 3, SIG_EX) for k in ks], color=cl.COLORS[1], ls="--", lw=1.4,
        label="3 tiers, leaf oversubscribed 3:1")
ax.axhline(L(META), color=cl.GRAY, lw=1, ls=":")
ax.text(150, L(META) * 0.55, "Meta 129k-GPU cluster (ledger)", fontsize=8.5)
for k, lab, l in ((48, "Al-Fares k=48", 3), (64, "51.2T as 64x800G", 3), (128, "51.2T as 128x400G", 3)):
    ax.plot([k], [cl.fattree_hosts(k, l)], "o", color=cl.COLORS[3], ms=6)
    ax.annotate(lab, (k, cl.fattree_hosts(k, l)), xytext=(4, -12), textcoords="offset points", fontsize=8.5)
ax.set_yscale("log")
ax.set_xlabel("Switch radix $k$ (ports at the host link rate)")
ax.set_ylabel("Hosts at full bisection, $N$")
ax.set_xlim(16, 260)
ax.legend(fontsize=8.5, loc="upper left")
ax.set_title("Computed: folded-Clos host count versus radix", fontsize=10)
cl.savefig(fig, "fattree_scaling")

r.save()
