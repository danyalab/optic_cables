"""Worked example 10.5: system vendors by segment and region, from annual reports.

Currencies (CNY, USD, EUR) are never mixed; only within-company ratios are
computed. Fiscal years: Huawei, ZTE, FiberHome, Nokia calendar 2025; Ciena
fiscal year ended 1 Nov 2025.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch10lib as cl

r = Results()

HW, HWI, HWC = "ch10.sys.huawei_2025_revenue", "ch10.sys.huawei_2025_ict_infra", "ch10.sys.huawei_2025_china_revenue"
hw = L(HW)
r.emit("hw_rev", hw / 1e3, "CNY bn", 4, [HW])
r.emit("hw_ict_pct", 100 * L(HWI) / hw, "%", 3, [HW, HWI])
r.emit("hw_cn_pct", 100 * L(HWC) / hw, "%", 3, [HW, HWC])
hw_am = cl.qnum(HWC, r"Americas CNY ?([0-9,]+)", field="notes")
r.emit("hw_am_pct", 100 * hw_am / hw, "%", 2, [HW, HWC])
r.emit("hw_growth_pct", cl.qnum(HW, r"increase of ([0-9.]+)%"), "%", 2, [HW])

ZT, ZTO = "ch10.sys.zte_2025_revenue", "ch10.sys.zte_2025_operator"
r.emit("zte_rev", L(ZT) / 1e3, "CNY bn", 4, [ZT])
r.emit("zte_op_pct", 100 * L(ZTO) / L(ZT), "%", 3, [ZT, ZTO])
r.emit("zte_growth_pct", cl.qnum(ZT, r"同比增长 ([0-9.]+)%"), "%", 4, [ZT])
r.emit("zte_op_change_pct", -cl.qnum(ZTO, r"同比减少 ([0-9.]+)%"), "%", 4, [ZTO])

FH, FHS, FHO = "ch10.sys.fiberhome_2025_revenue", "ch10.sys.fiberhome_2025_systems", "ch10.sys.fiberhome_2025_overseas"
fh = L(FH)
r.emit("fh_rev", fh / 1e3, "CNY bn", 4, [FH])
r.emit("fh_sys_pct", 100 * L(FHS) / fh, "%", 3, [FH, FHS])
r.emit("fh_os_pct", 100 * L(FHO) / fh, "%", 3, [FH, FHO])
r.emit("fh_change_pct", -cl.qnum(FH, r"同比下降 ([0-9.]+)%"), "%", 4, [FH])

CI, CIO, CIC, CIA = ("ch10.sys.ciena_fy25_revenue", "ch10.sys.ciena_fy25_optical",
                     "ch10.sys.ciena_fy25_cloud_customer", "ch10.sys.ciena_fy25_apac")
ci = L(CI)
ci_o24 = cl.qnum(CIO, r"FY2024: ([0-9,]+)", field="notes") / 1e3
ci_am = cl.qnum(CIA, r"Americas\$([0-9,]+)") / 1e3
r.emit("ci_rev", ci / 1e3, "BUSD", 3, [CI])
r.emit("ci_opt", L(CIO) / 1e3, "BUSD", 3, [CIO])
r.emit("ci_opt_pct", 100 * L(CIO) / ci, "%", 3, [CI, CIO])
r.emit("ci_opt_growth_pct", 100 * (L(CIO) / ci_o24 - 1), "%", 3, [CIO])
r.emit("ci_cloud_pct", 100 * L(CIC) / ci, "%", 3, [CI, CIC])
r.emit("ci_apac_pct", 100 * L(CIA) / ci, "%", 2, [CI, CIA])
r.emit("ci_am_pct", 100 * ci_am / ci, "%", 3, [CI, CIA])
assert abs(ci_am + L(CIA) + cl.qnum(CIA, r"EMEA ([0-9,]+)") / 1e3 - ci) < 0.01, "Ciena regions do not sum to total"

NK, NKI = "ch10.sys.nokia_2025_optical", "ch10.sys.nokia_infinera_close"
nk24 = cl.qnum(NK, r"3 019 \| ([0-9 ]+?) \|")
r.emit("nk_opt", L(NK) / 1e3, "BEUR", 3, [NK])
r.emit("nk_opt24", nk24 / 1e3, "BEUR", 3, [NK])
r.emit("nk_growth_pct", 100 * (L(NK) / nk24 - 1), "%", 2, [NK])
r.emit("nk_ccp_pct", cl.qnum(NK, r"([0-9]+)% ?([0-9]+)%$", group=2), "%", 2, [NK])
r.emit("nk_infinera", L(NKI), "BEUR", 2, [NKI])
r.save()
