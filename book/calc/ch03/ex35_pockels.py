"""Worked example 3.5: Pockels-effect modulator figures of merit.

Push-pull MZM with electrode gap g and field overlap Gamma:
  Delta phi per arm = pi n^3 r Gamma V L / (lambda g),  difference = 2x
  => V_pi L = lambda g / (2 n^3 r Gamma)  (push-pull),  xi := n^3 r Gamma / g = lambda / (2 V_pi L).
Voltage-loss FOM: V_pi L * alpha = V_pi * (alpha L) = V_pi * IL (on-chip propagation loss).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch03lib as cl

r = Results()
LAM = 1550e-9   # ASSUMPTION: all Pockels devices compared at 1550 nm

# Wang et al. three lengths
wang = []
vpi20 = L("ch03.tfln.wang_vpi_20mm")
note = cl.rec("ch03.tfln.wang_vpi_20mm")["notes"]
import re
v10 = float(re.search(r"10 mm: ([0-9.]+) V", note).group(1))
v5 = float(re.search(r"5 mm: ([0-9.]+) V", note).group(1))
assert abs(float(cl.cond("ch03.tfln.wang_bw_5mm", "Vpi_V")) - v5) < 1e-9
bw_note = cl.rec("ch03.tfln.wang_bw_5mm")["claim"]
bw10 = float(re.search(r"10 mm: ([0-9.]+) GHz", bw_note).group(1))
bw20 = float(re.search(r"20 mm: >([0-9.]+) GHz", bw_note).group(1))
bw5 = L("ch03.tfln.wang_bw_5mm")
insw = ["ch03.tfln.wang_vpi_20mm", "ch03.tfln.wang_bw_5mm"]
for tag, Lmm, vpi, bw in (("w5", 5, v5, bw5), ("w10", 10, v10, bw10), ("w20", 20, vpi20, bw20)):
    vpil = vpi * Lmm / 10
    wang.append((Lmm, vpi, bw, vpil))
    r.emit(f"{tag}_vpil", vpil, "V·cm", 2, insw)
    r.emit(f"{tag}_bw_over_vpi", bw / vpi, "GHz/V", 3, insw)
    r.emit(f"{tag}_xi", LAM / (2 * vpil * 1e-2), "1/V", 3, insw)
assert abs(wang[2][3] - float(cl.cond("ch03.tfln.wang_vpi_20mm", "VpiL_Vcm"))) < 1e-9
r.emit("w_p_10_20", math.log(bw10 / bw20) / math.log(2), "1", 2, insw)
r.emit("w_p_5_10", math.log(bw5 / bw10) / math.log(2), "1", 2, insw)
r.emit("w20_vpi_il", vpi20 * L("ch03.tfln.wang_loss"), "V·dB", 2, insw + ["ch03.tfln.wang_loss"])

# Valdez hybrid Si/LN
vl = L("ch03.tfln.valdez_vpil")
lv = float(cl.cond("ch03.tfln.valdez_110g", "length_cm"))
vpi_v = vl / lv
insv = ["ch03.tfln.valdez_vpil", "ch03.tfln.valdez_110g"]
r.emit("valdez_vpi", vpi_v, "V", 3, insv)
r.emit("valdez_bw_over_vpi", L("ch03.tfln.valdez_110g") / vpi_v, "GHz/V", 3, insv)
r.emit("valdez_vpi_il", vpi_v * float(cl.cond("ch03.tfln.valdez_110g", "on_chip_IL_dB")), "V·dB", 3, insv)
r.emit("valdez_xi", LAM / (2 * vl * 1e-2), "1/V", 3, insv)

# Yang wet-etched TFLN
yv = L("ch03.tfln.yang_vpil")
ya = float(cl.cond("ch03.tfln.yang_110g", "propagation_loss_dB_per_cm"))
r.emit("yang_vpil_alpha", yv * ya, "V·dB", 3, ["ch03.tfln.yang_vpil", "ch03.tfln.yang_110g"])

# Si depletion (Feng) for comparison
fv = L("ch03.si.feng_vpil")
fl = float(cl.cond("ch03.si.feng_vpil", "length_mm")) / 10
r.emit("si_vpi_1mm", fv / fl, "V", 3, ["ch03.si.feng_vpil"])
r.emit("si_vpil_alpha", fv * L("ch03.si.feng_doping_loss"), "V·dB", 3, ["ch03.si.feng_vpil", "ch03.si.feng_doping_loss"])
r.emit("si_bw_over_vpi", L("ch03.si.feng_bw_1mm") / (fv / fl), "GHz/V", 2, ["ch03.si.feng_vpil", "ch03.si.feng_bw_1mm"])
r.emit("yang_vs_si_alpha", fv * L("ch03.si.feng_doping_loss") / (yv * ya), "1", 3,
       ["ch03.si.feng_vpil", "ch03.si.feng_doping_loss", "ch03.tfln.yang_vpil", "ch03.tfln.yang_110g"])
r.emit("soh_vs_si", fv / (L("ch03.si.witzens_soh_vpil") / 10), "1", 3, ["ch03.si.feng_vpil", "ch03.si.witzens_soh_vpil"])

# InP (NTT)
vpi_inp = float(cl.cond("ch03.inp.ogiso_80g", "Vpi_V"))
r.emit("inp_bw_over_vpi", L("ch03.inp.ogiso_80g") / vpi_inp, "GHz/V", 3, ["ch03.inp.ogiso_80g"])
il_inp = float(cl.cond("ch03.inp.fiber_to_fiber_loss", "on_chip_loss_dB"))
r.emit("inp_vpi_il", vpi_inp * il_inp, "V·dB", 2, ["ch03.inp.ogiso_80g", "ch03.inp.fiber_to_fiber_loss"])
cpl = float(cl.cond("ch03.inp.fiber_to_fiber_loss", "coupling_dB_per_facet"))
r.emit("inp_ftf_calc", il_inp + 2 * cpl, "dB", 2, ["ch03.inp.fiber_to_fiber_loss"])
r.emit("inp_ftf_rest", L("ch03.inp.fiber_to_fiber_loss") - il_inp - 2 * cpl, "dB", 2, ["ch03.inp.fiber_to_fiber_loss"])

# bulk LN
vpi_b = float(cl.cond("ch03.tfln.legacy_ln", "Vpi_V"))
r.emit("bulk_bw_over_vpi", L("ch03.tfln.legacy_ln") / vpi_b, "GHz/V", 3, ["ch03.tfln.legacy_ln"])
r.emit("tfln_gain_over_bulk", (bw5 / v5) / (L("ch03.tfln.legacy_ln") / vpi_b), "1", 3, insw + ["ch03.tfln.legacy_ln"])

# ------------------------------------------------------------ figure: Vpi vs bandwidth
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.6, 4.2))
pts = [
    ("TFLN 5 mm", bw5, v5, 0), ("TFLN 10 mm", bw10, v10, 0), ("TFLN 20 mm (BW lower bound)", bw20, vpi20, 0),
    ("hybrid Si/TFLN", L("ch03.tfln.valdez_110g"), vpi_v, 1),
    ("InP IQ (2020)", L("ch03.inp.ogiso_80g"), vpi_inp, 2),
    ("bulk LN (typical)", L("ch03.tfln.legacy_ln"), vpi_b, 3),
    ("Si depletion 1 mm", L("ch03.si.feng_bw_1mm"), fv / fl, 4),
]
for name, bw, vpi, col in pts:
    ax.plot(bw, vpi, "o", color=cl.COLORS[col], ms=8)
    ax.annotate(name, (bw, vpi), textcoords="offset points", xytext=(6, 4), fontsize=8, color=cl.GRAY)
x = np.linspace(8, 130, 100)
for k in (10, 30, 50):
    ax.plot(x, x / k, color=cl.GRAY, lw=0.8, ls=":")
    ax.annotate(f"{k} GHz/V", (120, 120 / k), fontsize=7, color=cl.GRAY)
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("3-dB EO bandwidth (GHz)")
ax.set_ylabel("$V_\\pi$ (V)")
ax.set_title("Voltage and bandwidth of reported modulators", fontsize=10)
cl.savefig(fig, "modulator_fom")
r.save()
