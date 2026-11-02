"""Numerical answers for the Chapter 3 problem set."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import ch03lib as cl

r = Results()
OUT = pathlib.Path(__file__).parent / "out"
ex37 = json.loads((OUT / "ex37_packaging.json").read_text())

# P1: Henry linewidth scaling, 4 mW per facet
aH = L("ch03.las.henry_alpha_fit")
P1 = 4.0   # mW, chosen in the problem statement
dnu1 = L("ch03.las.henry_linewidth_1mw")
r.emit("p1_p", P1, "mW", 2)
r.emit("p1_dnu", dnu1 / P1, "MHz", 3, ["ch03.las.henry_linewidth_1mw"])
r.emit("p1_st", dnu1 / P1 / (1 + aH ** 2), "MHz", 3, ["ch03.las.henry_linewidth_1mw", "ch03.las.henry_alpha_fit"])
r.emit("p1_ratio_a2", (1 + aH ** 2) / (1 + 2.0 ** 2), "1", 3, ["ch03.las.henry_alpha_fit"])

# P2: K-factor needed for a 100 GHz damping-limited bandwidth
F2 = 100e9
K2 = 2 * math.sqrt(2) * math.pi / F2
r.emit("p2_f", F2 / 1e9, "GHz", 3)
r.emit("p2_k", K2 * 1e12, "ps", 3)
r.emit("p2_ratio", L("ch03.las.vcsel_min_kfactor", "lo") * 1e-9 / K2, "1", 3, ["ch03.las.vcsel_min_kfactor"])

# P3: modal-only reach of OM3 for the 400GBASE-SR8 lane at B = 0.5 R_s
rs8 = float(str(cl.cond("ch03.mmf.sr8_reach_om3", "lane")).split("(")[1].split()[0]) * 1e9
assert abs(rs8 - 26.5625e9) < 1
emb3 = L("ch03.mmf.om3_emb") * 1e9   # Hz*m
r.emit("p3_rs", rs8 / 1e9, "GBd", 6, ["ch03.mmf.sr8_reach_om3"])
r.emit("p3_l", emb3 / (0.5 * rs8), "m", 3, ["ch03.mmf.om3_emb", "ch03.mmf.sr8_reach_om3"])
r.emit("p3_bm70", emb3 / L("ch03.mmf.sr8_reach_om3") / 1e9, "GHz", 3, ["ch03.mmf.om3_emb", "ch03.mmf.sr8_reach_om3"])

# P4: carrier density for |dn| = 1e-3 with holes only / electrons only, and the loss cost
ce, ch = cl.eq_coeffs("ch03.eq.soref_dn_1550")
ae, ah = cl.eq_coeffs("ch03.eq.soref_dalpha_1550")
DN = 1e-3
Nh = (DN / ch) ** (1 / 0.8)
Ne = DN / ce
r.emit("p4_nh", Nh, "cm⁻³", 3, ["ch03.si.soref_dn_hole_1550"])
r.emit("p4_ne", Ne, "cm⁻³", 3, ["ch03.si.soref_dn_electron_1550"])
r.emit("p4_ah_db", 10 * math.log10(math.e) * ah * Nh, "dB/cm", 3, ["ch03.si.soref_dn_hole_1550"])
r.emit("p4_ae_db", 10 * math.log10(math.e) * ae * Ne, "dB/cm", 3, ["ch03.si.soref_dn_electron_1550"])

# P5: largest loaded Q whose optical linewidth is at least 50 GHz at 1310 nm
LAM5 = 1310e-9
r.emit("p5_lam", 1310, "nm", 4)
r.emit("p5_bw", 50, "GHz", 2)
r.emit("p5_q", cl.C0 / (LAM5 * 50e9), "1", 3)
r.emit("p5_tau", cl.C0 / (LAM5 * 50e9) * LAM5 / (2 * math.pi * cl.C0) * 1e12, "ps", 3)

# P6: tolerable sum linewidth for 64QAM at 130 GBd
RS6 = 130e9
r.emit("p6_rs", RS6 / 1e9, "GBd", 3)
r.emit("p6_dnu", L("ch02.dsp.bps_lw_64qam") * RS6 / 1e6, "MHz", 3, ["ch02.dsp.bps_lw_64qam"])
r.emit("p6_itla_sum", 2 * L("ch03.itla.oif_linewidth_app1"), "MHz", 2, ["ch03.itla.oif_linewidth_app1"])

# P7: APD excess noise
k = L("ch03.apd.kang_keff")
FA = lambda M, kk: kk * M + (1 - kk) * (2 - 1 / M)
for M in (5, 10, 20):
    r.emit(f"p7_f{M}", FA(M, k), "1", 3, ["ch03.apd.kang_keff"])
r.emit("p7_f10_k05", FA(10, 0.5), "1", 3)
r.emit("p7_bw", 25, "GHz", 2)
r.emit("p7_mcap", L("ch03.apd.kang_gbp") / 25.0, "1", 3, ["ch03.apd.kang_gbp"])

# P8: device-hours for a 10 FIT claim at 60 % and 90 % confidence, zero failures
r.emit("p8_fit", 10, "FIT", 2)
for cl_, tag in ((0.6, "60"), (0.9, "90")):
    r.emit(f"p8_h{tag}", -math.log(1 - cl_) / 10e-9, "device-hours", 3)
af = ex37["af_105_40"]["value"]
r.emit("p8_af", af, "1", 3, ["ch03.rel.vcsel_fit_105c"])
r.emit("p8_devices", -math.log(0.1) / 10e-9 / af / L("ch03.rel.accel_aging"), "devices", 3,
       ["ch03.rel.vcsel_fit_105c", "ch03.rel.accel_aging"])

# P9: mode mismatch between a 10.4 um fiber and a 3 um spot (butt coupling)
mfd_f = float(cl.cond("ch03.cpl.gc_double_etch", "fiber_mfd_um"))
w1, w2 = mfd_f / 2, 3.0 / 2
eta = 4 * w1 ** 2 * w2 ** 2 / (w1 ** 2 + w2 ** 2) ** 2
r.emit("p9_mfd", mfd_f, "µm", 3, ["ch03.cpl.gc_double_etch"])
r.emit("p9_spot", 3.0, "µm", 2)
r.emit("p9_loss", -cl.lin2db(eta), "dB", 3, ["ch03.cpl.gc_double_etch"])

# P10: largest capacitance for a 100 GHz RC limit into 50 ohm
r.emit("p10_f", 100, "GHz", 3)
r.emit("p10_c", 1 / (2 * math.pi * 50 * 100e9) * 1e15, "fF", 3)
r.emit("p10_ratio", 1 / (2 * math.pi * 50 * 100e9) * 1e15 / float(cl.cond("ch03.pd.imec_bw", "capacitance_fF")), "1", 3,
       ["ch03.pd.imec_bw"])
r.save()
