"""Worked example 1.4: L_eff, gamma, L_NL and per-span nonlinear phase for
G.652.D vs G.654.E, plus the FWM phase-matching efficiency figure.

gamma = n2 omega/(c A_eff) = 2 pi n2/(lambda A_eff)
L_eff = (1 - exp(-alpha L))/alpha,  L_NL = 1/(gamma P),  phi_NL = gamma P L_eff
FWM efficiency (Poggiolini 2012 eq. (2), book alpha = power coefficient):
  eta_FWM = |(1 - exp(-alpha L) exp(j dbeta L))/(alpha - j dbeta)|^2 / L_eff^2,
  dbeta = beta2 dw1 dw2
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch01lib as cl

r = Results()
c = L("ch01.const.speed_of_light_c")
lam = float(cl.cond("ch01.kerr.aeff_g652d_typ", "wavelength_nm")) * 1e-9

# ASSUMPTION: 80 km span (same as worked example 1.1).
SPAN_KM = 80.0
# ASSUMPTION: per-channel launch power 0 dBm (1 mW) for the illustration.
P_DBM = 0.0
P = cl.dbm2w(P_DBM)
r.emit("p_dbm", P_DBM, "dBm", 2)

n2_sup47 = L("ch01.kerr.n2_pure_silica_gsup47")
n2_kato = L("ch01.kerr.n2_kato1995_smf")
n2_kim = L("ch01.kerr.n2_kim1994_silica_core")
r.emit("n2_spread_pct", 100 * (n2_kato / n2_kim - 1), "%", 2,
       ["ch01.kerr.n2_kato1995_smf", "ch01.kerr.n2_kim1994_silica_core"])


def gamma(n2, aeff_um2):
    return 2 * math.pi * n2 / (lam * aeff_um2 * 1e-12)   # 1/(W m)


fibers = {
    "g652": dict(aeff=L("ch01.kerr.aeff_g652d_typ"), aeff_id="ch01.kerr.aeff_g652d_typ",
                 alpha=L("ch01.att.smf28ultra_max_1550"), alpha_id="ch01.att.smf28ultra_max_1550"),
    "g654": dict(aeff=L("ch01.kerr.aeff_g654e_typ", "hi"), aeff_id="ch01.kerr.aeff_g654e_typ",
                 alpha=L("ch01.kerr.pureadvance125_att"), alpha_id="ch01.kerr.pureadvance125_att"),
    "g654lo": dict(aeff=L("ch01.kerr.aeff_g654e_typ", "lo"), aeff_id="ch01.kerr.aeff_g654e_typ",
                   alpha=L("ch01.kerr.pureadvance125_att"), alpha_id="ch01.kerr.pureadvance125_att"),
}
out = {}
for key, f in fibers.items():
    g = gamma(n2_sup47, f["aeff"])
    a = cl.alpha_np_per_m(f["alpha"])
    le = cl.leff(a, SPAN_KM * 1e3)
    lnl = 1 / (g * P)
    phi = g * P * le
    ins = [f["aeff_id"], f["alpha_id"], "ch01.kerr.n2_pure_silica_gsup47"]
    r.emit(f"gamma_{key}", g * 1e3, "1/(W·km)", 3, ins)
    r.emit(f"alpha_lin_{key}", a * 1e3, "1/km", 3, [f["alpha_id"]])
    r.emit(f"leff_{key}", le / 1e3, "km", 3, [f["alpha_id"]])
    r.emit(f"leffa_{key}", 1 / a / 1e3, "km", 3, [f["alpha_id"]])
    r.emit(f"lnl_{key}", lnl / 1e3, "km", 3, ins)
    r.emit(f"phi_{key}", phi, "rad", 3, ins)
    out[key] = dict(g=g, le=le, phi=phi)

# gamma with Kato's (XPM) n2 for G.652.D: the upper end of the measured spread
r.emit("gamma_g652_kato", gamma(n2_kato, fibers["g652"]["aeff"]) * 1e3, "1/(W·km)", 3,
       ["ch01.kerr.n2_kato1995_smf", "ch01.kerr.aeff_g652d_typ"])
r.emit("phi_ratio_db", cl.lin2db(out["g652"]["phi"] / out["g654"]["phi"]), "dB", 2,
       ["ch01.kerr.aeff_g652d_typ", "ch01.kerr.aeff_g654e_typ"])

# Checks against model parameters used in the GN literature
assert abs(out["g652"]["g"] * 1e3 / L("ch01.kerr.gamma_smf_gn2012") - 1) < 0.05
assert abs(out["g654"]["g"] * 1e3 / L("ch01.kerr.gamma_pscf_gn2012") - 1) < 0.10
lo, hi = L("ch01.kerr.gamma_range_silica_agrawal", "lo"), L("ch01.kerr.gamma_range_silica_agrawal", "hi")
assert lo <= out["g652"]["g"] * 1e3 <= hi
# G.Sup47 asymptote check: 1/alpha for 0.25 dB/km = 17.24 km
a025 = cl.alpha_np_per_m(float(cl.cond("ch01.kerr.leff_asymptote_gsup47", "alpha_dB_per_km")))
# G.Sup47 rounds alpha to 0.000058 1/m, giving 17.24 km; the unrounded value is
# 17.37 km. Agreement within 1 % is the correct test.
assert abs(1 / a025 / 1e3 / L("ch01.kerr.leff_asymptote_gsup47") - 1) < 0.01
r.emit("leffa_025", 1 / a025 / 1e3, "km", 4, ["ch01.kerr.leff_asymptote_gsup47"])

# ---------------- FWM phase matching
def beta2(D):
    return cl.beta2_from_d(D, lam, c)


def eta_fwm(D, df, alpha_m, Lm):
    db = abs(beta2(D)) * (2 * math.pi * df) ** 2
    le = cl.leff(alpha_m, Lm)
    num = 1 - np.exp(-alpha_m * Lm) * np.exp(1j * db * Lm)
    return np.abs(num / (alpha_m - 1j * db)) ** 2 / le ** 2


Lsup = float(cl.cond("ch01.fwm.vanish_100ghz_d1", "L_km")) * 1e3
asup = cl.alpha_np_per_m(float(cl.cond("ch01.fwm.vanish_100ghz_d1", "alpha_dB_per_km")))
Dsup = float(cl.cond("ch01.fwm.vanish_100ghz_d1", "D_ps_nm_km"))
df_sup = L("ch01.fwm.vanish_100ghz_d1") * 1e9
e100 = eta_fwm(Dsup, df_sup, asup, Lsup)
e50 = eta_fwm(Dsup, df_sup / 2, asup, Lsup)
r.emit("eta_d1_100", cl.lin2db(e100), "dB", 3, ["ch01.fwm.vanish_100ghz_d1"])
r.emit("eta_d1_50", cl.lin2db(e50), "dB", 3, ["ch01.fwm.vanish_100ghz_d1"])
D17 = L("ch01.cd.g652_link_typ_d1550")
r.emit("eta_d17_50", cl.lin2db(eta_fwm(D17, df_sup / 2, asup, Lsup)), "dB", 3,
       ["ch01.cd.g652_link_typ_d1550", "ch01.fwm.vanish_100ghz_d1"])
# Coherence length 2 pi/dbeta at 50 GHz spacing
for tag, D, rid in (("d1", Dsup, "ch01.fwm.vanish_100ghz_d1"), ("d17", D17, "ch01.cd.g652_link_typ_d1550")):
    db = abs(beta2(D)) * (2 * math.pi * df_sup / 2) ** 2
    r.emit(f"lcoh50_{tag}", 2 * math.pi / db / 1e3, "km", 3, [rid])
r.emit("asup_inv_km", 1 / asup / 1e3, "km", 3, ["ch01.fwm.vanish_100ghz_d1"])

# ---------------- figure: FWM efficiency vs spacing
plt = cl.setup_mpl()
dfs = np.linspace(1e9, 200e9, 800)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
cases = [(0.0, "D = 0 (G.653 at its zero-dispersion wavelength)", cl.COLORS[4]),
         (L("ch01.fwm.g655_dmin_dmax_1996", "lo"), "D = 0.1 ps/(nm·km) (G.655 1996 lower bound)", cl.COLORS[3]),
         (Dsup, "D = 1 ps/(nm·km)", cl.COLORS[0]),
         (L("ch01.fwm.g655_dmin_dmax_1996", "hi"), "D = 6 ps/(nm·km) (G.655 1996 upper bound)", cl.COLORS[2]),
         (D17, "D = 17 ps/(nm·km) (G.652 typical)", cl.COLORS[1])]
for D, lab, col in cases:
    if D == 0:
        y = np.zeros_like(dfs)
    else:
        y = 10 * np.log10(eta_fwm(D, dfs, asup, Lsup))
    ax.plot(dfs / 1e9, y, color=col, lw=2, label=lab)
ax.set_xlabel(r"Channel spacing $\Delta f$ (GHz)")
ax.set_ylabel(r"FWM efficiency $\eta_{\mathrm{FWM}}$ (dB)")
ax.set_ylim(-50, 3)
ax.set_xlim(0, 200)
ax.legend(fontsize=8.5, loc="lower left")
ax.set_title("Computed: L = 50 km, 0.25 dB/km, degenerate FWM", fontsize=10)
cl.savefig(fig, "fwm_efficiency")

r.save()
