"""Section 4.2: generations, energy per bit at each step, and the timeline figure.

Dates come from ledger records only. Marker shape encodes the evidence tier:
filled circle = tier-A standard approval or IA; open square = tier-B MSA, OIF list
or IEEE task-force document; filled triangle = tier-B vendor annual report;
cross = tier-C press or news (shown because they are discussed in contested boxes).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch04lib as cl

r = Results()


def date_of(rid, key=None):
    v = cl.cond(rid, key) if key else cl.rec(rid)["value"]
    return cl.year_frac(v)


# ------------------------------------------------ energy per bit of shipping modules
mods = [
    # name, record, aggregate Gb/s, electrical lanes x rate
    ("dr4_qdd", "ch04.pmd.400g_dr4_power_qdd", 400),
    ("dr4_q112", "ch04.pmd.400g_dr4_power_qsfp112", 400),
    ("m800_2xdr4", "ch04.pmd.800g_2xdr4_power", 800),
    ("m1600_dr8", "ch04.pmd.1p6t_dr8_power", 1600),
]
eb = {}
for name, rid, rate in mods:
    eb[name] = cl.pj_per_bit(L(rid), rate)
    r.emit(f"eb_{name}", eb[name], "pJ/bit", 3, [rid])
r.emit("eb_m800_typ", cl.pj_per_bit(cl.cond("ch04.pmd.800g_2xdr4_power", "typ_W"), 800), "pJ/bit", 3,
       ["ch04.pmd.800g_2xdr4_power"])
# QSFP-DD (8 x 50G electrical) -> QSFP112 (4 x 100G electrical) for the same 400G-DR4 optics
d = L("ch04.pmd.400g_dr4_power_qdd") - L("ch04.pmd.400g_dr4_power_qsfp112")
r.emit("dr4_saving_w", d, "W", 2, ["ch04.pmd.400g_dr4_power_qdd", "ch04.pmd.400g_dr4_power_qsfp112"])
r.emit("dr4_saving_pct", 100 * d / L("ch04.pmd.400g_dr4_power_qdd"), "%", 2,
       ["ch04.pmd.400g_dr4_power_qdd", "ch04.pmd.400g_dr4_power_qsfp112"])
# 800G (100G lanes) -> 1.6T (200G lanes): doubling the lane rate at fixed lane count
r.emit("eb_ratio_1600_800", eb["m1600_dr8"] / eb["m800_2xdr4"], "1", 3,
       ["ch04.pmd.1p6t_dr8_power", "ch04.pmd.800g_2xdr4_power"])
r.emit("p_ratio_1600_800", L("ch04.pmd.1p6t_dr8_power") / L("ch04.pmd.800g_2xdr4_power"), "1", 3,
       ["ch04.pmd.1p6t_dr8_power", "ch04.pmd.800g_2xdr4_power"])
# each lane-rate doubling across the full sequence 400G(QSFP-DD) -> 1.6T: average E_b factor per doubling
import math
f = (eb["m1600_dr8"] / eb["dr4_qdd"]) ** (1 / 2)
r.emit("eb_factor_per_doubling", f, "1", 3, ["ch04.pmd.1p6t_dr8_power", "ch04.pmd.400g_dr4_power_qdd"])
assert eb["dr4_qdd"] > eb["dr4_q112"] > eb["m800_2xdr4"] > eb["m1600_dr8"]

# ------------------------------------------------ standards cadence
bs_par = cl.year_frac(cl.cond("ch04.std.8023bs_approval", "PAR_approval"))
bs = date_of("ch04.std.8023bs_approval")
df_par = cl.year_frac(cl.cond("ch04.std.8023df_approval_sa", "PAR_approval"))
df = date_of("ch04.std.8023df_approval_sa")
ck_par = cl.year_frac(cl.cond("ch04.std.8023ck_approval", "PAR_approval"))
ck = date_of("ch04.std.8023ck_approval")
dv_par = date_of("ch04.std.8023dv_par")
dv_rev = cl.year_frac(cl.cond("ch04.std.8023dv_par", "projected_RevCom"))
r.emit("bs_years", bs - bs_par, "years", 2, ["ch04.std.8023bs_approval"])
r.emit("ck_years", ck - ck_par, "years", 2, ["ch04.std.8023ck_approval"])
r.emit("df_years", df - df_par, "years", 2, ["ch04.std.8023df_approval_sa"])
r.emit("dv_years", dv_rev - dv_par, "years", 2, ["ch04.std.8023dv_par"])
# Vendor lead over the standard
inno800 = date_of("ch04.gen.innolight_800g_launch")
r.emit("lead_800g", df - inno800, "years", 2, ["ch04.std.8023df_approval_sa", "ch04.gen.innolight_800g_launch"])
dj_cond = cl.year_frac(str(cl.rec("ch04.std.8023dj_status")["value"]).split(",")[-1].strip())
ship16 = date_of("ch04.gen.innolight_1p6t_ship_2025q2")
r.emit("lead_1600g", dj_cond - ship16, "years", 2, ["ch04.std.8023dj_status", "ch04.gen.innolight_1p6t_ship_2025q2"])
eo400 = date_of("ch04.gen.eoptolink_1p6t_dr4_400g", "date")
r.emit("lead_400gl", dv_rev - eo400, "years", 2, ["ch04.std.8023dv_par", "ch04.gen.eoptolink_1p6t_dr4_400g"])
assert inno800 < df and ship16 < dj_cond and eo400 < dv_par

# ------------------------------------------------ units shipped (Chinese vendors' annual reports)
inn25 = L("ch04.gen.innolight_units_2025") / 100      # 10^4 units -> millions
inn24 = cl.cond("ch04.gen.innolight_units_2025", "2024_units_10k") / 100
eo25 = L("ch04.gen.eoptolink_units_2025") / 100
eo24 = cl.cond("ch04.gen.eoptolink_units_2025", "2024_sales_10k") / 100
r.emit("inno_units_2025", inn25, "million", 4, ["ch04.gen.innolight_units_2025"])
r.emit("inno_units_2024", inn24, "million", 4, ["ch04.gen.innolight_units_2025"])
r.emit("inno_growth", 100 * (inn25 / inn24 - 1), "%", 3, ["ch04.gen.innolight_units_2025"])
r.emit("eo_units_2025", eo25, "million", 4, ["ch04.gen.eoptolink_units_2025"])
r.emit("eo_units_2024", eo24, "million", 3, ["ch04.gen.eoptolink_units_2025"])
r.emit("eo_growth", 100 * (eo25 / eo24 - 1), "%", 3, ["ch04.gen.eoptolink_units_2025"])
rev = cl.cond("ch04.gen.innolight_units_2025", "revenue_RMB")
r.emit("inno_rev_per_unit", rev / (inn25 * 1e6), "RMB", 3, ["ch04.gen.innolight_units_2025"])

# ------------------------------------------------ timeline figure
A, B_DOC, B_VEN, C = "A", "Bdoc", "Bven", "C"
ROWS = {"400G": 0, "800G": 1, "1.6T": 2, "400G lane": 3, "Coherent": 4}
events = [
    # row, date, label, tier-class, record
    ("400G", cl.cond("ch04.ff.qsfpdd_msa_first_release", "note") and "2016-09-19", "QSFP-DD MSA 1.0", B_DOC, "ch04.ff.qsfpdd_msa_first_release"),
    ("400G", cl.cond("ch04.ff.osfp_rev10_19w8", "date"), "OSFP 1.0", B_DOC, "ch04.ff.osfp_rev10_19w8"),
    ("400G", cl.rec("ch04.std.8023bs_approval")["value"], "802.3bs", A, "ch04.std.8023bs_approval"),
    ("400G", cl.rec("ch04.std.8023cd_approval")["value"], "802.3cd", A, "ch04.std.8023cd_approval"),
    ("400G", cl.rec("ch04.std.8023cu_approval")["value"], "802.3cu", A, "ch04.std.8023cu_approval"),
    ("800G", cl.rec("ch04.gen.innolight_800g_launch")["value"], "Innolight 800G launch", B_VEN, "ch04.gen.innolight_800g_launch"),
    ("800G", cl.cond("ch04.ff.qsfpdd_rev6_25w", "date"), "QSFP-DD800", B_DOC, "ch04.ff.qsfpdd_rev6_25w"),
    ("800G", cl.rec("ch04.el.cei50_date")["value"], "CEI-5.0 (112G)", A, "ch04.el.cei50_date"),
    ("800G", cl.rec("ch04.std.8023ck_approval")["value"], "802.3ck", A, "ch04.std.8023ck_approval"),
    ("800G", cl.rec("ch04.std.8023df_approval_sa")["value"], "802.3df", A, "ch04.std.8023df_approval_sa"),
    ("800G", cl.rec("ch04.lpo.spec_rev1_date")["value"], "LPO MSA 1.0", B_DOC, "ch04.lpo.spec_rev1_date"),
    ("1.6T", cl.cond("ch04.gen.innolight_1p6t_demo_2023", "date"), "1.6T demo", C, "ch04.gen.innolight_1p6t_demo_2023"),
    ("1.6T", cl.cond("ch04.ff.qsfpdd1600_40w", "date"), "QSFP-DD1600", B_DOC, "ch04.ff.qsfpdd1600_40w"),
    ("1.6T", cl.cond("ch04.ff.osfp1600_42w9", "date"), "OSFP1600", B_DOC, "ch04.ff.osfp1600_42w9"),
    ("1.6T", cl.rec("ch04.gen.innolight_1p6t_ship_2025q2")["value"], "1.6T first shipments", C, "ch04.gen.innolight_1p6t_ship_2025q2"),
    ("1.6T", "2026-10-06", "802.3dj to RevCom", B_DOC, "ch04.std.8023dj_status"),
    ("400G lane", cl.rec("ch04.std.400gpl_sg_chartered")["value"], "400G/lane SG", B_DOC, "ch04.std.400gpl_sg_chartered"),
    ("400G lane", cl.cond("ch04.gen.eoptolink_1p6t_dr4_400g", "date"), "1.6T DR4 (400G/lane)", B_VEN, "ch04.gen.eoptolink_1p6t_dr4_400g"),
    ("400G lane", cl.rec("ch04.std.8023dv_par")["value"], "P802.3dv PAR", B_DOC, "ch04.std.8023dv_par"),
    ("Coherent", cl.cond("ch04.coh.400zr_reach", "date"), "400ZR", A, "ch04.coh.400zr_reach"),
    ("Coherent", cl.cond("ch04.coh.800zr_reach", "date"), "800ZR", A, "ch04.coh.800zr_reach"),
    ("Coherent", cl.cond("ch04.coh.800lr_baud", "date"), "800LR", A, "ch04.coh.800lr_baud"),
    ("Coherent", cl.rec("ch04.coh.1600zr_ia")["value"], "1600ZR", A, "ch04.coh.1600zr_ia"),
]
assert "2016-09-19" == str(cl.rec("ch04.ff.qsfpdd_msa_first_release")["value"])
assert "2026-10-06" in str(cl.rec("ch04.std.8023dj_status")["value"])
proj = [("400G lane", cl.cond("ch04.std.8023dv_par", "projected_RevCom"), "802.3dv RevCom (projected)"),
        ("400G lane", str(int(L("ch04.gen.innolight_3p2t_2028"))), "3.2T ramp (forecast)")]

# label placement (purely cosmetic): alternate above/below for neighbouring events
PLACE = {"OSFP 1.0": ("down", "center"), "QSFP-DD MSA 1.0": ("up", "right"), "802.3bs": ("up", "left"),
         "3.2T ramp (forecast)": ("down", "center"), "802.3cd": ("down", "center"),
         "Innolight 800G launch": ("up", "right"), "QSFP-DD800": ("down", "right"),
         "802.3ck": ("down", "left"), "LPO MSA 1.0": ("down", "center"),
         "QSFP-DD1600": ("down", "center"), "1.6T first shipments": ("down", "left"),
         "400G/lane SG": ("up", "right"), "1.6T DR4 (400G/lane)": ("down", "right"),
         "P802.3dv PAR": ("up", "left"), "802.3dv RevCom (projected)": ("up", "center"),
         "800ZR": ("up", "right"), "800LR": ("down", "center"), "802.3dj to RevCom": ("up", "left"),
         "OSFP1600": ("up", "right")}
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(9.0, 5.4))
style = {A: dict(marker="o", ms=8, color=cl.COLORS[0], mfc=cl.COLORS[0]),
         B_DOC: dict(marker="s", ms=7, color=cl.COLORS[2], mfc="none", mew=1.6),
         B_VEN: dict(marker="^", ms=8, color=cl.COLORS[1], mfc=cl.COLORS[1]),
         C: dict(marker="X", ms=8, color=cl.COLORS[4], mfc=cl.COLORS[4])}
labels = {A: "tier A: IEEE standard approval / OIF IA", B_DOC: "tier B: MSA, OIF list, IEEE task-force doc",
          B_VEN: "tier B: vendor annual report", C: "tier C: press / news (contested)"}
seen = set()
row_count = {}
last_x = {}
for row, dt, lab, tier, rid in events:
    x = cl.year_frac(dt)
    y = ROWS[row]
    k = row_count.get(row, 0)
    row_count[row] = k + 1
    ax.plot([x], [y], ls="none", label=None if tier in seen else labels[tier], **style[tier])
    seen.add(tier)
    pos, ha = PLACE.get(lab, ("up", "center"))
    ax.text(x, y + (0.2 if pos == "up" else -0.2), lab, fontsize=7.2, ha=ha,
            va="bottom" if pos == "up" else "top")
for row, dt, lab in proj:
    x = cl.year_frac(dt)
    y = ROWS[row]
    ax.plot([x], [y], ls="none", marker="o", ms=8, mfc="none", color=cl.GRAY, mew=1.2)
    pos, ha = PLACE.get(lab, ("up", "center"))
    ax.text(x, y + (0.2 if pos == "up" else -0.2), lab, fontsize=7.2, ha=ha,
            va="bottom" if pos == "up" else "top")
ax.plot([], [], ls="none", marker="o", ms=8, mfc="none", color=cl.GRAY, mew=1.2, label="projection / forecast")
ax.set_yticks(list(ROWS.values()))
ax.set_yticklabels(list(ROWS.keys()))
ax.set_ylim(-0.6, 4.6)
ax.set_xlim(2016, 2031)
ax.set_xlabel("Year")
ax.legend(fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2)
ax.set_title("Redrawn from ledger dates: standards, MSAs and vendor milestones", fontsize=10)
cl.savefig(fig, "timeline")

r.save()
