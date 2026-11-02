"""Worked example 9.4: MIIT access-network statistics, consistency checks and
the 双千兆 targets against outcomes.

All inputs are MIIT bulletin records (2025 values are preliminary) or records
that quote them; assumptions are named ASSUMPTION constants.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch09lib as cl

r = Results()
n = cl.num

# --- cable length: totals and split ------------------------------------------
C25, S25, C24 = "ch09.acc.cable_length_2025", "ch09.acc.cable_split_2025", "ch09.acc.cable_length_2024"
C24X = "ch09.acc.cable_length_2024_exact"
tot25 = n(L(C25))
lh25, lt25, ac25 = n(L(S25)), n(cl.cond(S25, "local_trunk_km")), n(cl.cond(S25, "access_km"))
tot24 = n(L(C24X))
lh24, lt24, ac24 = n(cl.cond(C24, "longhaul_km")), n(cl.cond(C24, "local_trunk_km")), n(cl.cond(C24, "access_km"))
ins = [C25, S25, C24, C24X]
r.emit("tot25_mkm", tot25 / 1e6, "million km", 4, [C25])
r.emit("tot24_mkm", tot24 / 1e6, "million km", 4, [C24X])
r.emit("lh25_mkm", lh25 / 1e6, "million km", 4, [S25])
r.emit("lt25_mkm", lt25 / 1e6, "million km", 4, [S25])
r.emit("ac25_mkm", ac25 / 1e6, "million km", 4, [S25])
r.emit("lh24_mkm", lh24 / 1e6, "million km", 4, [C24])
r.emit("lt24_mkm", lt24 / 1e6, "million km", 4, [C24])
r.emit("ac24_mkm", ac24 / 1e6, "million km", 4, [C24])
r.emit("lh25_pct", 100 * lh25 / tot25, "%", 2, [C25, S25])
r.emit("lt25_pct", 100 * lt25 / tot25, "%", 3, [C25, S25])
r.emit("ac25_pct", 100 * ac25 / tot25, "%", 3, [C25, S25])
r.emit("added25_mkm", n(cl.cond(C25, "added_2025_km")) / 1e6, "million km", 4, [C25])
r.emit("added24_mkm", cl.parse_num(C24X, r"Net increase ([0-9,]+) km") / 1e6, "million km", 4, [C24X])
r.emit("growth25_pct", 100 * (tot25 / tot24 - 1), "%", 2, [C25, C24X])
r.emit("d_lh_kkm", (lh25 - lh24) / 1e3, "thousand km", 2, [S25, C24])
r.emit("d_lt_mkm", (lt25 - lt24) / 1e6, "million km", 3, [S25, C24])
r.emit("d_ac_mkm", (ac25 - ac24) / 1e6, "million km", 2, [S25, C24])
# Consistency: the three components sum to the total (rounding of 万 km)
assert abs((lh25 + lt25 + ac25) - tot25) / tot25 < 1e-3
assert abs((lh24 + lt24 + ac24) - tot24) / tot24 < 1e-3
# and the component changes sum to the stated 2025 addition net of removals
r.emit("d_sum_mkm", ((lh25 - lh24) + (lt25 - lt24) + (ac25 - ac24)) / 1e6, "million km", 3, ins)

# --- ports and users -----------------------------------------------------------
FT, P10, P10b = "ch09.acc.ftth_ports_2025", "ch09.acc.10gpon_ports_2025", "ch09.acc.10gpon_ports_2024"
GU, GUb, FTTR = "ch09.acc.gigabit_users_2025", "ch09.acc.gigabit_users_2024", "ch09.acc.fttr_users_2025"
NFB = "ch09.op.national_fixed_bb_users_2025"
ftth, allp = n(L(FT)), n(cl.cond(FT, "total_ports"))
users = n(L(NFB))
p10, p10b = n(L(P10)), n(L(P10b))
gu, gub = n(L(GU)), n(L(GUb))
r.emit("ftth_b", ftth / 1e9, "billion", 3, [FT])
r.emit("allports_b", allp / 1e9, "billion", 4, [FT])
r.emit("ftth_share_calc", 100 * ftth / allp, "%", 3, [FT])
assert abs(100 * ftth / allp - float(cl.cond(FT, "share_pct"))) < 0.1
r.emit("users_m", users / 1e6, "million", 3, [NFB])
r.emit("ports_per_user", allp / users, "", 3, [FT, NFB])
r.emit("port_util_pct", 100 * users / allp, "%", 3, [FT, NFB])
r.emit("p10_m", p10 / 1e6, "million", 4, [P10])
r.emit("p10b_m", p10b / 1e6, "million", 3, [P10b])
r.emit("p10_add_m", n(cl.cond(P10, "net_add")) / 1e6, "million", 4, [P10])
r.emit("p10_growth_pct", 100 * (p10 / p10b - 1), "%", 3, [P10, P10b])
assert abs((p10 - p10b) - n(cl.cond(P10, "net_add"))) / p10 < 0.01
r.emit("gu_m", gu / 1e6, "million", 3, [GU])
r.emit("gub_m", gub / 1e6, "million", 3, [GUb])
r.emit("gu_growth_pct", 100 * (gu / gub - 1), "%", 3, [GU, GUb])
r.emit("gu_share_calc", 100 * gu / users, "%", 3, [GU, NFB])
assert abs(100 * gu / users - float(cl.cond(GU, "share_pct"))) < 0.3
r.emit("gu_per_p10", gu / p10, "", 3, [GU, P10])
r.emit("ftth_per_p10", ftth / p10, "", 3, [FT, P10])
r.emit("p10_over_ftth_pct", 100 * p10 / ftth, "%", 2, [FT, P10])
# ASSUMPTION: 10 Gb/s nominal downstream line rate of a 10G-PON port (the class name;
# the ITU-T line rate is not in the ledger).
R10G = 10e9
r.emit("r10g", R10G / 1e9, "Gb/s", 2)
r.emit("bw_per_gu", R10G / (gu / p10) / 1e6, "Mb/s", 3, [GU, P10])
r.emit("fttr_m", n(L(FTTR)) / 1e6, "million", 4, [FTTR])
r.emit("fttr_pct", 100 * n(L(FTTR)) / users, "%", 3, [FTTR, NFB])

# --- household bandwidth -------------------------------------------------------
HB = "ch09.acc.household_bw_2025"
HP = "ch09.cmp.cn_fixed_bb_household_penetration"
tot_bw = n(cl.cond(HB, "total_access_bw_Tbps")) * 1e12
hh = n(cl.cond(HP, "household_users"))
r.emit("hh_bw", L(HB), "Mb/s", 4, [HB])
r.emit("tot_bw_ptbps", tot_bw / 1e15, "Pb/s", 3, [HB])
r.emit("bw_per_user", tot_bw / users / 1e6, "Mb/s", 3, [HB, NFB])
r.emit("bw_per_hh", tot_bw / hh / 1e6, "Mb/s", 3, [HB, HP])
r.emit("hh_m", hh / 1e6, "million", 3, [HP])
r.emit("hh_share_pct", 100 * hh / users, "%", 3, [HP, NFB])

# --- 双千兆 targets (end-2023) against end-2024 outcomes ----------------------------
TG, GC = "ch09.acc.dual_gigabit_2023_targets", "ch09.acc.gigabit_cities_2024"
t_p10 = n(L(TG))
t_gu = n(cl.cond(TG, "gigabit_users"))
t_gc = float(cl.cond(TG, "gigabit_cities"))
r.emit("t_p10_m", t_p10 / 1e6, "million", 2, [TG])
r.emit("t_gu_m", t_gu / 1e6, "million", 2, [TG])
r.emit("t_gc", t_gc, "", 3, [TG])
r.emit("gc24", L(GC), "", 3, [GC])
r.emit("x_p10", p10b / t_p10, "", 3, [TG, P10b])
r.emit("x_gu", gub / t_gu, "", 2, [TG, GUb])
r.emit("x_gc", L(GC) / t_gc, "", 3, [TG, GC])
r.emit("gc25_share_pct", 100 * L("ch09.acc.gigabit_cities_2025_share"), "%", 2, ["ch09.acc.gigabit_cities_2025_share"])

# --- F5G reference values ------------------------------------------------------------
r.emit("f5g_otn_vs_cmcc", L("ch09.acc.f5g_otn_40t") / L("ch09.l400.cmcc_capacity_32t"), "", 3,
       ["ch09.acc.f5g_otn_40t", "ch09.l400.cmcc_capacity_32t"])

# --- figure: targets vs outcomes and the cable-length split ---------------------------
plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(8.6, 3.8), gridspec_kw={"width_ratios": [1.1, 1]})
names = ["10G-PON ports", "gigabit users", "gigabit cities"]
ratios = [p10b / t_p10, gub / t_gu, L(GC) / t_gc]
a1.bar(names, ratios, color=[cl.COLORS[0], cl.COLORS[1], cl.COLORS[2]], width=0.6)
a1.axhline(1.0, color=cl.GRAY, ls="--", lw=1)
for i, v in enumerate(ratios):
    a1.text(i, v + 0.1, f"{v:.1f}×", ha="center", fontsize=10)
a1.set_ylabel("end-2024 outcome / end-2023 target")
a1.set_ylim(0, 8)
a1.tick_params(axis="x", labelsize=9)
a1.grid(axis="x", visible=False)
yrs = ["2024", "2025"]
lh = [lh24 / 1e6, lh25 / 1e6]
lt = [lt24 / 1e6, lt25 / 1e6]
ac = [ac24 / 1e6, ac25 / 1e6]
a2.bar(yrs, lh, color=cl.COLORS[3], width=0.5, label="long-haul")
a2.bar(yrs, lt, bottom=lh, color=cl.COLORS[0], width=0.5, label="local-network trunk")
a2.bar(yrs, ac, bottom=[x + y for x, y in zip(lh, lt)], color=cl.COLORS[1], width=0.5, label="access network")
a2.set_ylabel("optical cable line length (million km)")
a2.set_ylim(0, 90)
a2.legend(loc="upper left", fontsize=8.5, ncol=1)
a2.grid(axis="x", visible=False)
fig.tight_layout()
cl.savefig(fig, "access_targets")
r.save()
