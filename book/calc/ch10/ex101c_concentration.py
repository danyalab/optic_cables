"""Worked example 10.1 (concentration): what HHI can and cannot say without share data.

No tier-A/B source in the ledger gives vendor market shares for any tier of
the optical supply chain (ch10_gaps.md, item 1). This script therefore uses
only the DOJ/FTC definitions (ch10.eq.hhi, ch10.eq.hhi_equal_firms) and
derives three share-free results:

1. HHI of N equal firms, 10^4/N, and the smallest N that is not "highly
   concentrated" under the 1,800 threshold;
2. the bounds s_1^2 <= HHI <= 100 s_1 in terms of the leading firm's share
   s_1 (percent), and the leader shares that decide the classification on
   their own;
3. the lower bound HHI >= CR_n^2 / n, which converts a published n-firm
   concentration ratio into a guaranteed minimum HHI.

Draws Figure 10.2.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch10lib as cl

r = Results()
HI, MONO, DELTA = ("ch10.chain.hhi_highly_concentrated", "ch10.chain.hhi_monopoly",
                   "ch10.chain.hhi_significant_change")
T, HMAX = L(HI), L(MONO)
ins = [HI, MONO]

# 1. Equal firms: HHI = N (100/N)^2 = 10^4 / N
def hhi_equal(n):
    return n * (100.0 / n) ** 2

assert math.isclose(hhi_equal(1), HMAX)
assert math.isclose(hhi_equal(5), 2000.0)                 # Guidelines footnote example
assert round(hhi_equal(6)) == 1667                         # Guidelines footnote example
n_star = HMAX / T
n_min_ok = math.floor(n_star) + 1
assert hhi_equal(n_min_ok) <= T < hhi_equal(n_min_ok - 1)
r.emit("n_star", n_star, "firms", 3, ins)
r.emit("n_min_ok", n_min_ok, "firms", 1, ins)
r.emit("hhi5", hhi_equal(5), "1", 4, ins)
r.emit("hhi6", hhi_equal(6), "1", 4, ins)
r.emit("threshold", T, "1", 4, [HI])
r.emit("delta", L(DELTA), "1", 3, [DELTA])

# 2. Leader-share bounds: sum s_i^2 >= s_1^2 and sum s_i^2 <= s_1 * sum s_i = 100 s_1
s1_sure_high = math.sqrt(T)        # s_1 above this => HHI > T whatever the rest
s1_sure_low = T / 100.0            # s_1 at or below this => HHI <= T whatever the rest
r.emit("s1_sure_high", s1_sure_high, "%", 3, [HI])
r.emit("s1_sure_low", s1_sure_low, "%", 3, [HI])

# Brute-force check of both bounds on random share vectors.
rng = np.random.default_rng(10)
for _ in range(2000):
    k = rng.integers(1, 15)
    s = rng.dirichlet(np.ones(k)) * 100
    h = float(np.sum(s ** 2))
    assert s.max() ** 2 - 1e-9 <= h <= 100 * s.max() + 1e-9

# 3. CR_n lower bound: HHI >= CR_n^2 / n (Cauchy-Schwarz on the top n shares)
for _ in range(2000):
    k = rng.integers(2, 15)
    s = np.sort(rng.dirichlet(np.ones(k)) * 100)[::-1]
    for n in range(1, k + 1):
        assert float(np.sum(s ** 2)) >= s[:n].sum() ** 2 / n - 1e-9
# Smallest CR_4 that guarantees "highly concentrated": CR_4^2/4 > T  =>  CR_4 > 2 sqrt(T)
r.emit("cr4_sure_high", 2 * math.sqrt(T), "%", 3, [HI])
r.emit("cr1_equiv", math.sqrt(T), "%", 3, [HI])

# Numbers-equivalent of the threshold (1/HHI in fractional shares)
r.emit("neq_threshold", HMAX / T, "firms", 3, ins)
r.save()

# ---------------- Figure 10.2 ----------------
plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
n = np.arange(1, 13)
a1.plot(n, [hhi_equal(k) for k in n], "o-", color=cl.COLORS[0], ms=5)
a1.axhline(T, color=cl.COLORS[1], lw=1.4, ls="--")
a1.text(12, T + 250, f"highly concentrated above {T:,.0f}", ha="right", color=cl.COLORS[1], fontsize=9.5)
a1.set_xlabel("number of equal firms N")
a1.set_ylabel("HHI")
a1.set_title("(a) N equal firms: HHI = 10⁴/N", fontsize=11)
a1.set_ylim(0, 10500)

s1 = np.linspace(0, 100, 401)
a2.fill_between(s1, s1 ** 2, 100 * s1, color=cl.COLORS[0], alpha=0.18, lw=0)
a2.plot(s1, s1 ** 2, color=cl.COLORS[0], lw=1.6)
a2.plot(s1, 100 * s1, color=cl.COLORS[0], lw=1.6)
a2.axhline(T, color=cl.COLORS[1], lw=1.4, ls="--")
a2.axvline(s1_sure_low, color=cl.COLORS[2], lw=1.0, ls=":")
a2.axvline(s1_sure_high, color=cl.COLORS[2], lw=1.0, ls=":")
a2.text(14, 5200, "HHI ≤ 100 s₁", color=cl.COLORS[0], fontsize=9.5)
a2.text(66, 2600, "HHI ≥ s₁²", color=cl.COLORS[0], fontsize=9.5)
a2.text(s1_sure_low + 1, 9000, "s₁ = 18", color=cl.COLORS[2], fontsize=9)
a2.text(s1_sure_high + 1, 9000, "s₁ = 42.4", color=cl.COLORS[2], fontsize=9)
a2.set_xlabel("leading firm's share s₁ (%)")
a2.set_ylabel("HHI")
a2.set_title("(b) feasible HHI given only the leader's share", fontsize=11)
a2.set_xlim(0, 100)
a2.set_ylim(0, 10500)
fig.tight_layout()
cl.savefig(fig, "hhi_bounds")
