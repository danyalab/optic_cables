"""Worked example 6.3: Raman gain, the effective noise figure of distributed
amplification, and ISRS power tilt across C, C+L and super C+L.

Part A  Raman gain efficiency from two measurements; consistency with the ISRS slope C_r.
Part B  Backward-pumped span: on-off gain, input-referred noise factor, effective NF
        F_BR = F_span / A_span, total NF with the following EDFA (Pelouch Eq. (12)),
        and the on-off gain that reproduces Pelouch's 4.75 dB OSNR advantage.
Part C  From linear OSNR gain to reach: the 2/3 rule (Xtera check), and the
        effective-length (NLI) correction from the Raman power profile.
Part D  ISRS tilt (Semrau JLT 2019 Eq. (3)) and exact profile (uniform launch).
"""
import math
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from scipy.optimize import brentq
import ch06lib as c6
from common import L, Results

r = Results()
h, c = c6.consts()
LAM = 1550e-9          # ASSUMPTION: signal wavelength for h nu (as in Chapter 1, A21)
nu = c / LAM

# ---------------------------------------------------------------- Part A
AN = "ch06.raman.peak_gr_ssmf_andre"
gR = L(AN)                                      # m/W
aeff_an = float(c6.cond(AN, "aeff_um2")) * 1e-12
CR_andre = gR / aeff_an * 1e3                   # 1/(W km)
CR_kjaer = L("ch06.raman.gain_eff_ssmf")        # 1/(W km)
r.emit("cr_andre", CR_andre, "1/(W·km)", 3, [AN])
r.emit("cr_kjaer", CR_kjaer, "1/(W·km)", 2, ["ch06.raman.gain_eff_ssmf"])
r.emit("cr_ratio_pct", 100 * (CR_andre / CR_kjaer - 1), "%", 2, [AN, "ch06.raman.gain_eff_ssmf"])
Cr = L("ch06.raman.cr_ssmf")                    # 1/(W km THz)
pk = c6.cond("ch06.raman.gain_eff_ssmf", "peak_shift_THz")
tri_peak = Cr * pk[0]
r.emit("cr_tri_peak", tri_peak, "1/(W·km)", 3, ["ch06.raman.cr_ssmf", "ch06.raman.gain_eff_ssmf"])
r.emit("peak_shift_lo", pk[0], "THz", 3, ["ch06.raman.gain_eff_ssmf"])
assert 0.8 < tri_peak / CR_kjaer < 1.0, "triangle slope x peak shift should sit just below the peak"

# ---------------------------------------------------------------- Part B
# ASSUMPTIONS for the distributed-amplification example
SPAN_KM = 100.0                                 # span length
A_S = L("ch01.att.smf28ultra_max_1550")         # signal loss, dB/km (datasheet, Section 1.1)
A_P = 0.25                                      # pump loss near 1450 nm, dB/km (ASSUMPTION)
NSP = 1.0                                       # Raman spontaneous factor, lower bound (ASSUMPTION)
NZ = 20001
z = np.linspace(0.0, SPAN_KM, NZ)
a_s = A_S / c6.LN10_10
a_p = A_P / c6.LN10_10
A_span = math.exp(a_s * SPAN_KM)
r.emit("span_km", SPAN_KM, "km", 3)
r.emit("ap_db", A_P, "dB/km", 2)
r.emit("span_loss_db", A_S * SPAN_KM, "dB", 3, ["ch01.att.smf28ultra_max_1550"])
leff_p = (1 - math.exp(-a_p * SPAN_KM)) / a_p
r.emit("leff_p", leff_p, "km", 3)


def span(gon_db):
    """Backward-pumped span with on-off gain gon_db. Returns dict of profile and noise."""
    shape = np.exp(-a_p * (SPAN_KM - z))
    g0 = (gon_db / c6.LN10_10) / np.trapezoid(shape, z)      # 1/km at z = L
    g = g0 * shape
    cum = np.concatenate([[0.0], np.cumsum(0.5 * (g[1:] + g[:-1]) * np.diff(z))])
    ln_g0z = cum - a_s * z                                    # ln G(0,z)
    gon = 10 ** (gon_db / 10)
    feff = 1.0 / gon + 2 * NSP / A_span * np.trapezoid(g * np.exp(-ln_g0z), z)
    leff_sig = np.trapezoid(np.exp(ln_g0z), z)
    return {"g0": g0, "feff": feff, "leff": leff_sig, "ln_g0z": ln_g0z, "gon": gon}


# Sanity checks of the noise integral
s0 = span(1e-9)
assert abs(s0["feff"] - 1.0) < 1e-6, "no pumping: the fictitious end amplifier is noiseless with G = 1"
assert abs(s0["leff"] - (1 - math.exp(-a_s * SPAN_KM)) / a_s) < 1e-3
# Lumped-limit check: confine the gain to the last 0.1 km -> F_eff -> 2 nsp (G-1)/G + 1/G
zz = np.linspace(SPAN_KM - 0.1, SPAN_KM, 2001)
gl = (10 / c6.LN10_10) / 0.1
G10 = 10.0
lump = 1 / G10 + 2 * NSP / A_span * np.trapezoid(gl * np.exp(-(gl * (zz - zz[0]) - a_s * zz)), zz)
assert abs(lump - (2 * NSP * (G10 - 1) / G10 + 1 / G10)) < 0.01

NF_E = c6.cond("ch06.raman.pelouch_bwd_osnr_gain", "nf_edfa_dB")
F_E = c6.db2lin(NF_E)
r.emit("nf_e", NF_E, "dB", 2, ["ch06.raman.pelouch_bwd_osnr_gain"])


def nf_tot_excl_span(gon_db):
    s = span(gon_db)
    return c6.lin2db(s["feff"] + (F_E - 1) / s["gon"])


# Pelouch: improvement 4.75 dB over EDFA-only = NF_E - NF_tot (span loss cancels)
imp_pub = L("ch06.raman.pelouch_bwd_osnr_gain")
nf_tot_pub = NF_E - imp_pub
r.emit("nf_tot_pub", nf_tot_pub, "dB", 3, ["ch06.raman.pelouch_bwd_osnr_gain"])
assert abs(nf_tot_pub - (-0.25)) < 1e-9, "Pelouch: total NF -0.25 dB plus span loss"
g_match = brentq(lambda gd: nf_tot_excl_span(gd) - nf_tot_pub, 1.0, 30.0)
sm = span(g_match)
P_pump = sm["g0"] / CR_kjaer
binsB = ["ch06.raman.pelouch_bwd_osnr_gain", "ch01.att.smf28ultra_max_1550"]
r.emit("g_match", g_match, "dB", 3, binsB)
r.emit("feff_match_db", c6.lin2db(sm["feff"]), "dB", 3, binsB)
r.emit("pump_mw", P_pump * 1e3, "mW", 3, binsB + ["ch06.raman.gain_eff_ssmf"])
r.emit("pump_pub_mw", c6.cond("ch06.raman.pelouch_bwd_osnr_gain", "pump_mW"), "mW", 3, ["ch06.raman.pelouch_bwd_osnr_gain"])
r.emit("g_pelouch_rule", c6.cond("ch06.raman.pelouch_span_loss_thresholds", "raman_gain_dB"), "dB", 2,
       ["ch06.raman.pelouch_span_loss_thresholds"])
# Lumped-pump estimate: G_on = exp(C_R P L_eff,p) -> P for 10 dB
r.emit("pump_10db_mw", math.log(10) / (CR_kjaer * leff_p) * 1e3, "mW", 3, ["ch06.raman.gain_eff_ssmf"])
r.emit("pump_10db_andre_mw", math.log(10) / (CR_andre * leff_p) * 1e3, "mW", 3, [AN])
table = {}
for gd in (5, 10, 15, 20):
    s = span(gd)
    table[gd] = s
    r.emit(f"feff_{gd}", c6.lin2db(s["feff"]), "dB", 3, binsB)
    r.emit(f"nftot_{gd}", nf_tot_excl_span(gd), "dB", 3, binsB)
    r.emit(f"imp_{gd}", NF_E - nf_tot_excl_span(gd), "dB", 3, binsB)
    r.emit(f"leff_{gd}", s["leff"], "km", 3, binsB)
r.emit("leff_0", s0["leff"], "km", 3, ["ch01.att.smf28ultra_max_1550"])

# Forward + backward (Pelouch Eq. (13)): forward gain G_FR divides the span loss
gfr = c6.cond("ch06.raman.pelouch_fwd_bwd_15db", "forward_gain_dB")
imp_fb = imp_pub + gfr
assert abs(imp_fb - L("ch06.raman.pelouch_fwd_bwd_15db")) <= 0.5
r.emit("imp_fwd_bwd", imp_fb, "dB", 3, ["ch06.raman.pelouch_fwd_bwd_15db", "ch06.raman.pelouch_bwd_osnr_gain"])
r.emit("gfr", gfr, "dB", 2, ["ch06.raman.pelouch_fwd_bwd_15db"])

# ---------------------------------------------------------------- Part C
nf_ratio = c6.cond("ch06.raman.xtera_reach_factor", "nf_ratio")
assert abs(nf_ratio ** (2 / 3) - L("ch06.raman.xtera_reach_factor")) < 0.01
r.emit("xtera_ratio", nf_ratio ** (2 / 3), "1", 3, ["ch06.raman.xtera_reach_factor"])
r.emit("xtera_nf_db", c6.lin2db(nf_ratio), "dB", 3, ["ch06.raman.xtera_reach_factor"])
lin_ratio = c6.db2lin(imp_pub)
gn_ratio = c6.db2lin(2 / 3 * imp_pub)
r.emit("lin_reach_ratio", lin_ratio, "1", 3, ["ch06.raman.pelouch_bwd_osnr_gain"])
r.emit("gn_reach_ratio", gn_ratio, "1", 3, ["ch06.raman.pelouch_bwd_osnr_gain"])
r.emit("gn_gain_db", 2 / 3 * imp_pub, "dB", 3, ["ch06.raman.pelouch_bwd_osnr_gain"])
# Effective-length correction (ASSUMPTION: eta scales as L_eff^2, asinh factor unchanged)
d_eta = 20 * math.log10(sm["leff"] / s0["leff"])
gn_corr = 2 / 3 * imp_pub - d_eta / 3
r.emit("leff_match", sm["leff"], "km", 3, binsB)
r.emit("d_eta_db", d_eta, "dB", 3, binsB)
r.emit("gn_corr_db", gn_corr, "dB", 3, binsB)
r.emit("gn_corr_ratio", c6.db2lin(gn_corr), "1", 3, binsB)
assert 1.0 < c6.db2lin(gn_corr) < gn_ratio < lin_ratio

# ---------------------------------------------------------------- Part D: ISRS tilt
# ASSUMPTIONS: 80 km span of SMF-28 Ultra (as in Chapter 1); 0 dBm per 75 GHz channel,
# uniform over the occupied band; C_r of SSMF from Semrau.
SPAN2 = 80.0
P_CH_DBM = 0.0
DF = 75e9
a2 = A_S / c6.LN10_10
leff80 = (1 - math.exp(-a2 * SPAN2)) / a2      # km
r.emit("leff80", leff80, "km", 4, ["ch01.att.smf28ultra_max_1550"])
r.emit("p_ch_dbm", P_CH_DBM, "dBm", 2)
psd = c6.dbm2w(P_CH_DBM) / DF                   # W/Hz
r.emit("psd_uw_ghz", psd * 1e9 * 1e6, "µW/GHz", 3)
B_C = (L("ch06.zr.cband_191p3_196p1", "hi") - L("ch06.zr.cband_191p3_196p1", "lo"))
B_CL = L("ch06.cl.semrau_cl_10thz")
sl = c6.cond("ch06.cl.super_cl_12thz_bands", "super_L_THz")
sc = c6.cond("ch06.cl.super_cl_12thz_bands", "super_C_THz")
B_SCL = (sl[1] - sl[0]) + (sc[1] - sc[0])
assert max(B_C, B_CL, B_SCL) <= L("ch06.raman.triangular_validity"), "triangular approximation valid"
bands = {"c": (B_C, ["ch06.zr.cband_191p3_196p1"]), "cl": (B_CL, ["ch06.cl.semrau_cl_10thz"]),
         "scl": (B_SCL, ["ch06.cl.super_cl_12thz_bands"])}
insD = ["ch06.raman.cr_ssmf", "ch01.att.smf28ultra_max_1550"]
for tag, (B, ins) in bands.items():
    nch = math.floor(B * 1e12 / DF + 1e-9)
    ptot = nch * c6.dbm2w(P_CH_DBM)
    x = ptot * Cr * leff80                      # 1/THz
    tilt = c6.LN10_10 * x * B
    r.emit(f"{tag}_nch", nch, "", 3, ins)
    r.emit(f"{tag}_ptot_dbm", c6.w2dbm(ptot), "dBm", 3, ins)
    r.emit(f"{tag}_tilt", tilt, "dB", 3, insD + ins)
    r.emit(f"{tag}_tilt_per_thz", tilt / B, "dB/THz", 2, insD + ins)
    # exact uniform-launch profile: edge gains relative to the flat (no-ISRS) level
    xb = x * B
    edge_lo = c6.lin2db(xb * math.exp(xb / 2) / (2 * math.sinh(xb / 2)))
    edge_hi = c6.lin2db(xb * math.exp(-xb / 2) / (2 * math.sinh(xb / 2)))
    assert abs((edge_lo - edge_hi) - tilt) < 1e-9
    r.emit(f"{tag}_edge_lo", edge_lo, "dB", 3, insD + ins)
    r.emit(f"{tag}_edge_hi", edge_hi, "dB", 3, insD + ins)
    if tag == "cl":
        x_cl, B_cl_v, p_cl = x, B, ptot
# Fixed-PSD scaling: tilt ~ B^2
assert abs(r.data["cl_tilt"]["value"] / r.data["c_tilt"]["value"]
           - (r.data["cl_nch"]["value"] * B_CL) / (r.data["c_nch"]["value"] * B_C)) < 1e-9
# Total C+L power for 1 dB of tilt
p1db = 1.0 / (c6.LN10_10 * Cr * leff80 * B_CL)
r.emit("cl_p_1db_dbm", c6.w2dbm(p1db), "dBm", 3, insD + ["ch06.cl.semrau_cl_10thz"])

# ---------------------------------------------------------------- figures
plt = c6.setup_mpl()
fig, axs = plt.subplots(1, 2, figsize=(9.6, 3.9))
ax = axs[0]
for i, gd in enumerate((0, 10, 15, 20)):
    s = span(gd if gd else 1e-9)
    ax.plot(z, 10 * s["ln_g0z"] / math.log(10), color=c6.COLORS[i], label=f"$G_{{\\mathrm{{on}}}}$ = {gd} dB")
ax.set_xlabel("Distance z (km)")
ax.set_ylabel("Signal power relative to launch (dB)")
ax.set_title(f"Computed: backward-pumped {SPAN_KM:.0f} km SMF span", fontsize=10)
ax.legend(fontsize=8.5, loc="lower left")
ax = axs[1]
gg = np.linspace(0.5, 22, 80)
ax.plot(gg, [c6.lin2db(span(g)["feff"]) for g in gg], color=c6.COLORS[0], label="$F_{\\mathrm{BR}}$ (Raman alone)")
ax.plot(gg, [nf_tot_excl_span(g) for g in gg], color=c6.COLORS[1], label=f"Raman + EDFA (NF {NF_E:g} dB)")
ax.axhline(NF_E, color=c6.GRAY, ls=":", lw=1)
ax.text(1, NF_E - 0.7, "EDFA only", fontsize=8.5)
ax.plot([g_match], [nf_tot_pub], "o", color=c6.COLORS[3], ms=7)
ax.annotate("Pelouch: 4.75 dB gain", (g_match, nf_tot_pub), xytext=(g_match - 3, nf_tot_pub + 2.2), fontsize=8.5,
            arrowprops=dict(arrowstyle="-", color=c6.GRAY, lw=0.8))
ax.set_xlabel("On-off Raman gain (dB)")
ax.set_ylabel("Noise figure, span loss removed (dB)")
ax.set_title("Computed: effective noise figure", fontsize=10)
ax.legend(fontsize=8.5, loc="upper right")
fig.tight_layout()
c6.savefig(fig, "raman_profile_nf")

fig, ax = plt.subplots(figsize=(7.2, 4.0))
f = np.linspace(-B_CL / 2, B_CL / 2, 401)
for i, pdbm in enumerate((-3.0, 0.0, 3.0)):
    pt = r.data["cl_nch"]["value"] * c6.dbm2w(pdbm)
    xx = pt * Cr * leff80
    prof = xx * B_CL * np.exp(-xx * f) / (2 * math.sinh(xx * B_CL / 2))
    ax.plot(f, 10 * np.log10(prof), color=c6.COLORS[i],
            label=f"{pdbm:+.0f} dBm/ch ({c6.w2dbm(pt):.1f} dBm total)")
ax.set_xlabel("Frequency offset from band centre (THz); low frequency (L side) at left")
ax.set_ylabel("Power at span end vs no ISRS (dB)")
ax.set_title("Computed: ISRS power transfer over 10 THz C+L, 80 km SSMF", fontsize=10)
ax.legend(fontsize=9, loc="upper right")
c6.savefig(fig, "isrs_tilt")

r.save()
