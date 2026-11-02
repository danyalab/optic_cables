"""Worked example 7.4: open-cable GSNR acceptance arithmetic (ITU-T G.977.1).

* signal droop: product rule 1 + 1/SNR_ASE = prod_n (1 + 1/SNR_n) versus the
  additive rule 1/SNR_ASE = sum_n 1/SNR_n, for identical amplifiers;
* G.977.1 measurement conditions: occupied bandwidth (1 + roll-off) R_s versus
  the allowed carrier spacing;
* removal of transceiver noise and the sensitivity to the back-to-back SNR;
* inverse Shannon: the smallest GSNR that supports each FASTER spectral
  efficiency step, and the SE-distance product.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import json
import math
from common import L, Results
import ch07lib as cl

r = Results()
HERE = pathlib.Path(__file__).parent
ex72 = json.loads((HERE / "out" / "ex72_power_limited.json").read_text())
LINK = "ch07.power.perin_link_reference"
N_s = int(cl.cond(LINK, "N_s"))

# ---------------------------------------------------------------- droop
def droop_penalty_db(snr_add_db, N):
    """Penalty of the product rule relative to the additive rule, identical amplifiers."""
    snr_add = cl.db2lin(snr_add_db)
    snr_n = N * snr_add                       # each amplifier's own SNR
    snr_prod = 1 / ((1 + 1 / snr_n) ** N - 1)
    return snr_add_db - cl.lin2db(snr_prod)


for tag, s in (("opt", ex72["snr_opt_db"]["value"]), ("gn", ex72["gsnr_max_db"]["value"])):
    r.emit(f"droop_{tag}_snr_db", s, "dB", 3, [LINK])
    r.emit(f"droop_{tag}_pen_db", droop_penalty_db(s, N_s), "dB", 2, [LINK])
# large-N limit: 1/SNR_prod = exp(1/SNR_add) - 1
s = cl.db2lin(ex72["snr_opt_db"]["value"])
lim = cl.lin2db(s) - cl.lin2db(1 / math.expm1(1 / s))
r.emit("droop_opt_limit_db", lim, "dB", 2, [LINK])
assert abs(lim - droop_penalty_db(ex72["snr_opt_db"]["value"], N_s)) < 0.01
assert droop_penalty_db(ex72["gsnr_max_db"]["value"], N_s) < 0.5

# ---------------------------------------------------------------- measurement conditions
ro = L("ch07.open.g9771_rolloff")
sp = L("ch07.open.g9771_carrier_spacing")
r.emit("rolloff", ro, "", 2, ["ch07.open.g9771_rolloff"])
r.emit("spacing", sp, "", 3, ["ch07.open.g9771_carrier_spacing"])
r.emit("guard_pct", 100 * (sp - (1 + ro)), "%", 2, ["ch07.open.g9771_rolloff", "ch07.open.g9771_carrier_spacing"])
r.emit("fill_pct", 100 / sp, "%", 3, ["ch07.open.g9771_carrier_spacing"])
assert sp > 1 + ro

# ---------------------------------------------------------------- transceiver noise removal
# ASSUMPTION (illustration): a line GSNR of 10 dB measured with a transceiver whose
# back-to-back SNR is the middle of the Chapter 1 range; the back-to-back value is
# then misestimated by 0.5 dB.
G_TRUE_DB = 10.0
tr_mid = L("ch01.gap.transceiver_snr_range", "mid")
meas = 1 / (1 / cl.db2lin(G_TRUE_DB) + 1 / cl.db2lin(tr_mid))
r.emit("tr_mid_db", tr_mid, "dB", 3, ["ch01.gap.transceiver_snr_range"])
r.emit("tr_true_db", G_TRUE_DB, "dB", 3)
r.emit("tr_meas_db", cl.lin2db(meas), "dB", 3, ["ch01.gap.transceiver_snr_range"])
for tag, err in (("lo", -0.5), ("hi", 0.5)):
    est = 1 / (1 / meas - 1 / cl.db2lin(tr_mid + err))
    r.emit(f"tr_err_{tag}_db", cl.lin2db(est) - G_TRUE_DB, "dB", 2, ["ch01.gap.transceiver_snr_range"])

# ---------------------------------------------------------------- GAWBS term (illustration)
for d in (10, 15, 20):
    r.emit(f"gawbs_pen_{d}", cl.lin2db(1 + cl.db2lin(-d)), "dB", 2)

# ---------------------------------------------------------------- FASTER inverse Shannon
F_ins = ["ch07.open.faster_design_se", "ch07.open.faster_live_4bpshz", "ch07.open.faster_ps64_6bpshz"]
for tag, rid in (("se2", "ch07.open.faster_design_se"), ("se4", "ch07.open.faster_live_4bpshz"),
                 ("se6", "ch07.open.faster_ps64_6bpshz")):
    se = L(rid)
    snr = 2 ** (se / 2) - 1           # SE in b/s/Hz over both polarizations, R_s = grid
    r.emit(f"{tag}", se, "b/s/Hz", 2, [rid])
    r.emit(f"{tag}_snr_db", cl.lin2db(snr) if snr != 1 else 0.0, "dB", 3, [rid])
r.emit("se3_snr_db", cl.lin2db(2 ** 1.5 - 1), "dB", 3, ["ch07.open.faster_design_se"])
r.emit("faster_L_km", float(cl.cond("ch07.open.faster_live_4bpshz", "L_km")), "km", 5,
       ["ch07.open.faster_live_4bpshz"])
sed = L("ch07.open.faster_ps64_6bpshz") * float(cl.cond("ch07.open.faster_live_4bpshz", "L_km"))
r.emit("faster_sed", sed, "b/s/Hz·km", 5, F_ins)
assert abs(sed - L("ch07.open.faster_se_distance")) < 1
r.emit("faster_sed_pub", L("ch07.open.faster_se_distance"), "b/s/Hz·km", 5, ["ch07.open.faster_se_distance"])
r.emit("faster_spacing_ghz", float(cl.cond("ch07.open.faster_live_4bpshz", "channel_spacing_GHz")), "GHz", 2,
       ["ch07.open.faster_live_4bpshz"])
# capacity of a 75 GHz slot at 4 b/s/Hz
r.emit("faster_slot_gbps", L("ch07.open.faster_live_4bpshz")
       * float(cl.cond("ch07.open.faster_live_4bpshz", "channel_spacing_GHz")), "Gb/s", 3,
       ["ch07.open.faster_live_4bpshz"])

r.save()
