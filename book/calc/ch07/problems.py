"""Answers to the Chapter 7 problems (inputs from the ledger and earlier scripts)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import json
import math
from scipy.optimize import brentq
from common import L, Results
import ch07lib as cl

r = Results()
HERE = pathlib.Path(__file__).parent
ex71 = json.loads((HERE / "out" / "ex71_power_feed.json").read_text())
ex72 = json.loads((HERE / "out" / "ex72_power_limited.json").read_text())
ex73 = json.loads((HERE / "out" / "ex73_sdm.json").read_text())
LINK = "ch07.power.perin_link_reference"
Lkm = L(LINK)
N_s = int(cl.cond(LINK, "N_s"))

# P1: 20 kV PFE, 0.7 ohm/km, reference length
V = L("ch07.arch.pfe_voltage_range_dry_plant", "hi") * 1e3
Rp = L("ch07.arch.cable_resistance_low_end")
ins1 = ["ch07.arch.pfe_voltage_range_dry_plant", "ch07.arch.cable_resistance_low_end", LINK]
P = cl.max_power_transfer(V, Rp * Lkm)
r.emit("p1_V_kv", V / 1e3, "kV", 2, ins1)
r.emit("p1_P_kw", P / 1e3, "kW", 3, ins1)
r.emit("p1_I_a", V / (2 * Rp * Lkm), "A", 3, ins1)
r.emit("p1_Prep_w", P / N_s, "W", 3, ins1)
r.emit("p1_ratio", P / (ex71["Pmax_kw"]["value"] * 1e3), "", 3, ins1)

# P2: double-end feeding, same total voltage vs same per-end voltage
r.emit("p2_Pdouble_kw", ex71["Pdouble_kw"]["value"], "kW", 3)
r.emit("p2_I_a", 2 * ex71["Iopt_a"]["value"], "A", 3)

# P3: span gain optimum
G1 = brentq(lambda G: math.log(G) - 2 * (1 - 1 / G), 1.5, 1e4)
r.emit("p3_exact_db", cl.lin2db(G1), "dB", 3)
r.emit("p3_highgain_db", 20 / math.log(10), "dB", 3)
r.emit("p3_margin_db", ex72["span_opt0_db"]["value"], "dB", 3)
r.emit("p3_km", 2 * cl.LN10_10 / ex72["alpha"]["value"], "km", 3, [LINK])

# P4: small-q approximation
r.emit("p4_q", ex72["q"]["value"], "", 3)
r.emit("p4_exact", ex72["x_opt"]["value"], "", 3)
r.emit("p4_approx", ex72["x_approx"]["value"], "", 3)
r.emit("p4_err_pct", 100 * (ex72["x_approx"]["value"] / ex72["x_opt"]["value"] - 1), "%", 2)
q_small = 0.01
x_small = brentq(lambda x: math.log1p(x) - (x + q_small) / (1 + x), 1e-9, 10)
r.emit("p4_qsmall", q_small, "", 1)
r.emit("p4_small_err_pct", 100 * (math.sqrt(2 * q_small) / x_small - 1), "%", 2)

# P5: C* = C_inf / (1 + x*)
r.emit("p5_frac_pct", 100 / (1 + ex72["x_opt"]["value"]), "%", 3)
assert abs(100 / (1 + ex72["x_opt"]["value"]) - ex72["c_opt_frac_pct"]["value"]) < 0.01

# P6: energy per bit in the wet plant
Pe = ex72["Pe_kw"]["value"] * 1e3
r.emit("p6_cinf_gbps_per_w", ex72["c_inf_tbps"]["value"] * 1e3 / Pe, "Gb/s per W", 3)
r.emit("p6_pj_per_bit_opt", Pe / (ex72["c_opt_tbps"]["value"] * 1e12) * 1e12, "pJ/bit", 3)
r.emit("p6_pj_per_bit_8", Pe / (ex72["c_8"]["value"] * 1e12) * 1e12, "pJ/bit", 3)

# P7: droop on a 140-span cable at an assumed additive SNR of 5 dB
N7 = int(ex73["ta_Ns"]["value"])
S7_DB = 5.0
s = cl.db2lin(S7_DB)
prod = 1 / ((1 + 1 / (N7 * s)) ** N7 - 1)
r.emit("p7_N", N7, "", 3)
r.emit("p7_snr_db", S7_DB, "dB", 2)
r.emit("p7_pen_db", S7_DB - cl.lin2db(prod), "dB", 2)

# P8: pump sharing, M = 4, N_s = 140
M = 4
delta = -cl.lin2db(1 - 1 / M)
r.emit("p8_drop_db", delta, "dB", 3)
r.emit("p8_pen_db", cl.lin2db((N7 - 1 + cl.db2lin(delta)) / N7), "dB", 2)

# P9: reliability on the 7,000 km cable
life = L("ch07.arch.design_life_25y")
nrep = L("ch07.arch.reliability_lt3_ship_repairs")
r.emit("p9_fit", nrep / (life * 365.25 * 24 * N7) * 1e9, "FIT", 2,
       ["ch07.arch.design_life_25y", "ch07.arch.reliability_lt3_ship_repairs"])

# P10: Desbruslais reconstruction (from ex72)
r.emit("p10_pch_dbm", ex72["des_pch_dbm"]["value"], "dBm", 3)
r.emit("p10_osnr_db", ex72["des_osnr_db"]["value"], "dB", 3)

r.save()
