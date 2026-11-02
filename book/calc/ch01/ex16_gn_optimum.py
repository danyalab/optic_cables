"""Worked example 1.6: GN-model optimum launch power, maximum GSNR and reach.

Step 1 reproduces the Poggiolini 2012 RS-SMF reference case (ledger
ch01.gn.ref_system_2012 / ch01.gn.popt_rs_smf_check) with the closed-form
GN expression (Poggiolini 2012 eq. (15), book notation, alpha = power coeff.):

  G_NLI(0) = (8/27) gamma^2 G_WDM^3 L_eff^2
             asinh( (pi^2/2) |beta2| L_eff,a B_ch^2 N_ch^(2 B_ch/Df) ) / (pi |beta2| L_eff,a)

With G_WDM = P_ch/R_s (rectangular-equivalent channel of bandwidth R_s) and the
NLI integrated over B_N = R_s (locally white):  P_NLI = eta P_ch^3 with
eta_1span = mu / R_s^2,  mu = the coefficient multiplying G_WDM^3 above.

Step 2 computes the book's 64 GBd DP-16QAM example over N x 80 km G.652.D.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import numpy as np
from scipy.optimize import minimize_scalar, brentq
from scipy.special import erfc
import ch01lib as cl

r = Results()
h = L("ch01.const.planck_h")
c = L("ch01.const.speed_of_light_c")
lam = float(cl.cond("ch01.osnr.gsup39_58db_constant", "wavelength_nm")) * 1e-9
nu = c / lam


def mu_coeff(gamma, alpha_db, D, Lspan_m, Rs, Df, Nch, Bch=None):
    """Coefficient mu [Hz^2/W^2] with G_NLI = mu * G_WDM^3 (one span)."""
    Bch = Rs if Bch is None else Bch
    a = cl.alpha_np_per_m(alpha_db)
    le = cl.leff(a, Lspan_m)
    lea = 1.0 / a
    b2 = abs(cl.beta2_from_d(D, lam, c))
    arg = (math.pi ** 2 / 2) * b2 * lea * Bch ** 2 * Nch ** (2 * Bch / Df)
    return (8.0 / 27.0) * gamma ** 2 * le ** 2 * math.asinh(arg) / (math.pi * b2 * lea), arg, b2, le


# =========================================================== Step 1: reference
REF = "ch01.gn.ref_system_2012"
CHK = "ch01.gn.popt_rs_smf_check"
Ls = cl.parse_field(REF, "Ls") * 1e3
Df = cl.parse_field(REF, "Δf") * 1e9
Rs = cl.parse_field(REF, "Rs") * 1e9
Nch = cl.parse_field(REF, "Nch")
a_db = cl.parse_field(REF, "α")
D = cl.parse_field(REF, "D")
gam = L("ch01.kerr.gamma_smf_gn2012") * 1e-3
NF = float(cl.cond(CHK, "NF_dB"))
assert (Ls, Df, Rs, Nch) == (cl.cond(CHK, "span_km") * 1e3, cl.cond(CHK, "spacing_GHz") * 1e9,
                             cl.cond(CHK, "symbol_rate_GBd") * 1e9, cl.cond(CHK, "channels"))

mu, arg, b2, le = mu_coeff(gam, a_db, D, Ls, Rs, Df, Nch)
G = cl.db2lin(a_db * Ls / 1e3)
G_ase = h * nu * cl.db2lin(NF) * (G - 1)          # W/Hz, both pols (Poggiolini 2014 eq. (51))
psd_opt = (G_ase / (2 * mu)) ** (1 / 3)           # W/Hz
p_opt_ref = psd_opt * Rs
ref_ins = [REF, CHK, "ch01.kerr.gamma_smf_gn2012", "ch01.const.planck_h"]
r.emit("ref_psd_opt", psd_opt / 1e-15, "µW/GHz", 3, ref_ins)
r.emit("ref_popt_dbm", cl.w2dbm(p_opt_ref), "dBm", 3, ref_ins)
r.emit("ref_popt_pub", L(CHK), "dBm", 2, [CHK])
r.emit("ref_dev_db", cl.w2dbm(p_opt_ref) - L(CHK), "dB", 2, ref_ins)
r.emit("ref_total_dbm", cl.w2dbm(p_opt_ref * Nch), "dBm", 3, ref_ins)
r.emit("ref_asinh_arg", arg, "1", 3, ref_ins)
r.emit("ref_beta2", b2 * 1e27, "ps²/km", 3, [REF])
r.emit("ref_leff", le / 1e3, "km", 3, [REF])
# Tolerance (justification):
#  * the published value is rounded to 0.1 dB (+-0.05 dB);
#  * eq. (15) differs from the full GN integral by < 0.5 dB in NLI at full C-band with
#    roll-off 0.3 (ledger note on ch01.eq.gn_nonnyquist_single_span); P_opt ∝ eta^(-1/3),
#    so this maps to <= 0.17 dB in P_opt;
#  * the paper's exact optical frequency is not stated (1550 nm assumed: < 0.02 dB).
# Sum: 0.05 + 0.17 + 0.02 ~ 0.25 dB.
TOL_DB = 0.25
assert abs(cl.w2dbm(p_opt_ref) - L(CHK)) < TOL_DB, "GN reference case not reproduced"
r.emit("ref_tol_db", TOL_DB, "dB", 2)
r.emit("ref_nf_db", NF, "dB", 2, [CHK])
_note = cl.cond(CHK, "note")
import re as _re
r.emit("ref_psd_pub", float(_re.search(r"PSD ([0-9.]+)", _note).group(1)), "µW/GHz", 3, [CHK])
r.emit("ref_total_pub", float(_re.search(r"~([0-9.]+) dBm", _note).group(1)), "dBm", 2, [CHK])
r.emit("gauss_rs", cl.cond("ch01.gn.gaussianization_distance", "symbol_rate_GBd"), "GBd", 2, ["ch01.gn.gaussianization_distance"])
r.emit("ny75_span", 75, "km", 2, ["ch01.gn.popt_ny_smf_75km_check"])
r.emit("ny100_span", 100, "km", 3, ["ch01.gn.popt_ny_smf_check"])

# Secondary check: Nyquist-WDM variant (B_ch = Df = Rs, 157 channels), 100 km and 75 km
NY_N = 157  # from the ledger note on ch01.gn.ref_system_2012 ('Nch = 157')
assert "157" in cl.cond(REF, "note")
for tag, span, rid in (("ny100", 100e3, "ch01.gn.popt_ny_smf_check"), ("ny75", 75e3, "ch01.gn.popt_ny_smf_75km_check")):
    m2, *_ = mu_coeff(gam, a_db, D, span, Rs, Rs, NY_N)
    G2 = cl.db2lin(a_db * span / 1e3)
    pp = (h * nu * cl.db2lin(NF) * (G2 - 1) / (2 * m2)) ** (1 / 3) * Rs
    r.emit(f"{tag}_popt_dbm", cl.w2dbm(pp), "dBm", 3, [rid, REF])
    # 'about -1 dBm': allow 0.5 dB (rounding to the nearest dB plus the 0.25 dB above)
    assert abs(cl.w2dbm(pp) - L(rid)) < 0.5, tag

# =========================================================== Step 2: book example
# ASSUMPTION: 64 GBd symbol rate for the coherent example (a design choice fixed by the syllabus).
RS = 64e9
# ASSUMPTION: 75 GHz channel grid for 64 GBd (B_ch/Df = 0.85).
DF = 75e9
# ASSUMPTION: C-band fully loaded across the ITU 1530-1565 nm band.
lam_lo = L("ch01.amp.cband_range_itu", "lo") * 1e-9
lam_hi = L("ch01.amp.cband_range_itu", "hi") * 1e-9
B_C = c / lam_lo - c / lam_hi
NCH = math.floor(B_C / DF)
# ASSUMPTION: 80 km spans; fibre = G.652.D with datasheet loss, D = ITU typical link value,
# gamma from n2 (G.Sup47) and A_eff = 80 µm² (computed in ex14).
SPAN = 80e3
ex11 = json.loads((pathlib.Path(__file__).parent / "out" / "ex11_span_budget.json").read_text())
ex14 = json.loads((pathlib.Path(__file__).parent / "out" / "ex14_nonlinear_lengths.json").read_text())
alpha_db = L("ch01.att.smf28ultra_max_1550")
Dbook = L("ch01.cd.g652_link_typ_d1550")
gbook = ex14["gamma_g652"]["value"] * 1e-3
Lspan_db = ex11["smf28u_bol"]["value"]
Lspan_eol = ex11["smf28u_eol"]["value"]
NFb = L("ch01.amp.accelink_mw_nf_max")
Fb = cl.db2lin(NFb)
Gb = cl.db2lin(Lspan_db)
book_ins = ["ch01.amp.cband_range_itu", "ch01.att.smf28ultra_max_1550",
            "ch01.cd.g652_link_typ_d1550", "ch01.kerr.n2_pure_silica_gsup47", "ch01.kerr.aeff_g652d_typ",
            "ch01.amp.accelink_mw_nf_max", "ch01.const.planck_h", "ch01.const.speed_of_light_c"]
r.emit("df_ghz", DF / 1e9, "GHz", 2)
r.emit("bc_thz", B_C / 1e12, "THz", 3, ["ch01.amp.cband_range_itu"])
r.emit("nch", NCH, "", 2, ["ch01.amp.cband_range_itu"])

# GN validity envelope (Poggiolini 2012): Rs >= 28 GBd, D >= 2, >= 3 ch, span loss >= 7 dB,
# beta2 >= 4 ps^2/km, B_ch/Df >= 0.25.
mub, argb, b2b, leb = mu_coeff(gbook, alpha_db, Dbook, SPAN, RS, DF, NCH)
assert RS >= 28e9 and Dbook >= 2 and NCH >= 3 and Lspan_db >= 7 and b2b * 1e27 >= 4 and RS / DF >= 0.25

eta1 = mub / RS ** 2                                  # 1/W^2 per span
pase1 = (Fb * Gb - 1) * h * nu * RS                   # W per span in B_N = Rs, both pols
r.emit("eta1", eta1, "1/W²", 3, book_ins)
r.emit("eta1_db", 10 * math.log10(eta1), "dB(1/W²)", 4, book_ins)
r.emit("pase1_dbm", cl.w2dbm(pase1), "dBm", 4, book_ins)
r.emit("asinh_arg", argb, "1", 3, book_ins)
r.emit("lspan", Lspan_db, "dB", 4, ["ch01.att.smf28ultra_max_1550"])


def gsnr(P, N, eps=0.0, pase=pase1, eta=eta1):
    return P / (N * pase + N ** (1 + eps) * eta * P ** 3)


popt = (pase1 / (2 * eta1)) ** (1 / 3)            # independent of N for eps = 0
gmax1 = (2.0 / 3.0) * popt / pase1                # GSNR_max after one span
alt = 1.0 / (3 * (eta1 / 4) ** (1 / 3) * pase1 ** (2 / 3))
assert abs(alt / gmax1 - 1) < 1e-12
r.emit("popt_dbm", cl.w2dbm(popt), "dBm", 2, book_ins)
r.emit("popt_total_dbm", cl.w2dbm(popt * NCH), "dBm", 3, book_ins)
r.emit("psd_opt", popt / RS / 1e-15, "µW/GHz", 3, book_ins)
r.emit("gmax1_db", cl.lin2db(gmax1), "dB", 4, book_ins)

# Numerical argmax check and the 1/3 : 2/3 split, at N = 20 (any N works when eps = 0)
NTEST = 20
res = minimize_scalar(lambda pdbm: -gsnr(cl.dbm2w(pdbm), NTEST), bounds=(-10, 10), method="bounded",
                      options={"xatol": 1e-6})
assert abs(res.x - cl.w2dbm(popt)) < 0.01, "numerical optimum must match closed form within 0.01 dB"
pnli = NTEST * eta1 * popt ** 3
pase = NTEST * pase1
assert abs(pnli / pase - 0.5) < 1e-9
r.emit("num_popt_dbm", res.x, "dBm", 4, book_ins)
r.emit("num_minus_closed_db", abs(res.x - cl.w2dbm(popt)), "dB", 1, book_ins)
r.emit("nli_frac", pnli / (pnli + pase), "1", 3, book_ins)

# Required SNR. Gray-coded square 16-QAM, BER = (3/8) erfc(sqrt(SNR/10)), reaches the
# 20 % SD-FEC threshold at snr_th. Transceiver noise (SNR_TR, ledger range) adds in
# inverse: 1/SNR_total = 1/GSNR + 1/SNR_TR, so the line must deliver
# GSNR_req = 1 / (1/snr_th - 1/SNR_TR).
ber_th = L("ch01.cap.soft_fec_threshold_20pct")
snr_th = brentq(lambda s: 3 / 8 * erfc(math.sqrt(s / 10)) - ber_th, 1.0, 100.0)
r.emit("snr_theory_db", cl.lin2db(snr_th), "dB", 4, ["ch01.cap.soft_fec_threshold_20pct"])
tr_ins = ["ch01.cap.soft_fec_threshold_20pct", "ch01.gap.transceiver_snr_range"]
greq = {}
for tag in ("lo", "hi"):
    snr_tr = cl.db2lin(L("ch01.gap.transceiver_snr_range", tag))
    inv = 1 / snr_th - 1 / snr_tr
    assert inv > 0, "transceiver SNR must exceed the threshold SNR"
    greq[tag] = 1 / inv
    r.emit(f"gsnr_req_{tag}", cl.lin2db(greq[tag]), "dB", 4, tr_ins)
    r.emit(f"nmax_{tag}", math.floor(gmax1 / greq[tag]), "spans", 3, book_ins + tr_ins)
    r.emit(f"reach_{tag}_km", math.floor(gmax1 / greq[tag]) * SPAN / 1e3, "km", 3, book_ins + tr_ins)
# Main case: the best transceiver of the range (upper SNR_TR)
snr_req = cl.lin2db(greq["hi"])
r.emit("snr_req_db", snr_req, "dB", 4, tr_ins)
r.emit("tr_penalty_hi", snr_req - cl.lin2db(snr_th), "dB", 2, tr_ins)
# Tier-C alternative for the contested box: Rafique's 64 GBd implementation penalty added in dB
snr_req_raf = cl.lin2db(snr_th) + L("ch01.gap.osnr_penalty_64gbd")
r.emit("snr_req_raf", snr_req_raf, "dB", 4, ["ch01.gap.osnr_penalty_64gbd"])
r.emit("nmax_raf", math.floor(gmax1 / cl.db2lin(snr_req_raf)), "spans", 3, ["ch01.gap.osnr_penalty_64gbd"])

nmax = math.floor(gmax1 / cl.db2lin(snr_req))
r.emit("nmax", nmax, "spans", 3, book_ins + tr_ins)
r.emit("reach_km", nmax * SPAN / 1e3, "km", 3, book_ins)
r.emit("gsnr_nmax_db", cl.lin2db(gmax1 / nmax), "dB", 4, book_ins)
# ε > 0: upper end of the typical 2014 range
eps = L("ch01.gn.eps_typical_2014", "hi")


def gmax_eps(N, e):
    po = (N * pase1 / (2 * N ** (1 + e) * eta1)) ** (1 / 3)
    return gsnr(po, N, e)


nmax_eps = max(n for n in range(1, 400) if gmax_eps(n, eps) >= cl.db2lin(snr_req))
r.emit("eps", eps, "1", 2, ["ch01.gn.eps_typical_2014"])
r.emit("nmax_eps", nmax_eps, "spans", 3, book_ins + ["ch01.gn.eps_typical_2014"])
r.emit("eps_penalty_db", cl.lin2db(gmax1 / nmax) - cl.lin2db(gmax_eps(nmax, eps)), "dB", 2,
       ["ch01.gn.eps_typical_2014"])

# End of life: margin raises P_ASE by MARGIN; GSNR_max falls by (2/3) MARGIN
G_eol = cl.db2lin(Lspan_eol)
pase1_eol = (Fb * G_eol - 1) * h * nu * RS
gmax1_eol = (2 / 3) * (pase1_eol / (2 * eta1)) ** (1 / 3) / pase1_eol
r.emit("eol_gsnr_loss_db", cl.lin2db(gmax1 / gmax1_eol), "dB", 3, book_ins)
r.emit("nmax_eol", math.floor(gmax1_eol / cl.db2lin(snr_req)), "spans", 3, book_ins)
r.emit("popt_eol_dbm", cl.w2dbm((pase1_eol / (2 * eta1)) ** (1 / 3)), "dBm", 3, book_ins)

# Shannon comparison at N_max (dual polarization, Nyquist-limit AWGN, GSNR in B_N = Rs)
g_at = gmax1 / nmax
c_pol = math.log2(1 + g_at)
r.emit("cap_per_pol", c_pol, "bit/symbol", 3, book_ins)
r.emit("cap_total", 2 * c_pol, "bit/symbol", 3, book_ins)
r.emit("cap_gbps", 2 * c_pol * RS / 1e9, "Gb/s", 3, book_ins)
# DP-16QAM with 20 % FEC overhead: 2 pol x 4 bit / 1.2
FEC_OH = 0.20  # from the record name/conditions of ch01.cap.soft_fec_threshold_20pct
assert cl.cond("ch01.cap.soft_fec_threshold_20pct", "FEC_overhead") == "20%"
net = 2 * 4 / (1 + FEC_OH)
r.emit("fec_oh_pct", 100 * FEC_OH, "%", 2, ["ch01.cap.soft_fec_threshold_20pct"])
r.emit("net_bits", net, "bit/symbol", 3, ["ch01.cap.soft_fec_threshold_20pct"])
r.emit("net_gbps", net * RS / 1e9, "Gb/s", 4, ["ch01.cap.soft_fec_threshold_20pct"])
snr_shannon = 2 ** (net / 2) - 1
r.emit("snr_shannon_db", cl.lin2db(snr_shannon), "dB", 3, ["ch01.cap.soft_fec_threshold_20pct"])
r.emit("gap_total_db", snr_req - cl.lin2db(snr_shannon), "dB", 3, book_ins)
r.emit("gap_theory_db", cl.lin2db(snr_th) - cl.lin2db(snr_shannon), "dB", 3, book_ins)
# Distance at which Shannon (no gap) would still carry the net rate: N_shannon
r.emit("nmax_shannon", math.floor(gmax1 / snr_shannon), "spans", 3, book_ins)

# EGN: GN overestimates NLI by 1-2 dB near max reach -> reach gain = 1/3 of that
for tag, pick in (("lo", "lo"), ("hi", "hi")):
    d_nli = L("ch01.egn.nli_overestimate_near_max_reach", pick)
    r.emit(f"egn_reach_gain_{tag}", d_nli / 3, "dB", 2, ["ch01.egn.nli_overestimate_near_max_reach"])
assert L("ch01.egn.nli_overestimate_near_max_reach", "lo") / 3 <= L("ch01.egn.gn_reach_underestimate", "hi")
assert L("ch01.egn.nli_overestimate_near_max_reach", "hi") / 3 >= L("ch01.egn.gn_reach_underestimate", "lo")

# 1 dB error in eta -> 1/3 dB in P_opt and GSNR_max
eta_p = eta1 * cl.db2lin(1.0)
r.emit("popt_shift_1db", cl.w2dbm(popt) - cl.w2dbm((pase1 / (2 * eta_p)) ** (1 / 3)), "dB", 3)

# G.654.E variant (ASSUMPTION: D = midpoint of the ITU G.654.E bound range at 1550 nm)
a654 = L("ch01.kerr.pureadvance125_att")
D654 = L("ch01.cd.g654e_d1550_range", "mid")
g654 = ex14["gamma_g654"]["value"] * 1e-3
L654 = ex11["pa125_bol"]["value"]
m654, *_ = mu_coeff(g654, a654, D654, SPAN, RS, DF, NCH)
eta654 = m654 / RS ** 2
pase654 = (Fb * cl.db2lin(L654) - 1) * h * nu * RS
popt654 = (pase654 / (2 * eta654)) ** (1 / 3)
gmax654 = (2 / 3) * popt654 / pase654
ins654 = ["ch01.kerr.pureadvance125_att", "ch01.cd.g654e_d1550_range", "ch01.kerr.aeff_g654e_typ",
          "ch01.kerr.n2_pure_silica_gsup47"]
r.emit("g654_d", D654, "ps/(nm·km)", 2, ["ch01.cd.g654e_d1550_range"])
r.emit("g654_popt_dbm", cl.w2dbm(popt654), "dBm", 3, ins654)
r.emit("g654_dpopt_db", cl.w2dbm(popt654) - cl.w2dbm(popt), "dB", 2, ins654)
r.emit("g654_gain_db", cl.lin2db(gmax654 / gmax1), "dB", 3, ins654)
r.emit("g654_eta_db", cl.lin2db(eta1 / eta654), "dB", 3, ins654)
r.emit("g654_pase_db", cl.lin2db(pase1 / pase654), "dB", 3, ins654)
r.emit("g654_nmax", math.floor(gmax654 / cl.db2lin(snr_req)), "spans", 3, ins654)
r.emit("g654_reach_km", math.floor(gmax654 / cl.db2lin(snr_req)) * SPAN / 1e3, "km", 3, ins654)

# ---------------- figure: GSNR vs launch power at N = nmax
plt = cl.setup_mpl()
pd = np.linspace(-8, 8, 600)
Pw = cl.dbm2w(pd)
N = nmax
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.plot(pd, 10 * np.log10(Pw / (N * pase1)), color=cl.COLORS[0], ls="--", lw=1.6,
        label=r"ASE only, $P/P_{\mathrm{ASE}}$")
ax.plot(pd, 10 * np.log10(1 / (N * eta1 * Pw ** 2)), color=cl.COLORS[1], ls="--", lw=1.6,
        label=r"NLI only, $P/P_{\mathrm{NLI}}$")
ax.plot(pd, 10 * np.log10(gsnr(Pw, N)), color=cl.COLORS[2], lw=2.4, label="GSNR (GN model)")
ax.axhline(snr_req, color=cl.GRAY, lw=1, ls=":")
ax.text(-7.8, snr_req + 0.3, "required SNR", fontsize=8.5)
yo = cl.lin2db(gsnr(popt, N))
ax.plot([cl.w2dbm(popt)], [yo], "o", ms=8, color=cl.COLORS[3])
ax.annotate(r"$P_{\mathrm{opt}}$: NLI = 1/3, ASE = 2/3 of noise", (cl.w2dbm(popt), yo),
            xytext=(-7.6, yo + 6.0), fontsize=9,
            arrowprops=dict(arrowstyle="-", color=cl.GRAY, lw=0.8))
ax.set_xlabel("Launch power per channel (dBm)")
ax.set_ylabel("SNR in $B_N = R_s$ (dB)")
ax.set_ylim(yo - 8, yo + 8)
ax.set_xlim(-8, 8)
ax.legend(fontsize=9, loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=3)
ax.set_title(f"Computed: 64 GBd, {NCH} ch at 75 GHz, {N} x 80 km G.652.D, NF 5 dB", fontsize=10)
cl.savefig(fig, "gsnr_vs_power")

r.save()
