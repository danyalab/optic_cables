"""Worked example 10.4: module makers' overseas exposure, capacity use and footprint.

Inputs are A-share and H-share annual-report tables (tier B), all calendar
2025 with the 2024 comparison column read from the same table row.

Draws Figure 10.3 (revenue split by region, and the change in overseas
share 2024 -> 2025).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import numpy as np
import ch10lib as cl

r = Results()

INNO, INOS = "ch10.chain.innolight_2025_revenue", "ch10.chain.innolight_2025_overseas_share"
EOP, EOS = "ch10.chain.eoptolink_2025_revenue", "ch10.chain.eoptolink_2025_overseas_share"
ACC, ACOS = "ch10.chain.accelink_2025_revenue", "ch10.chain.accelink_2025_overseas_share"
YOFC, YOS = "ch10.chain.yofc_2025_revenue", "ch10.chain.yofc_2025_overseas_share"

firms = {
    # name: (revenue MCNY, overseas share 2025, overseas share 2024 or None, ids)
    "Innolight": (L(INNO), L(INOS), cl.qnum(INOS, r"90\.58% \| [0-9,.]+ \| ([0-9.]+)%") / 100, [INNO, INOS]),
    "Eoptolink": (L(EOP), L(EOS), cl.qnum(EOS, r"96\.16% \| [0-9,.]+ \| ([0-9.]+)%") / 100, [EOP, EOS]),
    "Accelink": (L(ACC), L(ACOS), cl.qnum(ACOS, r"26\.69% \| [0-9,.]+ \| ([0-9.]+)%") / 100, [ACC, ACOS]),
    "YOFC": (L(YOFC), L(YOS), None, [YOFC, YOS]),
}
key = {"Innolight": "inno", "Eoptolink": "eop", "Accelink": "acc", "YOFC": "yofc"}
for name, (rev, s25, s24, ids) in firms.items():
    k = key[name]
    r.emit(f"{k}_os_pct", 100 * s25, "%", 4, ids)
    r.emit(f"{k}_os_rev", rev * s25 / 1e3, "CNY bn", 3, ids)
    if s24 is not None:
        r.emit(f"{k}_os24_pct", 100 * s24, "%", 4, ids)
        r.emit(f"{k}_os_dpp", 100 * (s25 - s24), "pp", 3, ids)

# Cross-checks against the absolute overseas amounts printed in the same rows.
# Tolerance: shares are printed to 0.01 pp, i.e. +-0.005% of revenue = +-1.9 MCNY for Innolight.
assert abs(L(INNO) * L(INOS) - cl.qnum(INOS, r"境外 \| ([0-9,.]+)") / 1e6) < 2.0
assert abs(L(EOP) * L(EOS) - cl.qnum(EOS, r"境外 \| ([0-9,.]+)") / 1e6) < 2.0
assert abs(L(YOFC) * L(YOS) / 100 - cl.qnum(YOS, r"人民币([0-9.]+) ?亿元")) < 0.08   # share printed to 0.1 pp: +-0.07 (100 MCNY)

# Combined exposure of the two largest exporters
os_two = L(INNO) * L(INOS) + L(EOP) * L(EOS)
r.emit("two_os_rev", os_two / 1e3, "CNY bn", 3, [INNO, INOS, EOP, EOS])
r.emit("two_os_pct", 100 * os_two / (L(INNO) + L(EOP)), "%", 3, [INNO, INOS, EOP, EOS])
# Overseas revenue growth, Innolight (from the same row)
r.emit("inno_os_growth_pct", cl.qnum(INOS, r"\| ([0-9.]+)%$"), "%", 4, [INOS])

# Capacity, production and sales (units)
IU, EU = "ch10.chain.innolight_2025_units_sold", "ch10.chain.eoptolink_2025_units_sold"
for k, rid in (("inno", IU), ("eop", EU)):
    cap = float(cl.cond(rid, "capacity_million_units"))
    prod = float(cl.cond(rid, "production_million_units"))
    sold = L(rid)
    r.emit(f"{k}_cap", cap, "million units", 4, [rid])
    r.emit(f"{k}_prod", prod, "million units", 4, [rid])
    r.emit(f"{k}_sold", sold, "million units", 4, [rid])
    r.emit(f"{k}_util_pct", 100 * prod / cap, "%", 3, [rid])
    r.emit(f"{k}_sell_pct", 100 * sold / prod, "%", 3, [rid])

# Average revenue per module (all rates mixed; not a price of any product)
IM = "ch10.chain.innolight_2025_module_revenue"
eop_mod = cl.qnum(EU, r"([0-9,]+\.[0-9]+)", field="notes") / 1e6        # MCNY, from the Sina row in notes
r.emit("inno_arpu", L(IM) / L(IU), "CNY/unit", 3, [IM, IU])
r.emit("eop_arpu", eop_mod / L(EU), "CNY/unit", 3, [EU])
r.emit("inno_gm_pct", 100 * L("ch10.chain.innolight_2025_module_gm"), "%", 4, ["ch10.chain.innolight_2025_module_gm"])
r.emit("eop_gm_pct", 100 * float(cl.cond(EU, "gross_margin")), "%", 4, [EU])

# Thailand subsidiary of Eoptolink: upper bound on Thai share (intra-group sales may be included)
TH = "ch10.chain.eoptolink_thailand_sub_revenue"
r.emit("eop_th_ratio_pct", 100 * L(TH) / L(EOP), "%", 3, [TH, EOP])
r.emit("eop_th_rev", L(TH) / 1e3, "CNY bn", 3, [TH])

# HGTECH overseas 800G capacity, annualized
HG = "ch10.mod.hgtech_overseas_800g_capacity"
r.emit("hg_month", L(HG) / 1e3, "thousand units/month", 3, [HG])
r.emit("hg_year", 12 * L(HG) / 1e6, "million units/yr", 2, [HG])
r.save()

# ---------------- Figure 10.3 ----------------
plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.5, 4.0), gridspec_kw={"width_ratios": [1.25, 1]})
names = list(firms)
rev = np.array([firms[n][0] for n in names]) / 1e3
os_ = np.array([firms[n][0] * firms[n][1] for n in names]) / 1e3
x = np.arange(len(names))
a1.bar(x, os_, color=cl.COLORS[0], label="outside mainland China")
a1.bar(x, rev - os_, bottom=os_, color=cl.COLORS[1], alpha=0.75, label="mainland China")
for i in range(len(names)):
    a1.text(x[i], rev[i] + 0.6, f"{100 * os_[i] / rev[i]:.1f}%", ha="center", fontsize=9.5, color=cl.GRAY)
a1.set_xticks(x, names)
a1.set_ylabel("2025 revenue (CNY bn)")
a1.set_title("(a) revenue by customer region, 2025", fontsize=11)
a1.legend(loc="upper right", fontsize=9)
a1.set_ylim(0, 44)

names2 = [n for n in names if firms[n][2] is not None]
for i, n in enumerate(names2):
    s24, s25 = 100 * firms[n][2], 100 * firms[n][1]
    a2.plot([2024, 2025], [s24, s25], "o-", color=cl.COLORS[i], ms=6)
    a2.text(2025.06, s25, n, va="center", fontsize=9.5, color=cl.COLORS[i])
a2.set_xlim(2023.8, 2025.6)
a2.set_xticks([2024, 2025])
a2.set_ylim(0, 100)
a2.set_ylabel("overseas share of revenue (%)")
a2.set_title("(b) overseas share, 2024 to 2025", fontsize=11)
fig.tight_layout()
cl.savefig(fig, "revenue_overseas")
