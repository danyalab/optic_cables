"""Worked example 10.1: revenues along the optical value chain, from filings.

All inputs are tier-B filing records (10-K, earnings release furnished on
8-K, A-share/H-share annual reports). Fiscal-year bases differ by company and
are carried in the result names. No currency conversion is done, because the
ledger holds no exchange-rate record: CNY, USD and EUR figures are compared
only through ratios within one company.

Also draws Figure 10.1, the value-chain map (a schematic; firm placement is
from the filings and instruments cited in the chapter).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch10lib as cl

r = Results()

# ---------------- US-listed component and chip firms (USD) ----------------
COH, COHN, COHN24 = ("ch10.chain.coherent_fy25_revenue", "ch10.chain.coherent_fy25_networking",
                     "ch10.chain.coherent_fy24_networking")
coh, cohn, cohn24 = L(COH), L(COHN), L(COHN24)
r.emit("coh_rev", coh / 1e3, "BUSD", 3, [COH])
r.emit("coh_net", cohn / 1e3, "BUSD", 3, [COHN])
r.emit("coh_net_share_pct", 100 * cohn / coh, "%", 3, [COH, COHN])
g_coh = 100 * (cohn / cohn24 - 1)
assert abs(g_coh - 49) < 0.5, "Coherent Networking growth should match the 49% in the 10-K sentence"
r.emit("coh_net_growth_pct", g_coh, "%", 3, [COHN, COHN24])

LUM, LUMC = "ch10.chain.lumentum_fy25_revenue", "ch10.chain.lumentum_fy25_cloud_networking"
lum, lumc = L(LUM), L(LUMC)
lumc24 = cl.qnum(LUMC, r"1,410\.8 \| ([0-9.,]+)")
g_lum = 100 * (lumc / lumc24 - 1)
assert abs(g_lum - cl.qnum(LUMC, r"\| ([0-9.]+)%")) < 0.05
r.emit("lum_rev", lum / 1e3, "BUSD", 4, [LUM])
r.emit("lum_cn", lumc / 1e3, "BUSD", 3, [LUMC])
r.emit("lum_cn_share_pct", 100 * lumc / lum, "%", 3, [LUM, LUMC])
r.emit("lum_cn_growth_pct", g_lum, "%", 3, [LUMC])

MDC, MOPT = "ch10.chain.marvell_fy26_datacenter", "ch10.chain.marvell_optical_share_of_dc"
mdc = L(MDC)
r.emit("mrvl_dc", mdc / 1e3, "BUSD", 3, [MDC])
r.emit("mrvl_dc_share_pct", 100 * float(cl.cond(MDC, "share_of_total")), "%", 2, [MDC])
r.emit("mrvl_opt_est", L(MOPT) * mdc / 1e3, "BUSD", 2, [MDC, MOPT])

# ---------------- Chinese firms (CNY) ----------------
INNO, INNOM = "ch10.chain.innolight_2025_revenue", "ch10.chain.innolight_2025_module_revenue"
inno = L(INNO)
inno24 = cl.qnum(INNO, r"38,239,935,640\.67 \| ([0-9,.]+)") / 1e6
g_inno = 100 * (inno / inno24 - 1)
assert abs(g_inno - cl.qnum(INNO, r"\| ([0-9.]+)%")) < 0.01
r.emit("inno_rev", inno / 1e3, "CNY bn", 4, [INNO])
r.emit("inno_rev24", inno24 / 1e3, "CNY bn", 4, [INNO])
r.emit("inno_growth_pct", g_inno, "%", 4, [INNO])
r.emit("inno_module_share_pct", 100 * L(INNOM) / inno, "%", 4, [INNO, INNOM])

EOP = "ch10.chain.eoptolink_2025_revenue"
eop = L(EOP)
g_eop = cl.qnum(EOP, r"分别增加 ([0-9.]+)%")
eop24 = eop / (1 + g_eop / 100)
# Cross-check the implied 2024 revenue against the 2024 overseas column (value / share).
EOS = "ch10.chain.eoptolink_2025_overseas_share"
eop24_b = cl.qnum(EOS, r"96\.16% \| ([0-9,.]+)") / cl.qnum(EOS, r"96\.16% \| [0-9,.]+ \| ([0-9.]+)%") * 100 / 1e6
assert abs(eop24 / eop24_b - 1) < 1e-3, "two routes to Eoptolink 2024 revenue disagree"
r.emit("eop_rev", eop / 1e3, "CNY bn", 4, [EOP])
r.emit("eop_rev24", eop24 / 1e3, "CNY bn", 3, [EOP, EOS])
r.emit("eop_growth_pct", g_eop, "%", 5, [EOP])
r.emit("eop_rev24_check_pct", 100 * (eop24 / eop24_b - 1), "%", 2, [EOP, EOS])

ACC, ACCD = "ch10.chain.accelink_2025_revenue", "ch10.chain.accelink_2025_datacom_access"
acc = L(ACC)
acc24 = cl.qnum(ACC, r"11,928,697,127\.38 \| ([0-9,.]+)") / 1e6
g_acc = 100 * (acc / acc24 - 1)
assert abs(g_acc - cl.qnum(ACC, r"\| ([0-9.]+)%")) < 0.01
r.emit("acc_rev", acc / 1e3, "CNY bn", 4, [ACC])
r.emit("acc_growth_pct", g_acc, "%", 3, [ACC])
r.emit("acc_datacom_share_pct", 100 * L(ACCD) / acc, "%", 4, [ACC, ACCD])

YOFC, YOFCI = "ch10.chain.yofc_2025_revenue", "ch10.chain.yofc_2025_interconnect"
r.emit("yofc_rev", L(YOFC) / 1e3, "CNY bn", 4, [YOFC])
r.emit("yofc_ic", L(YOFCI) / 1e3, "CNY bn", 4, [YOFCI])
r.emit("yofc_ic_share_pct", 100 * L(YOFCI) / L(YOFC), "%", 3, [YOFC, YOFCI])

HG = "ch10.chain.hgtech_2025_connect_revenue"
r.emit("hg_connect", L(HG) / 1e3, "CNY bn", 4, [HG])
r.emit("hg_growth_pct", cl.qnum(HG, r"增 ?长 ([0-9.]+)%"), "%", 4, [HG])

# Ratio of the two largest module makers' revenues (same currency, same calendar year).
r.emit("eop_over_inno", eop / inno, "1", 3, [EOP, INNO])

r.save()

# ---------------- Figure 10.1: value-chain map ----------------
plt = cl.setup_mpl()
from matplotlib.patches import FancyBboxPatch  # noqa: E402

fig, ax = plt.subplots(figsize=(12.0, 6.8))
ax.set_xlim(0, 100)
ax.set_ylim(0, 63)
ax.axis("off")
ax.grid(False)

tiers = [
    ("Materials and\nsubstrates", ["InP substrates:", " Sumitomo Electric (JP)", " AXT/Tongmei (made in CN)",
                                    "In-house InP wafers:", " Broadcom (US)", "MOCVD precursors:", " TMIn, TEIn"]),
    ("Chips", ["Lasers (EML, DML, CW):", " Coherent, Lumentum,", " Broadcom (US)", " Mitsubishi Electric (JP)",
               " Yuanjie, Accelink (CN)", "DSP, driver, TIA:", " Marvell, Broadcom,", " MaxLinear (US)",
               " Xiamen UX (CN, mostly 10G)"]),
    ("Modules", ["Innolight, Eoptolink,", " Accelink, HGTECH,", " YOFC (CN)", "Coherent, Lumentum (US)",
                 "Plants named in filings:", " CN, Thailand, Vietnam,", " US, UK, JP, Slovenia;", " CMs in Malaysia etc."]),
    ("Systems", ["Huawei, ZTE,", " FiberHome (CN)", "Ciena, Cisco (US)", "Nokia incl. Infinera", "",
                 "Switch / CPO platforms:", " NVIDIA, Broadcom (US)"]),
]
xs = [0.5, 26, 51.5, 77]
w, h, y0 = 21.5, 46, 10
for i, ((title, lines), x) in enumerate(zip(tiers, xs)):
    box = FancyBboxPatch((x, y0), w, h, boxstyle="round,pad=0.4,rounding_size=1.2",
                         linewidth=1.4, edgecolor=cl.COLORS[i], facecolor=cl.COLORS[i] + "18")
    ax.add_patch(box)
    ax.text(x + w / 2, y0 + h - 4, title, ha="center", va="center", fontsize=12.5,
            color=cl.COLORS[i], fontweight="bold")
    for k, line in enumerate(lines):
        ax.text(x + 1.2, y0 + h - 10.5 - 3.9 * k, line, ha="left", va="center", fontsize=9.0, color=cl.GRAY)
    if i < 3:
        ax.annotate("", xy=(xs[i + 1] - 0.3, y0 + h / 2), xytext=(x + w + 0.9, y0 + h / 2),
                    arrowprops=dict(arrowstyle="-|>", color=cl.GRAY, lw=1.6))

# Where instruments bite (labels only; details in Section 10.6).
notes = [
    (11.25, 4.5, "MOFCOM/GAC 2025 No. 10:\nInP, TMIn, TEIn licensing", cl.COLORS[0]),
    (36.75, 4.5, "MOFCOM/GAC 2023 No. 23:\nGaAs, InGaAs licensing", cl.COLORS[1]),
    (62.25, 4.5, "Sec. 301 List 4A: HTS 8517.62\n(US imports of CN-origin)", cl.COLORS[2]),
    (87.75, 4.5, "BIS Entity List entries include\nHuawei, FiberHome, Hengtong, HMN", cl.COLORS[3]),
]
for x, y, t, c in notes:
    ax.text(x, y, t, ha="center", va="center", fontsize=8.6, color=c, style="italic")
ax.text(50, 61, "Customers: hyperscale cloud operators (AI clusters), telecom operators",
        ha="center", va="center", fontsize=10.5, color=cl.GRAY)
ax.annotate("", xy=(88, 59.3), xytext=(88, y0 + h + 0.8),
            arrowprops=dict(arrowstyle="-|>", color=cl.GRAY, lw=1.2))
ax.annotate("", xy=(62, 59.3), xytext=(62, y0 + h + 0.8),
            arrowprops=dict(arrowstyle="-|>", color=cl.GRAY, lw=1.2))
cl.savefig(fig, "value_chain")
