"""Worked example 1.3: PMD outage probability for an IM/DD receiver.

Maxwellian DGD pdf (mean <dtau>):
  p(x) = 32 x^2 / (pi^2 m^3) exp(-4 x^2 / (pi m^2))
Survival function with a = m sqrt(pi/8) (Maxwell scale):
  P(X > x) = erfc(x / (a sqrt 2)) + sqrt(2/pi) (x/a) exp(-x^2 / (2 a^2))
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
from scipy.special import erfc
from scipy.integrate import quad
from scipy.optimize import brentq
import ch01lib as cl

r = Results()


def pdf(x, m):
    return 32 * x ** 2 / (math.pi ** 2 * m ** 3) * np.exp(-4 * x ** 2 / (math.pi * m ** 2))


def outage(x, m):
    a = m * math.sqrt(math.pi / 8)
    u = x / a
    return erfc(u / math.sqrt(2)) + math.sqrt(2 / math.pi) * u * math.exp(-u * u / 2)


# Self-consistency: pdf normalized, mean = m, RMS = sqrt(3 pi/8) m (G.650.2 eq. 3-3)
m = 1.0
assert abs(quad(pdf, 0, 20, args=(m,))[0] - 1) < 1e-9
assert abs(quad(lambda x: x * pdf(x, m), 0, 20)[0] - m) < 1e-9
rms = math.sqrt(quad(lambda x: x * x * pdf(x, m), 0, 20)[0])
assert abs(rms - math.sqrt(3 * math.pi / 8)) < 1e-9
r.emit("rms_over_mean", rms, "1", 4, ["ch01.pmd.dgd_maxwellian_g650_2"])

# Reproduce G.959.1 Table 8-3 tail probabilities
p30 = outage(3.0, 1.0)
p35 = outage(3.5, 1.0)
r.emit("p_ratio3", p30, "1", 2, ["ch01.pmd.g959_ratio_3p0_prob"])
r.emit("p_ratio35", p35, "1", 2, ["ch01.pmd.g959_ratio_3p5_prob"])
assert abs(p30 / L("ch01.pmd.g959_ratio_3p0_prob") - 1) < 0.03
assert abs(p35 / L("ch01.pmd.g959_ratio_3p5_prob") - 1) < 0.03

# ---------------- the example
RS = float(cl.cond("ch01.pmd.fr4_dgd_max", "symbol_rate_GBd")) * 1e9
T = 1e12 / RS                                    # ps
tol_msa = L("ch01.pmd.fr4_dgd_max")              # ps (MSA requirement)
# ASSUMPTION: apply the G.959.1 0.3-bit-period rule to the PAM4 symbol period.
tol_rule = L("ch01.pmd.g959_dgd_03_bit") * T
r.emit("tol_rule_ps", tol_rule, "ps", 3, ["ch01.pmd.g959_dgd_03_bit", "ch01.pmd.fr4_dgd_max"])

pmd_spec = L("ch01.pmd.g652d_pmdq")              # ps/sqrt(km)
pmd_ds = L("ch01.pmd.smf28ultra_ldv")
# ASSUMPTION: link lengths 2 km (FR4), 10 km (LR-class) and 40 km (ER-class).
for Lkm in (2, 10, 40):
    for tag, pmd, rid in (("spec", pmd_spec, "ch01.pmd.g652d_pmdq"), ("ds", pmd_ds, "ch01.pmd.smf28ultra_ldv")):
        mean = pmd * math.sqrt(Lkm)
        r.emit(f"mean_{tag}_{Lkm}", mean, "ps", 3, [rid])
        r.emit(f"pout_{tag}_{Lkm}", outage(tol_msa, mean), "1", 2, [rid, "ch01.pmd.fr4_dgd_max"])
        r.emit(f"pout_rule_{tag}_{Lkm}", outage(tol_rule, mean), "1", 2, [rid, "ch01.pmd.g959_dgd_03_bit"])

# Maximum length so that the outage is 4.2e-5 (tolerance = 3 x mean DGD)
for tag, pmd, rid in (("spec", pmd_spec, "ch01.pmd.g652d_pmdq"), ("ds", pmd_ds, "ch01.pmd.smf28ultra_ldv")):
    Lmax = (tol_msa / 3.0 / pmd) ** 2
    r.emit(f"lmax3_{tag}", Lmax, "km", 3, [rid, "ch01.pmd.fr4_dgd_max"])
# Ratio x/<dtau> for outage 1e-6 (ASSUMPTION: outage target 1e-6)
P_TARGET = 1e-6
ratio_1e6 = brentq(lambda x: outage(x, 1.0) - P_TARGET, 2.0, 6.0)
r.emit("ratio_1e6", ratio_1e6, "1", 3)
r.emit("lmax_1e6_spec", (tol_msa / ratio_1e6 / pmd_spec) ** 2, "km", 3, ["ch01.pmd.g652d_pmdq", "ch01.pmd.fr4_dgd_max"])
r.emit("lmax_1e6_ds", (tol_msa / ratio_1e6 / pmd_ds) ** 2, "km", 3, ["ch01.pmd.smf28ultra_ldv", "ch01.pmd.fr4_dgd_max"])

# coherent comparison: mean DGD over 1000 km with G.652.D PMDQ (ASSUMPTION: 1000 km)
r.emit("mean_spec_1000", pmd_spec * math.sqrt(1000), "ps", 3, ["ch01.pmd.g652d_pmdq"])

r.emit("gk_len", cl.cond("ch01.pmd.dgd_sqrt_length", "length_km"), "km", 3, ["ch01.pmd.dgd_sqrt_length"])

# ---------------- figure
plt = cl.setup_mpl()
x = np.linspace(0, 4.0, 600)
fig, ax = plt.subplots(figsize=(7.2, 4.2))
for i, Lkm in enumerate((2, 10, 40)):
    mean = pmd_spec * math.sqrt(Lkm)
    ax.plot(x, pdf(x, mean), color=cl.COLORS[i], lw=2,
            label=fr"$L$ = {Lkm} km, $\langle\Delta\tau\rangle$ = {mean:.2f} ps")
ax.axvline(tol_msa, color=cl.GRAY, ls="--", lw=1)
ax.text(tol_msa + 0.05, ax.get_ylim()[1] * 0.85, "MSA DGD\ntolerance", fontsize=9)
ax.set_xlabel(r"Differential group delay $\Delta\tau$ (ps)")
ax.set_ylabel(r"$p(\Delta\tau)$ (1/ps)")
ax.set_xlim(0, 4.0)
ax.set_ylim(bottom=0)
ax.legend(fontsize=9, title="Maxwellian, PMD coeff. = G.652.D PMDQ", title_fontsize=9)
cl.savefig(fig, "maxwellian_dgd")

r.save()
