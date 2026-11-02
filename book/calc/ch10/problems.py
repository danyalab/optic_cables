"""Chapter 10 problems: computed answers.

Inputs marked HYPOTHETICAL are problem data, not facts about any market or
product; they are stated as such in the problem text.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import ch10lib as cl

r = Results()
OUT = pathlib.Path(__file__).resolve().parent / "out"


def calc(script, name):
    return json.loads((OUT / f"{script}.json").read_text(encoding="utf-8"))[name]["value"]


T = L("ch10.chain.hhi_highly_concentrated")

# P1: HHI of a hypothetical four-firm tier, and the change from merging the two smallest
HYPOTHETICAL_SHARES = [40.0, 30.0, 20.0, 10.0]
s = HYPOTHETICAL_SHARES
hhi = sum(x * x for x in s)
d_merge = 2 * s[2] * s[3]
hhi_after = sum(x * x for x in s[:2]) + (s[2] + s[3]) ** 2
assert math.isclose(hhi_after - hhi, d_merge)
r.emit("p1_hhi", hhi, "1", 4, ["ch10.chain.hhi_highly_concentrated"])
r.emit("p1_neq", 1e4 / hhi, "firms", 3)
r.emit("p1_dmerge", d_merge, "1", 3, ["ch10.chain.hhi_significant_change"])
r.emit("p1_after", hhi_after, "1", 4)

# P2: what a published CR_4 alone guarantees
HYPOTHETICAL_CR4 = 80.0
r.emit("p2_cr4", HYPOTHETICAL_CR4, "%", 2)
r.emit("p2_hhi_min", HYPOTHETICAL_CR4 ** 2 / 4, "1", 4, ["ch10.chain.hhi_highly_concentrated"])
r.emit("p2_cr4_needed", 2 * math.sqrt(T), "%", 3, ["ch10.chain.hhi_highly_concentrated"])

# P3: Innolight 2025 revenue increment by region
INNO, INOS = "ch10.chain.innolight_2025_revenue", "ch10.chain.innolight_2025_overseas_share"
rev25 = L(INNO)
rev24 = cl.qnum(INNO, r"38,239,935,640\.67 \| ([0-9,.]+)") / 1e6
os25 = cl.qnum(INOS, r"境外 \| ([0-9,.]+)") / 1e6
os24 = cl.qnum(INOS, r"90\.58% \| ([0-9,.]+)") / 1e6
dom25, dom24 = rev25 - os25, rev24 - os24
r.emit("p3_dom25", dom25 / 1e3, "CNY bn", 3, [INNO, INOS])
r.emit("p3_dom24", dom24 / 1e3, "CNY bn", 3, [INNO, INOS])
r.emit("p3_dom_growth_pct", 100 * (dom25 / dom24 - 1), "%", 3, [INNO, INOS])
r.emit("p3_os_growth_pct", 100 * (os25 / os24 - 1), "%", 4, [INOS])
r.emit("p3_os_frac_incr_pct", 100 * (os25 - os24) / (rev25 - rev24), "%", 3, [INNO, INOS])

# P4: production minus sales (units) as a fraction of sales
for k, rid in (("inno", "ch10.chain.innolight_2025_units_sold"), ("eop", "ch10.chain.eoptolink_2025_units_sold")):
    prod = float(cl.cond(rid, "production_million_units"))
    sold = L(rid)
    r.emit(f"p4_{k}_gap", prod - sold, "million units", 3, [rid])
    r.emit(f"p4_{k}_gap_pct", 100 * (prod - sold) / sold, "%", 2, [rid])

# P5: Yuanjie data-center ASP, 2024 vs 2025
YDC, YU = "ch10.inp.yuanjie_2025_dc_revenue", "ch10.inp.yuanjie_2025_dc_units"
g_rev = cl.qnum(YDC, r"上升 ([0-9.]+)%")
g_units = cl.qnum(YU, r"738\.04 \| ([0-9.]+)")          # sales-volume growth column
asp25 = L(YDC) / L(YU)
asp24 = (L(YDC) / (1 + g_rev / 100)) / (L(YU) / (1 + g_units / 100))
r.emit("p5_g_units_pct", g_units, "%", 4, [YU])
r.emit("p5_asp25", asp25, "CNY/chip", 3, [YDC, YU])
r.emit("p5_asp24", asp24, "CNY/chip", 3, [YDC, YU])
r.emit("p5_asp_change_pct", 100 * (asp25 / asp24 - 1), "%", 2, [YDC, YU])
r.emit("p5_dc24", L(YDC) / (1 + g_rev / 100), "CNY million", 3, [YDC])

# P6: classify three hypothetical accelerators under ECCN 3A090.a
TPP1, (TPP2, PD2) = L("ch10.ctl.3a090a_tpp_4800"), (L("ch10.ctl.3a090a2_tpp_1600_pd_5p92", "lo"),
                                                    L("ch10.ctl.3a090a2_tpp_1600_pd_5p92", "hi"))
HYPOTHETICAL_CHIPS = {"A": (500.0, 8, 800.0), "B": (110.0, 8, 280.0), "C": (110.0, 8, 320.0)}  # MacTOPS, bits, mm^2
cls = {}
for name, (mac, bits, area) in HYPOTHETICAL_CHIPS.items():
    tpp = 2 * mac * bits
    pd = tpp / area
    a1 = tpp >= TPP1
    a2 = (tpp >= TPP2) and (pd >= PD2)
    cls[name] = "a.1" if a1 else ("a.2" if a2 else "neither")
    r.emit(f"p6_{name}_tpp", tpp, "1", 4, ["ch10.ctl.3a090a_tpp_4800"])
    r.emit(f"p6_{name}_pd", pd, "1/mm²", 3, ["ch10.ctl.3a090a2_tpp_1600_pd_5p92"])
assert cls == {"A": "a.1", "B": "a.2", "C": "neither"}
r.emit("p6_C_area_max", 2 * 110.0 * 8 / PD2, "mm²", 3, ["ch10.ctl.3a090a2_tpp_1600_pd_5p92"])

# P7: dates
r.emit("p7_m72_len", calc("ex106_controls", "m72_len"), "days", 3, ["ch10.ctl.mofcom2025_72_suspend46"])
r.emit("p7_aid_gap", calc("ex106_controls", "aid_gap"), "days", 1,
       ["ch10.ctl.ai_diffusion_rescission", "ch10.ctl.ai_diffusion_compliance"])
r.emit("p7_m46_active", calc("ex106_controls", "m46_to_m72_len"), "days", 3, ["ch10.ctl.mofcom2024_46_us_ban"])

# P8: Section 301 duty on a hypothetical USD 1,000 shipment, two HTS lines
r.emit("p8_tx", calc("ex106_controls", "duty_tx"), "USD", 3, ["ch10.ctl.s301_transceiver_7p5pct"])
r.emit("p8_pd", calc("ex106_controls", "duty_pd"), "USD", 3, ["ch10.ctl.s301_semis_50pct"])
r.emit("p8_diff", calc("ex106_controls", "duty_pd") - calc("ex106_controls", "duty_tx"), "USD", 3,
       ["ch10.ctl.s301_transceiver_7p5pct", "ch10.ctl.s301_semis_50pct"])

# P9: BOM exposure sensitivity (assumptions of ex104b)
c_laser = calc("ex104b_bom", "c_laser_pct") / 100
m_laser = calc("ex104b_bom", "m_laser_pct") / 100
X = calc("ex104b_bom", "X_ref_pct") / 100
TARGET_DROP = 0.05                 # problem data: lower X by five percentage points through lasers alone
dm = TARGET_DROP / c_laser
assert dm <= m_laser
r.emit("p9_X", 100 * X, "%", 3)
r.emit("p9_dm", 100 * dm, "pp", 3)
r.emit("p9_m_new", 100 * (m_laser - dm), "%", 2)

# P10: from an optics-only multiple to a switch-level multiple (Amdahl form)
EV = "ch04.cpo.evans_switch_power"
tot = L(EV, "hi")
opt_d, opt_c = float(cl.cond(EV, "optics_DSP_W")), float(cl.cond(EV, "optics_CPO_W"))
ser_d, ser_c = float(cl.cond(EV, "SerDes_DSP_W")), float(cl.cond(EV, "SerDes_CPO_W"))
f = opt_d / tot
N = opt_d / opt_c
n_sw_opt = 1 / (1 - f * (1 - 1 / N))
f2 = (opt_d + ser_d) / tot
N2 = (opt_d + ser_d) / (opt_c + ser_c)
n_sw_opt_ser = 1 / (1 - f2 * (1 - 1 / N2))
n_sw_rep = tot / L(EV, "lo")
assert n_sw_opt < n_sw_opt_ser < n_sw_rep
r.emit("p10_f_pct", 100 * f, "%", 3, [EV])
r.emit("p10_N", N, "x", 3, [EV])
r.emit("p10_nsw_opt", n_sw_opt, "x", 3, [EV])
r.emit("p10_f2_pct", 100 * f2, "%", 3, [EV])
r.emit("p10_nsw_opt_ser", n_sw_opt_ser, "x", 3, [EV])
r.emit("p10_nsw_rep", n_sw_rep, "x", 3, [EV])
r.emit("p10_resid_w", (tot - L(EV, "lo")) - ((opt_d + ser_d) - (opt_c + ser_c)), "W", 3, [EV])
r.save()
