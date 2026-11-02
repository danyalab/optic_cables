"""Worked example 3.1: band gaps, Henry linewidth, and the damping-limited
modulation bandwidth of a single-mode semiconductor laser.

Small-signal model (Michalzik & Ebeling 2003, Eqs. (48), (53), (55); book notation
f for modulation frequency, gamma_d for the damping rate):

  H(f) = f_r^2 / (f_r^2 - f^2 + i f gamma_d / (2 pi)),   gamma_d = K f_r^2 + gamma_0

The script (1) evaluates Varshni band gaps of GaAs and InP, (2) reproduces Henry's
factor of 30 from alpha_H = 5.4, (3) checks numerically that the maximum 3-dB
bandwidth over f_r equals 2 sqrt(2) pi / K and that the undamped ratio
f_3dB / f_r = sqrt(1 + sqrt(2)), and (4) plots response and RIN shapes.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
from scipy.optimize import brentq, minimize_scalar
import ch03lib as cl

r = Results()

# ------------------------------------------------------------ 1. band gaps
def varshni(eg0, a_mev, b_k, t):
    return eg0 - a_mev * 1e-3 * t ** 2 / (t + b_k)

T = 300.0  # ASSUMPTION: room temperature taken as 300 K
eg_gaas = varshni(L("ch03.mat.gaas_eg_0k"), L("ch03.mat.gaas_varshni_alpha"),
                  float(cl.cond("ch03.mat.gaas_varshni_alpha", "varshni_beta_K")), T)
eg_inp = varshni(L("ch03.mat.inp_eg_0k"), L("ch03.mat.inp_varshni_alpha"),
                 float(cl.cond("ch03.mat.inp_varshni_alpha", "varshni_beta_K")), T)
ins_g = ["ch03.mat.gaas_eg_0k", "ch03.mat.gaas_varshni_alpha"]
ins_i = ["ch03.mat.inp_eg_0k", "ch03.mat.inp_varshni_alpha"]
assert L("ch03.mat.gaas_eg_300k_range", "lo") <= eg_gaas <= L("ch03.mat.gaas_eg_300k_range", "hi")
r.emit("t_room", T, "K", 3)
r.emit("eg_gaas_300", eg_gaas, "eV", 4, ins_g)
r.emit("eg_inp_300", eg_inp, "eV", 4, ins_i)
r.emit("lam_gaas_300", cl.ev_to_nm(eg_gaas), "nm", 3, ins_g)
r.emit("lam_inp_300", cl.ev_to_nm(eg_inp), "nm", 3, ins_i)
r.emit("shift_gaas", (L("ch03.mat.gaas_eg_0k") - eg_gaas) * 1e3, "meV", 3, ins_g)
r.emit("shift_inp", (L("ch03.mat.inp_eg_0k") - eg_inp) * 1e3, "meV", 3, ins_i)
# local temperature coefficient dEg/dT at 300 K
def deg_dt(a_mev, b_k, t):
    return -a_mev * 1e-3 * (t ** 2 + 2 * t * b_k) / (t + b_k) ** 2
r.emit("degdt_gaas", -deg_dt(L("ch03.mat.gaas_varshni_alpha"), 204, T) * 1e3, "meV/K", 3, ins_g)
r.emit("degdt_inp", -deg_dt(L("ch03.mat.inp_varshni_alpha"), 162, T) * 1e3, "meV/K", 3, ins_i)
assert float(cl.cond("ch03.mat.inp_varshni_alpha", "varshni_beta_K")) == 162

# ------------------------------------------------------------ 2. Henry linewidth
aH = L("ch03.las.henry_alpha_fit")
fac = 1 + aH ** 2
assert abs(fac - L("ch03.las.henry_excess_ratio")) / L("ch03.las.henry_excess_ratio") < 0.02
r.emit("henry_factor", fac, "1", 3, ["ch03.las.henry_alpha_fit"])
lo, hi = L("ch03.las.henry_alpha_measured", "lo"), L("ch03.las.henry_alpha_measured", "hi")
r.emit("henry_factor_lo", 1 + lo ** 2, "1", 3, ["ch03.las.henry_alpha_measured"])
r.emit("henry_factor_hi", 1 + hi ** 2, "1", 3, ["ch03.las.henry_alpha_measured"])
dnu_meas = L("ch03.las.henry_linewidth_1mw")
r.emit("dnu_st_1mw", dnu_meas / fac, "MHz", 3, ["ch03.las.henry_linewidth_1mw", "ch03.las.henry_alpha_fit"])
vlo, vhi = abs(L("ch03.las.vcsel_alpha_range", "hi")), abs(L("ch03.las.vcsel_alpha_range", "lo"))
r.emit("vcsel_factor_lo", 1 + vlo ** 2, "1", 3, ["ch03.las.vcsel_alpha_range"])
r.emit("vcsel_factor_hi", 1 + vhi ** 2, "1", 3, ["ch03.las.vcsel_alpha_range"])
# Linewidth scales as 1/P: power at which the 1 mW laser would reach the ITLA 5 MHz spec
p_needed = dnu_meas / L("ch03.itla.oif_linewidth_app1")   # mW, from Delta nu ∝ 1/P
r.emit("p_for_5mhz", p_needed, "mW", 3, ["ch03.las.henry_linewidth_1mw", "ch03.itla.oif_linewidth_app1"])

# ------------------------------------------------------------ 3. modulation response
def h2(f, fr, gam):
    """|H(f)|^2, f and fr in Hz, gam in 1/s."""
    return fr ** 4 / ((fr ** 2 - f ** 2) ** 2 + (f * gam / (2 * math.pi)) ** 2)


def f3db(fr, gam):
    g = lambda f: h2(f, fr, gam) - 0.5          # half-power point
    return brentq(g, fr * 0.2 if g(fr * 0.2) > 0 else 1.0, fr * 5, xtol=1.0)


# undamped limit: f3dB / fr -> sqrt(1 + sqrt 2)
ratio_undamped = f3db(10e9, 1.0) / 10e9
assert abs(ratio_undamped - math.sqrt(1 + math.sqrt(2))) < 1e-4
r.emit("ratio_undamped", ratio_undamped, "1", 3)

for tag, pick in (("lo", "lo"), ("hi", "hi")):
    K = L("ch03.las.vcsel_min_kfactor", pick) * 1e-9
    res = minimize_scalar(lambda fr: -f3db(fr, K * fr ** 2), bounds=(1e9, 200e9), method="bounded",
                          options={"xatol": 1e3})
    fmax_num = -res.fun
    fmax_th = 2 * math.sqrt(2) * math.pi / K
    assert abs(fmax_num - fmax_th) / fmax_th < 1e-3, (fmax_num, fmax_th)
    r.emit(f"fmax_{tag}", fmax_th / 1e9, "GHz", 3, ["ch03.las.vcsel_min_kfactor"])
    r.emit(f"fr_at_fmax_{tag}", res.x / 1e9, "GHz", 3, ["ch03.las.vcsel_min_kfactor"])

# Analytic optimum (derived in the text): f_r* = 2 sqrt2 pi / K, at which f_3dB = f_r*.
Kref = L("ch03.las.vcsel_min_kfactor", "hi") * 1e-9
fr_opt = 2 * math.sqrt(2) * math.pi / Kref
assert abs(f3db(fr_opt, Kref * fr_opt ** 2) - 2 * math.sqrt(2) * math.pi / Kref) / (2 * math.sqrt(2) * math.pi / Kref) < 1e-6
r.emit("fr_opt_hi", fr_opt / 1e9, "GHz", 3, ["ch03.las.vcsel_min_kfactor"])
# At the optimum gamma_d = K f_r^2 = 2 sqrt2 pi f_r, so |H(f_r)|^2 = (2 pi f_r/gamma_d)^2 = 1/2:
# the response has no peak and is already 3 dB down at f_r.
assert abs(h2(fr_opt, fr_opt, Kref * fr_opt ** 2) - 0.5) < 1e-12
r.emit("k_ref", Kref * 1e9, "ns", 2, ["ch03.las.vcsel_min_kfactor"])

# VCSEL D-factor and MCEF
D = L("ch03.vcsel.chalmers_dfactor")
mcef = L("ch03.vcsel.chalmers_mcef")
r.emit("mcef_over_d", mcef / D, "1", 3, ["ch03.vcsel.chalmers_dfactor", "ch03.vcsel.chalmers_mcef"])
r.emit("mcef_theory", math.sqrt(1 + math.sqrt(2)) * D, "GHz/sqrt(mA)", 3, ["ch03.vcsel.chalmers_dfactor"])
# f_r at the 1.8 mA bias point, threshold taken from the -40..80 C range of a similar oxide VCSEL
# ASSUMPTION: the Chalmers device threshold lies in the ledger range of ch03.las.vcsel_ith_temp.
ib = float(cl.cond("ch03.vcsel.chalmers_bw_low_bias", "bias_mA"))
fr_lo = D * math.sqrt(ib - L("ch03.las.vcsel_ith_temp", "hi"))
fr_hi = D * math.sqrt(ib - L("ch03.las.vcsel_ith_temp", "lo"))
insv = ["ch03.vcsel.chalmers_dfactor", "ch03.las.vcsel_ith_temp", "ch03.vcsel.chalmers_bw_low_bias"]
r.emit("fr18_lo", fr_lo, "GHz", 3, insv)
r.emit("fr18_hi", fr_hi, "GHz", 3, insv)
r.emit("f3_undamped18_hi", fr_hi * math.sqrt(1 + math.sqrt(2)), "GHz", 3, insv)
assert fr_lo * math.sqrt(1 + math.sqrt(2)) > L("ch03.vcsel.chalmers_bw_low_bias")

# NTT membrane DML: intrinsic bandwidth vs f_r
r.emit("ntt_ratio", L("ch03.dml.ntt_membrane_intrinsic") / L("ch03.dml.ntt_membrane_fr"), "1", 3,
       ["ch03.dml.ntt_membrane_intrinsic", "ch03.dml.ntt_membrane_fr"])

# ------------------------------------------------------------ 4. RIN
I_pd = float(cl.cond("ch03.las.rin_shot_limit_1ma", "photocurrent_mA")) * 1e-3
rin_q = 10 * math.log10(2 * cl.Q_E / I_pd)
r.emit("rin_shot_1ma", rin_q, "dB/Hz", 4, ["ch03.las.rin_shot_limit_1ma"])
r.emit("rin_shot_10ma", 10 * math.log10(2 * cl.Q_E / (10 * I_pd)), "dB/Hz", 4, ["ch03.las.rin_shot_limit_1ma"])

# RIN spectral shape, Michalzik Eq. (61): (4 pi^2 f^2 + g*^2)/(16 pi^4 (fr^2-f^2)^2 + 4 pi^2 g^2 f^2)
# ASSUMPTION: gamma* = gamma_0 (numerator corner set by the damping offset).
# ASSUMPTION: damping offset gamma_0 = 1e10 1/s (typical order; not sourced).
GAMMA0 = 1e10


def rin_shape(f, fr, gam, gstar):
    return (4 * math.pi ** 2 * f ** 2 + gstar ** 2) / (16 * math.pi ** 4 * (fr ** 2 - f ** 2) ** 2
                                                       + 4 * math.pi ** 2 * gam ** 2 * f ** 2)


r.emit("gamma0", GAMMA0 / 1e9, "1/ns", 2)
for fr_ghz in (10, 20):
    fr = fr_ghz * 1e9
    gam = Kref * fr ** 2 + GAMMA0
    peak = rin_shape(fr, fr, gam, GAMMA0) / rin_shape(1e6, fr, gam, GAMMA0)
    r.emit(f"rin_peak_{fr_ghz}", 10 * math.log10(peak), "dB", 3, ["ch03.las.vcsel_min_kfactor"])
    r.emit(f"gamma_{fr_ghz}", gam / 1e9, "1/ns", 3, ["ch03.las.vcsel_min_kfactor"])
# Peak-to-low-frequency ratio: -> 16 pi^4 f_r^4 / (gamma_d^2 gamma*^2), which tends to the
# f_r-independent asymptote 16 pi^4 / (K^2 gamma*^2) once K f_r^2 >> gamma_0.
asym = 10 * math.log10(16 * math.pi ** 4 / (Kref ** 2 * GAMMA0 ** 2))
r.emit("rin_peak_asym", asym, "dB", 3, ["ch03.las.vcsel_min_kfactor"])
fr = 60e9
pk = rin_shape(fr, fr, Kref * fr ** 2 + GAMMA0, GAMMA0) / rin_shape(1e6, fr, Kref * fr ** 2 + GAMMA0, GAMMA0)
assert abs(10 * math.log10(pk) - asym) < 0.5

# ------------------------------------------------------------ figure
plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.8))
f = np.linspace(0.05e9, 80e9, 1200)
for i, fr_ghz in enumerate((10, 20, 30, 45)):
    fr = fr_ghz * 1e9
    gam = Kref * fr ** 2 + GAMMA0
    a1.plot(f / 1e9, [10 * math.log10(h2(x, fr, gam)) for x in f], color=cl.COLORS[i], label=f"$f_r$ = {fr_ghz} GHz")
    a2.plot(f / 1e9, [10 * math.log10(rin_shape(x, fr, gam, GAMMA0) / rin_shape(1e6, fr, gam, GAMMA0)) for x in f],
            color=cl.COLORS[i])
a1.axhline(-3, color=cl.GRAY, lw=0.8, ls="--")
a1.set_xlabel("modulation frequency $f$ (GHz)")
a1.set_ylabel("$|H(f)|^2$ (dB)")
a1.set_ylim(-15, 12)
a1.legend(fontsize=9)
a1.set_title(f"intrinsic response, K = {Kref*1e9:.1f} ns", fontsize=10)
a2.set_xlabel("frequency $f$ (GHz)")
a2.set_ylabel("RIN relative to low frequency (dB)")
a2.set_ylim(-30, 25)
a2.set_title("intrinsic RIN shape (Eq. 61 form)", fontsize=10)
cl.savefig(fig, "laser_response")
r.save()
