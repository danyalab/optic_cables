"""Worked example 10.3: the electrical-IC layer from filings and Chapter 4 records.

* Marvell: management's "roughly half" of data-center revenue as optical
  interconnect, turned into an order-of-magnitude dollar figure.
* Xiamen UX (优迅): 25G-and-above sales as a fraction of its own revenue.
* Why the DSP matters: its share of 1.6T and 800G module power (Chapter 4
  records, pie-chart readouts from an IEEE 802.3df contribution, tier B).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch10lib as cl

r = Results()

MDC, MOPT = "ch10.chain.marvell_fy26_datacenter", "ch10.chain.marvell_optical_share_of_dc"
r.emit("mrvl_opt_share_pct", 100 * L(MOPT), "%", 2, [MOPT])
r.emit("mrvl_opt_est", L(MOPT) * L(MDC) / 1e3, "BUSD", 2, [MDC, MOPT])

UX25, UXT = "ch10.eic.youxun_25g_plus_sales_h1_2025", "ch10.eic.youxun_total_rev_h1_2025"
r.emit("ux25", L(UX25), "CNY million", 5, [UX25])
r.emit("uxtot", L(UXT), "CNY million", 5, [UXT])
r.emit("ux25_pct", 100 * L(UX25) / L(UXT), "%", 2, [UX25, UXT])

MXL = "ch10.eic.maxlinear_infra_share"
r.emit("mxl_infra_pct", 100 * L(MXL), "%", 2, [MXL])

# DSP power share (Chapter 4). Module totals are upper bounds ('<22 W', '~11-12 W').
P16, P8 = "ch04.pw.1p6t_breakdown_dsp", "ch04.pw.800g_breakdown_dsp"
p16_tot = cl.qnum(P16, r"<([0-9.]+) ?W", field="quote")
dsp16 = L(P16) / 100 * p16_tot
r.emit("p16_total", p16_tot, "W", 2, [P16])
r.emit("p16_dsp_share_pct", L(P16), "%", 3, [P16])
r.emit("p16_dsp_w", dsp16, "W", 3, [P16])
p8_hi = cl.qnum(P8, r"~11~([0-9.]+)W", field="quote")
r.emit("p8_dsp_share_pct", L(P8), "%", 2, [P8])
r.emit("p8_dsp_w_hi", L(P8) / 100 * p8_hi, "W", 3, [P8])
r.emit("p8_total_hi", p8_hi, "W", 2, [P8])
r.save()
