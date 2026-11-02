"""Numerical answers for the Chapter 1 problem set."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
from scipy.special import erfc
from scipy.optimize import brentq
import ch01lib as cl

r = Results()
h = L("ch01.const.planck_h")
c = L("ch01.const.speed_of_light_c")
OUT = pathlib.Path(__file__).parent / "out"
ex16 = json.loads((OUT / "ex16_gn_optimum.json").read_text())

# P1: Rayleigh coefficient implied by the ITU 1260 nm extension
d = 1 / 1.26 ** 4 - 1 / 1.31 ** 4
A_imp = L("ch01.att.g652d_rayleigh_extension_1260") / d
r.emit("p1_A", A_imp, "dB/(km·µm⁴)", 3, ["ch01.att.g652d_rayleigh_extension_1260"])
r.emit("p1_ratio", A_imp / L("ch01.phys.rayleigh_coeff_fiber", "hi"), "1", 3,
       ["ch01.att.g652d_rayleigh_extension_1260", "ch01.phys.rayleigh_coeff_fiber"])

# P2: D and S at 1550 nm from the G.652 curve with lambda0 at mid-range and S0max
S0 = L("ch01.cd.g652d_s0_range", "hi")
l0 = L("ch01.cd.g652d_lambda0_range", "mid")
lam = 1550.0  # nm (C-band centre used throughout the chapter)
D = S0 * lam / 4 * (1 - (l0 / lam) ** 4)
S = S0 / 4 * (1 + 3 * (l0 / lam) ** 4)
ins2 = ["ch01.cd.g652d_s0_range", "ch01.cd.g652d_lambda0_range"]
r.emit("p2_l0", l0, "nm", 4, ins2)
r.emit("p2_D", D, "ps/(nm·km)", 3, ins2)
r.emit("p2_S", S, "ps/(nm²·km)", 3, ins2)

# P3: CD-induced spread in symbols, 64 GBd, 1000 km at D = 17 (ASSUMPTION: 1000 km)
RS = float(cl.cond("ch01.gap.osnr_penalty_64gbd", "symbol_rate_GBd")) * 1e9
D17 = L("ch01.cd.g652_link_typ_d1550")
lam_m = 1550e-9
dtau = cl.d_si(D17) * 1000e3 * lam_m ** 2 * RS / c        # s
r.emit("p3_dtau_ns", dtau * 1e9, "ns", 3, ["ch01.cd.g652_link_typ_d1550", "ch01.gap.osnr_penalty_64gbd"])
r.emit("p3_symbols", dtau * RS, "symbols", 3, ["ch01.cd.g652_link_typ_d1550", "ch01.gap.osnr_penalty_64gbd"])

# P4: first fading null for the 400G-LR4-10 most negative channel dispersion at 1264.5 nm
cd = abs(L("ch01.cd.lr4_10_channel_cd", "lo")) * 1e-12 / 1e-9   # s/m
le = float(cl.cond("ch01.cd.g652_oband_link_dmin_m1", "wavelength_nm")) * 1e-9
r.emit("p4_fnull", math.sqrt(c / (2 * le ** 2 * cd)) / 1e9, "GHz", 3, ["ch01.cd.lr4_10_channel_cd"])

# P5: coherent receiver, 1000 km G.652.D PMDQ: DGD exceeded with probability 4.2e-5
pmdq = L("ch01.pmd.g652d_pmdq")
mean = pmdq * math.sqrt(1000)
r.emit("p5_mean", mean, "ps", 3, ["ch01.pmd.g652d_pmdq"])
r.emit("p5_dgd3", 3 * mean, "ps", 3, ["ch01.pmd.g652d_pmdq", "ch01.pmd.g959_ratio_3p0_prob"])
r.emit("p5_symbols", 3 * mean * 1e-12 * RS, "symbols", 3, ["ch01.pmd.g652d_pmdq", "ch01.gap.osnr_penalty_64gbd"])

# P6: L_eff for the GN reference span; length beyond which L_eff grows < 1 %
a_db = cl.parse_field("ch01.gn.ref_system_2012", "α")
Ls = cl.parse_field("ch01.gn.ref_system_2012", "Ls") * 1e3
a = cl.alpha_np_per_m(a_db)
r.emit("p6_leff", cl.leff(a, Ls) / 1e3, "km", 4, ["ch01.gn.ref_system_2012"])
r.emit("p6_frac", cl.leff(a, Ls) * a, "1", 3, ["ch01.gn.ref_system_2012"])
r.emit("p6_L99", math.log(100) / a / 1e3, "km", 3, ["ch01.gn.ref_system_2012"])

# P7: n_sp of the low-noise amplifier (NF and minimum gain from the datasheet record)
F = cl.db2lin(L("ch01.amp.viavi_lownoise_nf"))
G = cl.db2lin(float(str(cl.cond("ch01.amp.viavi_lownoise_nf", "gain_dB")).replace(">=", "").strip()))
nsp = (F * G - 1) / (2 * (G - 1))
r.emit("p7_nsp", nsp, "1", 3, ["ch01.amp.viavi_lownoise_nf"])
r.emit("p7_excess", L("ch01.amp.viavi_lownoise_nf") - cl.lin2db(2.0), "dB", 2, ["ch01.amp.viavi_lownoise_nf"])

# P8: the '58 dB' constant at 1310 nm with a 0.1 nm reference bandwidth
dl = float(cl.cond("ch01.osnr.gsup39_58db_constant", "reference_bandwidth_nm")) * 1e-9
l13 = 1310e-9
k1310 = -10 * math.log10(h * (c / l13) * (c * dl / l13 ** 2) / 1e-3)
k1550 = -10 * math.log10(h * (c / lam_m) * (c * dl / lam_m ** 2) / 1e-3)
r.emit("p8_k1310", k1310, "dB", 4, ["ch01.const.planck_h", "ch01.const.speed_of_light_c"])
r.emit("p8_diff", k1550 - k1310, "dB", 3, ["ch01.const.planck_h", "ch01.const.speed_of_light_c"])

# P9: required OSNR (0.1 nm) for the book's 64 GBd DP-16QAM SNR requirement
bref = c * dl / lam_m ** 2
snr_req = ex16["snr_req_db"]["value"]
r.emit("p9_osnr_req", snr_req + 10 * math.log10(RS / bref), "dB", 3,
       ["ch01.cap.soft_fec_threshold_20pct", "ch01.gap.osnr_penalty_64gbd"])

# P10: 1 dB lower NF -> GSNR_max +2/3 dB -> reach factor 10^(2/30)
r.emit("p10_gain_db", 2 / 3, "dB", 3)
r.emit("p10_reach_factor", 10 ** (2 / 30), "1", 3)
r.emit("p10_nmax", math.floor(cl.db2lin(ex16["gmax1_db"]["value"] + 2 / 3) /
                             cl.db2lin(snr_req)), "spans", 3, ["ch01.amp.accelink_mw_nf_max"])

# P11: one-way latency difference over 1000 km, SMF-28 Ultra vs HCF with n_g = 1
ng = L("ch01.fiber.smf28ultra_group_index_1550")
ngh = L("ch01.hcf.ng_nanf_vs_smf28", "lo")
r.emit("p11_dt_ms", (ng - ngh) / c * 1000e3 * 1e3, "ms", 3,
       ["ch01.fiber.smf28ultra_group_index_1550", "ch01.hcf.ng_nanf_vs_smf28"])

# P12: Shannon capacity per polarization at the theoretical 16QAM threshold SNR
snr_th = ex16["snr_theory_db"]["value"]
r.emit("p12_cpol", math.log2(1 + cl.db2lin(snr_th)), "bit/symbol", 3, ["ch01.cap.soft_fec_threshold_20pct"])
r.save()
