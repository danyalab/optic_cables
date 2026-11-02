"""Worked example 3.4: silicon MZM and microring modulators.

A. Soref-Bennett plasma dispersion at 1550 nm (Reed 2010 Eqs. (1)-(2)).
B. Depletion-mode V_pi L estimate for the Feng et al. lateral PN junction.
C. Length optimization of a lossy Si MZM at fixed drive (OMA vs loss).
D. Microring FSR, linewidth, finesse, photon lifetime, thermal sensitivity.
E. Worked example: heater power budget for an 8-ring WDM transmitter.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
from scipy.optimize import brentq, minimize_scalar
import ch03lib as cl

r = Results()
LAM = 1550e-9   # Soref coefficients are for 1.55 um
assert abs(float(cl.cond("ch03.si.soref_dn_electron_1550", "wavelength_um")) - 1.55) < 1e-9

# ------------------------------------------------------------ A. Soref-Bennett
ce, ch = cl.eq_coeffs("ch03.eq.soref_dn_1550")
ae, ah = cl.eq_coeffs("ch03.eq.soref_dalpha_1550")
assert abs(ce - L("ch03.si.soref_dn_electron_1550")) < 1e-30 and abs(ch - L("ch03.si.soref_dn_hole_1550")) < 1e-25
dN = float(cl.cond("ch03.si.soref_worked_dn", "delta_N_cm3"))


def dn(Ne, Nh):
    return -(ce * Ne + ch * Nh ** 0.8)


def dalpha(Ne, Nh):   # 1/cm
    return ae * Ne + ah * Nh


dn5 = dn(dN, dN)
assert abs(dn5 - L("ch03.si.soref_worked_dn")) < 0.01e-3
inss = ["ch03.si.soref_dn_electron_1550", "ch03.si.soref_dn_hole_1550"]
r.emit("dn_5e17", dn5, "1", 3, inss + ["ch03.si.soref_worked_dn"])
r.emit("dn_e_5e17", -ce * dN, "1", 3, inss)
r.emit("dn_h_5e17", -ch * dN ** 0.8, "1", 3, inss)
r.emit("hole_over_e", (ch * dN ** 0.8) / (ce * dN), "1", 3, inss)
da = dalpha(dN, dN)
r.emit("dalpha_5e17", da, "1/cm", 3, ["ch03.si.soref_worked_dn"])
r.emit("dalpha_5e17_db", 10 * math.log10(math.e) * da, "dB/cm", 3, ["ch03.si.soref_worked_dn"])
# phase per unit loss for electrons vs holes (dn/dalpha)
r.emit("fom_e", (ce * dN) / (ae * dN), "cm", 3, inss)
r.emit("fom_h", (ch * dN ** 0.8) / (ah * dN), "cm", 3, inss)
# Length for a pi shift if the whole mode saw dn5: L_pi = lambda / (2 |dn|)
r.emit("lpi_ideal", LAM / (2 * abs(dn5)) * 1e6, "µm", 3, inss)

# ------------------------------------------------------------ B. depletion V_pi L estimate
NA = 5e17      # p doping, cm^-3 (ledger conditions of ch03.si.feng_vpil)
ND = 1e18      # n doping
assert "p 5e17" in cl.cond("ch03.si.feng_vpil", "doping") and "n 1e18" in cl.cond("ch03.si.feng_vpil", "doping")
EPS0 = 8.8541878188e-14      # F/cm; ASSUMPTION (needs CODATA ledger record)
EPS_SI = 11.7                # ASSUMPTION (needs ledger record): relative permittivity of Si
VBI = 0.9                    # V; ASSUMPTION: built-in potential of the PN junction
W_WG = 0.5e-4                # cm; ASSUMPTION: rib width 0.5 um, junction at the centre
GAMMA_Y = 0.8                # ASSUMPTION: fraction of mode power in the doped Si slab height
r.emit("vbi", VBI, "V", 2)
r.emit("w_wg", W_WG * 1e4, "µm", 2)
r.emit("gamma_y", GAMMA_Y, "1", 2)
r.emit("eps_si", EPS_SI, "1", 3)


def wdep(V):
    """Total depletion width (cm) of an abrupt junction at reverse bias V."""
    return math.sqrt(2 * EPS_SI * EPS0 * (VBI + V) * (NA + ND) / (cl.Q_E * NA * ND))


def dneff(V):
    """Effective-index change at reverse bias V relative to 0 V (negative of carrier removal)."""
    dW = wdep(V) - wdep(0.0)
    dxp = dW * ND / (NA + ND)
    dxn = dW * NA / (NA + ND)
    # lateral cos^2 mode of width W_WG peaks at 2/W_WG (normalized), junction at the peak
    return GAMMA_Y * (2 / W_WG) * (ch * NA ** 0.8 * dxp + ce * ND * dxn)   # positive: removing carriers raises n


r.emit("wdep0", wdep(0) * 1e7, "nm", 3)
VB = float(cl.cond("ch03.si.feng_vpil", "bias_V"))
r.emit("wdep_vb", wdep(VB) * 1e7, "nm", 3, ["ch03.si.feng_vpil"])
vpil_avg = LAM * 1e2 * VB / (2 * dneff(VB))          # V*cm, large-signal 0..VB, single arm
dd = 1e-3
vpil_ss0 = LAM * 1e2 / (2 * (dneff(dd) - dneff(0)) / dd)
vpil_ss2 = LAM * 1e2 / (2 * (dneff(2 + dd) - dneff(2)) / dd)
insb = ["ch03.si.feng_vpil", "ch03.si.soref_dn_electron_1550", "ch03.si.soref_dn_hole_1550"]
r.emit("vpil_avg", vpil_avg, "V·cm", 2, insb)
r.emit("vpil_ss0", vpil_ss0, "V·cm", 2, insb)
r.emit("vpil_ss2", vpil_ss2, "V·cm", 2, insb)
r.emit("vb", VB, "V", 2, ["ch03.si.feng_vpil"])
assert 0.5 < vpil_avg / L("ch03.si.feng_vpil") < 2.0   # order-of-magnitude model: within a factor of 2

# ------------------------------------------------------------ C. lossy MZM length optimum
VPIL = L("ch03.si.feng_vpil")           # V*cm
ALPHA_DB = L("ch03.si.feng_doping_loss")  # dB/cm
a_np = ALPHA_DB / (10 * math.log10(math.e))  # 1/cm (power)
VPP = 2.0   # ASSUMPTION: 2 Vpp differential drive in push-pull (1 V per arm)
r.emit("vpp", VPP, "V", 2)


def oma_rel(Lcm):
    vpi_pp = VPIL / (2 * Lcm)
    return math.exp(-a_np * Lcm) * math.sin(min(math.pi / 2, math.pi * VPP / (2 * vpi_pp)))


res = minimize_scalar(lambda x: -oma_rel(x), bounds=(0.01, 1.0), method="bounded", options={"xatol": 1e-7})
Lopt = res.x
th = math.pi * VPP * Lopt / VPIL
# stationarity: d/dL [e^{-aL} sin(kL)] = 0  ->  tan(kL) = k/a with k = pi VPP / VPIL
assert abs(math.tan(th) - (math.pi * VPP / VPIL) / a_np) / ((math.pi * VPP / VPIL) / a_np) < 1e-3
insc = ["ch03.si.feng_vpil", "ch03.si.feng_doping_loss"]
r.emit("a_np", a_np, "1/cm", 3, ["ch03.si.feng_doping_loss"])
r.emit("lopt", Lopt * 10, "mm", 3, insc)
r.emit("vpi_pp_opt", VPIL / (2 * Lopt), "V", 3, insc)
r.emit("il_opt", ALPHA_DB * Lopt, "dB", 3, insc)
r.emit("oma_opt_db", 10 * math.log10(oma_rel(Lopt)), "dB", 3, insc)
r.emit("vpil_alpha_si", VPIL * ALPHA_DB, "V·dB", 3, insc)

# ------------------------------------------------------------ D. microring
LAMR = float(cl.cond("ch03.ring.sun_q", "wavelength_nm")) * 1e-9
DIA = float(cl.cond("ch03.ring.sun_q", "diameter_um")) * 1e-6
NG = L("ch03.ring.bogaerts_ng")   # ASSUMPTION: Bogaerts wire group index applies to the Sun ring
Lr = math.pi * DIA
Q = L("ch03.ring.sun_q")
fsr = LAMR ** 2 / (NG * Lr)
fwhm = LAMR / Q
F = fsr / fwhm
tau = Q * LAMR / (2 * math.pi * cl.C0)
insd = ["ch03.ring.sun_q", "ch03.ring.bogaerts_ng"]
r.emit("ring_lam", LAMR * 1e9, "nm", 4, ["ch03.ring.sun_q"])
r.emit("ring_lr", Lr * 1e6, "µm", 3, ["ch03.ring.sun_q"])
r.emit("fsr", fsr * 1e9, "nm", 3, insd)
r.emit("fsr_ghz", cl.C0 * fsr / LAMR ** 2 / 1e9, "GHz", 3, insd)
r.emit("fwhm_pm", fwhm * 1e12, "pm", 3, ["ch03.ring.sun_q"])
r.emit("fwhm_ghz", cl.C0 / (LAMR * Q) / 1e9, "GHz", 3, ["ch03.ring.sun_q"])
r.emit("finesse", F, "1", 3, insd)
r.emit("tau_ph", tau * 1e12, "ps", 3, ["ch03.ring.sun_q"])
# loaded-Q -> round-trip product ra (Bogaerts Eq. (20)): Q = pi ng Lr sqrt(ra) / (lam (1 - ra))
ra = brentq(lambda x: math.pi * NG * Lr * math.sqrt(x) / (LAMR * (1 - x)) - Q, 0.5, 0.999999)
r.emit("ra", ra, "1", 4, insd)
# thermal: Sun locks 60 K with 3 nm -> dlambda/dT
dldT = float(cl.cond("ch03.ring.sun_lock_range", "tuning_nm")) / L("ch03.ring.sun_lock_range")   # nm/K
r.emit("dldt", dldT * 1e3, "pm/K", 3, ["ch03.ring.sun_lock_range"])
dndT = dldT * 1e-9 * NG / LAMR
r.emit("dndt", dndT, "1/K", 3, ["ch03.ring.sun_lock_range", "ch03.ring.bogaerts_ng"])
r.emit("dT_fwhm", fwhm * 1e9 / dldT, "K", 3, ["ch03.ring.sun_lock_range", "ch03.ring.sun_q"])
heff = L("ch03.ring.sun_heater_eff")     # nm/mW
r.emit("k_per_mw", heff / dldT, "K/mW", 3, ["ch03.ring.sun_heater_eff", "ch03.ring.sun_lock_range"])
r.emit("p_fsr", fsr * 1e9 / heff, "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_range", float(cl.cond("ch03.ring.sun_heater_eff", "tuning_range_nm")) / heff, "mW", 3, ["ch03.ring.sun_heater_eff"])
# electro-optic efficiency and energy
eo = L("ch03.ring.timurdogan_eo_shift") * 1e-12   # m/V
eo_ghz = cl.C0 * eo / LAM ** 2 / 1e9
# ASSUMPTION: the Timurdogan microdisk operates near 1550 nm
assert abs(eo_ghz - float(cl.cond("ch03.ring.timurdogan_eo_shift", "equivalent_GHz_per_V"))) / 30 < 0.06
r.emit("eo_ghz", eo_ghz, "GHz/V", 3, ["ch03.ring.timurdogan_eo_shift"])
vpp_t = float(cl.cond("ch03.ring.timurdogan_energy", "drive_Vpp"))
r.emit("eo_shift_pm", eo * vpp_t * 1e12, "pm", 3, ["ch03.ring.timurdogan_eo_shift", "ch03.ring.timurdogan_energy"])
r.emit("eo_shift_over_fwhm", eo * vpp_t / (LAM / Q), "1", 2, ["ch03.ring.timurdogan_eo_shift", "ch03.ring.sun_q"])
c_sun = float(cl.cond("ch03.ring.sun_er_il", "capacitance_fF")) * 1e-15
v_sun = float(cl.cond("ch03.ring.sun_er_il", "drive_Vpp"))
r.emit("e_sun", c_sun * v_sun ** 2 / 4 * 1e15, "fJ/bit", 3, ["ch03.ring.sun_er_il"])
r.emit("c_timurdogan", 4 * L("ch03.ring.timurdogan_energy") * 1e-15 / vpp_t ** 2 * 1e15, "fF", 3, ["ch03.ring.timurdogan_energy"])
# Reed heater benchmark: 1 mW / 10 Gb/s = 100 fJ/bit
assert abs(1e-3 / 10e9 * 1e15 - L("ch03.si.reed_ring_heater_budget")) < 1e-9

# ------------------------------------------------------------ E. WDM ring tuning budget
N = 8                 # ASSUMPTION: 8 wavelengths per bus
SPACING = fsr / N     # ASSUMPTION: channels evenly fill one FSR (grid = FSR/N)
SIG_LOCAL = 0.3e-9    # ASSUMPTION: 0.3 nm rms ring-to-ring resonance mismatch within a die
DT_AMB = L("ch03.ring.sun_lock_range")   # K, ambient swing to cover (Sun's lock range)
BR = 50e9             # ASSUMPTION: 50 Gb/s per ring
TRIALS = 20000
rng = np.random.default_rng(20261102)
r.emit("n_rings", N, "1", 2)
r.emit("spacing", SPACING * 1e9, "nm", 3, insd)
r.emit("spacing_ghz", cl.C0 * SPACING / LAMR ** 2 / 1e9, "GHz", 3, insd)
r.emit("sig_local", SIG_LOCAL * 1e9, "nm", 2)
r.emit("br", BR / 1e9, "Gb/s", 2)


def budget(sig_local, common_uniform=True, barrel=False, dT=0.0):
    """Mean and max heater power per ring (mW) over Monte-Carlo dies at ambient offset dT (K)
    above the coldest corner. Heaters only red-shift; thermal drift red-shifts by dldT*dT."""
    chans = np.arange(N) * SPACING
    common = rng.uniform(0, fsr, TRIALS) if common_uniform else np.zeros(TRIALS)
    res_ = chans[None, :] + common[:, None] + rng.normal(0, sig_local, (TRIALS, N)) + dldT * 1e-9 * dT
    if not barrel:
        need = np.mod(chans[None, :] - res_, fsr)
    else:
        best = None
        for k in range(N):
            tgt = np.roll(chans, -k)
            nk = np.mod(tgt[None, :] - res_, fsr)
            tot = nk.sum(axis=1)
            best = (nk, tot) if best is None else (np.where((tot < best[1])[:, None], nk, best[0]),
                                                  np.minimum(tot, best[1]))
        need = best[0]
    p = need * 1e9 / heff
    return p.mean(), p.sum(axis=1).max() / N, p


m_fixed, _, p_fixed = budget(SIG_LOCAL)
assert abs(m_fixed - fsr * 1e9 / 2 / heff) / (fsr * 1e9 / 2 / heff) < 0.02     # uniform -> FSR/2
m_bar, _, p_bar = budget(SIG_LOCAL, barrel=True)
m_bar0, _, _ = budget(0.0, barrel=True)
assert abs(m_bar0 - SPACING * 1e9 / 2 / heff) / (SPACING * 1e9 / 2 / heff) < 0.03  # sigma=0 -> spacing/2
m_bar_hot, _, _ = budget(SIG_LOCAL, barrel=True, dT=DT_AMB)
r.emit("p_fixed_mean", m_fixed, "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_fixed_bus", m_fixed * N, "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_fixed_p99", np.percentile(p_fixed, 99), "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_bar_mean", m_bar, "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_bar_bus", m_bar * N, "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_bar_p99", np.percentile(p_bar, 99), "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_bar0_mean", m_bar0, "mW", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("p_bar_hot_mean", m_bar_hot, "mW", 3, insd + ["ch03.ring.sun_heater_eff", "ch03.ring.sun_lock_range"])
r.emit("fj_fixed", m_fixed * 1e-3 / BR * 1e15, "fJ/bit", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("fj_bar", m_bar * 1e-3 / BR * 1e15, "fJ/bit", 3, insd + ["ch03.ring.sun_heater_eff"])
r.emit("frac_fixed_over_range", float((p_fixed > float(cl.cond("ch03.ring.sun_heater_eff", "tuning_range_nm")) / heff).mean()) * 100,
       "%", 2, insd + ["ch03.ring.sun_heater_eff"])
r.emit("frac_bar_over_range", float((p_bar > float(cl.cond("ch03.ring.sun_heater_eff", "tuning_range_nm")) / heff).mean()) * 100,
       "%", 2, insd + ["ch03.ring.sun_heater_eff"])
r.emit("tuning_ratio", m_fixed / m_bar, "1", 3, insd)

# ------------------------------------------------------------ figure
plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 3.9))
# critically coupled all-pass ring with the Q above: a = r = sqrt(ra)
aa = rr = math.sqrt(ra)
dl = np.linspace(-3 * fwhm, 3 * fwhm, 800)
for i, (shift, lab) in enumerate(((0.0, "0 V"), (eo * vpp_t, f"{vpp_t:g} V (EO shift of the disk)"))):
    phi = 2 * math.pi * NG * Lr * (dl - shift) / LAMR ** 2       # phase detuning about resonance
    T = (aa ** 2 - 2 * rr * aa * np.cos(phi) + rr ** 2) / (1 - 2 * aa * rr * np.cos(phi) + (rr * aa) ** 2)
    a1.plot(dl * 1e12, 10 * np.log10(np.maximum(T, 1e-4)), color=cl.COLORS[i], label=lab)
a1.set_xlabel("detuning from resonance (pm)")
a1.set_ylabel("through-port transmission (dB)")
a1.set_title(f"critically coupled ring, Q = {Q:.0f}", fontsize=10)
a1.legend(fontsize=8)
bins = np.linspace(0, fsr * 1e9 / heff, 60)
a2.hist(p_fixed.ravel(), bins=bins, color=cl.COLORS[0], alpha=0.6, density=True, label="fixed assignment")
a2.hist(p_bar.ravel(), bins=bins, color=cl.COLORS[1], alpha=0.6, density=True, label="barrel-shift assignment")
a2.axvline(float(cl.cond("ch03.ring.sun_heater_eff", "tuning_range_nm")) / heff, color=cl.GRAY, ls="--", lw=1)
a2.set_xlabel("heater power per ring (mW)")
a2.set_ylabel("probability density (1/mW)")
a2.set_title(f"{N} rings, Monte Carlo over dies", fontsize=10)
a2.legend(fontsize=8)
cl.savefig(fig, "ring_tuning")
r.save()
