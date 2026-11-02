"""Worked example 2.5: AWGN capacity vs uniform and MB-shaped QAM; shaping gain; PAS.

Square M^2-QAM on the complex AWGN channel is the product of two independent
M-ASK constellations, each seeing the same SNR, so per 2-D symbol
  MI_QAM(SNR) = 2 MI_ASK(SNR),  GMI_QAM = 2 GMI_ASK (Gray labels),  C = log2(1+SNR).
All integrals by Gauss-Hermite quadrature (ch02lib), checked against
Böcherer et al. (2015) Table I.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
from scipy.optimize import brentq, minimize_scalar
import ch02lib as cl

r = Results()
cap1 = cl.awgn_cap_1d

# ---------------- 1. ultimate shaping gain ----------------
gs = 10 * math.log10(math.pi * math.e / 6)
assert round(gs, 2) == L("ch02.ir.shaping_gain_ultimate")
r.emit("gs_ult", gs, "dB", 4, ["ch02.ir.shaping_gain_ultimate"])
r.emit("gs_ult_ratio", math.pi * math.e / 6, "1", 4, ["ch02.ir.shaping_gain_ultimate"])
# equivalently: entropy gap of a uniform density at equal power, bits per dimension
r.emit("gs_ult_bits", 0.5 * math.log2(math.pi * math.e / 6), "bit/dim", 3, ["ch02.ir.shaping_gain_ultimate"])

# ---------------- 2. Böcherer Table I checks ----------------
TAB = [(4, 1, "ch02.ir.uniform_4ask_snr_rate1", "4ask"),
       (8, 2, "ch02.ir.uniform_8ask_snr_rate2", "8ask"),
       (16, 3, "ch02.ir.uniform_16ask_snr_rate3", "16ask")]
for M, R, rid, tag in TAB:
    s_u = cl.snr_for_rate(lambda x: cl.ask_mi(M, x), R)
    s_c = 10 * math.log10(2 ** (2 * R) - 1)
    assert abs(s_u - L(rid)) < 2e-3, (tag, s_u, L(rid))
    assert abs(s_c - float(cl.cond(rid, "capacity_snr_dB"))) < 1e-3
    r.emit(f"snr_u_{tag}", s_u, "dB", 5, [rid])
    r.emit(f"snr_c_{tag}", s_c, "dB", 5, [rid])
    r.emit(f"gap_u_{tag}", s_u - s_c, "dB", 3, [rid])


def snr_mb_opt(M, R, lam_hi):
    """Minimum SNR over MB parameter at which MI = R bits per dimension."""
    def f(lam):
        p = cl.mb_probs(M, lam)
        if cl.entropy(p) <= R + 1e-3:
            return 99.0
        return cl.snr_for_rate(lambda x: cl.ask_mi(M, x, p), R)
    lam_max = brentq(lambda l: cl.entropy(cl.mb_probs(M, l)) - (R + 2e-3), 0.0, lam_hi)
    res = minimize_scalar(f, bounds=(0.0, lam_max), method="bounded", options={"xatol": 1e-7})
    return res.fun, res.x


s_mb8, lam8 = snr_mb_opt(8, 2, 0.2)
s_u8 = r.data["snr_u_8ask"]["value"]
assert abs((s_mb8 - s_u8) + L("ch02.ir.mb_gain_8ask_rate2")) < 5e-3, (s_mb8, s_u8)
r.emit("snr_mb_8ask", s_mb8, "dB", 5, ["ch02.ir.mb_gain_8ask_rate2"])
r.emit("gain_mb_8ask", s_u8 - s_mb8, "dB", 4, ["ch02.ir.mb_gain_8ask_rate2"])
r.emit("gap_mb_8ask", s_mb8 - r.data["snr_c_8ask"]["value"], "dB", 3, ["ch02.ir.mb_gain_8ask_rate2"])
r.emit("lam_mb_8ask", lam8, "1", 3)
r.emit("h_mb_8ask", cl.entropy(cl.mb_probs(8, lam8)), "bit/dim", 4)

# 64-ASK at 5 bit per dimension: MB gain over uniform, Böcherer 1.33 dB
s_u64 = cl.snr_for_rate(lambda x: cl.ask_mi(64, x), 5)
s_mb64, lam64 = snr_mb_opt(64, 5, 0.01)
g64 = s_u64 - s_mb64
assert abs(g64 - L("ch02.ir.mb_gain_64ask_rate5")) < 0.01, g64
r.emit("gain_mb_64ask", g64, "dB", 3, ["ch02.ir.mb_gain_64ask_rate5"])
r.emit("gap_u_64ask", s_u64 - 10 * math.log10(2 ** 10 - 1), "dB", 3, ["ch02.ir.mb_gain_64ask_rate5"])
r.emit("frac_ult_64", g64 / gs, "1", 3, ["ch02.ir.mb_gain_64ask_rate5", "ch02.ir.shaping_gain_ultimate"])

# ---------------- 3. gaps of uniform 16/64-QAM at relevant rates (per 2-D symbol) ----------------
# 16-QAM = 4-ASK^2, 64-QAM = 8-ASK^2; rates in bit per 2-D symbol
gaps = {}
for M, tag in ((4, "16"), (8, "64")):
    for R2 in ((3.0, 3.5) if M == 4 else (4.0, 5.0)):
        s_mi = cl.snr_for_rate(lambda x: 2 * cl.ask_mi(M, x), R2)
        s_gmi = cl.snr_for_rate(lambda x: 2 * cl.ask_gmi(M, x), R2)
        s_c = 10 * math.log10(2 ** R2 - 1)
        key = f"{tag}_{str(R2).replace('.', 'p')}"
        r.emit(f"snrmi_{key}", s_mi, "dB", 4)
        r.emit(f"snrgmi_{key}", s_gmi, "dB", 4)
        r.emit(f"snrc_{key}", s_c, "dB", 4)
        r.emit(f"gapmi_{key}", s_mi - s_c, "dB", 3)
        r.emit(f"gapgmi_{key}", s_gmi - s_c, "dB", 3)
        gaps[key] = (s_mi - s_c, s_gmi - s_c)
assert gaps["16_3p0"][0] < gaps["16_3p0"][1]          # GMI <= MI
# consistency with Böcherer row 4ASK at 2 bit/2D (= 1 bit/dim) and 8ASK at 4 bit/2D
assert abs(gaps["64_4p0"][0] - r.data["gap_u_8ask"]["value"]) < 1e-3

# MI and GMI at fixed SNRs (bit per 2-D symbol)
for snr_db in (10.0, 15.0, 20.0):
    s = cl.db2lin(snr_db)
    t = f"{int(snr_db)}"
    r.emit(f"c_{t}", math.log2(1 + s), "bit/2D", 4)
    r.emit(f"mi16_{t}", 2 * cl.ask_mi(4, s), "bit/2D", 4)
    r.emit(f"gmi16_{t}", 2 * cl.ask_gmi(4, s), "bit/2D", 4)
    r.emit(f"mi64_{t}", 2 * cl.ask_mi(8, s), "bit/2D", 4)
    r.emit(f"gmi64_{t}", 2 * cl.ask_gmi(8, s), "bit/2D", 4)

# ---------------- 4. PAS example: PCS-64QAM, fixed code rate ----------------
RC = float(cl.cond("ch02.ir.pcs_fixed_rate_loss", "code_rate"))
m = 3                                     # bits per dimension of 8-ASK
IR = 4.0                                  # ASSUMPTION: target information rate, bit per 2-D symbol
H_target = IR / 2 + m * (1 - RC)          # Cho & Winzer Eq. (5) inverted
lam_pas = brentq(lambda l: cl.entropy(cl.mb_probs(8, l)) - H_target, 1e-6, 1.0)
p_pas = cl.mb_probs(8, lam_pas)
s_pas = cl.snr_for_rate(lambda x: cl.ask_mi(8, x, p_pas), IR / 2)
labels = np.array([cl.gray(i) for i in range(8)])
hb = 0.0
for k in range(m):
    pk = p_pas[((labels >> k) & 1) == 1].sum()
    hb += cl.entropy([pk, 1 - pk])
# BMD rate of PAS: H(X) - sum_k H(B_k|Y) = sum_k I(B_k;Y) - (sum_k H(B_k) - H(X))
s_pas_gmi = cl.snr_for_rate(lambda x: cl.ask_gmi(8, x, p_pas) - (hb - cl.entropy(p_pas)), IR / 2)
r.emit("pas_rc", RC, "1", 2, ["ch02.ir.pcs_fixed_rate_loss"])
r.emit("pas_ir", IR, "bit/2D", 2)
r.emit("pas_h", H_target, "bit/dim", 3, ["ch02.ir.pcs_fixed_rate_loss"])
r.emit("pas_lam", lam_pas, "1", 3)
r.emit("pas_p_inner", p_pas[3], "1", 3)
r.emit("pas_p_outer", p_pas[0], "1", 3)
r.emit("pas_snr", s_pas, "dB", 4)
r.emit("pas_snr_bmd", s_pas_gmi, "dB", 4)
r.emit("pas_gain_vs_u64", s_u8 - s_pas, "dB", 3, ["ch02.ir.uniform_8ask_snr_rate2"])
r.emit("pas_loss_vs_opt", s_pas - s_mb8, "dB", 3)
assert s_pas - s_mb8 <= L("ch02.ir.pcs_fixed_rate_loss")   # Cho & Winzer: <= 0.3 dB
# power check: E|X|^2 of the shaped vs uniform 8-ASK at unit spacing
x8 = cl.ask_points(8)
r.emit("pas_pow_ratio_db", cl.lin2db((x8 ** 2).mean() / (p_pas * x8 ** 2).sum()), "dB", 3)
# code rate needed by uniform 64-QAM at the same IR: R_c = IR / log2(64)
r.emit("u64_rc", IR / 6, "1", 3)
# Cho & Winzer Eq. (6) check
assert abs((1 - (H_target - IR / 2) / m) - RC) < 1e-12

# ---------------- figures ----------------
plt = cl.setup_mpl()
snr_db = np.linspace(-2, 30, 65)
snr = cl.db2lin(snr_db)
fig, ax = plt.subplots(figsize=(6.6, 4.4))
ax.plot(snr_db, np.log2(1 + snr), color=cl.GRAY, lw=2.2, label="AWGN capacity log2(1+SNR)")
for i, (M, lab) in enumerate(((4, "16-QAM"), (8, "64-QAM"), (16, "256-QAM"))):
    mi = [2 * cl.ask_mi(M, s) for s in snr]
    ax.plot(snr_db, mi, color=cl.COLORS[i], label=f"uniform {lab}, MI")
    if M < 16:
        gmi = [2 * cl.ask_gmi(M, s) for s in snr]
        ax.plot(snr_db, gmi, color=cl.COLORS[i], ls=":", lw=1.6, label=f"uniform {lab}, GMI (Gray)")
mb = []
for s in snr:
    best = 0.0
    for lam in np.linspace(0, 0.3, 31):
        best = max(best, 2 * cl.ask_mi(16, s, cl.mb_probs(16, lam)))
    mb.append(best)
ax.plot(snr_db, mb, color=cl.COLORS[3], ls="--", label="MB-shaped 256-QAM, MI (grid over λ)")
ax.set_xlabel("SNR (dB)")
ax.set_ylabel("bit per 2-D symbol")
ax.set_xlim(-2, 30)
ax.set_ylim(0, 9)
ax.legend(fontsize=8.5, loc="upper left")
cl.savefig(fig, "air_curves")

fig, ax = plt.subplots(figsize=(6.0, 3.4))
w = 0.26
for i, (lam, lab) in enumerate(((0.0, "uniform, H = 3"), (lam8, f"MB opt. at 2 bit/dim, H = {cl.entropy(cl.mb_probs(8, lam8)):.2f}"),
                                (lam_pas, f"PAS, R_c = {RC:g}, H = {H_target:.2f}"))):
    ax.bar(x8 + (i - 1) * w * 2, cl.mb_probs(8, lam), width=2 * w, color=cl.COLORS[i], label=lab)
ax.set_xticks(x8)
ax.set_xlabel("8-ASK amplitude (one quadrature of 64-QAM)")
ax.set_ylabel("probability")
ax.legend(fontsize=8.5)
cl.savefig(fig, "mb_distribution")

r.save()
