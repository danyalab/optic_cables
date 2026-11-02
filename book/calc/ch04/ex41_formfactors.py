"""Section 4.1: form-factor power ceilings, lane rates, and the PMD table.

Every input is a ledger record (or a number in its `conditions`). Results:
* lane bit rate R_b = R_s log2 M for the PAM4 lanes in use (eq. ch04.eq.pam_bitrate);
* supply-current ceilings converted to watts and checked against the MSA tables;
* energy-per-bit ceilings E_b = P_max / R_mod implied by each form factor;
* the reach and wavelength cells of the PMD table.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import re
import ch04lib as cl

r = Results()

# ---------------------------------------------------------------- lane rates
PAM4_BITS = math.log2(4)  # 2 bits per PAM4 symbol (ch04.eq.pam_bitrate source states 'PAM4: 2 bits/symbol')
rs100 = cl.cond_num("ch04.pmd.100g_fr_lr_wavelength", "signaling")          # 53.125 GBd
rs200 = cl.cond_num("ch04.ff.osfpxd_lanes", "lane_signaling")                # '224G-PAM4, 106.25 GBd' -> 224? guard below
m = re.search(r"([0-9.]+)\s*GBd", str(cl.cond("ch04.ff.osfpxd_lanes", "lane_signaling")))
rs200 = float(m.group(1))
rs224 = L("ch04.el.cei224_pam4_112gbd")
assert rs100 == 53.125 and rs200 == 106.25
r.emit("rs100", rs100, "GBd", 5, ["ch04.pmd.100g_fr_lr_wavelength"])
r.emit("rs200", rs200, "GBd", 5, ["ch04.ff.osfpxd_lanes"])
r.emit("rb100", rs100 * PAM4_BITS, "Gb/s", 5, ["ch04.pmd.100g_fr_lr_wavelength"])
r.emit("rb200", rs200 * PAM4_BITS, "Gb/s", 5, ["ch04.ff.osfpxd_lanes"])
r.emit("rb224", rs224 * PAM4_BITS, "Gb/s", 3, ["ch04.el.cei224_pam4_112gbd"])
# overhead of the 106.25 Gb/s lane over a 100 Gb/s payload (RS(544,514) + transcoding)
r.emit("lane_oh_pct", 100 * (rs100 * PAM4_BITS / 100 - 1), "%", 3, ["ch04.pmd.100g_fr_lr_wavelength"])
# OSFP-XD: 16 lanes x 200 Gb/s
n_xd = cl.cond("ch04.ff.osfpxd_lanes", "lanes")
assert n_xd * 200 == L("ch04.ff.osfpxd_lanes") * 1000
r.emit("xd_lanes", n_xd, "", 2, ["ch04.ff.osfpxd_lanes"])
# PAM6 / PAM8 alternatives at 224 Gb/s (framework states ~90 and ~75 GBd): ideal log2 M rates
r.emit("rs_pam6_ideal", 224 / math.log2(6), "GBd", 3, ["ch04.el.cei224_pam4_112gbd"])
r.emit("rs_pam8_ideal", 224 / math.log2(8), "GBd", 3, ["ch04.el.cei224_pam4_112gbd"])

# ---------------------------------------------------------------- power ceilings
V = cl.cond("ch04.ff.qsfpdd_class7_max", "supply_V")     # 3.3 V nominal
r.emit("vcc", V, "V", 2, ["ch04.ff.qsfpdd_class7_max"])
icc8 = L("ch04.ff.qsfpdd_icc8_steady")
p8 = icc8 * V
r.emit("qdd_c8_ceiling", p8, "W", 3, ["ch04.ff.qsfpdd_icc8_steady", "ch04.ff.qsfpdd_class7_max"])
# OSFP: current x 3.3 V must reproduce the MSA power-summary table
for rid in ("ch04.ff.osfp_rev40_33w", "ch04.ff.osfp_rev10_19w8"):
    assert abs(cl.cond(rid, "max_current_A") * V - L(rid)) < 0.05, rid
r.emit("osfp_r4_amps", cl.cond("ch04.ff.osfp_rev40_33w", "max_current_A"), "A", 2, ["ch04.ff.osfp_rev40_33w"])
r.emit("osfp_r1_amps", cl.cond("ch04.ff.osfp_rev10_19w8", "max_current_A"), "A", 2, ["ch04.ff.osfp_rev10_19w8"])
# QSFP-DD contact rating per Rev 6.0 / 7.0: power per contact-amp
r.emit("osfp_growth", L("ch04.ff.osfp1600_42w9") / L("ch04.ff.osfp_rev10_19w8"), "1", 3,
       ["ch04.ff.osfp1600_42w9", "ch04.ff.osfp_rev10_19w8"])
# Class 8 hot-plug currents (eq. ch04.eq.qsfpdd_class8_current) at the steady-state ceiling
r.emit("qdd_c8_ip", p8 / 2.5, "A", 3, ["ch04.ff.qsfpdd_icc8_steady"])
r.emit("qdd_c8_sp", p8 / 3.03, "A", 3, ["ch04.ff.qsfpdd_icc8_steady"])

# Energy-per-bit ceilings. ASSUMPTION: each ceiling is evaluated at the aggregate rate
# that the form factor revision was introduced for (QSFP-DD Class 7 at 400G, QSFP-DD800 at
# 800G, QSFP-DD1600 / OSFP1600 at 1.6T, OSFP-XD at 3.2T). The MSAs do not tie a power class
# to a data rate.
ceil = [
    ("eb_qdd_c7_400", L("ch04.ff.qsfpdd_class7_max"), 400, ["ch04.ff.qsfpdd_class7_max"]),
    ("eb_qdd800_800", L("ch04.ff.qsfpdd_rev6_25w"), 800, ["ch04.ff.qsfpdd_rev6_25w"]),
    ("eb_osfp_r4_800", L("ch04.ff.osfp_rev40_33w"), 800, ["ch04.ff.osfp_rev40_33w"]),
    ("eb_qdd1600_1600", L("ch04.ff.qsfpdd1600_40w"), 1600, ["ch04.ff.qsfpdd1600_40w"]),
    ("eb_osfp1600_1600", L("ch04.ff.osfp1600_42w9"), 1600, ["ch04.ff.osfp1600_42w9"]),
    ("eb_osfpxd_3200", L("ch04.ff.osfpxd_40w_target"), 3200, ["ch04.ff.osfpxd_40w_target"]),
]
for name, p, rate, ins in ceil:
    r.emit(name, cl.pj_per_bit(p, rate), "pJ/bit", 3, ins)
# ceilings fall roughly as 1/rate: product rate * E_b must not stay constant
assert cl.pj_per_bit(40, 3200) < cl.pj_per_bit(14, 400) / 2

# ---------------------------------------------------------------- PMD table cells
dr_lo, fr_hi = L("ch04.std.8023dj_dr_reach", "lo"), L("ch04.std.8023dj_dr_reach", "hi")
r.emit("dr_reach", dr_lo, "m", 3, ["ch04.std.8023dj_dr_reach"])
r.emit("fr_reach", fr_hi / 1e3, "km", 2, ["ch04.std.8023dj_dr_reach"])
lr = cl.cond("ch04.pmd.100g_fr_lr_wavelength", "reach")        # 'FR 2 km, LR 10 km'
lr_km = float(re.search(r"LR\s+([0-9.]+)\s*km", lr).group(1))
fr_km = float(re.search(r"FR\s+([0-9.]+)\s*km", lr).group(1))
assert fr_km * 1e3 == fr_hi
r.emit("lr_reach", lr_km, "km", 2, ["ch04.pmd.100g_fr_lr_wavelength"])
r.emit("fr4_reach", cl.cond("ch04.pmd.400g_fr4_grid", "reach_km"), "km", 2, ["ch04.pmd.400g_fr4_grid"])
lo, hi = L("ch04.pmd.100g_fr_lr_wavelength", "lo"), L("ch04.pmd.100g_fr_lr_wavelength", "hi")
r.emit("dr_lam_c", 0.5 * (lo + hi), "nm", 4, ["ch04.pmd.100g_fr_lr_wavelength"])
r.emit("dr_lam_w", hi - lo, "nm", 3, ["ch04.pmd.100g_fr_lr_wavelength"])
lanes = [float(x.replace("nm", "")) for x in str(cl.cond("ch04.pmd.400g_fr4_grid", "lanes")).split(",")]
spacing = lanes[1] - lanes[0]
assert all(abs((b - a) - spacing) < 1e-9 for a, b in zip(lanes, lanes[1:]))
r.emit("fr4_spacing", spacing, "nm", 2, ["ch04.pmd.400g_fr4_grid"])
r.emit("fr4_lam0", lanes[0], "nm", 4, ["ch04.pmd.400g_fr4_grid"])
r.emit("fr4_lam3", lanes[-1], "nm", 4, ["ch04.pmd.400g_fr4_grid"])
r.emit("fr4_nlanes", len(lanes), "", 1, ["ch04.pmd.400g_fr4_grid"])
# FR4 lane passband width (Table 2-1: 1264.5 to 1277.5 nm for L0)
q = cl.rec("ch04.pmd.400g_fr4_grid")["quote"]
a, b = [float(x) for x in re.search(r"([0-9.]+) to ([0-9.]+) nm", q).groups()]
r.emit("fr4_passband", b - a, "nm", 3, ["ch04.pmd.400g_fr4_grid"])

# DSP CMOS nodes quoted with the power claims (for prose without bare units)
r.emit("node_3nm", cl.cond("ch04.pw.sian3_1p6t_sub23w", "node_nm"), "nm", 1, ["ch04.pw.sian3_1p6t_sub23w"])
m5 = re.search(r"(\d+) nm DSP", cl.rec("ch04.pw.1p6t_breakdown_dsp")["claim"])
r.emit("node_5nm", float(m5.group(1)), "nm", 1, ["ch04.pw.1p6t_breakdown_dsp"])

r.save()
