"""Worked example 1.2: IM/DD power fading for 53 GBd PAM4 at 1310 vs 1550 nm.

Small-signal, chirp-free IM/DD transfer function |H(f)| = |cos(2 pi^2 beta2 f^2 L)|
(Zhu 2021 eqs. (3)-(4); Ouyang 2019 eq. (4)). First null where the argument
equals pi/2:  f_1 = sqrt(c / (2 lambda^2 |D| L)).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch01lib as cl

r = Results()
c = L("ch01.const.speed_of_light_c")

# Symbol rate of 400G-FR4 lanes, from the conditions of the FR4 DGD record.
RS = float(cl.cond("ch01.pmd.fr4_dgd_max", "symbol_rate_GBd")) * 1e9
r.emit("rs_gbd", RS / 1e9, "GBd", 5, ["ch01.pmd.fr4_dgd_max"])
r.emit("nyq_ghz", RS / 2e9, "GHz", 4, ["ch01.pmd.fr4_dgd_max"])
r.emit("tsym_ps", 1e12 / RS, "ps", 3, ["ch01.pmd.fr4_dgd_max"])

lam1550 = float(cl.cond("ch01.cd.g652_link_typ_d1550", "wavelength_nm")) * 1e-9
lam1310 = float(cl.cond("ch01.att.smf28ultra_max_1310", "wavelength_nm")) * 1e-9
D1550 = L("ch01.cd.g652_link_typ_d1550")
D1550_max = L("ch01.cd.g652d_d1550_range", "hi")

# Worst-case |D| at 1310 nm from the G.652 dispersion curve
# D(lam) = S0 lam/4 [1 - (lam0/lam)^4], over the lambda0 range, with S0max.
S0max = L("ch01.cd.g652d_s0_range", "hi")
l0lo = L("ch01.cd.g652d_lambda0_range", "lo")
l0hi = L("ch01.cd.g652d_lambda0_range", "hi")


def d_curve(lam_nm, lam0_nm, s0):
    return s0 * lam_nm / 4.0 * (1.0 - (lam0_nm / lam_nm) ** 4)


lam_nm = lam1310 * 1e9
D1310_neg = d_curve(lam_nm, l0hi, S0max)
D1310_pos = d_curve(lam_nm, l0lo, S0max)
D1310 = max(abs(D1310_neg), abs(D1310_pos))
ins = ["ch01.cd.g652d_s0_range", "ch01.cd.g652d_lambda0_range"]
r.emit("d1310_neg", D1310_neg, "ps/(nm·km)", 3, ins)
r.emit("d1310_pos", D1310_pos, "ps/(nm·km)", 3, ins)
r.emit("d1310_worst", D1310, "ps/(nm·km)", 3, ins)

# FR4 lane-edge check against the ITU statistical boundary at 1264.5 nm
lam_edge = float(cl.cond("ch01.cd.g652_oband_link_dmin_m1", "wavelength_nm"))
r.emit("d1264_curve", d_curve(lam_edge, l0hi, S0max), "ps/(nm·km)", 3, ins)

# beta2 from D, and check against the SSMF beta2 recorded with Essiambre's parameters
b2_1550 = cl.beta2_from_d(D1550, lam1550, c)
b2_1310 = cl.beta2_from_d(D1310, lam1310, c)
r.emit("beta2_1550", cl.beta2_ps2_per_km(b2_1550), "ps²/km", 3,
       ["ch01.cd.g652_link_typ_d1550", "ch01.const.speed_of_light_c"])
r.emit("beta2_1310_abs", abs(cl.beta2_ps2_per_km(b2_1310)), "ps²/km", 3, ins)
b2_ref = float(cl.cond("ch01.kerr.gamma_ssmf_essiambre_params", "beta2_ps2_per_km"))
assert abs(cl.beta2_ps2_per_km(b2_1550) / b2_ref - 1) < 0.01, "beta2 from D=17 should match -21.7 ps^2/km"

# Dispersion length with T0 = symbol period (ASSUMPTION: T0 := 1/Rs as the time scale)
T0 = 1.0 / RS
r.emit("ld_1550_km", T0 ** 2 / abs(b2_1550) / 1e3, "km", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("ld_1310_km", T0 ** 2 / abs(b2_1310) / 1e3, "km", 3, ins)


def f_null(D_ps, lam, Lm):
    return math.sqrt(c / (2 * lam ** 2 * cl.d_si(abs(D_ps)) * Lm))


def reach_for_null_at(D_ps, lam, f):
    return c / (2 * lam ** 2 * cl.d_si(abs(D_ps)) * f ** 2)


# ASSUMPTION: illustrative lengths 2 km (FR4) and 10 km (LR-class).
for Lkm in (2, 10):
    r.emit(f"fnull_1550_{Lkm}km", f_null(D1550, lam1550, Lkm * 1e3) / 1e9, "GHz", 3,
           ["ch01.cd.g652_link_typ_d1550"])
    r.emit(f"fnull_1310_{Lkm}km", f_null(D1310, lam1310, Lkm * 1e3) / 1e9, "GHz", 3, ins)

# Reach criteria at the Nyquist frequency Rs/2:
#  (i) null exactly at Rs/2;  (ii) |H| = 1/sqrt(2) (3 dB electrical) at Rs/2, which
#  is the argument pi/4, i.e. half the length of (i). Criterion (ii) is an ASSUMPTION.
fn = RS / 2
for tag, D, lam, inp in (("1550", D1550, lam1550, ["ch01.cd.g652_link_typ_d1550"]),
                         ("1550max", D1550_max, lam1550, ["ch01.cd.g652d_d1550_range"]),
                         ("1310", D1310, lam1310, ins)):
    Ln = reach_for_null_at(D, lam, fn)
    r.emit(f"reach_null_{tag}", Ln / 1e3, "km", 3, inp + ["ch01.pmd.fr4_dgd_max"])
    r.emit(f"reach_3db_{tag}", Ln / 2e3, "km", 3, inp + ["ch01.pmd.fr4_dgd_max"])

# Accumulated-dispersion limits of the MSA channels
cd_fr4 = L("ch01.cd.fr4_channel_cd_min")
cd_lr4 = L("ch01.cd.lr4_10_channel_cd", "lo")
lam_e = lam_edge * 1e-9
fn_fr4 = math.sqrt(c / (2 * lam_e ** 2 * abs(cd_fr4) * 1e-12 / 1e-9))
fn_lr4 = math.sqrt(c / (2 * lam_e ** 2 * abs(cd_lr4) * 1e-12 / 1e-9))
r.emit("fnull_fr4_chan", fn_fr4 / 1e9, "GHz", 3, ["ch01.cd.fr4_channel_cd_min"])
r.emit("fnull_lr4_chan", fn_lr4 / 1e9, "GHz", 3, ["ch01.cd.lr4_10_channel_cd"])
assert fn_fr4 > fn and fn_lr4 > fn, "MSA CD limits must keep the first null above Nyquist"
# Equivalent 1550 nm length with the same accumulated dispersion as the FR4 limit
r.emit("l1550_equiv_fr4", abs(cd_fr4) / D1550, "km", 3,
       ["ch01.cd.fr4_channel_cd_min", "ch01.cd.g652_link_typ_d1550"])

# ---------------------------------------------------------------- figure
plt = cl.setup_mpl()
f = np.linspace(0.01e9, 60e9, 1200)
fig, ax = plt.subplots(figsize=(7.2, 4.2))


def hdb(D, lam, Lm):
    b2 = cl.beta2_from_d(D, lam, c)
    h = np.abs(np.cos(2 * math.pi ** 2 * b2 * f ** 2 * Lm))
    return 20 * np.log10(np.maximum(h, 1e-3))


ax.plot(f / 1e9, hdb(D1550, lam1550, 2e3), color=cl.COLORS[1], lw=2, label="1550 nm, 2 km")
ax.plot(f / 1e9, hdb(D1550, lam1550, 10e3), color=cl.COLORS[4], lw=2, label="1550 nm, 10 km")
ax.plot(f / 1e9, hdb(D1310, lam1310, 10e3), color=cl.COLORS[0], lw=2.2,
        label="1310 nm, 10 km (worst-case G.652.D |D|)")
ax.axvline(fn / 1e9, color=cl.GRAY, ls="--", lw=1)
ax.text(fn / 1e9 + 0.6, -27, r"$R_s/2$", fontsize=10)
ax.set_xlabel("Baseband frequency f (GHz)")
ax.set_ylabel(r"$20\log_{10}|H(f)|$ (dB)")
ax.set_ylim(-30, 2)
ax.set_xlim(0, 60)
ax.legend(fontsize=9, loc="lower left")
cl.savefig(fig, "power_fading")

r.save()
