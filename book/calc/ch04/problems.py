"""Chapter 4 end-of-chapter problems: answers computed from ledger records and the
outputs of the worked-example scripts (which `make calc` runs first, alphabetically)."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import ch04lib as cl

r = Results()
OUT = pathlib.Path(__file__).parent / "out"


def C(script, name):
    return json.loads((OUT / f"{script}.json").read_text())[name]["value"]


# P1: lane arithmetic
rb200 = C("ex41_formfactors", "rb200")
r.emit("p1_lanes_16", 1600 / 200, "", 1, ["ch04.ff.osfpxd_lanes"])
r.emit("p1_line16", 8 * rb200, "Gb/s", 4, ["ch04.ff.osfpxd_lanes"])
r.emit("p1_nyq200", C("ex41_formfactors", "rs200") / 2, "GHz", 4, ["ch04.ff.osfpxd_lanes"])

# P2: form-factor ceilings
r.emit("p2_c8", C("ex41_formfactors", "qdd_c8_ceiling"), "W", 3, ["ch04.ff.qsfpdd_icc8_steady"])
r.emit("p2_c8_eb1600", cl.pj_per_bit(C("ex41_formfactors", "qdd_c8_ceiling"), 1600), "pJ/bit", 3, ["ch04.ff.qsfpdd_icc8_steady"])
r.emit("p2_ratio_xd", C("ex41_formfactors", "eb_qdd_c7_400") / C("ex41_formfactors", "eb_osfpxd_3200"), "1", 3,
       ["ch04.ff.qsfpdd_class7_max", "ch04.ff.osfpxd_40w_target"])

# P3: the 1.6T power model and a DSP node change
s_dsp = C("ex43_power_model", "s16_DSP") / 100
P16 = C("ex43_power_model", "p16")
# ASSUMPTION (problem statement): a node change cuts DSP power by 25 % and nothing else changes.
CUT = 0.25
r.emit("p3_cut", 100 * CUT, "%", 2)
r.emit("p3_newp", P16 * (1 - s_dsp * CUT), "W", 3, ["ch04.pw.1p6t_breakdown_dsp"])
r.emit("p3_neweb", cl.pj_per_bit(P16 * (1 - s_dsp * CUT), 1600), "pJ/bit", 3, ["ch04.pw.1p6t_breakdown_dsp"])
r.emit("p3_save_pct", 100 * s_dsp * CUT, "%", 3, ["ch04.pw.1p6t_breakdown_dsp"])
r.emit("p3_newshare", 100 * s_dsp * (1 - CUT) / (1 - s_dsp * CUT), "%", 3, ["ch04.pw.1p6t_breakdown_dsp"])

# P4: LPO saving decomposition
r.emit("p4_mod", C("ex44_lpo", "eo_saving_pct"), "%", 3, ["ch04.lpo.eoptolink_40pct"])
r.emit("p4_extra", C("ex44_lpo", "eo_implied_extra"), "W", 2, ["ch04.lpo.eoptolink_40pct"])
r.emit("p4_sys", C("ex44_lpo", "eo_saving_pct") * C("ex44_lpo", "bech_optics_share") / 100, "%", 3,
       ["ch04.lpo.eoptolink_40pct", "ch04.lpo.bechtolsheim_50pct"])

# P5: 102.4T switch with 1.6T pluggables vs CPO
p_plug = C("ex45_cpo_switch", "p102_16_ds")
p_cpo = C("ex45_cpo_switch", "p102_cpo")
r.emit("p5_plug", p_plug, "W", 4, ["ch04.pmd.1p6t_dr8_power"])
r.emit("p5_cpo", p_cpo, "W", 3, ["ch04.cpo.bailly_5p5w"])
r.emit("p5_save", p_plug - p_cpo, "W", 3, ["ch04.pmd.1p6t_dr8_power", "ch04.cpo.bailly_5p5w"])
r.emit("p5_save_pct", 100 * (1 - p_cpo / p_plug), "%", 3, ["ch04.pmd.1p6t_dr8_power", "ch04.cpo.bailly_5p5w"])
# fraction of the Evans 102.4T DSP-case switch power
r.emit("p5_frac_sw", 100 * (p_plug - p_cpo) / C("ex45_cpo_switch", "ev_dsp_tot"), "%", 3,
       ["ch04.cpo.evans_switch_power"])

# P6: reliability demonstration
FIT_TARGET = 100  # ASSUMPTION (problem statement): target failure rate per port
CL = C("ex45_cpo_switch", "cl") / 100
T_need = -math.log(1 - CL) / (FIT_TARGET * 1e-9)
r.emit("p6_fit", FIT_TARGET, "FIT", 3)
r.emit("p6_hours", T_need, "port-h", 3)
r.emit("p6_ratio", T_need / L("ch04.cpo.meta_1m_hours"), "1", 3, ["ch04.cpo.meta_1m_hours"])
r.emit("p6_years_128", T_need / 128 / 8766, "years", 3)
r.emit("p6_ub", C("ex45_cpo_switch", "meta_lambda_ub_fit"), "FIT", 3, ["ch04.cpo.meta_1m_hours"])

# P7: OSNR to SNR for 400ZR and 800ZR
r.emit("p7_snr800", C("ex46_coherent", "snr800_req"), "dB", 3, ["ch04.coh.800zr_osnr"])
r.emit("p7_snr400", C("ex46_coherent", "snr400_req"), "dB", 3, ["ch04.coh.400zr_osnr_26"])
r.emit("p7_naive", L("ch04.coh.400zr_osnr_26") + C("ex46_coherent", "baud_ratio_db"), "dB", 3,
       ["ch04.coh.400zr_osnr_26", "ch04.coh.800zr_baud"])
r.emit("p7_diff", L("ch04.coh.400zr_osnr_26") + C("ex46_coherent", "baud_ratio_db") - L("ch04.coh.800zr_osnr"), "dB", 3,
       ["ch04.coh.400zr_osnr_26", "ch04.coh.800zr_osnr"])

# P8: noise figure needed to close 120 km on the ITU cabled link with booster-limited launch
deficit = -C("ex46_coherent", "margincap_itulink_120")
nf_need = L("ch01.amp.accelink_mw_nf_max") - deficit
r.emit("p8_deficit", deficit, "dB", 2, ["ch04.coh.800zr_osnr"])
r.emit("p8_nf_need", nf_need, "dB", 2, ["ch01.amp.accelink_mw_nf_max"])
nf_q = L("ch01.amp.nf_quantum_limit_3db_carney")
r.emit("p8_nf_limit", nf_q, "dB", 2, ["ch01.amp.nf_quantum_limit_3db_carney"])
assert nf_need < nf_q
r.emit("p8_lmax", C("ex46_coherent", "lmaxcap_itulink"), "km", 3, ["ch04.coh.800zr_osnr"])

# P9: 800LR symbol rate and budgets
r.emit("p9_rs", C("ex46_coherent", "lr_rs_calc"), "GBd", 6, ["ch04.coh.800lr_baud"])
r.emit("p9_o", C("ex46_coherent", "lr_o_margin"), "dB", 2, ["ch04.coh.800lr_loss_budget"])
r.emit("p9_c", C("ex46_coherent", "lr_c_margin"), "dB", 2, ["ch04.coh.800lr_loss_budget"])
r.emit("p9_vs_zr", 100 * (C("ex46_coherent", "rs_lr") / C("ex46_coherent", "rs800") - 1), "%", 3,
       ["ch04.coh.800lr_baud", "ch04.coh.800zr_baud"])

# P10: external laser source budget
mw_hi = C("ex45_cpo_switch", "elsfp_hi_mw")
r.emit("p10_mw", mw_hi, "mW", 3, ["ch04.cpo.elsfp_power_classes"])
# ASSUMPTION (problem statement): 8 wavelength-fibre outputs per ELSFP at the top class.
NOUT = 8
r.emit("p10_nout", NOUT, "", 1)
r.emit("p10_opt_total", NOUT * mw_hi / 1e3, "W", 3, ["ch04.cpo.elsfp_power_classes"])
r.emit("p10_wpe_min", 100 * NOUT * mw_hi / 1e3 / C("ex45_cpo_switch", "elsfp_pmax"), "%", 3,
       ["ch04.cpo.elsfp_power_classes", "ch04.cpo.elsfp_supply"])

r.save()
