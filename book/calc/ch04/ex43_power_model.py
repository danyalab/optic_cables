"""Section 4.3: component-level power model of an 800G and a 1.6T pluggable.

Inputs
* Chang and Yu (IEEE 802.3df contribution, tier B) pie charts: component shares at 70 C
  for a 1.6T (8x200G) DR8/2xFR4 module (<22 W) and an 800G (4x200G) DR4/FR4 module
  (~11-12 W). The share-to-legend mapping is the ledger's (flagged for verification).
* Nagarajan et al. (tier A): DSP about 50 % of module power; DC-DC and distribution
  overhead 10 to 15 %.
* Datasheet maxima for reconciliation (tier B).

Model: E_b,i = s_i P_mod / R_mod for each component i (eq. ch04.eq.energy_per_bit).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import re
import numpy as np
import ch04lib as cl

r = Results()
COMP = ["TEC", "laser", "DSP", "TIA", "MCU", "other"]


def shares(rid):
    txt = str(cl.cond(rid, "other_shares_pct"))
    out = {}
    for name in COMP:
        if name == "DSP":
            continue
        m = re.search(rf"{name}\s+([0-9.]+)", txt)
        out[name] = float(m.group(1))
    out["DSP"] = L(rid)
    tot = sum(out.values())
    assert abs(tot - 100.0) < 0.05, (rid, tot)      # the pie must close
    return {k: v / 100 for k, v in out.items()}


s16 = shares("ch04.pw.1p6t_breakdown_dsp")
s8 = shares("ch04.pw.800g_breakdown_dsp")

# ASSUMPTION: the 1.6T module dissipates exactly its stated bound, 22 W ("<22 W" in the slide title).
P16 = float(re.search(r"<([0-9.]+) W", cl.cond("ch04.pw.1p6t_breakdown_dsp", "module")).group(1))
# ASSUMPTION: the 800G module dissipates the midpoint of the stated "~11-12 W".
lo8, hi8 = [float(x) for x in re.search(r"~([0-9.]+)-([0-9.]+) W", cl.cond("ch04.pw.800g_breakdown_dsp", "module")).groups()]
P8 = 0.5 * (lo8 + hi8)
R16, R8 = 1600.0, 800.0
N16, N8 = 8, 4          # optical lanes of 200 Gb/s (from the record claims "8x200G", "4x200G")
assert "8x200G" in cl.rec("ch04.pw.1p6t_breakdown_dsp")["claim"] and "4x200G" in cl.rec("ch04.pw.800g_breakdown_dsp")["claim"]
I16 = ["ch04.pw.1p6t_breakdown_dsp"]
I8 = ["ch04.pw.800g_breakdown_dsp"]
r.emit("p16", P16, "W", 3, I16)
r.emit("p8", P8, "W", 3, I8)
r.emit("p8_lo", lo8, "W", 3, I8)
r.emit("p8_hi", hi8, "W", 3, I8)
r.emit("eb16", cl.pj_per_bit(P16, R16), "pJ/bit", 3, I16)
r.emit("eb8", cl.pj_per_bit(P8, R8), "pJ/bit", 3, I8)
for tag, sh, P, R, ins in (("16", s16, P16, R16, I16), ("8", s8, P8, R8, I8)):
    for k in COMP:
        r.emit(f"w{tag}_{k}", sh[k] * P, "W", 3, ins)
        r.emit(f"e{tag}_{k}", cl.pj_per_bit(sh[k] * P, R), "pJ/bit", 3, ins)
        r.emit(f"s{tag}_{k}", 100 * sh[k], "%", 3, ins)
    r.emit(f"e{tag}_optics", cl.pj_per_bit((sh["TEC"] + sh["laser"] + sh["TIA"]) * P, R), "pJ/bit", 3, ins)
    r.emit(f"s{tag}_cooled_laser", 100 * (sh["TEC"] + sh["laser"]), "%", 3, ins)

# per-lane view: two-point fit P = P0 + N p_lane through (4 lanes, P8) and (8 lanes, P16)
p_lane = (P16 - P8) / (N16 - N8)
p0 = P8 - N8 * p_lane
r.emit("p_lane", p_lane, "W", 3, I16 + I8)
r.emit("p0", p0, "W", 2, I16 + I8)
r.emit("dsp_per_lane16", s16["DSP"] * P16 / N16, "W", 3, I16)
r.emit("dsp_per_lane8", s8["DSP"] * P8 / N8, "W", 3, I8)
r.emit("laser_per_lane16", s16["laser"] * P16 / N16, "W", 3, I16)
r.emit("tia_per_lane16", s16["TIA"] * P16 / N16 * 1e3, "mW", 3, I16)

# -------------------------------- cross-check with Nagarajan (tier A)
dsp_n = L("ch04.pw.dsp_half_module") / 100
oh_lo, oh_hi = L("ch04.pw.power_overhead", "lo") / 100, L("ch04.pw.power_overhead", "hi") / 100
r.emit("nag_dsp_pct", 100 * dsp_n, "%", 2, ["ch04.pw.dsp_half_module"])
r.emit("dsp16_minus_nag", 100 * (s16["DSP"] - dsp_n), "percentage points", 3, I16 + ["ch04.pw.dsp_half_module"])
r.emit("other16_in_overhead", 1.0 if oh_lo <= s16["other"] <= oh_hi else 0.0, "1", 1, I16 + ["ch04.pw.power_overhead"])
assert oh_lo <= s16["other"] <= oh_hi         # 1.6T 'other' slice lies inside 10-15 % overhead
assert s8["other"] < oh_lo                     # 800G 'other' slice does not: overhead must be distributed
# Nagarajan-style split applied to the 1.6T datasheet maximum
Pds = L("ch04.pmd.1p6t_dr8_power")
oh_mid = 0.5 * (oh_lo + oh_hi)
r.emit("nag_ds_dsp", dsp_n * Pds, "W", 3, ["ch04.pw.dsp_half_module", "ch04.pmd.1p6t_dr8_power"])
r.emit("nag_ds_oh", oh_mid * Pds, "W", 3, ["ch04.pw.power_overhead", "ch04.pmd.1p6t_dr8_power"])
r.emit("nag_ds_rest", (1 - dsp_n - oh_mid) * Pds, "W", 3, ["ch04.pw.dsp_half_module", "ch04.pw.power_overhead", "ch04.pmd.1p6t_dr8_power"])

# -------------------------------- reconciliation with datasheet maxima
r.emit("ds16_eb", cl.pj_per_bit(Pds, R16), "pJ/bit", 3, ["ch04.pmd.1p6t_dr8_power"])
r.emit("ds16_over_model", Pds / P16, "1", 3, ["ch04.pmd.1p6t_dr8_power"] + I16)
r.emit("ds16_minus_model", Pds - P16, "W", 2, ["ch04.pmd.1p6t_dr8_power"] + I16)
r.emit("ds16_frac_osfp1600", 100 * Pds / L("ch04.ff.osfp1600_42w9"), "%", 3, ["ch04.pmd.1p6t_dr8_power", "ch04.ff.osfp1600_42w9"])
ref8 = L("ch04.pw.broadcom_pluggable_14w_800g")
r.emit("ref8_eb", cl.pj_per_bit(ref8, R8), "pJ/bit", 3, ["ch04.pw.broadcom_pluggable_14w_800g"])
ds8 = L("ch04.pmd.800g_2xdr4_power")
r.emit("ds8_eb", cl.pj_per_bit(ds8, R8), "pJ/bit", 3, ["ch04.pmd.800g_2xdr4_power"])
r.emit("ds8_over_model", ds8 / P8, "1", 3, ["ch04.pmd.800g_2xdr4_power"] + I8)
# Under the 200G-lane model, how much of the 100G-lane 800G module is beyond the model
r.emit("ref8_over_model", ref8 / P8, "1", 3, ["ch04.pw.broadcom_pluggable_14w_800g"] + I8)

# -------------------------------- what a '20 % module saving' from a 3 nm DSP implies (tier C claims)
claim = L("ch04.pw.marvell_ara_20pct") / 100
assert claim == L("ch04.pw.eoptolink_3nm_20pct") / 100
r.emit("dsp_cut_needed", 100 * claim / s16["DSP"], "%", 3, I16 + ["ch04.pw.marvell_ara_20pct"])
r.emit("p16_after_20", P16 * (1 - claim), "W", 3, I16 + ["ch04.pw.marvell_ara_20pct"])
sian = L("ch04.pw.sian3_1p6t_sub23w")
r.emit("sian3_eb", cl.pj_per_bit(sian, R16), "pJ/bit", 3, ["ch04.pw.sian3_1p6t_sub23w"])
r.emit("sian3_800_eb", cl.pj_per_bit(cl.cond("ch04.pw.sian3_1p6t_sub23w", "800G_W"), R8), "pJ/bit", 3,
       ["ch04.pw.sian3_1p6t_sub23w"])

# -------------------------------- figure: stacked energy per bit
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.4, 4.6))
labels = ["800G (4x200G)\nmodel", "1.6T (8x200G)\nmodel"]
data = [(s8, P8, R8), (s16, P16, R16)]
x = np.arange(2)
bottom = np.zeros(2)
cols = {"DSP": cl.COLORS[0], "laser": cl.COLORS[1], "TEC": cl.COLORS[5], "TIA": cl.COLORS[2],
        "MCU": cl.COLORS[3], "other": cl.COLORS[6]}
for k in ["DSP", "laser", "TEC", "TIA", "MCU", "other"]:
    vals = np.array([cl.pj_per_bit(sh[k] * P, R) for sh, P, R in data])
    ax.bar(x, vals, bottom=bottom, width=0.5, color=cols[k], label=k, edgecolor="none")
    bottom += vals
marks = [(0, cl.pj_per_bit(ds8, R8), "800G 2xDR4 datasheet max\n(100G lanes)"),
         (0, cl.pj_per_bit(ref8, R8), "Broadcom pluggable reference"),
         (1, cl.pj_per_bit(Pds, R16), "1.6T DR8 datasheet max")]
for xi, v, lab in marks:
    ax.plot([xi - 0.32, xi + 0.32], [v, v], color=cl.GRAY, lw=1.4, ls="--")
    ax.text(xi + 0.34, v, lab, fontsize=8, va="center")
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_xlim(-0.5, 2.3)
ax.set_ylabel("Energy per bit (pJ/bit)")
ax.legend(fontsize=8.5, ncol=6, loc="upper center", bbox_to_anchor=(0.45, -0.14))
ax.set_title("Computed from component shares (Chang and Yu) and datasheet maxima", fontsize=10)
cl.savefig(fig, "power_anatomy")

r.save()
