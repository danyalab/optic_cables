"""Worked example 1.5: the 58 dB constant and OSNR after N identical 80 km spans.

ASE PSD per polarization: S_ASE = n_sp h nu (G - 1);  F = 2 n_sp (G-1)/G + 1/G
OSNR (noise in both polarizations, B_ref):  OSNR = P / (N_s * 2 S_ASE * B_ref)
                                             = P / (N_s (F G - 1) h nu B_ref)
dB form: OSNR = 58 + P[dBm] - L_span - NF - 10 log10 N_s   (G = L_span)
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import ch01lib as cl

r = Results()
h = L("ch01.const.planck_h")
c = L("ch01.const.speed_of_light_c")
lam = float(cl.cond("ch01.osnr.gsup39_58db_constant", "wavelength_nm")) * 1e-9
dlam = float(cl.cond("ch01.osnr.gsup39_58db_constant", "reference_bandwidth_nm")) * 1e-9
nu = c / lam
bref = c * dlam / lam ** 2
ins0 = ["ch01.const.planck_h", "ch01.const.speed_of_light_c", "ch01.osnr.gsup39_58db_constant"]
r.emit("nu_thz", nu / 1e12, "THz", 4, ins0)
r.emit("bref_ghz", bref / 1e9, "GHz", 4, ins0)
r.emit("hnu_j", h * nu, "J", 4, ins0)
hnuB_mw = h * nu * bref / 1e-3
const = -10 * math.log10(hnuB_mw)
r.emit("const58", const, "dB", 4, ins0)
r.emit("hnuB_dbm", -const, "dBm", 4, ins0)
assert abs(const - L("ch01.osnr.gsup39_58db_constant")) < 0.1, "58 dB constant must reproduce"
# With the rounded 12.5 GHz bandwidth
const_125 = -10 * math.log10(h * nu * L("ch01.osnr.bref_0p1nm_equals_12p5ghz") * 1e9 / 1e-3)
r.emit("const58_125", const_125, "dB", 4, ins0 + ["ch01.osnr.bref_0p1nm_equals_12p5ghz"])
assert abs(const_125 - const) < 0.01

# ---------------- amplifier
NF = L("ch01.amp.accelink_mw_nf_max")              # dB, datasheet
F = cl.db2lin(NF)
ex11 = json.loads((pathlib.Path(__file__).parent / "out" / "ex11_span_budget.json").read_text())
Lspan = ex11["smf28u_bol"]["value"]                # dB, SMF-28 Ultra fibre + splices + connectors
Lspan_eol = ex11["smf28u_eol"]["value"]
G = cl.db2lin(Lspan)
nsp = (F * G - 1) / (2 * (G - 1))
r.emit("nf_db", NF, "dB", 2, ["ch01.amp.accelink_mw_nf_max"])
r.emit("lspan", Lspan, "dB", 4, ["ch01.att.smf28ultra_max_1550"])
r.emit("lspan_eol", Lspan_eol, "dB", 4, ["ch01.att.smf28ultra_max_1550"])
r.emit("nsp", nsp, "1", 3, ["ch01.amp.accelink_mw_nf_max"])
# Ideal amplifier: n_sp = 1 -> F -> 2 (1 - 1/G) + 1/G
F_ideal = 2 * (G - 1) / G + 1 / G
r.emit("nf_ideal", cl.lin2db(F_ideal), "dB", 4, ["ch01.amp.nsp_unity_full_inversion"])
assert abs(cl.lin2db(F_ideal) - L("ch01.amp.nf_quantum_limit_3db_carney")) < 0.05  # 10 log10 2 = 3.01
S_ase = nsp * h * nu * (G - 1)
r.emit("s_ase", S_ase, "W/Hz", 3, ["ch01.amp.accelink_mw_nf_max"])
r.emit("p_ase_bref_dbm", cl.w2dbm(2 * S_ase * bref), "dBm", 4, ["ch01.amp.accelink_mw_nf_max"])

# ---------------- OSNR after N spans
# ASSUMPTION: launch power 0 dBm per channel for this example (optimized in 1.6).
P_DBM = 0.0
P = cl.dbm2w(P_DBM)
r.emit("p_dbm", P_DBM, "dBm", 2)
for N in (1, 10, 20, 40):
    exact = P / (N * (F * G - 1) * h * nu * bref)
    rule = const + P_DBM - Lspan - NF - 10 * math.log10(N)
    r.emit(f"osnr_{N}", cl.lin2db(exact), "dB", 4, ins0 + ["ch01.amp.accelink_mw_nf_max"])
    r.emit(f"osnr_rule_{N}", rule, "dB", 4, ins0 + ["ch01.amp.accelink_mw_nf_max"])
    assert abs(cl.lin2db(exact) - rule) < 0.05
# Booster with gain equal to span loss adds one more amplifier: N -> N + 1
r.emit("osnr_20_booster", const + P_DBM - Lspan - NF - 10 * math.log10(21), "dB", 4, ins0)
# Each doubling of N costs 10 log10 2 dB
r.emit("doubling_db", 10 * math.log10(2), "dB", 3)
# End-of-life (margin consumed): OSNR after 20 spans
r.emit("osnr_20_eol", const + P_DBM - Lspan_eol - NF - 10 * math.log10(20), "dB", 4, ins0)

# ---------------- OSNR -> SNR at 64 GBd, dual polarization (p = 2)
# ASSUMPTION: 64 GBd symbol rate for the coherent example (a design choice fixed by the syllabus).
RS = 64e9
conv = 10 * math.log10(2 * bref / (2 * RS))
r.emit("rs_gbd", RS / 1e9, "GBd", 3)
r.emit("osnr_to_snr_db", conv, "dB", 3, ins0)
r.emit("snr_20", cl.lin2db(P / (20 * (F * G - 1) * h * nu * bref)) + conv, "dB", 4, ins0)

r.save()
