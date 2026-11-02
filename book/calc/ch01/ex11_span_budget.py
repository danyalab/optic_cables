"""Worked example 1.1: loss-spectrum model checks and the 80 km span budget.

Part A checks the Rayleigh model alpha_R = A_R / lambda^4 against ledger
datasheet and record values, and draws the loss-spectrum model figure.
Part B is the span budget  A_span = alpha L + a_s x + a_c y + M  (ITU-T G.652
App. I eq. (I-1), plus a margin), for several fibre choices.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch01lib as cl

r = Results()

# ---------------------------------------------------------------- assumptions
# ASSUMPTION: span length. The syllabus fixes an 80 km span; it is a design
# choice, not a sourced fact.
SPAN_KM = 80.0
# ASSUMPTION: cable section (reel) length between fusion splices.
SECTION_KM = 4.0
# ASSUMPTION: mean fusion-splice loss per splice (no ledger record; see needs file).
SPLICE_DB = 0.05
# ASSUMPTION: two line connectors per span (patch panels at both amplifier huts).
N_CONN = 2
CONN_DB = 0.5
# ASSUMPTION: end-of-life margin for ageing and cable repairs.
MARGIN_DB = 3.0
# ASSUMPTION: shape of the infrared multiphonon tail, alpha_IR ∝ exp(-b/lambda),
# with b = 48.48 µm (a commonly used empirical slope; not in the ledger). Only
# its magnitude at 1550 nm is a ledger value (ch01.phys.ir_absorption_1550).
IR_B_UM = 48.48

# ---------------------------------------------------------------- Part A
A_ge = L("ch01.phys.rayleigh_coeff_gedoped")          # dB/(km µm^4)
A_psc = L("ch01.phys.rayleigh_coeff_psc_record")
A_fib_lo = L("ch01.phys.rayleigh_coeff_fiber", "lo")
A_fib_hi = L("ch01.phys.rayleigh_coeff_fiber", "hi")
A_bulk = L("ch01.phys.rayleigh_coeff_bulk_silica")
ir1550 = L("ch01.phys.ir_absorption_1550")


def rayleigh(A, lam_um):
    return A / lam_um ** 4


def ir_tail(lam_um):
    return ir1550 * np.exp(IR_B_UM * (1 / 1.55 - 1 / np.asarray(lam_um)))


in_a = ["ch01.phys.rayleigh_coeff_gedoped", "ch01.phys.ir_absorption_1550"]
tot_ge_1550 = rayleigh(A_ge, 1.55) + ir1550
tot_psc_1550 = rayleigh(A_psc, 1.55) + ir1550
r.emit("ray_ge_1550", rayleigh(A_ge, 1.55), "dB/km", 3, ["ch01.phys.rayleigh_coeff_gedoped"])
r.emit("tot_ge_1550", tot_ge_1550, "dB/km", 3, in_a)
r.emit("ray_psc_1550", rayleigh(A_psc, 1.55), "dB/km", 3, ["ch01.phys.rayleigh_coeff_psc_record"])
r.emit("tot_psc_1550", tot_psc_1550, "dB/km", 3,
       ["ch01.phys.rayleigh_coeff_psc_record", "ch01.phys.ir_absorption_1550"])
r.emit("ray_frac_ge_1550", rayleigh(A_ge, 1.55) / tot_ge_1550, "1", 2, in_a)
r.emit("ray_ge_1310", rayleigh(A_ge, 1.31), "dB/km", 3, ["ch01.phys.rayleigh_coeff_gedoped"])
r.emit("ray_fibhi_1310", rayleigh(A_fib_hi, 1.31), "dB/km", 3, ["ch01.phys.rayleigh_coeff_fiber"])
r.emit("ray_bulk_1550", rayleigh(A_bulk, 1.55), "dB/km", 3, ["ch01.phys.rayleigh_coeff_bulk_silica"])
r.emit("psc_vs_ge_pct", 100 * (A_ge / A_psc - 1), "%", 2,
       ["ch01.phys.rayleigh_coeff_gedoped", "ch01.phys.rayleigh_coeff_psc_record"])

# Consistency checks against measured / datasheet values
smf28_1550 = L("ch01.att.smf28ultra_max_1550")
rec_1550 = L("ch01.ull.sato2025_record_1550")
assert abs(tot_ge_1550 - smf28_1550) < 0.01, "Ge-doped model should sit near the SMF-28 Ultra 1550 nm max"
assert abs(tot_psc_1550 - rec_1550) < 0.005, "PSC model should reproduce the 1550 nm record within 5 mdB/km"
r.emit("psc_model_minus_record", 1e3 * (tot_psc_1550 - rec_1550), "mdB/km", 2,
       ["ch01.ull.sato2025_record_1550", "ch01.phys.rayleigh_coeff_psc_record"])

# Rayleigh fraction lower bound (Kanamori: >= 0.8)
assert rayleigh(A_ge, 1.55) / tot_ge_1550 >= L("ch01.phys.rayleigh_fraction_of_loss")

# ITU 1260 nm extension: delta = A (1.26^-4 - 1.31^-4)
d_lam = (1 / 1.26 ** 4 - 1 / 1.31 ** 4)
r.emit("ext_1260_fib_lo", A_fib_lo * d_lam, "dB/km", 2, ["ch01.phys.rayleigh_coeff_fiber"])
r.emit("ext_1260_ge", A_ge * d_lam, "dB/km", 2, ["ch01.phys.rayleigh_coeff_gedoped"])
r.emit("ext_1260_implied_A", L("ch01.att.g652d_rayleigh_extension_1260") / d_lam, "dB/(km·µm⁴)", 3,
       ["ch01.att.g652d_rayleigh_extension_1260"])
r.emit("ext_1260_factor", d_lam, "µm⁻⁴", 3, [])

# ---------------------------------------------------------------- Part B
n_splice = int(round(SPAN_KM / SECTION_KM)) - 1
acc_bol = n_splice * SPLICE_DB + N_CONN * CONN_DB
r.emit("span_km", SPAN_KM, "km", 2)
r.emit("n_splice", n_splice, "", 2)
r.emit("splice_db", SPLICE_DB, "dB", 2)
r.emit("conn_db", CONN_DB, "dB", 1)
r.emit("margin_db", MARGIN_DB, "dB", 1)
r.emit("section_km", SECTION_KM, "km", 1)
r.emit("acc_bol", acc_bol, "dB", 3)

cases = {
    "g652d_spec": "ch01.att.g652d_max_1530_1565",
    "g652_link": "ch01.att.g652_link_typ_cband",
    "smf28u": "ch01.att.smf28ultra_max_1550",
    "g654e_spec": "ch01.att.g654e_max_1550",
    "pa125": "ch01.att.sumitomo_pureadvance125_typ",
    "oband_link": "ch01.att.g652_link_typ_oband",
}
for key, rid in cases.items():
    a = L(rid)
    fib = a * SPAN_KM
    bol = fib + acc_bol
    eol = bol + MARGIN_DB
    r.emit(f"{key}_fiber", fib, "dB", 3, [rid])
    r.emit(f"{key}_bol", bol, "dB", 3, [rid])
    r.emit(f"{key}_eol", eol, "dB", 3, [rid])

# Check of the ZTE statement: 0.02 dB/km lower loss over 80 km = 1.6 dB
assert abs(0.02 * SPAN_KM - L("ch01.att.zte_g654e_vs_g652d_80km")) < 1e-9
# Difference between the datasheet G.652.D and the G.654.E product
r.emit("smf28u_minus_pa125", (L(cases["smf28u"]) - L(cases["pa125"])) * SPAN_KM, "dB", 2,
       [cases["smf28u"], cases["pa125"]])
r.emit("oband_minus_cband_link", (L(cases["oband_link"]) - L(cases["g652_link"])) * SPAN_KM, "dB", 3,
       [cases["oband_link"], cases["g652_link"]])

# ---------------------------------------------------------------- figure
plt = cl.setup_mpl()
lam = np.linspace(1.20, 1.70, 400)
fig, ax = plt.subplots(figsize=(7.2, 4.4))
ax.semilogy(lam * 1e3, rayleigh(A_ge, lam), color=cl.COLORS[0], ls="--", lw=1.5,
            label=r"Rayleigh, $A_R$ Ge-doped core (model)")
ax.semilogy(lam * 1e3, rayleigh(A_psc, lam), color=cl.COLORS[2], ls="--", lw=1.5,
            label=r"Rayleigh, $A_R$ PSC record (model)")
ax.semilogy(lam * 1e3, ir_tail(lam), color=cl.COLORS[1], ls=":", lw=2,
            label="IR multiphonon tail (model, assumed slope)")
ax.semilogy(lam * 1e3, rayleigh(A_ge, lam) + ir_tail(lam), color=cl.COLORS[0], lw=2.2,
            label="Total, Ge-doped core (model)")
ax.semilogy(lam * 1e3, rayleigh(A_psc, lam) + ir_tail(lam), color=cl.COLORS[2], lw=2.2,
            label="Total, PSC (model)")
ax.plot([1310, 1550], [L("ch01.att.smf28ultra_max_1310"), smf28_1550], "o", ms=8,
        color=cl.COLORS[3], label="SMF-28 Ultra maxima (datasheet)")
ax.plot([1550], [rec_1550], "D", ms=8, color=cl.COLORS[4], label="Silica-core record (1550 nm)")
oh_nm = L("ch01.phys.oh_overtone_1380") * 1e3
ax.axvline(oh_nm, color=cl.GRAY, lw=1, ls="-.")
ax.text(oh_nm + 4, 0.55, "OH overtone\n(not modeled)", fontsize=9)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Attenuation (dB/km)")
ax.set_ylim(0.005, 1.0)
ax.set_xlim(1200, 1700)
ax.legend(fontsize=8.5, loc="lower left", ncol=1)
cl.savefig(fig, "loss_model")

r.save()
