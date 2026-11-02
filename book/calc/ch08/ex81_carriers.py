"""Section 8.1: carrier footprint metrics on comparable bases.

Route-miles vs fiber-miles, conversion to km (for the Section 9.6 comparison),
the AT&T purchase of Lumen's consumer fiber business per location, and
consistency checks on tier-C company statements (contested box only).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch08lib as cl

r = Results()
MI = cl.MI_KM
r.emit("mi_km", MI, "km", 7)

# ---------- Lumen 10-K (tier B)
RM = "ch08.carrier.lumen_route_miles_2025"
rm = L(RM)
r.emit("lumen_route_km", rm * MI, "route-km", 3, [RM])
r.emit("lumen_route_km_k", rm * MI / 1e3, "thousand route-km", 3, [RM])
ON = "ch08.carrier.lumen_onnet_buildings_2025"
metros = cl.cond(ON, "metro_markets")
r.emit("lumen_metros", metros, "metro markets", 3, [ON])
r.emit("lumen_bldg_per_metro", L(ON) / metros, "buildings per market", 2, [ON])
# Round-trip propagation across 1000 route-km of SMF (one-way and RTT stated separately)
tkm = cl.us_per_km()
r.emit("us_per_km", tkm, "µs/km", 4, [cl.NG_ID, cl.C_ID])
r.emit("us_per_mi", tkm * MI, "µs/mi", 3, [cl.NG_ID, cl.C_ID])

# ---------- AT&T purchase of Lumen Mass Markets FTTH (tier B, both 10-Ks)
P = "ch08.carrier.lumen_att_sale_proceeds"
LOC = "ch08.carrier.att_lumen_fiber_locations"
proceeds = L(P) * 1e9
locs = L(LOC)
cust = cl.cond(LOC, "customers")
r.emit("sale_states", cl.cond(P, "states"), "states", 2, [P])
r.emit("sale_per_location", proceeds / locs, "USD per location", 3, [P, LOC])
r.emit("sale_per_customer", proceeds / cust, "USD per customer", 3, [P, LOC])
r.emit("sale_customers_m", cust / 1e6, "million customers", 2, [LOC])
r.emit("sale_take_rate", 100 * cust / locs, "%", 2, [LOC])
assert proceeds / locs < proceeds / cust
# AT&T consumer fiber penetration, end of 2025
AC = "ch08.carrier.att_fiber_customers_2025"
AL = "ch08.carrier.att_fiber_locations_2025"
r.emit("att_take_rate", 100 * L(AC) / L(AL, "lo"), "%", 3, [AC, AL])
r.emit("att_loc_growth", L(AL, "hi") / L(AL, "lo"), "1", 3, [AL])
r.emit("att_lumen_share", 100 * locs / L(AL, "lo"), "%", 2, [LOC, AL])

# ---------- Tier-C company statements (contested box only)
PCF = "ch08.carrier.lumen_pcf_contracts_8p5b"
PCF2 = "ch08.carrier.lumen_pcf_contracts_q2_2025"
REV = "ch08.carrier.lumen_pcf_annual_revenue"
assert "20-year" in cl.rec(REV)["quote"]
YEARS = 20
undiscounted = L(REV) * 1e6 * YEARS
r.emit("pcf_rev_x20", undiscounted / 1e9, "billion USD", 2, [REV])
r.emit("pcf_ratio", undiscounted / (L(PCF) * 1e9), "1", 2, [REV, PCF])
r.emit("pcf_growth", L(PCF2) - L(PCF), "billion USD", 1, [PCF, PCF2])

FM25 = "ch08.carrier.lumen_intercity_fiber_miles_2025"
FM28 = "ch08.carrier.lumen_intercity_fiber_miles_2028"
NEW = "ch08.carrier.lumen_2025_new_fiber_vs_route_miles"
r.emit("lumen_fiber_km_2025", L(FM25) * MI / 1e6, "million fiber-km", 3, [FM25])
r.emit("lumen_fiber_km_2028", L(FM28) * MI / 1e6, "million fiber-km", 3, [FM28])
r.emit("lumen_fm_growth", L(FM28) / L(FM25), "1", 3, [FM25, FM28])
# Average fibers per route: intercity fiber-miles over ALL route-miles. Because the
# denominator also contains metro and Asia-Pacific route-miles, this is a lower bound
# on the average fiber count of intercity routes (and mixes tier B with tier C).
r.emit("lumen_avg_fibers_lb", L(FM25) / rm, "fibers", 2, [FM25, RM])
new_ratio = L(NEW, "lo") / L(NEW, "hi")
r.emit("lumen_new_fibers_per_route", new_ratio, "fibers", 2, [NEW])
assert new_ratio > L(FM25) / rm   # new builds are far denser than the installed average
r.emit("lumen_new_route_km", L(NEW, "hi") * MI, "route-km", 2, [NEW])

ZA = "ch08.carrier.zayo_fiber_miles_na_2024"
ZB = "ch08.carrier.zayo_fiber_miles_na_2024_bw"
r.emit("zayo_fm_diff_pct", 100 * (L(ZA) - L(ZB)) / L(ZB), "%", 2, [ZA, ZB])
r.emit("zayo_fiber_km", L(ZA) * MI / 1e6, "million fiber-km", 3, [ZA])
MA = "ch08.carrier.zayo_chi_msp_route_pr"
MB = "ch08.carrier.zayo_chi_msp_route_blog"
r.emit("zayo_msp_diff_mi", L(MA) - L(MB), "mi", 2, [MA, MB])
r.emit("zayo_msp_diff_pct", 100 * (L(MA) - L(MB)) / L(MB), "%", 2, [MA, MB])
r.emit("zayo_msp_km_pr", L(MA) * MI, "km", 3, [MA])
r.emit("zayo_msp_km_blog", L(MB) * MI, "km", 3, [MB])
# A 16-mile route-length discrepancy expressed as one-way latency
r.emit("zayo_msp_diff_us", (L(MA) - L(MB)) * MI * tkm, "µs", 2, [MA, MB, cl.NG_ID])
ZC = "ch08.carrier.zayo_completed_longhaul_5y"
r.emit("zayo_overbuild_share", 100 * cl.cond(ZC, "overbuild_route_miles") /
       (cl.cond(ZC, "new_route_miles") + cl.cond(ZC, "overbuild_route_miles")), "%", 2, [ZC])
assert cl.cond(ZC, "new_route_miles") + cl.cond(ZC, "overbuild_route_miles") >= L(ZC)
r.save()
