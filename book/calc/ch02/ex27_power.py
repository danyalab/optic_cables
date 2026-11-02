"""Worked example 2.7: a pJ/bit model of coherent DSP power vs CMOS node and baud rate.

E_bit(n, R_s, L) = [ e_op(n) * c_sym(R_s, L) + 2 * n_ss * e_adc(n) ] / b_sym
  c_sym : complex multiplications per dual-pol symbol from Section 2.4 (ch02lib.ops_per_symbol)
  e_op  : effective energy per complex multiplication, e_22 (n/22)^S_NODE
  e_adc : energy per ADC conversion, Crivelli 40 nm value scaled with the same law;
          four ADCs (I/Q x two polarizations) at n_ss R_s
  b_sym : gross bits per dual-pol symbol
e_22 is calibrated on one published anchor (Fougstedt 2020, 22 nm, 400 Gb/s receiver
DSP + FEC units, 5 W); the result is then compared with the 7 nm 400ZR DSP budget.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import numpy as np
import ch02lib as cl

r = Results()
c = L("ch01.const.speed_of_light_c")
D = L("ch01.cd.g652_link_typ_d1550")
lam = float(cl.cond("ch01.cd.g652_link_typ_d1550", "wavelength_nm")) * 1e-9
b2 = cl.d_si(D) * lam ** 2 / (2 * math.pi * c)

# consistency with Section 2.4 table
tab = json.loads((cl.OUT / "ex24_complexity_table.json.txt").read_text())
for rs_s, row in tab.items():
    for lk, v in row.items():
        assert abs(cl.ops_per_symbol(b2, float(lk) * 1e3, float(rs_s) * 1e9) - v) < 1e-9

# ---- assumptions ----
NSS = 2.0
BSYM = 8.0                 # ASSUMPTION: DP-16QAM gross bits per symbol for every case
S_NODE = 1.0               # ASSUMPTION: energy per operation proportional to the node name (C V^2, V ~ const)
L_CAL = 200e3              # ASSUMPTION: CD length of the calibration design (DCI, of order 200 km)
RS_CAL = L("ch02.sym.400zr_symbol_rate") * 1e9   # ASSUMPTION: calibration design runs at the 400ZR rate
r.emit("s_node", S_NODE, "1", 2)
r.emit("l_cal_km", L_CAL / 1e3, "km", 3)

# ---- calibration: Fougstedt 22 nm, 5 W for the key DSP and FEC units of a 400G receiver ----
P_F = L("ch02.pwr.fougstedt_22nm")
node_F = float(cl.cond("ch02.pwr.fougstedt_22nm", "cmos_node_nm"))
c_cal = cl.ops_per_symbol(b2, L_CAL, RS_CAL)
e22 = P_F / (c_cal * RS_CAL)
r.emit("c_cal", c_cal, "mult/symbol", 3, ["ch02.pwr.fougstedt_22nm"])
r.emit("e22_pj", e22 * 1e12, "pJ", 3, ["ch02.pwr.fougstedt_22nm"])
r.emit("fougstedt_pj_bit", P_F / 400e9 * 1e12, "pJ/bit", 3, ["ch02.pwr.fougstedt_22nm"])


def e_op(node):
    return e22 * (node / node_F) ** S_NODE


E_ADC40 = L("ch02.pwr.adc_40nm_fom") * 1e-12
node_A = float(cl.cond("ch02.pwr.adc_40nm_fom", "cmos_node_nm"))


def e_adc(node):
    return E_ADC40 * (node / node_A) ** S_NODE


def e_bit(node, rs, length):
    core = e_op(node) * cl.ops_per_symbol(b2, length, rs)
    adc = 4 * NSS * e_adc(node)          # four ADCs, NSS samples per symbol each
    return core / BSYM, adc / BSYM


# ---- 7 nm 400ZR check against the NTT budget ----
core7, adc7 = e_bit(7, RS_CAL, 120e3)
p7 = (core7 + adc7) * L("ch02.sym.400zr_line_rate") * 1e9
budget = L("ch02.pwr.ntt_400zr_dsp_budget")
r.emit("zr7_core_pj", core7 * 1e12, "pJ/bit", 3, ["ch02.pwr.fougstedt_22nm"])
r.emit("zr7_adc_pj", adc7 * 1e12, "pJ/bit", 2, ["ch02.pwr.adc_40nm_fom"])
r.emit("zr7_p_w", p7, "W", 2, ["ch02.pwr.fougstedt_22nm", "ch02.pwr.adc_40nm_fom"])
r.emit("zr7_budget_w", budget, "W", 2, ["ch02.pwr.ntt_400zr_dsp_budget"])
r.emit("zr7_frac_pct", 100 * p7 / budget, "%", 2, ["ch02.pwr.ntt_400zr_dsp_budget"])
r.emit("budget_pj_bit_line", budget / (L("ch02.sym.400zr_line_rate") * 1e9) * 1e12, "pJ/bit", 3,
       ["ch02.pwr.ntt_400zr_dsp_budget", "ch02.sym.400zr_line_rate"])
r.emit("budget_pj_bit_net", budget / 400e9 * 1e12, "pJ/bit", 3, ["ch02.pwr.ntt_400zr_dsp_budget"])
assert p7 < budget
# with no node scaling at all (S_NODE = 0) the 22 nm units would still fit the 7 nm budget
p7_flat = e22 * cl.ops_per_symbol(b2, 120e3, RS_CAL) * RS_CAL + 4 * NSS * E_ADC40 * RS_CAL
r.emit("zr7_p_flat_w", p7_flat, "W", 2, ["ch02.pwr.fougstedt_22nm", "ch02.pwr.adc_40nm_fom"])
assert p7_flat < budget
# module view: DSP ~50 % of module; module energy implied by the budget
share = L("ch02.pwr.dsp_share_of_module") / 100
r.emit("module_from_budget_w", budget / share, "W", 3, ["ch02.pwr.ntt_400zr_dsp_budget", "ch02.pwr.dsp_share_of_module"])
r.emit("module_from_budget_pj", budget / share / 400e9 * 1e12, "pJ/bit", 3,
       ["ch02.pwr.ntt_400zr_dsp_budget", "ch02.pwr.dsp_share_of_module"])
mod_ntt = float(cl.cond("ch02.pwr.ntt_400zr_dsp_budget", "module_W"))
r.emit("ntt_module_w", mod_ntt, "W", 3, ["ch02.pwr.ntt_400zr_dsp_budget"])
r.emit("ntt_dsp_share_pct", 100 * budget / mod_ntt, "%", 2, ["ch02.pwr.ntt_400zr_dsp_budget"])
# tier-C comparison only (contested box): module 40-60 pJ/bit at 7 nm
pm_lo, pm_hi = L("ch02.pwr.puttegowda_7nm_pj_bit", "lo"), L("ch02.pwr.puttegowda_7nm_pj_bit", "hi")
r.emit("putt_dsp_lo", pm_lo * share, "pJ/bit", 2, ["ch02.pwr.puttegowda_7nm_pj_bit", "ch02.pwr.dsp_share_of_module"])
r.emit("putt_dsp_hi", pm_hi * share, "pJ/bit", 2, ["ch02.pwr.puttegowda_7nm_pj_bit", "ch02.pwr.dsp_share_of_module"])

# ---- extrapolation: node and baud ----
for node in (5, 3):
    for rs in (120e9, 200e9):
        co, ad = e_bit(node, rs, 120e3)
        r.emit(f"eb_{node}nm_{int(rs / 1e9)}", (co + ad) * 1e12, "pJ/bit", 3, ["ch02.pwr.fougstedt_22nm"])
        r.emit(f"p_{node}nm_{int(rs / 1e9)}", (co + ad) * rs * BSYM, "W", 3, ["ch02.pwr.fougstedt_22nm"])
# baud dependence at fixed node: energy per bit grows only logarithmically
co60, _ = e_bit(7, 60e9, 120e3)
co200, _ = e_bit(7, 200e9, 120e3)
r.emit("baud_ratio_core", co200 / co60, "1", 3)
# distance dependence (Pillai: receiver energy dominates at long reach)
co_lh, _ = e_bit(7, 64e9, 3000e3)
co_dci, _ = e_bit(7, 64e9, 120e3)
r.emit("lh_over_dci", co_lh / co_dci, "1", 3)
# ADC: 5 nm Walden FoM (tier C, contested box): P = FoM 2^ENOB f_s
fom5 = L("ch02.pwr.adc_5nm_fom") * 1e-15
fs5 = float(cl.cond("ch02.pwr.adc_5nm_fom", "sample_rate_GSps")) * 1e9
ENOB = 5.5                 # ASSUMPTION: effective number of bits of an 8-bit 200 GS/s ADC
p_adc5 = 4 * fom5 * 2 ** ENOB * fs5
r.emit("enob", ENOB, "bit", 2)
r.emit("adc5_w", p_adc5, "W", 2, ["ch02.pwr.adc_5nm_fom"])
r.emit("adc5_conv_pj", fom5 * 2 ** ENOB * 1e12, "pJ", 2, ["ch02.pwr.adc_5nm_fom"])
r.emit("adc5_model_pj", e_adc(5) * 1e12, "pJ", 2, ["ch02.pwr.adc_40nm_fom"])
# NTT mode saving range
r.emit("ntt_save_lo", L("ch02.pwr.ntt_mode_saving", "lo"), "%", 2, ["ch02.pwr.ntt_mode_saving"])

# ---- figure ----
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.4, 4.1))
nodes = np.array([3, 5, 7, 10, 16, 22, 28, 40])
for i, rs in enumerate((60e9, 120e9, 200e9)):
    for ls, length in (("-", 120e3), (":", 3000e3)):
        y = [sum(e_bit(n, rs, length)) * 1e12 for n in nodes]
        lab = f"{int(rs / 1e9)} GBd, {int(length / 1e3)} km"
        ax.loglog(nodes, y, ls, color=cl.COLORS[i], label=lab, lw=1.8)
ax.plot(node_F, P_F / 400e9 * 1e12, "s", color=cl.GRAY, ms=7, label="calibration: 22 nm, 400G units")
ax.plot(7, budget / 400e9 * 1e12, "v", color=cl.COLORS[4], ms=8, label="7 nm 400ZR DSP budget (upper bound)")
ax.set_xlabel("CMOS node (nm)")
ax.set_ylabel("DSP energy (pJ/bit)")
ax.set_xticks(nodes)
ax.set_xticklabels([str(n) for n in nodes])
ax.legend(fontsize=8, loc="upper left")
cl.savefig(fig, "dsp_power")

r.save()
