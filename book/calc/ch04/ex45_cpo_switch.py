"""Section 4.5: switch-level optics power with pluggables, LPO and CPO; CPO reliability bounds.

Worked example: optics power of a 51.2T (64 x 800G) and a 102.4T (128 x 800G) switch,
computed from per-800G module or engine powers in the ledger, and compared with the
Evans (JLT 2026) switch model.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch04lib as cl

r = Results()

# ------------------------------------------------ per-800G powers (tier A/B only in the main cases)
ev = "ch04.cpo.evans_switch_power"
meta = L("ch04.cpo.meta_65pct") / 100
p_ds = L("ch04.pmd.800g_2xdr4_power")
# ASSUMPTION: Meta's measured 65 % CPO saving (relative to its own retimed 100G/lane pluggables, whose
# wattage is not in the ledger) is applied to the 800G 2xDR4 datasheet maximum.
cases = [
    ("dsp_ds", "Retimed pluggable,\ndatasheet max", p_ds, ["ch04.pmd.800g_2xdr4_power"]),
    ("dsp_ev", "Retimed pluggable,\nEvans model", cl.cond(ev, "optics_DSP_W") / 128, [ev]),
    ("lpo_ev", "LPO,\nEvans model", cl.cond(ev, "optics_LPO_W") / 128, [ev]),
    ("cpo_meta", "CPO, Meta saving\non datasheet max", p_ds * (1 - meta), ["ch04.cpo.meta_65pct", "ch04.pmd.800g_2xdr4_power"]),
    ("cpo_ev", "CPO,\nEvans model", cl.cond(ev, "optics_CPO_W") / 128, [ev]),
]
# tier-C slide values, used only in the contested box
cases_c = [
    ("dsp_ref", L("ch04.pw.broadcom_pluggable_14w_800g"), ["ch04.pw.broadcom_pluggable_14w_800g"]),
    ("lpo_eo", cl.cond_num("ch04.lpo.eoptolink_40pct", "to_W"), ["ch04.lpo.eoptolink_40pct"]),
    ("cpo", L("ch04.cpo.bailly_5p5w"), ["ch04.cpo.bailly_5p5w"]),
]
SW = {"51": 51.2e3, "102": 102.4e3}         # Gb/s
power = {}
for key, *rest in cases + [(k, None, p, i) for k, p, i in cases_c]:
    lab, p800, ins = rest
    r.emit(f"w_{key}", p800, "W", 3, ins)
    r.emit(f"eb_{key}", cl.pj_per_bit(p800, 800), "pJ/bit", 3, ins)
    for s, cap in SW.items():
        n = cap / 800
        power[(key, s)] = n * p800
        r.emit(f"p{s}_{key}", n * p800, "W", 3, ins)
r.emit("n51", SW["51"] / 800, "", 2)
r.emit("n102", SW["102"] / 800, "", 3)
for s in SW:
    r.emit(f"save{s}_meta", power[("dsp_ds", s)] - power[("cpo_meta", s)], "W", 3, cases[3][3])
    r.emit(f"save{s}_ev", power[("dsp_ev", s)] - power[("cpo_ev", s)], "W", 3, [ev])
    r.emit(f"save{s}_cpo_vs_ref", power[("dsp_ref", s)] - power[("cpo", s)], "W", 3,
           ["ch04.pw.broadcom_pluggable_14w_800g", "ch04.cpo.bailly_5p5w"])
r.emit("cpo_vs_ref_pct", 100 * (1 - L("ch04.cpo.bailly_5p5w") / L("ch04.pw.broadcom_pluggable_14w_800g")), "%", 3,
       ["ch04.pw.broadcom_pluggable_14w_800g", "ch04.cpo.bailly_5p5w"])
r.emit("meta_implied_cpo_w", L("ch04.pw.broadcom_pluggable_14w_800g") * (1 - meta), "W", 3,
       ["ch04.cpo.meta_65pct", "ch04.pw.broadcom_pluggable_14w_800g"])
r.emit("meta_pct", 100 * meta, "%", 2, ["ch04.cpo.meta_65pct"])
# 1.6T pluggables in a 102.4T switch (64 modules), model and datasheet
ex43 = __import__("json").loads((pathlib.Path(__file__).parent / "out" / "ex43_power_model.json").read_text())
p16 = ex43["p16"]["value"]
r.emit("p102_16_model", 64 * p16, "W", 3, ["ch04.pw.1p6t_breakdown_dsp"])
r.emit("p102_16_ds", 64 * L("ch04.pmd.1p6t_dr8_power"), "W", 3, ["ch04.pmd.1p6t_dr8_power"])

# ------------------------------------------------ Evans 102.4T switch
E = {k: cl.cond(ev, k) for k in ("DSP_W", "LPO_W", "CPO_W", "optics_DSP_W", "optics_LPO_W", "optics_CPO_W",
                                    "SerDes_DSP_W", "SerDes_CPO_W")}
r.emit("ev_dsp_tot", E["DSP_W"], "W", 4, [ev])
r.emit("ev_lpo_tot", E["LPO_W"], "W", 4, [ev])
r.emit("ev_cpo_tot", E["CPO_W"], "W", 4, [ev])
r.emit("ev_opt_dsp", E["optics_DSP_W"], "W", 4, [ev])
r.emit("ev_opt_lpo", E["optics_LPO_W"], "W", 3, [ev])
r.emit("ev_opt_cpo", E["optics_CPO_W"], "W", 3, [ev])
r.emit("ev_serdes_dsp", E["SerDes_DSP_W"], "W", 3, [ev])
r.emit("ev_serdes_cpo", E["SerDes_CPO_W"], "W", 2, [ev])
r.emit("ev_cpo_vs_dsp_sw", 100 * (1 - E["CPO_W"] / E["DSP_W"]), "%", 3, [ev])
r.emit("ev_cpo_vs_lpo_sw", 100 * (1 - E["CPO_W"] / E["LPO_W"]), "%", 3, [ev])
r.emit("ev_cpo_vs_dsp_opt", 100 * (1 - E["optics_CPO_W"] / E["optics_DSP_W"]), "%", 3, [ev])
r.emit("ev_eb_cpo", cl.pj_per_bit(E["optics_CPO_W"], 102400), "pJ/bit", 3, [ev])
r.emit("ev_cpo_per800", E["optics_CPO_W"] / 128, "W", 3, [ev])
# DSP-case decomposition from the locator of equation record ch04.eq.switch_power_sum:
# 'ASIC+sup + optics + SerDes + cooling + PSU = total'
import re, yaml
eqs = yaml.safe_load((pathlib.Path(__file__).resolve().parents[2] / "ledger" / "ch04_equations.yaml").read_text())
loc = next(e["locator"] for e in eqs["equations"] if e["id"] == "ch04.eq.switch_power_sum")
terms = [float(t) for t in re.search(r"([0-9+]+) = ([0-9]+) W", loc).group(1).split("+")]
asic, opt_d, ser_d, cool, psu = terms
assert opt_d == E["optics_DSP_W"] and ser_d == E["SerDes_DSP_W"] and sum(terms) == E["DSP_W"]
r.emit("ev_asic", asic, "W", 4, [ev])
r.emit("ev_cool", cool, "W", 3, [ev])
r.emit("ev_psu", psu, "W", 3, [ev])
r.emit("ev_cool_psu_dsp", cool + psu, "W", 4, [ev])
# CPO saving with SerDes included vs Evans' stated 69 %
inc = 1 - (E["optics_CPO_W"] + E["SerDes_CPO_W"]) / (E["optics_DSP_W"] + E["SerDes_DSP_W"])
r.emit("ev_incl_serdes_pct", 100 * inc, "%", 3, [ev])
# The abstract's 69 % ('current' CPO, incl. SerDes) is smaller than the table-implied value:
# the table is a 102.4T projection, the abstract compares current transceivers. Emit both.
r.emit("ev_abs_incl_serdes", cl.cond("ch04.cpo.evans_eff_vs_dsp", "incl_SerDes_vs_DSP_pct"), "%", 2, ["ch04.cpo.evans_eff_vs_dsp"])
assert 100 * inc > L("ch04.cpo.evans_eff_vs_dsp")

# ------------------------------------------------ Humboldt (TH4, previous generation)
hum = L("ch04.cpo.humboldt_102w")
per800 = cl.cond("ch04.cpo.humboldt_102w", "per_800G_W")
r.emit("hum_per800", per800, "W", 2, ["ch04.cpo.humboldt_102w"])
r.emit("hum_eb", cl.pj_per_bit(per800, 800), "pJ/bit", 3, ["ch04.cpo.humboldt_102w"])
r.emit("hum_cap", hum / per800 * 0.8, "Tb/s", 3, ["ch04.cpo.humboldt_102w"])
r.emit("hum_lane", hum / per800 * 800 / cl.cond_num("ch04.cpo.humboldt_102w", "lanes"), "Gb/s", 3, ["ch04.cpo.humboldt_102w"])
r.emit("hum_opt_vs_asic", 100 * hum / cl.cond("ch04.cpo.humboldt_102w", "switch_ASIC_W"), "%", 3, ["ch04.cpo.humboldt_102w"])
r.emit("bailly_over_hum", 100 * (1 - L("ch04.cpo.bailly_5p5w") / per800), "%", 3, ["ch04.cpo.humboldt_102w", "ch04.cpo.bailly_5p5w"])

# ------------------------------------------------ external laser sources
lo_dbm, hi_dbm = L("ch04.cpo.elsfp_power_classes", "lo"), L("ch04.cpo.elsfp_power_classes", "hi")
r.emit("elsfp_lo_mw", cl.dbm2w(lo_dbm) * 1e3, "mW", 3, ["ch04.cpo.elsfp_power_classes"])
r.emit("elsfp_hi_mw", cl.dbm2w(hi_dbm) * 1e3, "mW", 3, ["ch04.cpo.elsfp_power_classes"])
r.emit("elsfp_step", cl.cond("ch04.cpo.elsfp_power_classes", "MP") - cl.cond("ch04.cpo.elsfp_power_classes", "LP"), "dB", 2,
       ["ch04.cpo.elsfp_power_classes"])
pairs = cl.cond_num("ch04.cpo.elsfp_supply", "pins")
amax = L("ch04.cpo.elsfp_supply")
V = cl.cond("ch04.ff.qsfpdd_class7_max", "supply_V")
r.emit("elsfp_pmax", pairs * amax * V, "W", 3, ["ch04.cpo.elsfp_supply"])
ports = 128  # Bailly: 128 x 400G FR4 (ledger conditions of ch04.cpo.bailly_70pct_claim)
assert str(ports) in cl.cond("ch04.cpo.bailly_70pct_claim", "ports")
pls = ports / L("ch04.cpo.meta_pls_8ports")
r.emit("n_pls", pls, "", 2, ["ch04.cpo.meta_pls_8ports", "ch04.cpo.bailly_70pct_claim"])
r.emit("bailly_ports", ports, "", 3, ["ch04.cpo.bailly_70pct_claim"])
tj = L("ch04.cpo.meta_laser_tj")
r.emit("tj_delta", cl.cond("ch04.cpo.meta_laser_tj", "pluggable_uncooled_C") - tj, "K", 2, ["ch04.cpo.meta_laser_tj"])

# ------------------------------------------------ reliability: zero-failure confidence bounds
# With zero events in T device-hours, the one-sided upper confidence limit on a constant
# failure rate at confidence CL is -ln(1-CL)/T ('rule of three' at 95 %).
CL = 0.95
T = L("ch04.cpo.meta_1m_hours")
lam_ub = -math.log(1 - CL) / T
r.emit("cl", 100 * CL, "%", 2)
r.emit("meta_lambda_ub_fit", lam_ub * 1e9, "FIT", 3, ["ch04.cpo.meta_1m_hours"])
r.emit("meta_mtbf_lb", 1 / lam_ub, "h", 3, ["ch04.cpo.meta_1m_hours"])
r.emit("meta_mtbf_lb_yr", 1 / lam_ub / 8766, "years", 3, ["ch04.cpo.meta_1m_hours"])
T15 = cl.cond("ch04.cpo.meta_15m_hours_5x_mtbf", "CPO_device_hours")
r.emit("alduino_lambda_ub_fit", -math.log(1 - CL) / T15 * 1e9, "FIT", 3, ["ch04.cpo.meta_15m_hours_5x_mtbf"])
# switch-level: expected link events per year for 128 ports at the bound
r.emit("meta_events_yr_ub", lam_ub * 128 * 8766, "per year", 3, ["ch04.cpo.meta_1m_hours"])

# ------------------------------------------------ NVIDIA claims (tier C): what baselines they imply
qx = L("ch04.cpo.nvidia_quantumx_ports") * cl.cond("ch04.cpo.nvidia_quantumx_ports", "port_rate_Gbps") / 1e3
r.emit("qx_cap", qx, "Tb/s", 4, ["ch04.cpo.nvidia_quantumx_ports"])
for tag, rid in (("3p5", "ch04.cpo.nvidia_3p5x"), ("5", "ch04.cpo.nvidia_5x_2026")):
    w = L("ch04.pw.broadcom_pluggable_14w_800g") / L(rid)
    r.emit(f"nv_{tag}_w", w, "W", 3, [rid, "ch04.pw.broadcom_pluggable_14w_800g"])
    r.emit(f"nv_{tag}_eb", cl.pj_per_bit(w, 800), "pJ/bit", 3, [rid, "ch04.pw.broadcom_pluggable_14w_800g"])
    r.emit(f"nv_{tag}_pct", 100 * (1 - 1 / L(rid)), "%", 3, [rid])
dl = cl.cond("ch04.cpo.nvidia_electrical_loss", "pluggable_dB") - L("ch04.cpo.nvidia_electrical_loss")
r.emit("nv_loss_delta", dl, "dB", 2, ["ch04.cpo.nvidia_electrical_loss"])
r.emit("nv_loss_amp", 10 ** (dl / 20), "1", 2, ["ch04.cpo.nvidia_electrical_loss"])

# ------------------------------------------------ figure (tier A/B inputs only)
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.8, 4.6))
x = np.arange(len(cases))
w = 0.36
for j, (sk, lab) in enumerate((("51", "51.2T switch (64 x 800G)"), ("102", "102.4T switch (128 x 800G)"))):
    vals = [power[(k, sk)] for k, *_ in cases]
    ax.bar(x + (j - 0.5) * w, vals, width=w, color=cl.COLORS[j * 2], label=lab, edgecolor="none")
ax.set_xticks(x)
ax.set_xticklabels([c[1] for c in cases], fontsize=8.2)
ax.set_ylabel("Optics power per switch (W)")
ax.legend(fontsize=8.5, loc="upper right")
ax.set_title("Computed: switch optics power = (capacity / 800G) x power per 800G", fontsize=10)
cl.savefig(fig, "switch_optics")

r.save()
