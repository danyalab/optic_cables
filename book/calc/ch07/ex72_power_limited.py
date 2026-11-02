"""Worked example 7.2: capacity of a cable at fixed electrical power.

Model (ch07lib.PowerLimitedCable): the electrical power P_e that maximum power
transfer delivers to the wet plant (Section 7.1) is shared by 2 N_fp N_s
amplifiers. Each amplifier converts the electrical power above an overhead P_0
into signal power with overall efficiency eta_EO. Per fiber the channel is the
Chapter 1 ASE + GN channel; capacity is 2 B log2(1 + Gamma GSNR) per fiber and
direction, and the cable carries N_fp times that.

Linear-regime closed forms derived in Section 7.2:
    k = Gamma eta_EO / (S_ASE B),  p = P_e/(2 N_s),  q = k P_0
    C(N) = 2 B N log2(1 + k (p/N - P_0))
    C_inf = 2 B k p / ln 2                         (P_0 = 0, N -> infinity)
    x*: ln(1+x) = (x+q)/(1+x);  N* = k p/(x*+q);  C* = C_inf/(1+x*)
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import math
import numpy as np
from scipy.optimize import brentq, minimize_scalar
from common import L, Results
import ch07lib as cl

r = Results()
FEED = "ch07.power.perin_feed_voltage_resistance"
LINK = "ch07.power.perin_link_reference"
EO = "ch07.arch.pce_typical_5pct"
P0REC = "ch07.power.desbruslais_span_loss_min_voltage"

# ------------------------------------------------------------------ inputs
V = L(FEED) * 1e3
Rp = float(cl.cond(FEED, "rho_ohm_per_km"))
Lkm = L(LINK)
N_s = int(cl.cond(LINK, "N_s"))
span_km = float(cl.cond(LINK, "span_km"))
span_db = float(cl.cond(LINK, "span_att_dB"))
alpha = float(cl.cond(LINK, "alpha_dB_per_km"))
margin_db = span_db - alpha * span_km              # 1.5 dB per span in Perin's Table 1
n_sp = float(cl.cond(LINK, "n_sp"))
gamma = float(cl.cond(LINK, "gamma_per_W_km"))
D = float(cl.cond(LINK, "D_ps_nm_km"))
Gamma = cl.db2lin(float(cl.cond(LINK, "coding_gap_dB")))
P_e = cl.max_power_transfer(V, Rp * Lkm)
eta_EO = L(EO) / 100
B = cl.cband_hz()
# ASSUMPTION: Nyquist WDM at 50 GBd on a 50 GHz grid filling the ITU C-band.
RS = 50e9
NCH = math.floor(B / RS)
B = NCH * RS
# ASSUMPTION: per-amplifier overhead P_0 equals 10 % of the per-amplifier electrical power
# of an 8-fiber-pair design on the reference link (Desbruslais's P_0/P_r = 0.1, his
# 8-fiber-pair example).
P0_FRAC = float(cl.cond(P0REC, "P0_over_Pr"))
N_REF = int(cl.cond("ch07.power.desbruslais_8fp_example", "fiber_pairs"))
P_0 = P0_FRAC * P_e / (2 * N_s * N_REF)

eta1 = cl.gn_eta1(gamma, alpha, D, span_km, RS, RS, NCH)
base_ins = [FEED, LINK, EO, P0REC, "ch07.power.desbruslais_8fp_example", "ch01.amp.cband_range_itu",
            "ch01.const.planck_h", "ch01.const.speed_of_light_c"]


def cable(P_e=P_e, P_0=P_0, eta_EO=eta_EO, span_db=span_db, N_s=N_s, span_km=span_km, nli=True):
    e1 = cl.gn_eta1(gamma, alpha, D, span_km, RS, RS, NCH) if nli else None
    return cl.PowerLimitedCable(P_e, N_s, span_db, n_sp, eta_EO, P_0, B, RS, Gamma, eta1=e1)


m = cable()
r.emit("gamma", gamma, "1/(W·km)", 2, [LINK])
r.emit("D", D, "ps/(nm·km)", 2, [LINK])
r.emit("alpha", alpha, "dB/km", 3, [LINK])
r.emit("span_db", span_db, "dB", 3, [LINK])
r.emit("margin_db", margin_db, "dB", 2, [LINK])
r.emit("n_sp", n_sp, "", 2, [LINK])
r.emit("gap_db", float(cl.cond(LINK, "coding_gap_dB")), "dB", 1, [LINK])
r.emit("Gamma", Gamma, "", 3, [LINK])
r.emit("nf_db", cl.lin2db(m.F), "dB", 3, [LINK])
r.emit("eta_eo_pct", 100 * eta_EO, "%", 2, [EO])
r.emit("B_thz", B / 1e12, "THz", 3, ["ch01.amp.cband_range_itu"])
r.emit("rs_gbd", RS / 1e9, "GBd", 2)
r.emit("nch", NCH, "", 2, ["ch01.amp.cband_range_itu"])
r.emit("p0_frac_pct", 100 * P0_FRAC, "%", 2, [P0REC])
r.emit("n_ref", N_REF, "", 1, ["ch07.power.desbruslais_8fp_example"])
r.emit("Pe_kw", P_e / 1e3, "kW", 3, [FEED, LINK])
r.emit("p_w", m.p, "W", 3, [FEED, LINK])
r.emit("P0_mw", 1e3 * P_0, "mW", 3, base_ins)
r.emit("S_ase_dbm_ghz", cl.w2dbm(m.S_ase * 1e9), "dBm/GHz", 3, base_ins)
r.emit("P_ase_band_dbm", cl.w2dbm(m.S_ase * B), "dBm", 3, base_ins)
r.emit("k_per_w", m.k, "1/W", 3, base_ins)
r.emit("q", m.q, "", 3, base_ins)
r.emit("q_db", cl.lin2db(m.q), "dB", 3, base_ins)

# ------------------------------------------------------------------ GN check per fiber
r.emit("eta1_db", cl.lin2db(eta1), "dB(1/W²)", 4, base_ins)
r.emit("popt_dbm", cl.w2dbm(m.P_opt), "dBm", 3, base_ins)
r.emit("popt_total_dbm", cl.w2dbm(m.P_opt * NCH), "dBm", 3, base_ins)
gsnr_max = m.P_opt / (1.5 * m.P_ase_ch)
r.emit("gsnr_max_db", cl.lin2db(gsnr_max), "dB", 3, base_ins)
r.emit("cfp_max_tbps", 2 * B * math.log2(1 + Gamma * gsnr_max) / 1e12, "Tb/s", 3, base_ins)
# the GN cap binds when P_sig/N_ch exceeds P_opt
n_knee = m.p / (m.P_opt * NCH / eta_EO + P_0)
r.emit("n_knee", n_knee, "", 2, base_ins)

# ------------------------------------------------------------------ closed-form optimum
x_s, n_s_opt, c_s = m.optimum_linear()
c_inf = m.c_inf()
r.emit("c_inf_tbps", c_inf / 1e12, "Tb/s", 3, base_ins)
r.emit("x_opt", x_s, "", 3, base_ins)
r.emit("x_opt_db", cl.lin2db(x_s), "dB", 3, base_ins)
r.emit("snr_opt_db", cl.lin2db(x_s / Gamma), "dB", 3, base_ins)
r.emit("x_approx", math.sqrt(2 * m.q), "", 3, base_ins)
r.emit("n_opt", n_s_opt, "", 3, base_ins)
r.emit("c_opt_tbps", c_s / 1e12, "Tb/s", 3, base_ins)
r.emit("c_opt_frac_pct", 100 * c_s / c_inf, "%", 3, base_ins)
se_opt = 2 * math.log2(1 + x_s)
r.emit("se_opt", se_opt, "b/s/Hz", 3, base_ins)
r.emit("cfp_opt_tbps", c_s / n_s_opt / 1e12, "Tb/s", 3, base_ins)
assert abs(c_s / n_s_opt - 2 * B * math.log2(1 + x_s)) < 1e-6 * c_s

# numerical optimum over integer N_fp with the full (ASE + GN) model
grid = np.arange(1, 200)
caps = np.array([m.capacity(int(n)) for n in grid])
n_num = int(grid[np.argmax(caps)])
r.emit("n_opt_num", n_num, "", 3, base_ins)
r.emit("c_opt_num_tbps", caps.max() / 1e12, "Tb/s", 3, base_ins)
assert abs(n_num - n_s_opt) <= 1.0, "closed form and numerical optimum disagree"
assert abs(caps.max() - c_s) / c_s < 0.01
# linear regime at the optimum: channel power far below the GN optimum
pch_opt = m.p_ch(n_num)
r.emit("pch_opt_dbm", cl.w2dbm(pch_opt), "dBm", 3, base_ins)
r.emit("pch_below_popt_db", cl.w2dbm(m.P_opt) - cl.w2dbm(pch_opt), "dB", 2, base_ins)
r.emit("nli_frac_opt_pct", 100 * m.eta * pch_opt ** 3 / (m.P_ase_ch + m.eta * pch_opt ** 3), "%", 2, base_ins)
assert cl.w2dbm(m.P_opt) - cl.w2dbm(pch_opt) > 5
# per-amplifier operating point at the optimum
P_el = m.p / n_num
r.emit("pel_opt_mw", 1e3 * P_el, "mW", 3, base_ins)
r.emit("psig_opt_dbm", cl.w2dbm(m.p_sig(n_num)), "dBm", 3, base_ins)
eta_pump = L("ch07.power.perin_pump_efficiency")
r.emit("ppump_opt_mw", 1e3 * eta_pump * (P_el - P_0), "mW", 3, base_ins + ["ch07.power.perin_pump_efficiency"])
r.emit("perin_lin_pump_mw", L("ch07.power.perin_linear_regime_pump"), "mW", 3, ["ch07.power.perin_linear_regime_pump"])
assert 1e3 * eta_pump * (P_el - P_0) < L("ch07.power.perin_linear_regime_pump")

# table of capacity vs N_fp
for n in (1, 2, 4, 8, 12, 16, 24, 32, 48, 64):
    r.emit(f"c_{n}", m.capacity(n) / 1e12, "Tb/s", 3, base_ins)
    r.emit(f"snr_{n}", cl.lin2db(m.gsnr(n)), "dB", 3, base_ins)
    r.emit(f"se_{n}", 2 * math.log2(1 + Gamma * m.gsnr(n)), "b/s/Hz", 3, base_ins)
# homogeneity: doubling N_fp and P_e together doubles capacity (P_0 scales out only if
# P_0 = 0); show the scaling vs doubling power alone at N_fp = 8
m0 = cable(P_0=0.0, nli=False)
m0x2 = cable(P_e=2 * P_e, P_0=0.0, nli=False)
r.emit("hom_8", m0.capacity(8) / 1e12, "Tb/s", 3, base_ins)
r.emit("hom_8_2p", m0x2.capacity(8) / 1e12, "Tb/s", 3, base_ins)
r.emit("hom_16_2p", m0x2.capacity(16) / 1e12, "Tb/s", 3, base_ins)
assert abs(m0x2.capacity(16) - 2 * m0.capacity(8)) < 1e-6 * m0.capacity(8)
r.emit("hom_gain_power_pct", 100 * (m0x2.capacity(8) / m0.capacity(8) - 1), "%", 3, base_ins)

# sensitivity of the optimum to P_0 and eta_EO
for tag, kw in (("p0half", dict(P_0=P_0 / 2)), ("p0double", dict(P_0=2 * P_0)),
                ("eo_downie", dict(eta_EO=L("ch07.power.downie_overall_eo_eff_c") / 100)),
                ("v18", dict(P_e=cl.max_power_transfer(L("ch07.arch.max_single_end_voltage_18kv") * 1e3,
                                                       L("ch07.arch.cable_resistance_low_end") * Lkm)))):
    mm = cable(**kw)
    xx, nn, cc = mm.optimum_linear()
    extra = ["ch07.power.downie_overall_eo_eff_c", "ch07.arch.max_single_end_voltage_18kv",
             "ch07.arch.cable_resistance_low_end"]
    r.emit(f"{tag}_n", nn, "", 3, base_ins + extra)
    r.emit(f"{tag}_c", cc / 1e12, "Tb/s", 3, base_ins + extra)
    r.emit(f"{tag}_se", 2 * math.log2(1 + xx), "b/s/Hz", 3, base_ins + extra)
    r.emit(f"{tag}_q", mm.q, "", 3, base_ins + extra)
r.emit("eo_downie_pct", L("ch07.power.downie_overall_eo_eff_c"), "%", 2, ["ch07.power.downie_overall_eo_eff_c"])

# check the small-q scaling N* ∝ P_0^(-1/2): ratio for halving P_0
mh = cable(P_0=P_0 / 2)
r.emit("p0half_ratio", mh.optimum_linear()[1] / n_s_opt, "", 3, base_ins)

# ------------------------------------------------------------------ span-length optimum
# P_0 = 0 analytic: maximize l^2 exp(-a l)  ->  a l = 2  (fiber loss 2 / ln(10)*10 dB)
r.emit("span_opt_analytic_db", 2 * cl.LN10_10, "dB", 3)
r.emit("span_opt_analytic_km", 2 * cl.LN10_10 / alpha, "km", 3, [LINK])


def c_star_vs_span(l_km, P0=P_0):
    ns = Lkm / l_km
    sdb = alpha * l_km + margin_db
    mm = cl.PowerLimitedCable(P_e, ns, sdb, n_sp, eta_EO, P0, B, RS, Gamma)
    return mm.optimum_linear()[2]


res0 = minimize_scalar(lambda l: -c_star_vs_span(l, 0.0), bounds=(10, 150), method="bounded")
res1 = minimize_scalar(lambda l: -c_star_vs_span(l), bounds=(10, 150), method="bounded")
r.emit("span_opt0_km", res0.x, "km", 3, base_ins)
r.emit("span_opt0_db", alpha * res0.x + margin_db, "dB", 3, base_ins)
r.emit("span_opt0_fiber_db", alpha * res0.x, "dB", 3, base_ins)
r.emit("span_opt1_km", res1.x, "km", 3, base_ins)
r.emit("span_opt1_db", alpha * res1.x + margin_db, "dB", 3, base_ins)
r.emit("span_gain_vs_ref_pct", 100 * (c_star_vs_span(res1.x) / c_star_vs_span(span_km) - 1), "%", 2, base_ins)
# with F independent of G and no margin, a l = 2 exactly
# with ASE proportional to (G - 1) the P_0 = 0 optimum solves ln(G/G_m) = 2 (1 - 1/G),
# G_m = margin; check the numerical optimum against it
Gm = cl.db2lin(margin_db)
G0 = brentq(lambda G: math.log(G / Gm) - 2 * (1 - 1 / G), Gm * 1.01, 1e4)
assert abs(cl.lin2db(G0) - (alpha * res0.x + margin_db)) < 0.05
# no margin: ln G = 2 (1 - 1/G)
G00 = brentq(lambda G: math.log(G) - 2 * (1 - 1 / G), 1.5, 1e4)
r.emit("span_opt_nomargin_db", cl.lin2db(G00), "dB", 3)

# ------------------------------------------------------------------ Desbruslais 8 FP reconstruction
DES = "ch07.power.desbruslais_8fp_example"
Vd = float(cl.cond(DES, "V_kV")) * 1e3
Ld = float(cl.cond(DES, "L_km"))
nfp = int(cl.cond(DES, "fiber_pairs"))
nch_d = int(cl.cond(DES, "channels_per_fp"))
alpha_d = float(cl.cond(P0REC, "alpha_dB_per_km"))
nf_d = float(cl.cond(P0REC, "NF_dB"))
eta_c = float(cl.cond(P0REC, "eta_c"))
# ASSUMPTION: span loss 9 dB, the middle of Desbruslais's 8-10 dB ideal range, and
# 1 ohm/km conductor (Perin's value) for the reconstruction.
SPAN_D_DB = 9.0
l_d = SPAN_D_DB / alpha_d
n_r_d = math.floor(Ld / l_d)
P_r_d = Vd ** 2 / (4 * Rp * Ld * n_r_d)
P_ch_d = eta_c * (1 - P0_FRAC) * P_r_d / (2 * nfp * nch_d)       # Desbruslais Eq. (14)
dins = [DES, P0REC, FEED, "ch07.power.desbruslais_ideal_span_loss"]
r.emit("des_span_db", SPAN_D_DB, "dB", 2, ["ch07.power.desbruslais_ideal_span_loss"])
r.emit("des_span_km", l_d, "km", 3, dins)
r.emit("des_nr", n_r_d, "", 3, dins)
r.emit("des_prep_w", P_r_d, "W", 3, dins)
r.emit("des_pch_dbm", cl.w2dbm(P_ch_d), "dBm", 3, dins)
r.emit("des_ptot_dbm", cl.w2dbm(P_ch_d * nch_d), "dBm", 3, dins)
Bref = 0.1e-9 * L("ch01.const.speed_of_light_c") / (1550e-9) ** 2
Gd = cl.db2lin(SPAN_D_DB)
Fd = cl.db2lin(nf_d)
osnr_d = P_ch_d / (n_r_d * cl.h_nu() * (Fd * Gd - 1) * Bref)
r.emit("des_osnr_db", cl.lin2db(osnr_d), "dB", 3, dins + ["ch01.const.planck_h"])
r.emit("des_nf_db", nf_d, "dB", 2, [P0REC])
r.emit("des_eta_c_pct", 100 * eta_c, "%", 2, [P0REC])

# ------------------------------------------------------------------ figures
plt = cl.setup_mpl()
ns = np.unique(np.round(np.logspace(0, math.log10(150), 120)).astype(int))
ns_snr = ns[ns < m.p / P_0]
fig, ax = plt.subplots(figsize=(7.4, 4.4))
for (lab, kw, col, ls) in (("baseline overhead $P_0$", {}, cl.COLORS[0], "-"),
                           ("$P_0/2$", dict(P_0=P_0 / 2), cl.COLORS[2], "-"),
                           ("$2P_0$", dict(P_0=2 * P_0), cl.COLORS[1], "-"),
                           ("$P_0 = 0$", dict(P_0=0.0), cl.COLORS[3], "--")):
    mm = cable(**kw)
    ax.plot(ns, [mm.capacity(int(n)) / 1e12 for n in ns], color=col, ls=ls, label=lab)
    if kw.get("P_0", 1) != 0.0:
        xx, nn, cc = mm.optimum_linear()
        ax.plot([nn], [cc / 1e12], "o", color=col, ms=6)
ax.axhline(c_inf / 1e12, color=cl.GRAY, lw=1, ls=":")
ax.text(1.1, c_inf / 1e12 * 1.02, r"$C_\infty$ (linear-regime limit)", fontsize=8.5)
for nfp_mark, lab in ((16, "16"), (24, "24"), (50, "~50")):
    ax.axvline(nfp_mark, color=cl.GRAY, lw=0.8, ls="--", alpha=0.6)
    ax.text(nfp_mark * 1.03, 15, lab + " FP", fontsize=8, rotation=90, va="bottom")
ax.set_xscale("log")
ax.set_xlabel(r"fiber pairs $N_{\mathrm{fp}}$ sharing the same electrical power")
ax.set_ylabel("cable capacity per direction (Tb/s)")
ax.set_ylim(0, c_inf / 1e12 * 1.12)
ax.legend(fontsize=8.5, loc="center left")
fig.tight_layout()
cl.savefig(fig, "capacity_vs_fp")

fig, ax1 = plt.subplots(figsize=(7.4, 4.2))
ax1.plot(ns_snr, [cl.lin2db(m.gsnr(int(n))) for n in ns_snr], color=cl.COLORS[0], label="GSNR per fiber (dB)")
ax1.axhline(cl.lin2db(gsnr_max), color=cl.COLORS[0], lw=0.8, ls=":")
ax1.set_xscale("log")
ax1.set_xlabel(r"fiber pairs $N_{\mathrm{fp}}$")
ax1.set_ylabel("GSNR per fiber (dB)", color=cl.COLORS[0])
ax2 = ax1.twinx()
ax2.plot(ns_snr, [2 * math.log2(1 + Gamma * m.gsnr(int(n))) for n in ns_snr], color=cl.COLORS[1],
         label="spectral efficiency")
asn_lo, asn_hi = L("ch07.power.asn_optimum_se", "lo"), L("ch07.power.asn_optimum_se", "hi")
ax2.axhspan(asn_lo, asn_hi, color=cl.COLORS[1], alpha=0.12)
ax2.text(1.05, asn_hi + 0.08, "SLTE optimum SE quoted for ASN SDM design", fontsize=8, color=cl.COLORS[1])
ax2.set_ylabel("spectral efficiency per fiber (b/s/Hz)", color=cl.COLORS[1])
ax2.spines["right"].set_visible(True)
ax2.grid(False)
ax1.axvline(n_s_opt, color=cl.GRAY, lw=0.8, ls="--")
ax1.text(n_s_opt * 1.04, ax1.get_ylim()[0] + 1, "capacity optimum", fontsize=8, rotation=90, va="bottom")
fig.tight_layout()
cl.savefig(fig, "snr_per_fp")

fig, ax = plt.subplots(figsize=(7.0, 4.0))
ls_km = np.linspace(15, 130, 150)
for P0v, lab, col in ((0.0, "$P_0 = 0$", cl.COLORS[3]), (P_0, "baseline $P_0$", cl.COLORS[0]),
                      (2 * P_0, "$2P_0$", cl.COLORS[1])):
    cs = np.array([c_star_vs_span(l, P0v) for l in ls_km])
    ax.plot(alpha * ls_km + margin_db, cs / cs.max(), color=col, label=lab)
ax.axvspan(L("ch07.power.desbruslais_ideal_span_loss", "lo"), L("ch07.power.desbruslais_ideal_span_loss", "hi"),
           color=cl.GRAY, alpha=0.12)
ax.text(L("ch07.power.desbruslais_ideal_span_loss", "lo") + 0.1, 0.42, "Desbruslais\nideal range", fontsize=8)
ax.set_xlabel("span loss including margin (dB)")
ax.set_ylabel(r"optimized capacity $C^*$ / its maximum")
ax.set_ylim(0.4, 1.02)
ax.legend(fontsize=8.5)
fig.tight_layout()
cl.savefig(fig, "span_loss_opt")

r.save()
