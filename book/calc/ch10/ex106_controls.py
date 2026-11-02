"""Worked example 10.6: reading the instruments quantitatively.

Part A: ECCN 3A090 metrics (TPP = 2 x MacTOPS x bit length; PD = TPP / die
area) from the Feb 2025 restatement (bis_fr_2025_02655): reproduce the rule's
own worked equivalences, and derive the die-area boundary of 3A090.a.2.
Part B: dates and intervals of the US and Chinese instruments, as of the
retrieval date of the ledger. Draws Figure 10.5 (timeline).
Part C: Section 301 duty arithmetic for two HTS lines.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import datetime as dt
import ch10lib as cl

r = Results()

# ---------------- A. 3A090 ----------------
T1, T2, EX = "ch10.ctl.3a090a_tpp_4800", "ch10.ctl.3a090a2_tpp_1600_pd_5p92", "ch10.ctl.3a090_example_fp16"
tpp_a1 = L(T1)
tpp_a2, pd_a2 = L(T2, "lo"), L(T2, "hi")


def tpp(mactops, bits):
    return 2.0 * mactops * bits


# The rule's equivalences: 2 x 300 MacTOPS at 8 bits, and 300 dense TFLOPS at 16 bits.
mac_int8 = cl.qnum(EX, r"2 × ([0-9]+) ‘MacTOPS’")
assert tpp(mac_int8, 8) == tpp_a1
tflops16 = L(EX)
mac_fp16 = tflops16 / 2.0                     # one multiply-accumulate = two floating-point operations
assert tpp(mac_fp16, 16) == tpp_a1
r.emit("tpp_a1", tpp_a1, "1", 4, [T1])
r.emit("tpp_a2", tpp_a2, "1", 4, [T2])
r.emit("pd_a2", pd_a2, "1", 3, [T2])
r.emit("mac_int8", mac_int8, "MacTOPS", 3, [EX])
r.emit("tflops16", tflops16, "TFLOPS", 3, [EX])
r.emit("mac_fp16", mac_fp16, "MacTOPS", 3, [EX])
# FP8 dense rate that reaches the a.1 threshold
mac8_at_a1 = tpp_a1 / (2 * 8)
r.emit("tflops8_at_a1", 2 * mac8_at_a1, "TFLOPS", 3, [T1])
# Die-area boundary for a.2: PD >= 5.92  <=>  A_die <= TPP / 5.92
r.emit("adie_at_1600", tpp_a2 / pd_a2, "mm²", 3, [T2])
r.emit("adie_at_4800", tpp_a1 / pd_a2, "mm²", 3, [T1, T2])

# ---------------- B. dates ----------------
asof = cl.retrieved("ch10.ctl.affiliates_rule_stayed")
d = {
    "aff_eff": dt.date.fromisoformat(str(cl.cond("ch10.ctl.affiliates_rule_50pct", "effective"))),
    "aff_stay_end": cl.date("ch10.ctl.affiliates_rule_stayed"),
    "aid_compl": cl.date("ch10.ctl.ai_diffusion_compliance"),
    "aid_resc": cl.date("ch10.ctl.ai_diffusion_rescission"),
    "m70_end": cl.date("ch10.ctl.mofcom2025_70_suspension"),
    "m72_end": cl.date("ch10.ctl.mofcom2025_72_suspend46"),
    "m46": cl.date("ch10.ctl.mofcom2024_46_us_ban"),
    "m23_eff": cl.date("ch10.ctl.mofcom2023_23_effective"),
    "m10": cl.date("ch10.ctl.mofcom2025_10_inp"),
    "oct22": cl.date("ch10.ctl.oct2022_ifr_effective"),
    "oct23": cl.date("ch10.ctl.oct2023_acs_effective"),
    "dec24": cl.date("ch10.ctl.dec2024_hbm_ifr_effective"),
    "fh": cl.date("ch10.ctl.el_2020_fiberhome"),
    "h1260": cl.date("ch10.ctl.dod1260h_innolight"),
    "s5548": cl.date("ch10.ctl.s5548_introduced"),
}
# Dates stated in source records (venue strings, notes) rather than in a record value:
D_M70_START = dt.date(2025, 11, 7)      # mofcom_gac_2025_70: announcement date (= 'from today')
D_M72_START = dt.date(2025, 11, 9)      # mofcom_2025_72: announcement date (= 'from today')
D_M23_PUB = dt.date(2023, 7, 3)         # mofcom_gac_2023_23: announcement date
D_EL2021 = dt.date(2021, 12, 17)        # bis_entity_list_2021_12_17 (86 FR 71557)
D_STAY_PUB = dt.date(2025, 11, 12)      # bis_fr_2025_19846 (90 FR 50857) publication
D_AID_EFF = dt.date(2025, 1, 13)        # ch10.ctl.ai_diffusion_compliance claim text
D_301_SEMI = dt.date.fromisoformat(str(cl.cond("ch10.ctl.s301_semis_50pct", "effective")))
D_301_NOTICE = dt.date(2024, 9, 18)     # ustr_fr_2024_21217 (89 FR 76581) publication
D_EL_DEC24 = dt.date(2024, 12, 5)       # bis_fr_2024_28267 (89 FR 96830) publication
D_PERMIT = cl.date("ch10.inp.axt_inp_permit_first")
D_M18 = dt.date.fromisoformat(str(cl.cond("ch10.ctl.mofcom2025_18_rare_earths", "date")))
assert "effective 13 Jan 2025" in str(cl.rec("ch10.ctl.ai_diffusion_compliance")["claim"])

days = lambda a, b: (b - a).days  # noqa: E731
r.emit("asof_to_aff_end", days(asof, d["aff_stay_end"]), "days", 2, ["ch10.ctl.affiliates_rule_stayed"])
r.emit("asof_to_m70_end", days(asof, d["m70_end"]), "days", 2, ["ch10.ctl.mofcom2025_70_suspension"])
r.emit("asof_to_m72_end", days(asof, d["m72_end"]), "days", 2, ["ch10.ctl.mofcom2025_72_suspend46"])
r.emit("m72_len", days(D_M72_START, d["m72_end"]), "days", 3, ["ch10.ctl.mofcom2025_72_suspend46"])
r.emit("m70_len", days(D_M70_START, d["m70_end"]), "days", 3, ["ch10.ctl.mofcom2025_70_suspension"])
r.emit("aid_gap", days(d["aid_resc"], d["aid_compl"]), "days", 1,
       ["ch10.ctl.ai_diffusion_rescission", "ch10.ctl.ai_diffusion_compliance"])
r.emit("aff_in_force_to_stay_pub", days(d["aff_eff"], D_STAY_PUB), "days", 2, ["ch10.ctl.affiliates_rule_50pct"])
r.emit("m23_notice", days(D_M23_PUB, d["m23_eff"]), "days", 2, ["ch10.ctl.mofcom2023_23_effective"])
r.emit("m46_to_m72_len", days(d["m46"], D_M72_START), "days", 3, ["ch10.ctl.mofcom2024_46_us_ban"])
r.emit("s5548_years", L("ch10.ctl.s5548_transition"), "years", 1, ["ch10.ctl.s5548_transition"])
r.emit("asof_year", asof.year, "1", 4)

# ---------------- C. Section 301 arithmetic ----------------
S_TX, S_SEMI = "ch10.ctl.s301_transceiver_7p5pct", "ch10.ctl.s301_semis_50pct"
ASSUMPTION_CUSTOMS_VALUE = 1000.0      # USD, illustrative customs value of one shipment
v = ASSUMPTION_CUSTOMS_VALUE
r.emit("cv", v, "USD", 4)
r.emit("duty_tx", v * L(S_TX) / 100, "USD", 3, [S_TX])
r.emit("duty_pd", v * L(S_SEMI) / 100, "USD", 3, [S_SEMI])
r.emit("duty_ratio", L(S_SEMI) / L(S_TX), "1", 3, [S_TX, S_SEMI])
r.save()

# ---------------- Figure 10.5: timeline ----------------
plt = cl.setup_mpl()
import matplotlib.dates as mdates  # noqa: E402

us = [  # (date, label, kind)  kind: rule | list | bill | notice
    (dt.date(2019, 5, 16), "Huawei on Entity List\n(84 FR 22963, May 2019)", "list"),
    (d["fh"], "FiberHome group listed\n85 FR 34503", "list"),
    (D_EL2021, "Hengtong, ZTT Sub., HMN\n86 FR 71557", "list"),
    (d["oct22"], "Adv. computing/SME IFR\n87 FR 62186", "rule"),
    (d["oct23"], "3A090 TPP rule\n88 FR 73458", "rule"),
    (D_301_SEMI, "Sec. 301: 8541/8542\nto 50% (89 FR 76581)", "notice"),
    (d["dec24"], "HBM/FDP rule 89 FR 96790;\n140 entities 89 FR 96830", "rule"),
    (D_AID_EFF, "AI Diffusion IFR\n90 FR 4544", "rule"),
    (d["aid_resc"], "Rescission announced\n(press release)", "notice"),
    (d["aff_eff"], "Affiliates (50%) rule\n90 FR 47201", "rule"),
    (d["h1260"], "DoD 1260H: Innolight\n91 FR 35189", "list"),
    (d["s5548"], "S. 5548 introduced\n(bill, not law)", "bill"),
]
cn = [
    (d["m23_eff"], "2023 No. 23 in force:\nGa, Ge (incl. GaAs, InGaAs)", "rule"),
    (d["m46"], "2024 No. 46: no Ga/Ge/Sb/\nsuperhard licences to US", "rule"),
    (d["m10"], "2025 No. 10: InP,\nTMIn, TEIn, 3E004", "rule"),
    (D_M18, "2025 No. 18: seven\nrare earths", "rule"),
    (D_PERMIT, "First InP export permit\n(AXT/Tongmei 10-K)", "notice"),
    (D_M70_START, "2025 No. 70 suspends\nNos. 55-58, 61, 62", "rule"),
    (D_M72_START, "2025 No. 72 suspends\nArt. 2 of No. 46", "rule"),
]
mk = {"rule": "o", "list": "s", "bill": "D", "notice": "^"}
ev = [(t, lab.replace("\n", " "), kind, "US") for t, lab, kind in us] + \
     [(t, lab.replace("\n", " "), kind, "CN") for t, lab, kind in cn]
ev.sort(key=lambda e: e[0])
col = {"US": cl.COLORS[0], "CN": cl.COLORS[1]}
fig, ax = plt.subplots(figsize=(12.0, 7.6))
n = len(ev)
split = dt.date(2024, 1, 1)
for i, (t, lab, kind, side) in enumerate(ev):
    y = n - i
    c = col[side]
    ax.plot([t], [y], marker=mk[kind], color=c, ms=7, mfc=c if kind != "bill" else "none", ls="none")
    if t < split:
        ax.text(t + dt.timedelta(days=45), y, lab, va="center", ha="left", fontsize=8.6, color=c)
    else:
        ax.text(t - dt.timedelta(days=45), y, lab, va="center", ha="right", fontsize=8.6, color=c)
# Suspension intervals, drawn on the rows of the instruments that created them
y_aff = n - [i for i, e in enumerate(ev) if e[1].startswith("Affiliates")][0]
y_72 = n - [i for i, e in enumerate(ev) if e[1].startswith("2025 No. 72")][0]
y_70 = n - [i for i, e in enumerate(ev) if e[1].startswith("2025 No. 70")][0]
ax.plot([D_STAY_PUB, d["aff_stay_end"]], [y_aff, y_aff], color=cl.COLORS[0], lw=5, alpha=0.35, solid_capstyle="butt")
ax.plot([D_M70_START, d["m70_end"]], [y_70, y_70], color=cl.COLORS[1], lw=5, alpha=0.35, solid_capstyle="butt")
ax.plot([D_M72_START, d["m72_end"]], [y_72, y_72], color=cl.COLORS[1], lw=5, alpha=0.35, solid_capstyle="butt")
ax.axvline(asof, color=cl.GRAY, ls=":", lw=1.2)
ax.text(asof, n + 1.0, "ledger retrieval", ha="center", va="bottom", fontsize=8.5, color=cl.GRAY)
ax.set_ylim(0.3, n + 1.8)
ax.set_xlim(dt.date(2019, 1, 1), dt.date(2027, 3, 1))
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.grid(axis="y", visible=False)
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
handles = [Line2D([], [], marker=mk[k], color=cl.GRAY, ls="none", mfc=cl.GRAY if k != "bill" else "none", label=lab)
           for k, lab in (("rule", "regulation or announcement"), ("list", "listing"),
                          ("notice", "notice, press release or company event"), ("bill", "bill (not law)"))]
handles += [Patch(color=cl.COLORS[0], label="United States"), Patch(color=cl.COLORS[1], label="China"),
            Patch(color=cl.GRAY, alpha=0.35, label="stay or suspension period")]
ax.legend(handles=handles, loc="upper left", bbox_to_anchor=(0.0, -0.05), ncol=4, fontsize=8.5)
cl.savefig(fig, "controls_timeline")
