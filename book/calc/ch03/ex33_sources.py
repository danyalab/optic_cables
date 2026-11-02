"""Worked example 3.3: source requirements for IM/DD and coherent links.

1. ITLA linewidth vs the carrier-recovery tolerance of Section 2.4 (Pfau et al. 2009 BPS
   linewidth x symbol-duration products, 1 dB penalty at BER 1e-3) at the 400ZR symbol rate.
2. Wall-plug energy per bit of external CW lasers for silicon photonics.
3. DML/EML bandwidth relative to symbol rate.
4. Quantum-confined Stark shift: numerical check of the second-order coefficient for an
   infinite square well (dimensionless; no material constants needed).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
from scipy.linalg import eigh_tridiagonal
import ch03lib as cl

r = Results()

# ------------------------------------------------------------ 1. ITLA linewidth vs CPR tolerance
RS = L("ch02.sym.400zr_symbol_rate") * 1e9
r.emit("rs_400zr", RS / 1e9, "GBd", 6, ["ch02.sym.400zr_symbol_rate"])
tol = {}
for fmt in ("4qam", "16qam", "64qam", "256qam"):
    rid = f"ch02.dsp.bps_lw_{fmt}"
    tol[fmt] = L(rid) * RS            # tolerable linewidth (Hz)
    r.emit(f"prod_{fmt}", L(rid), "1", 2, [rid])
    r.emit(f"dnu_tol_{fmt}", tol[fmt] / 1e6, "MHz", 3, [rid, "ch02.sym.400zr_symbol_rate"])
# ASSUMPTION: the Pfau product refers to the sum linewidth of transmitter and LO lasers, and
# both lasers are identical, so the per-laser budget is half the tolerance.
SUM_FACTOR = 2
itla = L("ch03.itla.oif_linewidth_app1") * 1e6
r.emit("itla_sum", SUM_FACTOR * itla / 1e6, "MHz", 2, ["ch03.itla.oif_linewidth_app1"])
r.emit("itla_vs_16qam", SUM_FACTOR * itla / tol["16qam"], "1", 3, ["ch03.itla.oif_linewidth_app1", "ch02.dsp.bps_lw_16qam"])
assert SUM_FACTOR * itla > tol["16qam"]     # the 5 MHz ceiling would not even support 16QAM at 400ZR rate
assert SUM_FACTOR * itla < tol["4qam"]      # but it does support QPSK
for tag, rid in (("furukawa", "ch03.itla.furukawa_linewidth"), ("sedi", "ch03.itla.sedi_linewidth")):
    s = SUM_FACTOR * L(rid) * 1e3
    r.emit(f"{tag}_sum", s / 1e6, "MHz", 2, [rid])
    for fmt in ("16qam", "64qam", "256qam"):
        r.emit(f"{tag}_margin_{fmt}", tol[fmt] / s, "1", 3, [rid, f"ch02.dsp.bps_lw_{fmt}"])
assert SUM_FACTOR * L("ch03.itla.sedi_linewidth") * 1e3 < tol["64qam"]
assert SUM_FACTOR * L("ch03.itla.furukawa_linewidth") * 1e3 < tol["256qam"]
# Symbol rate at which the ITLA spec would be just tolerable for 16QAM: Rs = 2*5MHz / product
r.emit("rs_min_itla_16qam", SUM_FACTOR * itla / L("ch02.dsp.bps_lw_16qam") / 1e9, "GBd", 3,
       ["ch03.itla.oif_linewidth_app1", "ch02.dsp.bps_lw_16qam"])
# Frequency error: worst-case Tx-LO offset the DSP must acquire
r.emit("itla_foff", 2 * L("ch03.itla.oif_freq_error"), "GHz", 2, ["ch03.itla.oif_freq_error"])
r.emit("itla_foff_frac", 2 * L("ch03.itla.oif_freq_error") / (RS / 1e9), "1", 2,
       ["ch03.itla.oif_freq_error", "ch02.sym.400zr_symbol_rate"])
r.emit("furukawa_foff", 2 * L("ch03.itla.furukawa_freq_accuracy"), "GHz", 2, ["ch03.itla.furukawa_freq_accuracy"])
# Henry: linewidth of a 1 mW laser ~ 1/P, power needed to reach the per-laser budget for 16QAM
r.emit("p_for_16qam_budget", L("ch03.las.henry_linewidth_1mw") * 1e6 / (tol["16qam"] / SUM_FACTOR), "mW", 3,
       ["ch03.las.henry_linewidth_1mw", "ch02.dsp.bps_lw_16qam"])

# ------------------------------------------------------------ 2. CW lasers for silicon photonics
# ASSUMPTION: one CW laser feeds 8 lanes of 200 Gb/s (1.6 Tb/s).
AGG = 8 * 200e9
r.emit("agg", AGG / 1e12, "Tb/s", 2)
for tag, p_rid, eff in (("gokhale", "ch03.cw.gokhale_100mw_pce", None),
                        ("lam", "ch03.cw.lam_100mw_75c", float(cl.cond("ch03.cw.lam_100mw_75c", "pce_percent")))):
    if tag == "gokhale":
        p = float(cl.cond(p_rid, "power_mW")) * 1e-3
        pce = L(p_rid) / 100
    else:
        p = L(p_rid) * 1e-3
        pce = eff / 100
    pel = p / pce
    r.emit(f"{tag}_pel", pel * 1e3, "mW", 3, [p_rid])
    r.emit(f"{tag}_pj", pel / AGG * 1e12, "pJ/bit", 2, [p_rid])
    r.emit(f"{tag}_heat", (pel - p) * 1e3, "mW", 3, [p_rid])
p_in = L("ch03.cw.inoue_350mw") * 1e-3
pce_in = float(str(cl.cond("ch03.cw.inoue_350mw", "pce_percent")).strip("> ")) / 100
r.emit("inoue_pel_max", p_in / pce_in, "W", 3, ["ch03.cw.inoue_350mw"])
# Coupling loss of the Lam laser into lensed fiber
r.emit("lam_coupled", L("ch03.cw.lam_100mw_75c") * cl.db2lin(-float(cl.cond("ch03.cw.lam_100mw_75c", "lensed_fiber_coupling_loss_dB"))),
       "mW", 3, ["ch03.cw.lam_100mw_75c"])

# ------------------------------------------------------------ 3. DML/EML bandwidth vs symbol rate
pam = float(cl.cond("ch03.dml.ntt_membrane_pam4", "energy_fJ_per_bit"))
r.emit("ntt_dc_power", pam * 1e-15 * L("ch03.dml.ntt_membrane_pam4") * 1e9 * 1e3, "mW", 3, ["ch03.dml.ntt_membrane_pam4"])
r.emit("ntt_baud", L("ch03.dml.ntt_membrane_pam4") / 2, "GBd", 3, ["ch03.dml.ntt_membrane_pam4"])
r.emit("ntt_bw_over_baud", L("ch03.dml.ntt_membrane_bw") / (L("ch03.dml.ntt_membrane_pam4") / 2), "1", 2,
       ["ch03.dml.ntt_membrane_bw", "ch03.dml.ntt_membrane_pam4"])
r.emit("ntt_ppr_gain", L("ch03.dml.ntt_membrane_bw") / L("ch03.dml.ntt_membrane_intrinsic"), "1", 2,
       ["ch03.dml.ntt_membrane_bw", "ch03.dml.ntt_membrane_intrinsic"])
bb = float(cl.cond("ch03.eml.broadcom_uncooled_bw", "symbol_rate_GBd"))
r.emit("bcm_ratio", L("ch03.eml.broadcom_uncooled_bw") / bb, "1", 2, ["ch03.eml.broadcom_uncooled_bw"])
mit_br = float(str(cl.cond("ch03.eml.mitsubishi_225g_bw", "bit_rate")).split()[0])   # Gb/s, PAM4
r.emit("mit_baud", mit_br / 2, "GBd", 4, ["ch03.eml.mitsubishi_225g_bw"])
r.emit("mit_ratio", L("ch03.eml.mitsubishi_225g_bw") / (mit_br / 2), "1", 2, ["ch03.eml.mitsubishi_225g_bw"])

# ------------------------------------------------------------ 4. QCSE, infinite well
# Dimensionless: -psi'' + f s psi = eps psi on s in [-1/2, 1/2], psi(+-1/2) = 0.
# Energy unit E0 = hbar^2/(2 m L^2); f = 2 m e F L^3 / hbar^2.
# Second-order shift Delta eps = -c2 f^2  =>  Delta E = -(2 c2) m e^2 F^2 L^4 / hbar^2.
N = 4000
s = np.linspace(-0.5, 0.5, N + 2)[1:-1]
hgrid = s[1] - s[0]


def ground(f):
    d = 2.0 / hgrid ** 2 + f * s
    e = -np.ones(N - 1) / hgrid ** 2
    w = eigh_tridiagonal(d, e, select="i", select_range=(0, 0), eigvals_only=True)
    return w[0]


e0 = ground(0.0)
assert abs(e0 - math.pi ** 2) / math.pi ** 2 < 1e-5
fs = np.array([1.0, 2.0, 4.0])
c2 = np.polyfit(fs ** 2, [ground(x) - e0 for x in fs], 1)[0] * -1
c_num = 2 * c2
c_th = (15 - math.pi ** 2) / (24 * math.pi ** 4)
assert abs(c_num - c_th) / c_th < 1e-3, (c_num, c_th)
r.emit("qcse_coeff", c_th, "1", 4)
r.emit("qcse_coeff_num", c_num, "1", 4)
r.save()
