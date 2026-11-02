"""Section 8.1 worked example: conduit sharing and shared-risk link groups.

From the published InterTubes tenancy distribution (fractions of the 542
long-haul conduits shared by >= 2, >= 3, >= 4 and > 17 of 20 ISPs) we build the
probability mass function of K, the number of ISPs whose fiber is cut when a
single conduit is cut, assuming the cut falls on a conduit chosen uniformly at
random. The 4..17 bin is not resolved by the source; we carry it as a bin and
give bounds (all mass at 4, or all at 17) and an assumed uniform split.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import numpy as np
import ch08lib as cl

r = Results()
MAP = "ch08.intertubes.map_size"
G2, G3, G4 = "ch08.intertubes.share_ge2", "ch08.intertubes.share_ge3", "ch08.intertubes.share_ge4"
G18 = "ch08.intertubes.conduits_gt17"
N2 = "ch08.intertubes.shared_by_ge2_count"
ISP = "ch08.intertubes.isp_count"
ins = [MAP, G2, G3, G4, G18, N2, ISP]

n_cond = int(cl.rec(MAP)["value"][2])
n_isp = 20      # study scope stated in the quote of ch08.intertubes.isp_count
assert "20 ISPs" in cl.rec(ISP)["quote"]
# ASSUMPTION: a single cut falls on one conduit chosen uniformly at random
# (not weighted by conduit length or by exposure to construction).
# ASSUMPTION: every conduit in the map carries at least one ISP (K >= 1), true by construction of the map.

c2 = round(L(G2) / 100 * n_cond)
c3 = round(L(G3) / 100 * n_cond)
c4 = round(L(G4) / 100 * n_cond)
c18 = int(L(G18))
assert c2 == int(L(N2)), "percentage and count of >=2-ISP conduits must agree"
for c, g in ((c3, G3), (c4, G4)):
    assert abs(100 * c / n_cond - L(g)) < 0.01, "counts must reproduce the published percentages"
bins = {"1": n_cond - c2, "2": c2 - c3, "3": c3 - c4, "4-17": c4 - c18, "18-20": c18}
assert sum(bins.values()) == n_cond
for k, v in bins.items():
    tag = k.replace("-", "_")
    r.emit(f"n_{tag}", v, "conduits", 3, ins)
    r.emit(f"p_{tag}", 100 * v / n_cond, "%", 3, ins)
r.emit("n_cond", n_cond, "conduits", 3, [MAP])
r.emit("n_isp", n_isp, "ISPs", 2, [ISP])
r.emit("c3", c3, "conduits", 3, [G3])
r.emit("c4", c4, "conduits", 3, [G4])
r.emit("p_ge2", L(G2), "%", 4, [G2])
r.emit("p_ge18", 100 * c18 / n_cond, "%", 2, [G18, MAP])

# pmf under three resolutions of the 4..17 bin
def pmf(mode):
    p = np.zeros(n_isp + 1)
    p[1], p[2], p[3] = bins["1"], bins["2"], bins["3"]
    if mode == "lo":
        p[4] += bins["4-17"]; p[18] += c18
    elif mode == "hi":
        p[17] += bins["4-17"]; p[20] += c18
    else:  # ASSUMPTION (central case): uniform over 4..17 and over 18..20
        p[4:18] += bins["4-17"] / 14.0; p[18:21] += c18 / 3.0
    return p / n_cond

k = np.arange(n_isp + 1)
res = {}
for mode in ("lo", "mid", "hi"):
    p = pmf(mode)
    assert abs(p.sum() - 1) < 1e-12
    ek = (k * p).sum()
    ekk = (k * (k - 1) * p).sum()
    # Exchangeable-ISP model: if ISP A is in a conduit, the chance ISP B is too
    # is E[K(K-1)] / ((n-1) E[K])   (size-biased sampling of conduits by tenancy)
    q = ekk / ((n_isp - 1) * ek)
    res[mode] = (ek, q)
    r.emit(f"ek_{mode}", ek, "ISPs", 3, ins)
    r.emit(f"q_{mode}", 100 * q, "%", 2, ins)
    # fraction of ISP-conduit tenancies that sit in conduits shared by >= 4 ISPs
    r.emit(f"tenancy_ge4_{mode}", 100 * (k[4:] * p[4:]).sum() / ek, "%", 3, ins)
assert res["lo"][0] < res["mid"][0] < res["hi"][0]
assert res["lo"][1] < res["mid"][1] < res["hi"][1]

# Two-path diversity: a customer buys two ISPs over a path of m conduits each,
# and the paths share the same rights-of-way (the InterTubes situation). Under the
# exchangeable model the chance that a cut of a given conduit on A's path also hits B:
# q per conduit; probability that at least one of m conduits is shared: 1-(1-q)^m.
# ASSUMPTION: m = 5 conduits on a typical intercity path; conduit sharing independent.
M = 5
r.emit("m_path", M, "conduits", 1)
for mode in ("lo", "mid", "hi"):
    q = res[mode][1]
    r.emit(f"path_shared_{mode}", 100 * (1 - (1 - q) ** M), "%", 2, ins)

# ---------- Line of sight vs right of way latency gap -> excess fiber length
tkm = cl.us_per_km()
LM = "ch08.intertubes.los_vs_row_latency_median"
L75 = "ch08.intertubes.los_vs_row_latency_p75"
r.emit("los_med_km", L(LM) / tkm, "km", 2, [LM, cl.NG_ID, cl.C_ID])
r.emit("los_p75_km", L(L75) / tkm, "km", 2, [L75, cl.NG_ID, cl.C_ID])
# The paper's own conversions ('approximately 20 km', 'more than 100 km') imply 5 us/km
assert abs(L(LM) / tkm - 20) < 1.0 and abs(L(L75) / tkm - 100) < 5.0
r.emit("los_med_rtt", 2 * L(LM) / 1e3, "ms", 2, [LM])
r.emit("lh_def_km", L("ch08.intertubes.longhaul_definition") * cl.MI_KM, "km", 2,
       ["ch08.intertubes.longhaul_definition"])

# ---------- figure: pmf (bins) and CCDF points
plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.0, 3.8))
labels = list(bins.keys())
vals = [100 * v / n_cond for v in bins.values()]
a1.bar(range(len(labels)), vals, color=cl.COLORS[0], width=0.65)
for i, v in enumerate(vals):
    a1.text(i, v + 1, f"{v:.1f}%", ha="center", fontsize=9)
a1.set_xticks(range(len(labels)), labels)
a1.set_xlabel("ISPs sharing the conduit, K")
a1.set_ylabel("Share of the 542 conduits (%)")
a1.set_ylim(0, 60)
xs = [1, 2, 3, 4, 18]
ys = [100, L(G2), L(G3), L(G4), 100 * c18 / n_cond]
a2.step([1, 2, 3, 4, 18, 21], ys + [0], where="post", color=cl.GRAY, lw=1, ls=":")
a2.plot(xs, ys, "o", color=cl.COLORS[1], ms=7, label="published points")
for mode, col, lab in (("lo", cl.COLORS[2], "4-17 bin at K=4"), ("hi", cl.COLORS[3], "4-17 bin at K=17")):
    p = pmf(mode)
    ccdf = [100 * p[kk:].sum() for kk in range(1, 21)]
    a2.step(range(1, 21), ccdf, where="post", color=col, lw=1.6, label=lab)
a2.set_xlabel("k")
a2.set_ylabel(r"P(K $\geq$ k) for a random conduit cut (%)")
a2.set_xlim(0.5, 20.5)
a2.set_ylim(0, 105)
a2.legend(fontsize=8.5, loc="upper right")
fig.suptitle("Computed from published InterTubes fractions (US long-haul, 20 ISPs, 542 conduits)", fontsize=10)
fig.tight_layout()
cl.savefig(fig, "conduit_sharing")
r.save()
