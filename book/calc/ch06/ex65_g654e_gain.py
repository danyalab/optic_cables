"""Worked example 6.5: expected GSNR gain of G.654.E over G.652.D in a terrestrial
EDFA line, from the GN model of Section 1.6 and its dampening rules.

GSNR_max = (1/3) (4/eta)^(1/3) P_ASE^(-2/3), so
  dGSNR_max [dB] = (1/3) d(1/eta) [dB] + (2/3) d(1/P_ASE) [dB]      (exact for identical spans)
and the span count, hence reach, scales by the same factor (eps = 0).

Three cases for the attenuation difference; the effective area, n2 and D differences are
common to all three. The operator-reported +3.5 dB (tier C) is compared in the prose box.
"""
import math
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from scipy.optimize import brentq
import ch06lib as c6
from common import L, Results

r = Results()
h, c = c6.consts()
LAM = 1550e-9                    # ASSUMPTION (Chapter 1, A21)
nu = c / LAM
RS = 64e9                        # ASSUMPTION: Chapter 1 symbol rate (A15)
DF = 75e9                        # ASSUMPTION: 75 GHz grid
NCH = 64                         # 4.8 THz C-band / 75 GHz (Section 6.1, ex61.nc_75)
SPAN = 80e3                      # ASSUMPTION: 80 km spans (Chapter 1, A1)
OVH = 1.95                       # ASSUMPTION: splices + connectors per span, dB (Chapter 1 span budget)
NF = L("ch01.amp.accelink_mw_nf_max")
F = c6.db2lin(NF)

# Fibre parameters
A652 = L("ch01.kerr.aeff_g652d_typ")
A654 = c6.from_text("ch01.att.yofc_ct_shanghai_guangzhou", r"A_eff (\d+)")
n2_652 = L("ch01.kerr.n2_kato1995_smf")
n2_654 = L("ch01.kerr.n2_kato1995_pscf")
D652 = L("ch01.cd.g652_link_typ_d1550")
D654 = L("ch01.cd.g654e_d1550_range", "mid")      # ASSUMPTION: midpoint of the ITU range
g652 = c6.gamma_from(n2_652, A652, LAM, c)
g654 = c6.gamma_from(n2_654, A654, LAM, c)
fib_ins = ["ch01.kerr.aeff_g652d_typ", "ch01.att.yofc_ct_shanghai_guangzhou", "ch01.kerr.n2_kato1995_smf",
           "ch01.kerr.n2_kato1995_pscf", "ch01.cd.g652_link_typ_d1550", "ch01.cd.g654e_d1550_range"]
r.emit("a654", A654, "µm²", 3, ["ch01.att.yofc_ct_shanghai_guangzhou"])
r.emit("a652", A652, "µm²", 2, ["ch01.kerr.aeff_g652d_typ"])
r.emit("g652", g652 * 1e3, "1/(W·km)", 3, fib_ins)
r.emit("g654", g654 * 1e3, "1/(W·km)", 3, fib_ins)
r.emit("d654", D654, "ps/(nm·km)", 2, ["ch01.cd.g654e_d1550_range"])
r.emit("d652", D652, "ps/(nm·km)", 2, ["ch01.cd.g652_link_typ_d1550"])
r.emit("n2_ratio_db", c6.lin2db(n2_652 / n2_654), "dB", 2, ["ch01.kerr.n2_kato1995_smf", "ch01.kerr.n2_kato1995_pscf"])
r.emit("aeff_ratio_db", c6.lin2db(A654 / A652), "dB", 3, fib_ins)


def one_span(alpha_db, gamma, D, span=SPAN):
    mu = c6.mu_coeff(gamma, alpha_db, D, span, RS, DF, NCH, LAM, c)
    eta = mu / RS ** 2
    G = c6.db2lin(alpha_db * span / 1e3 + OVH)
    pase = (F * G - 1) * h * nu * RS
    popt = (pase / (2 * eta)) ** (1 / 3)
    gmax = (2 / 3) * popt / pase
    return eta, pase, popt, gmax


def compare(a652, a654, span=SPAN):
    e1, p1, po1, g1 = one_span(a652, g652, D652, span)
    e2, p2, po2, g2 = one_span(a654, g654, D654, span)
    gain = c6.lin2db(g2 / g1)
    d_eta = c6.lin2db(e1 / e2)
    d_ase = c6.lin2db(p1 / p2)
    assert abs(gain - (d_eta / 3 + 2 * d_ase / 3)) < 1e-9, "dampening rule is exact for identical spans"
    return gain, d_eta, d_ase, c6.w2dbm(po2) - c6.w2dbm(po1)


cases = {
    "ds": (L("ch01.att.smf28ultra_max_1550"), L("ch01.att.yofc_ct_shanghai_guangzhou"),
           ["ch01.att.smf28ultra_max_1550", "ch01.att.yofc_ct_shanghai_guangzhou"]),
    "zte": (0.18, 0.18 - L("ch01.att.zte_g654e_vs_g652d_80km") / 80.0, ["ch01.att.zte_g654e_vs_g652d_80km"]),
    "itu": (L("ch01.att.g652d_max_1530_1565"), L("ch01.att.g654e_max_1550"),
            ["ch01.att.g652d_max_1530_1565", "ch01.att.g654e_max_1550"]),
}
assert c6.cond("ch01.att.zte_g654e_vs_g652d_80km", "span_km") == 80
base = ["ch01.amp.accelink_mw_nf_max"] + fib_ins
for tag, (a1, a2, ins) in cases.items():
    gain, d_eta, d_ase, dpopt = compare(a1, a2)
    r.emit(f"{tag}_dloss", (a1 - a2) * SPAN / 1e3, "dB", 3, ins)
    r.emit(f"{tag}_gain", gain, "dB", 3, base + ins)
    r.emit(f"{tag}_deta", d_eta, "dB", 3, base + ins)
    r.emit(f"{tag}_dase", d_ase, "dB", 3, base + ins)
    r.emit(f"{tag}_dpopt", dpopt, "dB", 3, base + ins)
    r.emit(f"{tag}_reach_pct", 100 * (c6.db2lin(gain) - 1), "%", 2, base + ins)

# Breakdown of d(1/eta) for the datasheet case: gamma^2 (A_eff and n2), dispersion/asinh, L_eff
a1, a2 = cases["ds"][0], cases["ds"][1]
gam_part = 2 * c6.lin2db(g652 / g654)
e_mixed, *_ = one_span(a1, g654, D652)      # G.652.D loss and D, G.654.E gamma
e_d, *_ = one_span(a1, g654, D654)          # add G.654.E dispersion
e_all, *_ = one_span(a2, g654, D654)
e1, *_ = one_span(a1, g652, D652)
assert abs(c6.lin2db(e1 / e_mixed) - gam_part) < 1e-9
r.emit("bd_gamma", gam_part, "dB", 3, fib_ins)
r.emit("bd_disp", c6.lin2db(e_mixed / e_d), "dB", 2, fib_ins)
r.emit("bd_leff", c6.lin2db(e_d / e_all), "dB", 2, fib_ins)

# Fixed launch power (same per-channel power on both fibres): ASE-limited OSNR gain = d P_ASE
r.emit("ds_fixed_launch", r.data["ds_dase"]["value"], "dB", 3, base)
r.emit("zte_fixed_launch", r.data["zte_dase"]["value"], "dB", 3, base)

# Attenuation difference that would make the model gain equal a target X (used for the 3.5 dB claim)
def dalpha_for(target_db, span=SPAN):
    return brentq(lambda da: compare(0.18, 0.18 - da, span)[0] - target_db, 0.0, 0.15)


X = L("ch06.g654e.ctel_osnr_3p5db")      # tier C: used only in the contested box
da = dalpha_for(X)
r.emit("ct_claim", X, "dB", 2, ["ch06.g654e.ctel_osnr_3p5db"])
r.emit("ct_dalpha", da, "dB/km", 2, ["ch06.g654e.ctel_osnr_3p5db"] + base)
r.emit("ct_dloss", da * SPAN / 1e3, "dB", 2, ["ch06.g654e.ctel_osnr_3p5db"] + base)
r.emit("ct_gap", X - r.data["zte_gain"]["value"], "dB", 2, ["ch06.g654e.ctel_osnr_3p5db"] + base)
# At fixed launch power the 3.5 dB would need a span-loss difference of 3.5 dB
r.emit("ct_dalpha_fixed", X / (SPAN / 1e3), "dB/km", 2, ["ch06.g654e.ctel_osnr_3p5db"])

# Corning FOM band (tier B)
fom = c6.rec("ch06.g654e.corning_fom_range")["value"]
r.emit("fom_lo", fom[0], "dB", 2, ["ch06.g654e.corning_fom_range"])
r.emit("fom_hi", fom[1], "dB", 2, ["ch06.g654e.corning_fom_range"])
assert fom[0] <= r.data["zte_gain"]["value"] <= fom[1] + 0.2

# Reach ratios reported in the literature, converted to dB
haz = c6.rec("ch06.g654e.aston_raman_rin")["value"]
r.emit("haz_db", c6.lin2db(haz[0] / haz[1]), "dB", 2, ["ch06.g654e.aston_raman_rin"])
r.emit("haz_pct", 100 * (haz[0] / haz[1] - 1), "%", 2, ["ch06.g654e.aston_raman_rin"])
cor = c6.from_text("ch06.g654e.corning_fom_range", r"400G reach \+(\d+)%")
r.emit("cor_pct", cor, "%", 2, ["ch06.g654e.corning_fom_range"])
r.emit("cor_db", c6.lin2db(1 + cor / 100), "dB", 2, ["ch06.g654e.corning_fom_range"])
r.emit("dow_db", c6.lin2db(1 + L("ch06.g654e.downie_reach_55pct") / 100), "dB", 2, ["ch06.g654e.downie_reach_55pct"])
cu = c6.rec("ch06.g654e.cunicom_800g_1100km")["value"]
r.emit("cu_db", c6.lin2db(cu[0] / cu[1]), "dB", 2, ["ch06.g654e.cunicom_800g_1100km"])

# Span-length dependence (ZTE-type 0.02 dB/km advantage, and the datasheet pair)
spans = np.arange(50, 125, 5) * 1e3
dz = L("ch01.att.zte_g654e_vs_g652d_80km") / 80.0
gz = [compare(0.18, 0.18 - dz, s)[0] for s in spans]
gd = [compare(a1, a2, s)[0] for s in spans]
r.emit("zte_gain_120", gz[-1], "dB", 3, base)
r.emit("zte_gain_50", gz[0], "dB", 3, base)

plt = c6.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.0))
ax.plot(spans / 1e3, gz, color=c6.COLORS[0], label=f"loss advantage {dz:.3f} dB/km (ZTE typical)")
ax.plot(spans / 1e3, gd, color=c6.COLORS[1], label=f"datasheet pair ({a1:g} vs {a2:g} dB/km)")
ax.axhspan(fom[0], fom[1], color=c6.COLORS[2], alpha=0.15, lw=0)
ax.text(52, fom[1] - 0.25, "Corning FOM range (vendor)", fontsize=8.5)
ax.axhline(X, color=c6.COLORS[3], ls="--", lw=1.3)
ax.text(52, X + 0.08, "China Telecom field claim (contested)", fontsize=8.5)
ax.set_xlabel("Span length (km)")
ax.set_ylabel("GSNR$_{\\max}$ gain of G.654.E (dB)")
ax.set_ylim(0, 4.2)
ax.set_title("Computed: GN-model gain, A_eff 130 vs 80 µm², NF 5 dB, 64 x 75 GHz", fontsize=10)
ax.legend(fontsize=8.5, loc="lower right")
c6.savefig(fig, "g654e_gain")

r.save()
