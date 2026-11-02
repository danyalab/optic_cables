"""Worked example 10.2: a Chinese laser-chip supplier from its filing, InP substrate
exposure, and why two localization figures can differ by a factor of ten.

Part A (tier B, Yuanjie 2025 annual report): data-center share of revenue,
implied average selling price and unit cost per chip, export share.
Part B (tier B, AXT 10-K): North American revenue share before and after the
Feb 2025 InP control and the 2025 US tariff changes.
Part C (contested box): Mitsubishi EML capacity statements on two baselines.
Part D (contested box): a two-class toy model of localization rates. All of
its inputs are HYPOTHETICAL ASSUMPTIONS chosen only to show how definitions
(unit vs value weighting, product scope) move the number. They are not
estimates of the Chinese market.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch10lib as cl

r = Results()

# ---------------- A. Yuanjie ----------------
YR, YDC, YGM, YU, YX = ("ch10.inp.yuanjie_2025_revenue", "ch10.inp.yuanjie_2025_dc_revenue",
                        "ch10.inp.yuanjie_2025_dc_gm", "ch10.inp.yuanjie_2025_dc_units",
                        "ch10.inp.yuanjie_2025_export_share")
rev, dc, gm, units, exp_ = L(YR), L(YDC), L(YGM), L(YU), L(YX)
g = cl.qnum(YR, r"同比增加 ([0-9.]+)%")
g_dc = cl.qnum(YDC, r"上升 ([0-9.]+)%")
asp = dc / units                      # MCNY / million chips = CNY per chip
r.emit("yj_rev", rev, "CNY million", 4, [YR])
r.emit("yj_growth_pct", g, "%", 4, [YR])
r.emit("yj_rev24", rev / (1 + g / 100), "CNY million", 3, [YR])
r.emit("yj_dc_share_pct", 100 * dc / rev, "%", 3, [YR, YDC])
r.emit("yj_dc_growth_pct", g_dc, "%", 4, [YDC])
r.emit("yj_dc_x", 1 + g_dc / 100, "1", 3, [YDC])
r.emit("yj_asp", asp, "CNY/chip", 3, [YDC, YU])
r.emit("yj_unit_cost", asp * (1 - gm), "CNY/chip", 3, [YDC, YU, YGM])
r.emit("yj_dc_gm_pct", 100 * gm, "%", 4, [YGM])
r.emit("yj_export_pct", 100 * exp_ / rev, "%", 2, [YR, YX])
r.emit("yj_prod", float(cl.cond(YU, "production_million")), "million chips", 4, [YU])
r.emit("yj_units", units, "million chips", 4, [YU])
# unit cost cross-check: cost of sales column in the quote of the GM record
cogs = cl.qnum(YGM, r"393,257,791\.72 \| ([0-9,.]+)") / 1e6
assert abs((dc - cogs) / dc - gm) < 1e-3, "Yuanjie DC gross margin does not reproduce from revenue and cost"
assert abs(asp * (1 - gm) - cogs / units) < 1e-2

# ---------------- B. AXT ----------------
AXN = "ch10.inp.axt_na_revenue_share_2025"
na24 = cl.qnum(AXN, r"In 2024, ([0-9.]+)%")
r.emit("axt_na24_pct", na24, "%", 2, [AXN])
r.emit("axt_na25_pct", 100 * L(AXN), "%", 2, [AXN])
r.emit("axt_na_factor", na24 / (100 * L(AXN)), "1", 2, [AXN])
r.emit("axt_sub_pct", 100 * L("ch10.inp.axt_substrate_share_of_revenue"), "%", 2,
       ["ch10.inp.axt_substrate_share_of_revenue"])
d_ctl = cl.date("ch10.ctl.mofcom2025_10_inp")
d_permit = cl.date("ch10.inp.axt_inp_permit_first")
r.emit("axt_permit_days", (d_permit - d_ctl).days, "days", 3,
       ["ch10.ctl.mofcom2025_10_inp", "ch10.inp.axt_inp_permit_first"])

# ---------------- C. Mitsubishi EML capacity (contested) ----------------
MC, MP = "ch10.inp.mitsubishi_eml_capacity_x3_fy2030", "ch10.inp.mitsubishi_eml_capacity_x3_fy2028_press"
# Company page: C(FY2030) > 3 C(FY2026). Press: C(FY2028) = 3 C(FY2024). Both span four fiscal years.
cagr_c = L(MC) ** (1 / 4) - 1
cagr_p = L(MP) ** (1 / 4) - 1
assert abs(cagr_c - cagr_p) < 1e-12
r.emit("mel_cagr_pct", 100 * cagr_c, "%/yr", 3, [MC, MP])
# If the press path held at constant rate through FY2030, C(FY2030)/C(FY2024) = 3^(6/4)
r.emit("mel_2030_over_2024", L(MP) ** 1.5, "1", 3, [MP])

# ---------------- D. Localization: definitions (contested) ----------------
# Two product classes: k=1 lower-speed or CW/DFB lasers, k=2 high-speed EMLs.
ASSUMPTION_X1 = 0.55     # unit fraction of class 1 among the >=25G chips counted (hypothetical)
ASSUMPTION_D1 = 0.70     # domestic-supplier unit share within class 1 (hypothetical)
ASSUMPTION_D2 = 0.03     # domestic-supplier unit share within class 2 (hypothetical)
ASSUMPTION_P = 20.0      # price ratio p2/p1 (hypothetical)
x1, d1, d2, P = ASSUMPTION_X1, ASSUMPTION_D1, ASSUMPTION_D2, ASSUMPTION_P
x2 = 1 - x1
r_unit = x1 * d1 + x2 * d2
r_value = (x1 * d1 + x2 * P * d2) / (x1 + x2 * P)
r_value_eml_only = d2
assert r_value < r_unit and r_value > d2
r.emit("loc_x1_pct", 100 * x1, "%", 2)
r.emit("loc_d1_pct", 100 * d1, "%", 2)
r.emit("loc_d2_pct", 100 * d2, "%", 1)
r.emit("loc_P", P, "1", 2)
r.emit("loc_unit_pct", 100 * r_unit, "%", 3)
r.emit("loc_value_pct", 100 * r_value, "%", 2)
r.emit("loc_eml_pct", 100 * r_value_eml_only, "%", 1)
r.emit("loc_ratio", r_unit / r_value, "1", 2)
# Sourced numbers for comparison (tier C; contested box only)
K4, E41 = "ch10.open.kaiyuan_25g_localization_4pct", "ch10.open.eetchina_25g_localization_41pct"
r.emit("loc_claim_ratio", L(E41) / L(K4), "1", 2, [K4, E41])
r.save()
