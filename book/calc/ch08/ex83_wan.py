"""Section 8.3: growth, utilization and availability arithmetic for B4, SWAN, EBB."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import ch08lib as cl

r = Results()
# ---------- utilization (B4 vs conventional)
U, OP, B4U = "ch08.b4.typical_wan_util", "ch08.b4.overprovisioning", "ch08.b4.avg_util"
r.emit("gain_lo", L(B4U) / L(U, "hi"), "1", 3, [U, B4U])
r.emit("gain_hi", L(B4U) / L(U, "lo"), "1", 3, [U, B4U])
r.emit("gain_mid", L(B4U) / L(U, "mid"), "1", 2, [U, B4U])
# Headroom relative to a fully loaded link, 1/u, is 2.5-3.3x for u = 30-40 %; the paper's
# '2-3x' overlaps this range (it does not say what the factor is relative to).
r.emit("op_lo", 100 / L(U, "hi"), "1", 3, [U])
r.emit("op_hi", 100 / L(U, "lo"), "1", 3, [U])
assert 100 / L(U, "hi") <= L(OP, "hi") and L(OP, "lo") <= 100 / L(U, "lo"), "ranges must overlap"
assert L(B4U) / L(U, "hi") < L(OP, "lo") < L(B4U) / L(U, "lo")

# ---------- growth: B4 (100x in 5 years) vs stated 9-month doubling
G, TD = "ch08.b4after.traffic_growth_5y", "ch08.b4after.doubling_time"
months = 60.0          # 'five year period' in the quote of the growth record
assert "five year" in cl.rec(G)["quote"]
td = months * math.log(2) / math.log(L(G))
r.emit("b4_ndoublings", math.log2(L(G)), "doublings", 3, [G])
r.emit("b4_td_months", td, "months", 3, [G])
r.emit("b4_td_diff_pct", 100 * (td - L(TD)) / L(TD), "%", 2, [G, TD])
assert abs(td - L(TD)) < 0.5, "100x in 60 months must match a ~9-month doubling"
r.emit("b4_annual_factor", L(G) ** (12 / months), "1", 3, [G])
r.emit("b4_annual_pct", 100 * (L(G) ** (12 / months) - 1), "%/yr", 3, [G])
r.emit("b4_5y_from_9m", 2 ** (months / L(TD)), "1", 3, [TD])
# Zhao 2013: Internet traffic 50-60 %/yr -> doubling time
Z = "ch08.google_optical.traffic_growth"
for tag in ("lo", "hi"):
    g = 1 + L(Z, tag) / 100
    r.emit(f"zhao_td_{tag}", 12 * math.log(2) / math.log(g), "months", 3, [Z])
# EBB: >100x over 2015-2023 (8 years) -> doubling time (upper bound since growth is a lower bound)
E = "ch08.ebb.traffic_growth"
per = cl.cond(E, "period")
y0, y1 = (int(x) for x in per.split("-"))
ebb_td = 12 * (y1 - y0) * math.log(2) / math.log(L(E))
r.emit("ebb_years", y1 - y0, "years", 1, [E])
r.emit("ebb_td_months", ebb_td, "months", 3, [E])
r.emit("ebb_annual_pct", 100 * (L(E) ** (1 / (y1 - y0)) - 1), "%/yr", 2, [E])

# ---------- availability: minutes of unavailability in a 30-day window
A = "ch08.b4after.availability"
WIN = 30 * 24 * 60
r.emit("win_min", WIN, "min", 5)
r.emit("unavail_lo", WIN * (1 - L(A, "lo") / 100), "min", 3, [A])
r.emit("unavail_hi", WIN * (1 - L(A, "hi") / 100), "min", 3, [A])
S = "ch08.blastshield.slo"
r.emit("slo0_min", WIN * (1 - L(S, "lo") / 100), "min", 2, [S])
r.emit("slo1_min", WIN * (1 - L(S, "hi") / 100), "min", 2, [S])

# ---------- B4 site generations
ST, SA = "ch08.b4after.stargate_capacity", "ch08.b4after.saturn_capacity"
r.emit("sg_over_sat_lo", L(ST) / L(SA, "hi"), "1", 3, [ST, SA])
r.emit("sg_over_sat_hi", L(ST) / L(SA, "lo"), "1", 3, [ST, SA])
r.emit("sg_fiber_pairs_2013", L(ST) / L("ch08.google_optical.fiber_pair_capacity"), "fiber pairs", 2,
       [ST, "ch08.google_optical.fiber_pair_capacity"])

# ---------- EBB planes: utilization ceiling that survives one plane failure
P = "ch08.ebb.planes"
for tag, n in (("4", 4), ("8", int(L(P)))):
    r.emit(f"plane_ceiling_{tag}", 100 * (n - 1) / n, "%", 3, [P])
    r.emit(f"plane_loss_{tag}", 100 / n, "%", 3, [P])
assert int(L(P)) == 8

# ---------- SWAN numbers
SW = "ch08.swan.gain_vs_mpls"
r.emit("swan_factor", 1 + L(SW) / 100, "1", 2, [SW])
r.emit("blast_remaining", 100 - L("ch08.blastshield.loss_reduction"), "%", 2, ["ch08.blastshield.loss_reduction"])
r.save()
