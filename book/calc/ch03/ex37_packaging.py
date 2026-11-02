"""Worked example 3.7: fiber coupling and reliability statistics.

Gaussian-mode coupling (Michalzik Eq. (70) and its lateral-offset extension):
  eta = 4 w1^2 w2^2 / (w1^2 + w2^2)^2 * exp(-2 d^2 / (w1^2 + w2^2)).
Zero-failure upper bound on a constant failure rate at confidence CL:
  lambda_UB = -ln(1 - CL) / T_device,   1 FIT = 1 failure per 1e9 device-hours.
Acceleration (VI Systems Eq. (2)): AF = (J_s/J_u)^N exp[(Ea/kB)(1/T_u - 1/T_s)].
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import re
import numpy as np
import ch03lib as cl

r = Results()


def eta_mm(w1, w2, d=0.0):
    return 4 * w1 ** 2 * w2 ** 2 / (w1 ** 2 + w2 ** 2) ** 2 * math.exp(-2 * d ** 2 / (w1 ** 2 + w2 ** 2))


# ------------------------------------------------------------ edge coupler mode mismatch
mfd_s = float(cl.cond("ch03.cpl.ec_sion", "fiber_mfd_um"))
ec9 = float(cl.cond("ch03.cpl.ec_sion", "with_9um_MFD_dB"))
mm = -cl.lin2db(eta_mm(mfd_s / 2, 9.0 / 2))      # 9 um fiber MFD from the record's key name
assert "9um" in "with_9um_MFD_dB"
pred = abs(L("ch03.cpl.ec_sion")) + mm
assert abs(pred - abs(ec9)) < 0.4
inse = ["ch03.cpl.ec_sion"]
r.emit("ec_mismatch", mm, "dB", 3, inse)
r.emit("ec_pred_9um", pred, "dB", 3, inse)
r.emit("ec_meas_9um", abs(ec9), "dB", 2, inse)

# lateral tolerance of a large SSC matched to 10 um MFD (ASSUMPTION: 10 um MFD on both sides)
w = 10.0 / 2
d1 = L("ch03.cpl.large_ssc_tol")
loss_d1 = -cl.lin2db(eta_mm(w, w, d1))
assert abs(loss_d1 - 1.0) < 0.15
r.emit("ssc_loss_at_tol", loss_d1, "dB", 3, ["ch03.cpl.large_ssc_tol"])
r.emit("ssc_tol_exact", w * math.sqrt(math.log(cl.db2lin(1.0))), "µm", 3, ["ch03.cpl.large_ssc_tol"])
# inverse taper with lens: 3 dB at 1 um -> effective equal-mode radius
d3 = L("ch03.cpl.ec_misalign")
w3 = d3 / math.sqrt(math.log(2.0))
r.emit("taper_w", w3, "µm", 3, ["ch03.cpl.ec_misalign"])
r.emit("taper_mfd", 2 * w3, "µm", 3, ["ch03.cpl.ec_misalign"])
r.emit("tol_ratio", d1 / d3, "1", 3, ["ch03.cpl.large_ssc_tol", "ch03.cpl.ec_misalign"])

# grating couplers
gc = cl.db2lin(L("ch03.cpl.gc_record"))
assert abs(100 * gc - float(cl.cond("ch03.cpl.gc_record", "efficiency_percent"))) < 0.5
r.emit("gc_rec_pct", 100 * gc, "%", 3, ["ch03.cpl.gc_record"])
r.emit("gc_de_pct", 100 * cl.db2lin(L("ch03.cpl.gc_double_etch")), "%", 3, ["ch03.cpl.gc_double_etch"])

# ------------------------------------------------------------ reliability statistics
CL60 = float(cl.cond("ch03.rel.vcsel_fit_lab", "confidence_percent")) / 100
T = float(cl.cond("ch03.rel.vcsel_fit_lab", "device_hours"))
lam_ub = -math.log(1 - CL60) / T * 1e9
assert abs(lam_ub - L("ch03.rel.vcsel_fit_lab")) / L("ch03.rel.vcsel_fit_lab") < 0.02
insr = ["ch03.rel.vcsel_fit_lab"]
r.emit("chi60", -math.log(1 - CL60), "1", 3, insr)
r.emit("fit_ub_calc", lam_ub, "FIT", 3, insr)
r.emit("hours_1fit", -math.log(1 - CL60) / 1e-9, "device-hours", 3, insr)
r.emit("hours_10fit", -math.log(1 - CL60) / 10e-9, "device-hours", 3, insr)
r.emit("hours_ratio", (-math.log(1 - CL60) / 1e-9) / T, "1", 3, insr)
r.emit("chi90", -math.log(0.1), "1", 3)

# Hoser (TRUMPF): Ea 0.35 eV, 105 C vs 40 C
Ea = float(cl.cond("ch03.rel.vcsel_fit_105c", "Ea_eV"))
assert Ea == L("ch03.rel.gr468_default_ea")
T105, T40 = 105 + 273.15, 40 + 273.15
af = math.exp(Ea * cl.Q_E / cl.K_B * (1 / T40 - 1 / T105))
r.emit("af_105_40", af, "1", 3, ["ch03.rel.vcsel_fit_105c"])
r.emit("fit40_from_105", L("ch03.rel.vcsel_fit_105c") / af, "FIT", 2, ["ch03.rel.vcsel_fit_105c"])
assert L("ch03.rel.vcsel_fit_105c") / af < 1.0      # consistent with '< 1 FIT at 40 C'
dh = float(str(cl.cond("ch03.rel.vcsel_fit_105c", "device_hours")).replace("about", "").strip())
chi_impl = L("ch03.rel.vcsel_fit_105c") * 1e-9 * dh
r.emit("hoser_chi", chi_impl, "1", 3, ["ch03.rel.vcsel_fit_105c"])
r.emit("hoser_cl", 100 * (1 - math.exp(-chi_impl)), "%", 2, ["ch03.rel.vcsel_fit_105c"])
r.emit("field_vs_lab", L("ch03.rel.vcsel_fit_lab") / L("ch03.rel.vcsel_fit_field"), "1", 3,
       ["ch03.rel.vcsel_fit_lab", "ch03.rel.vcsel_fit_field"])

# Wear-out vs random acceleration models.
# ASSUMPTION: use condition 45 C / 5 mA (the VI Systems reference), stress 95 C at 1.5x current.
T_use = 45 + 273.15
T_st = 95 + 273.15
J_RATIO = 1.5
r.emit("t_stress", T_st - 273.15, "°C", 3)
r.emit("j_ratio", J_RATIO, "1", 2)


def AF(Ea_, N_):
    return J_RATIO ** N_ * math.exp(Ea_ * cl.Q_E / cl.K_B * (1 / T_use - 1 / T_st))


Ew, Nw = L("ch03.rel.vcsel_wearout_ea"), float(cl.cond("ch03.rel.vcsel_wearout_ea", "current_exponent_N"))
Er, Nr = L("ch03.rel.gr468_default_ea"), float(cl.cond("ch03.rel.gr468_default_ea", "current_exponent_N"))
m = re.search(r"Ea about ([0-9.]+) eV, N = (\d+)", cl.cond("ch03.rel.vcsel_wearout_ea", "literature_low_J"))
El, Nl = float(m.group(1)), float(m.group(2))
r.emit("af_wear", AF(Ew, Nw), "1", 3, ["ch03.rel.vcsel_wearout_ea"])
r.emit("af_lit", AF(El, Nl), "1", 3, ["ch03.rel.vcsel_wearout_ea"])
r.emit("af_rand", AF(Er, Nr), "1", 3, ["ch03.rel.gr468_default_ea"])
aging_h = L("ch03.rel.accel_aging")
r.emit("aging_equiv_wear_y", aging_h * AF(Ew, Nw) / 8766, "years", 3, ["ch03.rel.accel_aging", "ch03.rel.vcsel_wearout_ea"])
r.emit("aging_equiv_rand_y", aging_h * AF(Er, Nr) / 8766, "years", 3, ["ch03.rel.accel_aging", "ch03.rel.gr468_default_ea"])
r.emit("aging_equiv_lit_y", aging_h * AF(El, Nl) / 8766, "years", 3, ["ch03.rel.accel_aging", "ch03.rel.vcsel_wearout_ea"])

# ------------------------------------------------------------ figure: coupling vs offset
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.2, 3.8))
dd = np.linspace(0, 5, 200)
for i, (wl, lab) in enumerate(((w3, f"inverse taper + lens (MFD {2*w3:.1f} µm, inferred)"),
                               (mfd_s / 2, f"SiON SSC to {mfd_s:g} µm MFD fiber"),
                               (w, "large SSC to 10 µm MFD fiber"))):
    ax.plot(dd, [-cl.lin2db(eta_mm(wl, wl, x)) for x in dd], color=cl.COLORS[i], label=lab)
ax.plot([d3], [3.0], "o", color=cl.COLORS[0])
ax.plot([d1], [loss_d1], "o", color=cl.COLORS[2])
ax.set_ylim(0, 6)
ax.set_xlabel("lateral offset $d$ (µm)")
ax.set_ylabel("excess coupling loss (dB)")
ax.set_title("Gaussian-mode offset loss (computed); dots: reported tolerances", fontsize=10)
ax.legend(fontsize=8)
cl.savefig(fig, "coupling_offset")
r.save()
