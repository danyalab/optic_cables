"""Worked example 9.5: China's international Internet exit bandwidth, 2018-2022,
its growth rate, and its size against backbone and per-fiber capacities.

The 2018-2020 values are the CNNIC Figure 4 series as recorded in the notes of
ledger record ch09.intl.exit_bw_2022 (same figure as the record's quote).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import re
import ch09lib as cl

r = Results()
X22, X21 = "ch09.intl.exit_bw_2022", "ch09.intl.exit_bw_2021"
series = {int(y): float(v.replace(",", "")) for y, v in
          re.findall(r"(20\d\d) ([0-9,]{9,})", cl.rec(X22)["notes"])}
assert series[2022] == L(X22) and series[2021] == L(X21)
years = sorted(series)
tb = {y: series[y] / 1e6 for y in years}          # Mb/s -> Tb/s
for y in years:
    r.emit(f"bw_{y}", tb[y], "Tb/s", 4, [X22])
yoy = 100 * (tb[2022] / tb[2021] - 1)
r.emit("yoy_2022_pct", yoy, "%", 3, [X22, X21])
assert abs(yoy - 33.5) < 0.1          # the 33.5 % growth stated in the quote
n_y = years[-1] - years[0]
cagr = (tb[years[-1]] / tb[years[0]]) ** (1 / n_y) - 1
r.emit("cagr_pct", 100 * cagr, "%", 3, [X22])
r.emit("n_years", n_y, "", 1, [X22])
r.emit("doubling_yr", math.log(2) / math.log(1 + cagr), "yr", 2, [X22])

# Scale comparisons (different metrics and years; see prose)
CAP = "ch09.l400.cmcc_capacity_32t"
BW = "ch09.op.cmcc_interprovincial_bw_2025"
INTL = "ch09.intl.cmcc_intl_2025"
CU = "ch09.op.cu_intl_interconnect_6p7t"
rate = float(cl.cond(CAP, "rate_Gbps"))
r.emit("waves_400g", tb[2022] * 1e3 / rate, "", 3, [X22, CAP])
r.emit("frac_fiber", tb[2022] / L(CAP), "", 2, [X22, CAP])
r.emit("ratio_backbone", L(BW) / tb[2022], "", 2, [X22, BW])
r.emit("ratio_cmcc_intl", L(INTL) / tb[2022], "", 2, [X22, INTL])
r.emit("cu_intl", L(CU), "Tb/s", 2, [CU])
r.emit("cu_sub_tb", float(cl.cond(CU, "submarine_capacity_T")), "Tb/s", 3, [CU])

# Cross-border terrestrial capacity, 2014 and ~2018 (definitions differ)
CB14, CB18 = "ch09.intl.crossborder_2014", "ch09.intl.crossborder_caict"
r.emit("cb14_tbps", L(CB14) / 1e3, "Tb/s", 2, [CB14])
r.emit("cb18_tbps", L(CB18), "Tb/s", 2, [CB18])
r.emit("cb18_sub_tbps", float(cl.cond(CB18, "submarine_bw_T")), "Tb/s", 2, [CB18])

# Figure
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.8, 3.8))
ax.bar([str(y) for y in years], [tb[y] for y in years], color=cl.COLORS[0], width=0.6)
for i, y in enumerate(years):
    ax.text(i, tb[y] + 0.3, f"{tb[y]:.1f}", ha="center", fontsize=10)
ax.set_ylabel("international Internet exit bandwidth (Tb/s)")
ax.set_ylim(0, 21)
ax.grid(axis="x", visible=False)
cl.savefig(fig, "exit_bandwidth")
r.save()
