"""Chapter 6 problem solutions (computed)."""
import json
import math
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from scipy.optimize import brentq
from scipy.special import erfinv
import ch06lib as c6
from common import L, Results

r = Results()
OUT = pathlib.Path(__file__).parent / "out"
ex62 = json.loads((OUT / "ex62_wss_filtering.json").read_text())
ex63 = json.loads((OUT / "ex63_raman_isrs.json").read_text())

# P1: 112.5 GHz slots (m = 9) in the 4.8 THz C-band
B_C = (L("ch06.zr.cband_191p3_196p1", "hi") - L("ch06.zr.cband_191p3_196p1", "lo")) * 1e3   # GHz
m = 9
w = m * L("ch06.grid.flex_slot_granularity")
n1 = math.floor(B_C / w)
r.emit("p1_w", w, "GHz", 4, ["ch06.grid.flex_slot_granularity"])
r.emit("p1_n", n1, "", 3, ["ch06.zr.cband_191p3_196p1"])
r.emit("p1_left", B_C - n1 * w, "GHz", 3, ["ch06.zr.cband_191p3_196p1"])

# P2: subcarriers needed for superchannel SE within 5 % of its asymptote (62.5 GHz pitch, 12.5 GHz guard)
SUB, G = 62.5, 12.5
k = next(k for k in range(1, 100) if k * SUB / (k * SUB + G) >= 0.95)
r.emit("p2_k", k, "", 2)
r.emit("p2_kreal", 0.95 * G / (0.05 * SUB), "", 3)

# P3: edge position for a level and -3 dB width after 12 WSSs (fitted device of 6.2)
sig = ex62["sigma_fit"]["value"]
x05 = math.sqrt(2) * sig * erfinv(2 * 10 ** (-0.05) - 1)
r.emit("p3_x05_sig", x05 / sig, "σ", 3)
r.emit("p3_x05", x05, "GHz", 3, ["ch06.wss.huang_passband_50ghz"])
r.emit("p3_w12", ex62["w3_n12"]["value"], "GHz", 3, ["ch06.wss.huang_passband_50ghz"])
x12 = math.sqrt(2) * sig * erfinv(2 * 0.5 ** (1 / 12) - 1)
r.emit("p3_w12_approx", ex62["b_fit"]["value"] - 2 * x12, "GHz", 3, ["ch06.wss.huang_passband_50ghz"])
assert abs((ex62["b_fit"]["value"] - 2 * x12) - ex62["w3_n12"]["value"]) < 0.05

# P4: lumped-pump estimate of pump power for 15 dB on-off gain
leffp = ex63["leff_p"]["value"]
for tag, cr in (("k", L("ch06.raman.gain_eff_ssmf")), ("a", ex63["cr_andre"]["value"])):
    r.emit(f"p4_{tag}", 1.5 * math.log(10) / (cr * leffp) * 1e3, "mW", 3, ["ch06.raman.gain_eff_ssmf",
                                                                          "ch06.raman.peak_gr_ssmf_andre"])

# P5: total launch power for 3 dB tilt over super C+L, 80 km SMF-28 Ultra
sl = c6.cond("ch06.cl.super_cl_12thz_bands", "super_L_THz")
sc = c6.cond("ch06.cl.super_cl_12thz_bands", "super_C_THz")
B = (sl[1] - sl[0]) + (sc[1] - sc[0])
P3 = 3.0 / (c6.LN10_10 * L("ch06.raman.cr_ssmf") * ex63["leff80"]["value"] * B)
r.emit("p5_b", B, "THz", 4, ["ch06.cl.super_cl_12thz_bands"])
r.emit("p5_p", c6.w2dbm(P3), "dBm", 3, ["ch06.raman.cr_ssmf", "ch06.cl.super_cl_12thz_bands"])
r.emit("p5_pch", c6.w2dbm(P3 / 154), "dBm", 3, ["ch06.raman.cr_ssmf"])

# P6: forward + backward Raman, 14.75 dB linear OSNR gain -> reach ratios
imp = ex63["imp_fwd_bwd"]["value"]
r.emit("p6_lin", c6.db2lin(imp), "1", 3, ["ch06.raman.pelouch_fwd_bwd_15db"])
r.emit("p6_gn", c6.db2lin(2 * imp / 3), "1", 3, ["ch06.raman.pelouch_fwd_bwd_15db"])

# P7: K = 6 node chain at d = C: hop-by-hop K(K^2-1)/3 vs express K(K-1); crossover
K = 6
r.emit("p7_hbh", K * (K ** 2 - 1) // 3, "", 3)
r.emit("p7_exp", K * (K - 1), "", 3)


def hbh(d, k=K, cap=400.0):
    return 2 * sum(math.ceil(d * i * (k - i) / cap - 1e-12) for i in range(1, k))


def exp_(d, k=K, cap=400.0):
    return k * (k - 1) * math.ceil(d / cap - 1e-12)


cross = next(d for d in range(5, 805, 5) if exp_(d) <= hbh(d))
r.emit("p7_cross", cross, "Gb/s", 3)

# P8: span length at which the G.654.E gain reaches 3 dB (0.02 dB/km advantage), using ex65 helpers
h, c = c6.consts()
LAM, RS, DF, NCH, OVH = 1550e-9, 64e9, 75e9, 64, 1.95
F = c6.db2lin(L("ch01.amp.accelink_mw_nf_max"))
g652 = c6.gamma_from(L("ch01.kerr.n2_kato1995_smf"), L("ch01.kerr.aeff_g652d_typ"), LAM, c)
g654 = c6.gamma_from(L("ch01.kerr.n2_kato1995_pscf"), c6.from_text("ch01.att.yofc_ct_shanghai_guangzhou", r"A_eff (\d+)"), LAM, c)
D652, D654 = L("ch01.cd.g652_link_typ_d1550"), L("ch01.cd.g654e_d1550_range", "mid")
dz = L("ch01.att.zte_g654e_vs_g652d_80km") / 80.0


def gmax(a, g, D, span):
    eta = c6.mu_coeff(g, a, D, span, RS, DF, NCH, LAM, c) / RS ** 2
    pase = (F * c6.db2lin(a * span / 1e3 + OVH) - 1) * h * (c / LAM) * RS
    return (2 / 3) * (pase / (2 * eta)) ** (1 / 3) / pase


def gain(span):
    return c6.lin2db(gmax(0.18 - dz, g654, D654, span) / gmax(0.18, g652, D652, span))


ex65 = json.loads((OUT / "ex65_g654e_gain.json").read_text())
assert abs(gain(80e3) - ex65["zte_gain"]["value"]) < 1e-9
r.emit("p8_span", brentq(lambda s: gain(s) - 3.0, 50e3, 200e3) / 1e3, "km", 3, ["ch01.att.zte_g654e_vs_g652d_80km"])

# P9: 20-year fibre ageing on 100 km spans; ASE-limited penalty and GSNR penalty at re-optimized power
fa = c6.cond("ch06.margin.pointurier_table", "fiber_aging_dB_per_km_per_year")
d20 = fa * 100 * 20
r.emit("p9_dloss", d20, "dB", 3, ["ch06.margin.pointurier_table"])
r.emit("p9_dgsnr", 2 * d20 / 3, "dB", 3, ["ch06.margin.pointurier_table", "ch06.margin.linear_to_total_2over3"])

# P10: QPSK at CFEC vs oFEC thresholds
sq_c = c6.snr_at_ber_qpsk(L("ch06.zr.cfec_threshold"))
sq_o = c6.snr_at_ber_qpsk(L("ch06.openroadm.ofec_threshold"))
r.emit("p10_c", c6.lin2db(sq_c), "dB", 3, ["ch06.zr.cfec_threshold"])
r.emit("p10_o", c6.lin2db(sq_o), "dB", 3, ["ch06.openroadm.ofec_threshold"])
r.emit("p10_d", c6.lin2db(sq_c / sq_o), "dB", 2, ["ch06.zr.cfec_threshold", "ch06.openroadm.ofec_threshold"])
r.emit("p10_ratio", sq_c / sq_o, "1", 3)

r.save()
