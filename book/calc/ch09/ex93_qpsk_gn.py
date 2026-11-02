"""Worked example 9.3: why China Mobile's 400G backbone uses ~130 GBd DP-QPSK
on a 150 GHz grid in C6T+L6T, analysed with the Chapter 1 GN model.

Steps
  1. spectral efficiency, line rate and overhead of the deployed format;
  2. capacity decomposition relative to the 100G (C4T) generation;
  3. closed-form GN model (Section 1.6) for three ways of carrying 400 Gb/s
     per carrier in the same 12 THz: DP-QPSK ~130 GBd / 150 GHz,
     PCS-16QAM ~90 GBd / 100 GHz, DP-16QAM ~60 GBd / 75 GHz;
  4. required SNR from measured back-to-back OSNR tolerances, and a constant
     "gap to Shannon" model calibrated on QPSK;
  5. maximum reach, L-band noise-figure penalty, and a check against the
     ECOC 2023 field trial;
  6. stimulated Raman scattering (SRS) tilt with the triangular ISRS formula
     (Section 6.3) and the total launch power implied by the measured tilt.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import re
import ch09lib as cl

r = Results()
c = cl.c_light()
h = cl.h_planck()

# ---------------------------------------------------------------- inputs
Q = "ch09.l400.cmcc_qpsk_130gbd_150ghz"
CAP = "ch09.l400.cmcc_capacity_32t"
CCSA = "ch09.l400.ct_ccsa_400g_qpsk_params"
ECOC = "ch09.l400.ecoc2023_reach_2502"
EDGE = "ch09.l400.ecoc2023_band_edges"
NFR = "ch09.l400.ecoc2023_edfa_nf"
MARG = "ch09.l400.ecoc2023_osnr_tolerance_margin"
QB2B = "ch09.l400.qpsk_b2b_osnr_15p8"
PB2B = "ch09.l400.pcs16qam_b2b_17p5"
SRS = "ch09.l400.srs_power_transfer_7db"
SRSB = "ch09.l400.srs_peak_13p4"
G58 = "ch01.osnr.gsup39_58db_constant"
ALPHA = "ch01.att.g652_link_typ_cband"
DISP = "ch01.cd.g652_link_typ_d1550"
N2 = "ch01.kerr.n2_pure_silica_gsup47"
AEFF = "ch01.kerr.aeff_g652d_typ"
CR = "ch06.raman.cr_ssmf"

rs_q = L(Q) * 1e9
df_q = float(cl.cond(Q, "grid_GHz")) * 1e9
nch_q = int(cl.cond(Q, "channels"))
r_net = float(cl.cond(CAP, "rate_Gbps")) * 1e9
assert int(cl.cond(CAP, "channels")) == nch_q

# Reference wavelength and OSNR reference bandwidth (0.1 nm at 1550 nm), as in Ch. 1
lam = float(cl.cond(G58, "wavelength_nm")) * 1e-9
nu = c / lam
bref = cl.bref_hz(lam, float(cl.cond(G58, "reference_bandwidth_nm")) * 1e-9)
r.emit("bref_ghz", bref / 1e9, "GHz", 4, [G58])

# ---------------------------------------------------------------- step 1
B_opt = nch_q * df_q
se = r_net / df_q
line = 2 * 2 * rs_q                     # 2 pol x 2 bit/symbol
rs_ecoc = float(cl.cond(ECOC, "symbol_rate_GBd")) * 1e9
ins_q = [Q, CAP]
r.emit("rs_q", rs_q / 1e9, "GBd", 3, [Q])
r.emit("df_q", df_q / 1e9, "GHz", 3, [Q])
r.emit("nch_q", nch_q, "", 2, [Q])
r.emit("b_opt", B_opt / 1e12, "THz", 3, [Q])
r.emit("cap_fiber", nch_q * r_net / 1e12, "Tb/s", 3, ins_q)
r.emit("se_net", se, "b/(s·Hz)", 3, ins_q)
r.emit("line_rate", line / 1e9, "Gb/s", 3, [Q])
r.emit("overhead_pct", 100 * (line / r_net - 1), "%", 2, ins_q)
r.emit("rs_ecoc", rs_ecoc / 1e9, "GBd", 3, [ECOC])
r.emit("line_rate_ecoc", 4 * rs_ecoc / 1e9, "Gb/s", 3, [ECOC])
r.emit("overhead_ecoc_pct", 100 * (4 * rs_ecoc / r_net - 1), "%", 2, [ECOC, CAP])
r.emit("fill_q", rs_q / df_q, "", 3, [Q])
r.emit("guard_q", (df_q - rs_q) / 1e9, "GHz", 2, [Q])
r.emit("bits_per_sym_pol_q", r_net / (2 * rs_q), "bit", 3, ins_q)
assert abs(B_opt - 12e12) < 1 and abs(nch_q * r_net - 32e12) < 1

# Band edges of the ECOC trial (nm -> THz)
c6 = cl.cond(EDGE, "C6T_nm")
l6 = cl.cond(EDGE, "L6T_nm")
f = lambda nm: c / (nm * 1e-9) / 1e12
r.emit("c6t_thz", f(c6[0]) - f(c6[1]), "THz", 3, [EDGE])
r.emit("l6t_thz", f(l6[0]) - f(l6[1]), "THz", 3, [EDGE])
r.emit("cl_gap_thz", f(c6[1]) - f(l6[0]), "THz", 2, [EDGE])
r.emit("cl_span_thz", f(c6[0]) - f(l6[1]), "THz", 3, [EDGE])
r.emit("c6t_hi_thz", f(c6[0]), "THz", 4, [EDGE])
r.emit("l6t_lo_thz", f(l6[1]), "THz", 4, [EDGE])

# ---------------------------------------------------------------- step 2: vs 100G (C4T)
note = cl.rec(Q)["notes"]
df_100 = float(re.search(r"(\d+) GHz, C4T", note).group(1)) * 1e9
n_100 = int(re.search(r"C4T, (\d+) waves", note).group(1))
rs_100 = float(re.search(r"~(\d+) GBd", note).group(1)) * 1e9
cap_100 = n_100 * 100e9                       # 100G per wave (the generation's name)
se_100 = 100e9 / df_100
r.emit("df_100", df_100 / 1e9, "GHz", 2, [Q])
r.emit("rs_100", rs_100 / 1e9, "GBd", 2, [Q])
r.emit("b_100", n_100 * df_100 / 1e12, "THz", 2, [Q])
r.emit("cap_100", cap_100 / 1e12, "Tb/s", 2, [Q])
r.emit("se_100", se_100, "b/(s·Hz)", 2, [Q])
r.emit("cap_ratio", nch_q * r_net / cap_100, "", 2, ins_q)
r.emit("band_ratio", B_opt / (n_100 * df_100), "", 2, [Q])
r.emit("se_ratio", se / se_100, "", 3, ins_q)
assert abs((B_opt / (n_100 * df_100)) * (se / se_100) - nch_q * r_net / cap_100) < 1e-9

# ---------------------------------------------------------------- step 3: GN set-up
alpha_db = L(ALPHA)
D = L(DISP)
gamma = 2 * math.pi * L(N2) / (lam * L(AEFF) * 1e-12)       # 1/(W m)
# ASSUMPTION: 80 km spans of G.652.D whose whole link coefficient (cable, splices)
# is distributed along the fiber; this gives the 22 dB CCSA reference span.
SPAN = 80e3
lspan_db = alpha_db * SPAN / 1e3
ccsa_span_db = float(re.search(r"跨（(\d+)dB）", cl.rec(CCSA)["quote"]).group(1))
assert abs(lspan_db - ccsa_span_db) < 1e-9, "80 km x ITU typical link value should equal 22 dB"
G = cl.db2lin(lspan_db)
nf_c, nf_l = float(cl.cond(NFR, "C_band_NF_max_dB")), float(cl.cond(NFR, "L_band_NF_max_dB"))
gase_c = h * nu * cl.db2lin(nf_c) * (G - 1)     # W/Hz, both polarizations
gase_l = h * nu * cl.db2lin(nf_l) * (G - 1)
gn_ins = [ALPHA, DISP, N2, AEFF, NFR, G58, "ch01.const.planck_h", "ch01.const.speed_of_light_c"]
r.emit("alpha", alpha_db, "dB/km", 3, [ALPHA])
r.emit("D", D, "ps/(nm·km)", 2, [DISP])
r.emit("gamma", gamma * 1e3, "1/(W·km)", 3, [N2, AEFF])
r.emit("span_km", SPAN / 1e3, "km", 2)
r.emit("lspan_db", lspan_db, "dB", 3, [ALPHA])
r.emit("nf_c", nf_c, "dB", 2, [NFR])
r.emit("nf_l", nf_l, "dB", 2, [NFR])
r.emit("leff", cl.leff(cl.alpha_np_per_m(alpha_db), SPAN) / 1e3, "km", 3, [ALPHA])

# Three formats delivering the same net 400 Gb/s per carrier in the same 12 THz
alt = cl.cond(CCSA, "pcs16qam_alt")
rs_p = float(re.search(r"~(\d+) GBaud", alt).group(1)) * 1e9
df_p = float(re.search(r"(\d+) GHz", alt).group(1)) * 1e9
spans_p_ccsa = int(re.search(r"(\d+) spans", alt).group(1))
dci = cl.rec(CCSA)["notes"]
rs_16 = float(re.search(r"PM-16QAM, ~(\d+) GBaud", dci).group(1)) * 1e9
df_16 = float(re.search(r"x (\d+) GHz", dci).group(1)) * 1e9
spans_q_ccsa_c6, spans_q_ccsa_cl = (int(v) for v in cl.cond(CCSA, "spans_22dB"))
FORMATS = {
    "q": dict(rs=rs_q, df=df_q),
    "p": dict(rs=rs_p, df=df_p),
    "m": dict(rs=rs_16, df=df_16),
}
for k, F in FORMATS.items():
    F["nch"] = int(round(B_opt / F["df"]))
    F["bits_pol"] = r_net / (2 * F["rs"])
    F["shannon_snr"] = 2 ** F["bits_pol"] - 1
    mu, arg = cl.gn_mu(gamma, alpha_db, D, SPAN, F["rs"], F["df"], F["nch"], lam)
    F["mu"], F["arg"] = mu, arg
    F["gopt"], F["snr1"] = cl.gn_span_optimum(mu, gase_c)
    F["popt_dbm"] = cl.w2dbm(F["gopt"] * F["rs"])
    F["ptot_dbm"] = cl.w2dbm(F["gopt"] * F["rs"] * F["nch"])
    r.emit(f"{k}_rs", F["rs"] / 1e9, "GBd", 2, [CCSA] if k != "q" else [Q])
    r.emit(f"{k}_df", F["df"] / 1e9, "GHz", 3, [CCSA] if k != "q" else [Q])
    r.emit(f"{k}_nch", F["nch"], "", 3, [Q, CCSA])
    r.emit(f"{k}_cap", F["nch"] * r_net / 1e12, "Tb/s", 2, [Q, CCSA, CAP])
    r.emit(f"{k}_se", r_net / F["df"], "b/(s·Hz)", 3, [CCSA, CAP])
    r.emit(f"{k}_fill", F["rs"] / F["df"], "", 2, [CCSA, Q])
    r.emit(f"{k}_bits_pol", F["bits_pol"], "bit", 3, [CCSA, CAP])
    r.emit(f"{k}_shannon_db", cl.lin2db(F["shannon_snr"]), "dB", 3, [CCSA, CAP])
    r.emit(f"{k}_asinh", arg, "", 3, gn_ins)
    r.emit(f"{k}_psd_opt", F["gopt"] / 1e-15, "µW/GHz", 3, gn_ins)
    r.emit(f"{k}_popt_dbm", F["popt_dbm"], "dBm", 3, gn_ins)
    r.emit(f"{k}_ptot_dbm", F["ptot_dbm"], "dBm", 3, gn_ins)
    r.emit(f"{k}_snr1_db", cl.lin2db(F["snr1"]), "dB", 4, gn_ins)

# The per-span maximum SNR barely depends on the format: assert < 0.5 dB spread
spread = max(cl.lin2db(F["snr1"]) for F in FORMATS.values()) - min(cl.lin2db(F["snr1"]) for F in FORMATS.values())
r.emit("snr1_spread_db", spread, "dB", 2, gn_ins)
assert spread < 0.5

# ---------------------------------------------------------------- step 4: required SNR
osnr_q = L(QB2B)
better = float(re.search(r"提升(\d+(?:\.\d+)?)dB", cl.rec(QB2B)["quote"]).group(1))
osnr_p_same = osnr_q + better              # PCS-16QAM, same 2023 hardware generation
osnr_p_2024 = L(PB2B)                      # PCS-16QAM, CMCC 2024 article
# ASSUMPTION: the 2023 QPSK tolerance was measured at the ~130 GBd rate of the
# deployed format, and the PCS tolerances at the ~90 GBd of the CCSA draft.
o2s = lambda osnr_db, rs: osnr_db + cl.lin2db(bref / rs)
s2o = lambda snr_db, rs: snr_db - cl.lin2db(bref / rs)
snr_req_q = o2s(osnr_q, rs_q)
gap = snr_req_q - cl.lin2db(FORMATS["q"]["shannon_snr"])
snr_req_p_same = o2s(osnr_p_same, rs_p)
snr_req_p_2024 = o2s(osnr_p_2024, rs_p)
# ASSUMPTION: the same gap to Shannon for the other formats ("constant-gap" model)
snr_req_p_gap = cl.lin2db(FORMATS["p"]["shannon_snr"]) + gap
snr_req_m_gap = cl.lin2db(FORMATS["m"]["shannon_snr"]) + gap
r.emit("osnr_q", osnr_q, "dB", 3, [QB2B])
r.emit("osnr_p_same", osnr_p_same, "dB", 3, [QB2B])
r.emit("osnr_p_2024", osnr_p_2024, "dB", 3, [PB2B])
r.emit("q_better_db", better, "dB", 2, [QB2B])
r.emit("snr_req_q", snr_req_q, "dB", 3, [QB2B, Q, G58])
r.emit("gap_db", gap, "dB", 3, [QB2B, Q, CAP, G58])
r.emit("snr_req_p_same", snr_req_p_same, "dB", 3, [QB2B, CCSA, G58])
r.emit("snr_req_p_2024", snr_req_p_2024, "dB", 3, [PB2B, CCSA, G58])
r.emit("snr_req_p_gap", snr_req_p_gap, "dB", 3, [QB2B, CCSA, CAP, G58])
r.emit("osnr_p_gap", s2o(snr_req_p_gap, rs_p), "dB", 3, [QB2B, CCSA, CAP, G58])
r.emit("snr_req_m_gap", snr_req_m_gap, "dB", 3, [QB2B, CCSA, CAP, G58])
r.emit("osnr_m_gap", s2o(snr_req_m_gap, rs_16), "dB", 3, [QB2B, CCSA, CAP, G58])
r.emit("osnr_q_to_snr", cl.lin2db(bref / rs_q), "dB", 3, [Q, G58])
# The gap model reproduces the measured PCS tolerance to within ~0.7 dB
dev_p = s2o(snr_req_p_gap, rs_p) - osnr_p_same
r.emit("p_gap_dev_db", dev_p, "dB", 2, [QB2B, CCSA, CAP, G58])
assert abs(dev_p) < 1.0 and abs(s2o(snr_req_p_gap, rs_p) - osnr_p_2024) < 1.0
# SNR advantage of QPSK over PCS at equal PSD (the quantity that sets reach)
r.emit("adv_qp_same", snr_req_p_same - snr_req_q, "dB", 2, [QB2B, CCSA, G58])
r.emit("adv_qp_2024", snr_req_p_2024 - snr_req_q, "dB", 2, [QB2B, PB2B, CCSA, G58])
r.emit("baud_term_qp", cl.lin2db(rs_q / rs_p), "dB", 2, [Q, CCSA])

# ---------------------------------------------------------------- step 5: reach
def nmax(snr1, req_db):
    return math.floor(snr1 / cl.db2lin(req_db))


cases = {
    "q": (FORMATS["q"], snr_req_q),
    "p_same": (FORMATS["p"], snr_req_p_same),
    "p_2024": (FORMATS["p"], snr_req_p_2024),
    "m": (FORMATS["m"], snr_req_m_gap),
}
for k, (F, req) in cases.items():
    n = nmax(F["snr1"], req)
    r.emit(f"n_{k}", n, "", 3, gn_ins + [QB2B, PB2B])
    r.emit(f"reach_{k}", n * SPAN / 1e3, "km", 3, gn_ins + [QB2B, PB2B])
n_q = nmax(FORMATS["q"]["snr1"], snr_req_q)
n_p = nmax(FORMATS["p"]["snr1"], snr_req_p_2024)
r.emit("reach_ratio_qp", n_q / n_p, "", 2, gn_ins + [QB2B, PB2B])
r.emit("ccsa_ratio_c6", spans_q_ccsa_c6 / spans_p_ccsa, "", 3, [CCSA])
r.emit("ccsa_ratio_cl", spans_q_ccsa_cl / spans_p_ccsa, "", 3, [CCSA])
r.emit("ccsa_q_c6", spans_q_ccsa_c6, "", 2, [CCSA])
r.emit("ccsa_q_cl", spans_q_ccsa_cl, "", 2, [CCSA])
r.emit("ccsa_p", spans_p_ccsa, "", 2, [CCSA])
r.emit("ccsa_q_km", spans_q_ccsa_cl * SPAN / 1e3, "km", 3, [CCSA])
# Margin (dB) at the CCSA span count, C-band QPSK
gsnr_ccsa = FORMATS["q"]["snr1"] / spans_q_ccsa_cl
r.emit("q_margin_ccsa", cl.lin2db(gsnr_ccsa) - snr_req_q, "dB", 2, gn_ins + [QB2B, CCSA])
assert n_q > n_p > nmax(FORMATS["m"]["snr1"], snr_req_m_gap)

# Shannon comparison at the QPSK maximum reach
gsnr_nq = FORMATS["q"]["snr1"] / n_q
cap_pol = math.log2(1 + gsnr_nq)
r.emit("gsnr_nq_db", cl.lin2db(gsnr_nq), "dB", 3, gn_ins + [QB2B])
r.emit("shannon_slot", 2 * cap_pol * rs_q / 1e9, "Gb/s", 3, gn_ins + [QB2B])
r.emit("shannon_ratio", 2 * cap_pol * rs_q / r_net, "", 3, gn_ins + [QB2B, CAP])

# L-band penalty: two-thirds rule
_, snr1_l = cl.gn_span_optimum(FORMATS["q"]["mu"], gase_l)
pen_l = cl.lin2db(FORMATS["q"]["snr1"]) - cl.lin2db(snr1_l)
r.emit("nf_diff", nf_l - nf_c, "dB", 2, [NFR])
r.emit("l_penalty_db", pen_l, "dB", 3, gn_ins)
r.emit("n_q_l", nmax(snr1_l, snr_req_q), "", 3, gn_ins + [QB2B])
r.emit("reach_q_l", nmax(snr1_l, snr_req_q) * SPAN / 1e3, "km", 3, gn_ins + [QB2B])
mL, mC = (float(v) for v in cl.rec(MARG)["value"])  # ledger range [L6T, C6T]
r.emit("ecoc_margin_c", mC, "dB", 2, [MARG])
r.emit("ecoc_margin_l", mL, "dB", 2, [MARG])
r.emit("ecoc_margin_diff", mC - mL, "dB", 2, [MARG])
assert abs(pen_l - (2 / 3) * (nf_l - nf_c)) < 0.05

# ECOC 2023 field-trial check: OSNR delivered after 42 spans
ns_e = int(cl.cond(ECOC, "spans"))
L_e = L(ECOC)
g_c = float(cl.cond(NFR, "C_gain_dB"))
tol_c = float(cl.cond(MARG, "osnr_tolerance_C_dB"))
tol_l = float(cl.cond(MARG, "osnr_tolerance_L_dB"))
osnr_meas_c = tol_c + mC
osnr_meas_l = tol_l + mL
span_e = L_e / ns_e * 1e3
mu_e, _ = cl.gn_mu(gamma, alpha_db, D, span_e, rs_ecoc, df_q, nch_q, lam)
gase_e = h * nu * cl.db2lin(nf_c) * (cl.db2lin(g_c) - 1)
_, snr1_e = cl.gn_span_optimum(mu_e, gase_e)
gsnr_e = snr1_e / ns_e
osnr_eq_e = s2o(cl.lin2db(gsnr_e), rs_ecoc)
r.emit("ecoc_spans", ns_e, "", 2, [ECOC])
r.emit("ecoc_avg_span", span_e / 1e3, "km", 3, [ECOC])
r.emit("ecoc_gain_c", g_c, "dB", 3, [NFR])
r.emit("ecoc_osnr_meas_c", osnr_meas_c, "dB", 3, [MARG])
r.emit("ecoc_osnr_meas_l", osnr_meas_l, "dB", 3, [MARG])
r.emit("ecoc_tol_c", tol_c, "dB", 3, [MARG])
r.emit("ecoc_tol_l", tol_l, "dB", 3, [MARG])
# Like-for-like: the trial's tolerance-plus-margin is an ASE OSNR (NLI and filtering
# appear as the path penalty inside the tolerance), so compare the model's ASE-only
# OSNR at the GN-optimum launch power; the GSNR is 10 log10(3/2) lower.
osnr_ase_e = osnr_eq_e + cl.lin2db(1.5)
r.emit("ecoc_osnr_model", osnr_eq_e, "dB", 3, gn_ins + [ECOC])
r.emit("ecoc_osnr_ase_model", osnr_ase_e, "dB", 3, gn_ins + [ECOC])
r.emit("ecoc_meas_minus_ase", osnr_meas_c - osnr_ase_e, "dB", 2, gn_ins + [ECOC, MARG])
r.emit("ecoc_path_pen_c", tol_c - osnr_q, "dB", 2, [MARG, QB2B])
# ASE OSNR rises dB for dB with launch power above the optimum; the excess launch
# power x that would close the gap, and the NLI/ASE ratio it would imply:
x_db = osnr_meas_c - osnr_ase_e
r.emit("ecoc_excess_db", x_db, "dB", 2, gn_ins + [ECOC, MARG])
r.emit("ecoc_nli_over_ase", 0.5 * cl.db2lin(2 * x_db), "", 2, gn_ins + [ECOC, MARG])
# The model (EDFA-only, maximum NF, optimum power) must not exceed the measurement,
# and the gap must be small enough to be explained by Raman spans and power choice.
assert 0.0 < osnr_meas_c - osnr_ase_e < 3.0

# ---------------------------------------------------------------- step 6: SRS
Cr = L(CR) / 1e12                       # 1/(W km Hz)
le_km = cl.leff(cl.alpha_np_per_m(alpha_db), SPAN) / 1e3
B_srs = L(SRSB) * 1e12
tilt_meas = L(SRS)
k_db = cl.LN10_10                        # 10 log10(e)
ptot_impl = tilt_meas / (k_db * Cr * le_km * B_srs)
r.emit("cr", L(CR), "1/(W·km·THz)", 2, [CR])
r.emit("srs_b", B_srs / 1e12, "THz", 3, [SRSB])
r.emit("srs_meas", tilt_meas, "dB", 2, [SRS])
r.emit("srs_ptot_impl_dbm", cl.w2dbm(ptot_impl), "dBm", 3, [SRS, SRSB, CR, ALPHA])
r.emit("srs_pch_impl_dbm", cl.w2dbm(ptot_impl / nch_q), "dBm", 3, [SRS, SRSB, CR, ALPHA, Q])
tilt_gnopt = k_db * Cr * le_km * B_srs * cl.dbm2w(FORMATS["q"]["ptot_dbm"])
r.emit("srs_tilt_at_gnopt", tilt_gnopt, "dB", 2, gn_ins + [CR, SRSB])
# Same per-channel PSD over C4T (100G era) and C4.8T+L4.8T (China Unicom plan)
for tag, b in (("c4", n_100 * df_100), ("cu96", 9.6e12)):
    t = tilt_meas * (b / B_srs) ** 2      # P_tot scales with B at fixed PSD
    r.emit(f"srs_{tag}", t, "dB", 2, [SRS, SRSB, Q])
r.emit("srs_100g_claim", 1.0, "dB", 1, [SRS])   # '<1 dB for C4T' (claim text)
assert "<1 dB for C4T" in cl.rec(SRS)["claim"]
assert tilt_meas * ((n_100 * df_100) / B_srs) ** 2 < 1.0

# ---------------------------------------------------------------- figures
plt = cl.setup_mpl()

# (a) GSNR versus distance and the three thresholds
fig, ax = plt.subplots(figsize=(7.2, 4.3))
labels = {"q": "DP-QPSK, %d GBd / %d GHz" % (rs_q / 1e9, df_q / 1e9),
          "p": "PCS-16QAM, %d GBd / %d GHz" % (rs_p / 1e9, df_p / 1e9),
          "m": "DP-16QAM, %d GBd / %d GHz" % (rs_16 / 1e9, df_16 / 1e9)}
reqs = {"q": snr_req_q, "p": snr_req_p_2024, "m": snr_req_m_gap}
for i, k in enumerate(("q", "p", "m")):
    F = FORMATS[k]
    ns = list(range(1, 91))
    ax.plot([n * SPAN / 1e3 for n in ns], [cl.lin2db(F["snr1"] / n) for n in ns], color=cl.COLORS[i], label=labels[k])
    ax.axhline(reqs[k], color=cl.COLORS[i], ls="--", lw=1.2)
    n = nmax(F["snr1"], reqs[k])
    ax.plot([n * SPAN / 1e3], [cl.lin2db(F["snr1"] / n)], "o", color=cl.COLORS[i], ms=6)
ax.set_xlabel("distance (km), 80 km spans")
ax.set_ylabel("GSNR at optimum launch power (dB)")
ax.set_xlim(0, 7200)
ax.set_ylim(2, 22)
ax.legend(loc="upper right", fontsize=9)
cl.savefig(fig, "gsnr_formats")

# (b) spectrum plan: 100G C4T vs 400G C6T+L6T
fig, ax = plt.subplots(figsize=(7.2, 2.8))
# 400G: 40 channels in each of C6T and L6T (from 80 channels split evenly, 6 THz each)
for lo_nm, hi_nm, col in ((c6[0], c6[1], cl.COLORS[0]), (l6[0], l6[1], cl.COLORS[1])):
    fhi, flo = f(lo_nm), f(hi_nm)
    n_band = int(round((fhi - flo) * 1e12 / df_q))
    for j in range(n_band):
        x0 = flo + j * df_q / 1e12
        ax.add_patch(plt.Rectangle((x0 + 0.01, 1.1), df_q / 1e12 - 0.02, 0.8, color=col, alpha=0.75, lw=0))
# 100G C4T: drawn centred on the C6T band (position illustrative)
cen = 0.5 * (f(c6[0]) + f(c6[1]))
b100 = n_100 * df_100 / 1e12
for j in range(n_100):
    x0 = cen - b100 / 2 + j * df_100 / 1e12
    ax.add_patch(plt.Rectangle((x0 + 0.004, 0.1), df_100 / 1e12 - 0.008, 0.8, color=cl.COLORS[2], alpha=0.75, lw=0))
ax.text(cen, 0.5, "80 × 50 GHz (C4T)", ha="center", va="center", fontsize=8.5, color="#ffffff")
ax.text(0.5 * (f(c6[0]) + f(c6[1])), 1.5, "C6T: 40 × 150 GHz", ha="center", va="center", fontsize=8.5, color="#ffffff")
ax.text(0.5 * (f(l6[0]) + f(l6[1])), 1.5, "L6T: 40 × 150 GHz", ha="center", va="center", fontsize=8.5, color="#ffffff")
ax.set_xlim(f(l6[1]) - 0.3, f(c6[0]) + 0.3)
ax.set_ylim(0, 2.1)
ax.set_yticks([0.5, 1.5])
ax.set_yticklabels(["100G", "400G QPSK"])
ax.set_xlabel("optical frequency (THz)")
ax.grid(False)
cl.savefig(fig, "spectrum_plan")

# (c) SRS tilt versus total launch power
fig, ax = plt.subplots(figsize=(7.2, 4.0))
ps = [x / 10 for x in range(100, 281)]
for i, (b, lab) in enumerate(((n_100 * df_100, "4 THz (C4T)"), (9.6e12, "9.6 THz (C4.8T+L4.8T)"), (B_srs, "12.5 THz (C6T+L6T edges)"))):
    ax.plot(ps, [k_db * Cr * le_km * b * cl.dbm2w(p) for p in ps], color=cl.COLORS[i], label=lab)
ax.axhline(tilt_meas, color=cl.GRAY, ls="--", lw=1.0)
ax.text(10.3, tilt_meas + 0.2, "measured, 80 km G.652.D (CMCC 2024)", fontsize=9)
ax.axvline(FORMATS["q"]["ptot_dbm"], color=cl.COLORS[3], ls=":", lw=1.2)
ax.text(FORMATS["q"]["ptot_dbm"] - 0.3, 9.3, "GN optimum, 80 ch", rotation=90, ha="right", va="top", fontsize=9)
ax.set_xlabel("total launch power (dBm)")
ax.set_ylabel("SRS power transfer, edge to edge (dB)")
ax.set_ylim(0, 10)
ax.legend(loc="upper left", fontsize=9)
cl.savefig(fig, "srs_tilt")
# ---------------------------------------------------------------- misc ledger values
SL = "ch09.l400.ecoc2023_span_loss"
FT = "ch09.l400.field_5616km"
r.emit("margin_db_km", float(cl.cond(SL, "margin_dB_per_km")), "dB/km", 2, [SL])
r.emit("share_gt20", float(cl.cond(SL, "share_spans_gt_20dB_pct")), "%", 2, [SL])
r.emit("field_margin", float(cl.cond(FT, "osnr_margin_dB")), "dB", 2, [FT])
r.emit("pcs_oxc_km", float(cl.cond(PB2B, "oxc_reach_km")), "km", 3, [PB2B])
r.emit("pcs_p2p_km", float(cl.cond(PB2B, "p2p_reach_km")), "km", 4, [PB2B])
r.emit("g654_gain_pct", float(cl.cond("ch09.l400.reach_1500_g652d_edfa", "g654e_reach_gain_pct")), "%", 2,
       ["ch09.l400.reach_1500_g652d_edfa"])
r.emit("gain_l", float(cl.cond(NFR, "L_gain_dB")), "dB", 3, [NFR])
lo_p, hi_p = (float(v) for v in cl.cond("ch09.l400.ct_l6t_penalty_1db", "c6t_vs_100g_penalty_dB"))
r.emit("ct_c6t_pen_lo", lo_p, "dB", 1, ["ch09.l400.ct_l6t_penalty_1db"])
r.emit("ct_c6t_pen_hi", hi_p, "dB", 1, ["ch09.l400.ct_l6t_penalty_1db"])
r.emit("ccsa_ch_lo", float(cl.cond(CCSA, "channels")[0]), "", 2, [CCSA])
r.emit("ccsa_ch_hi", float(cl.cond(CCSA, "channels")[1]), "", 2, [CCSA])
r.emit("srs_gain_peak", float(cl.cond(SRSB, "srs_gain_peak_THz")), "THz", 3, [SRSB])
r.emit("ofc_rs", float(cl.cond("ch09.l400.ofc2023_3075km", "symbol_rate_GBd")), "GBd", 3, ["ch09.l400.ofc2023_3075km"])
r.save()
