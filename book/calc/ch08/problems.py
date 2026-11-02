"""Numerical answers for the Chapter 8 problem set."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import ch08lib as cl

r = Results()
OUT = pathlib.Path(__file__).parent / "out"
ex81s = json.loads((OUT / "ex81_srlg.json").read_text())
ex84 = json.loads((OUT / "ex84_radwan.json").read_text())
tkm = cl.us_per_km()
MI = cl.MI_KM

# P1: bases. ASSUMPTION: 144 fibers per cable on every route; 4,000 km coast-to-coast fiber path.
RM = "ch08.carrier.lumen_route_miles_2025"
F = 144
r.emit("p1_F", F, "fibers", 3)
r.emit("p1_route_km", L(RM) * MI / 1e3, "thousand route-km", 3, [RM])
r.emit("p1_fiber_km", L(RM) * MI * F / 1e6, "million fiber-km", 3, [RM])
D = 4000.0
r.emit("p1_D", D, "km", 2)
r.emit("p1_ow", D * tkm / 1e3, "ms", 3, [cl.NG_ID, cl.C_ID])
r.emit("p1_rtt", 2 * D * tkm / 1e3, "ms", 3, [cl.NG_ID, cl.C_ID])

# P2: SRLG
p2 = ex81s["p_2"]["value"] / 100
p3 = ex81s["p_3"]["value"] / 100
p4 = L("ch08.intertubes.share_ge4") / 100
r.emit("p2_exact23", 100 * (p2 + p3), "%", 3, ["ch08.intertubes.share_ge2", "ch08.intertubes.share_ge4"])
r.emit("p2_two_cuts", 100 * p4 ** 2, "%", 3, ["ch08.intertubes.share_ge4"])
r.emit("p2_ek_lo", ex81s["ek_lo"]["value"], "ISPs", 3)
r.emit("p2_ek_hi", ex81s["ek_hi"]["value"], "ISPs", 3)

# P3: peering at 2015 prices
CP, TE, P15 = "ch08.peering.cost_assumption", "ch08.peering.effective_10g_bw", "ch08.peering.transit_price_2015"
save_port = L(P15) * L(TE)
r.emit("p3_pstar", L(CP) / L(TE), "USD/(Mb/s·month)", 3, [CP, TE])
r.emit("p3_save_port", save_port, "USD/month", 3, [P15, TE])
r.emit("p3_ratio", save_port / L(CP), "1", 3, [P15, TE, CP])
r.emit("p3_cost_needed", save_port, "USD/month", 3, [P15, TE])

# P4: growth
G = "ch08.b4after.doubling_time"
r.emit("p4_months_1000", math.log2(1000) * L(G), "months", 3, [G])
r.emit("p4_years_1000", math.log2(1000) * L(G) / 12, "years", 3, [G])
E = "ch08.ebb.traffic_growth"
r.emit("p4_ebb_td", 12 * 8 * math.log(2) / math.log(L(E)), "months", 3, [E])

# P5: planes. Utilization ceiling to survive k simultaneous plane failures with n planes
P = "ch08.ebb.planes"
n = int(L(P))
r.emit("p5_k1", 100 * (n - 1) / n, "%", 3, [P])
r.emit("p5_k2", 100 * (n - 2) / n, "%", 3, [P])
r.emit("p5_b4", L("ch08.b4.avg_util"), "%", 2, ["ch08.b4.avg_util"])

# P6: RADWAN margins
r.emit("p6_m200", ex84["m200"]["value"], "dB", 3)
r.emit("p6_reach_ratio", 100 * 10 ** (-ex84["m200"]["value"] / 10), "%", 3)
r.emit("p6_reach_200", L("ch08.radwan.reach_qpsk") * 10 ** (-ex84["m200"]["value"] / 10), "km", 3,
       ["ch08.radwan.reach_qpsk", "ch08.radwan.snr_req_100g"])
r.emit("p6_hi_asym", ex84["dRdB_hi"]["value"], "Gb/s per dB", 3)

# P7: churn. A 150 Gb/s link reconfigured once; and churn-equivalent of the fast method
RC, RF = "ch08.radwan.reconfig_latency", "ch08.radwan.reconfig_fast"
r.emit("p7_slow", 150e9 * L(RC) / 8 / 1e9, "GB", 3, [RC])
r.emit("p7_fast", 150e9 * L(RF) * 1e-3 / 8 / 1e6, "MB", 3, [RF])
# How many slow changes fit in the 99.99 % unavailability budget of a 30-day window
A = "ch08.b4after.availability"
budget = 30 * 86400 * (1 - L(A, "hi") / 100)
r.emit("p7_budget_s", budget, "s", 3, [A])
r.emit("p7_changes", budget / L(RC), "changes per 30 days", 3, [A, RC])
r.emit("p7_changes_fast", budget / (L(RF) * 1e-3), "changes per 30 days", 3, [A, RF])

# P8: regional distance under the 1.2 ms RTT, SMF vs hollow core (n_g of NANF, Chapter 1)
RTT = "ch08.iris.rtt_example"
ng_h = L("ch01.hcf.ng_nanf_vs_smf28", "lo")
c = L(cl.C_ID)
d_smf = L(RTT) * 1e-3 / 2 * c / L(cl.NG_ID) / 1e3
d_hcf = L(RTT) * 1e-3 / 2 * c / ng_h / 1e3
r.emit("p8_smf", d_smf, "km", 3, [RTT, cl.NG_ID])
r.emit("p8_hcf", d_hcf, "km", 3, [RTT, "ch01.hcf.ng_nanf_vs_smf28"])
r.emit("p8_gain", 100 * (d_hcf / d_smf - 1), "%", 2, [RTT, cl.NG_ID, "ch01.hcf.ng_nanf_vs_smf28"])
r.emit("p8_area", (d_hcf / d_smf) ** 2, "1", 3, [RTT])

# P9: four campuses, step time 5 s (ASSUMPTION), else as Section 8.5
ex85 = json.loads((OUT / "ex85_multicampus.json").read_text())
S, T = 4, 5.0
X = ex85["grad_tb"]["value"] * 1e12
alpha = ex85["alpha_ms"]["value"] * 1e-3
f = ex85["f"]["value"] / 100
Dv = 2 * (S - 1) / S * X
bw = Dv / (f * T - 2 * (S - 1) * alpha)
r.emit("p9_T", T, "s", 2)
r.emit("p9_D", Dv / 1e12, "Tb", 3)
r.emit("p9_bw", bw / 1e12, "Tb/s", 3)
r.emit("p9_lat", 2 * (S - 1) * alpha * 1e3, "ms", 3)
r.emit("p9_bdp", bw * 2 * alpha / 8 / 1e9, "GB", 3)
r.save()
