"""Worked example 2.2: PAM-M penalties, TDECQ constant, RIN and MPI penalties,
and a 100G-FR (53.125 GBd PAM4) optical link budget.

Model: IM/DD with signal-independent receiver noise sigma; levels equally spaced
between P0 and P0 + OMA; Gray coding so BER ~ SER / log2(M).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
from scipy.optimize import brentq
import ch02lib as cl

r = Results()

# ---------------- 1. ideal PAM-M penalties at equal OMA ----------------
pen_e = 20 * math.log10(4 - 1)
pen_o = 10 * math.log10(4 - 1)
assert round(pen_e, 1) == L("ch02.imdd.pam4_penalty_electrical")
assert round(pen_o, 1) == L("ch02.imdd.pam4_penalty_optical")
assert round(10 * math.log10(16 - 1), 1) == L("ch02.imdd.pam16_penalty_optical")
assert round(10 * math.log10(math.sqrt(16) - 1), 1) == L("ch02.imdd.qam16_penalty_optical")
r.emit("pen4_e", pen_e, "dB", 3, ["ch02.imdd.pam4_penalty_electrical"])
r.emit("pen4_o", pen_o, "dB", 3, ["ch02.imdd.pam4_penalty_optical"])
r.emit("pen16_o", 10 * math.log10(15), "dB", 3, ["ch02.imdd.pam16_penalty_optical"])
r.emit("pen8_e", 20 * math.log10(7), "dB", 3)
r.emit("pen8_o", 10 * math.log10(7), "dB", 3)
# same bit rate: PAM4 runs at half the symbol rate -> half the noise bandwidth
r.emit("pen4_e_samerate", pen_e - 10 * math.log10(2), "dB", 3)
r.emit("pen4_o_samerate", pen_o - 5 * math.log10(2), "dB", 3)

# ---------------- 2. required eye Q at the KP4 BER limit ----------------
BER_KP4 = L("ch02.fec.kp4_ber_limit")
q_nrz = cl.qinv(BER_KP4)                     # BER = Q(q) for NRZ
q_pam4 = cl.qinv(BER_KP4 * 2 / 1.5)          # BER = SER/2, SER = 1.5 Q(q)
r.emit("q_nrz", q_nrz, "1", 4, ["ch02.fec.kp4_ber_limit"])
r.emit("q_pam4", q_pam4, "1", 4, ["ch02.fec.kp4_ber_limit"])

# ---------------- 3. TDECQ: Q_t from the target SER ----------------
SER_T = L("ch02.imdd.tdecq_target_ser")
QT = L("ch02.imdd.tdecq_qt")
qt_calc = cl.qinv(SER_T / 1.5)
assert abs(qt_calc - QT) < 2e-3, (qt_calc, QT)
assert abs(SER_T / 2 - BER_KP4) < 1e-12        # Gray: BER = SER/2 = KP4 limit
r.emit("qt_calc", qt_calc, "1", 4, ["ch02.imdd.tdecq_target_ser"])
TDECQ_MAX = L("ch02.imdd.tdecq_max_100g_fr")
r.emit("tdecq_noise_ratio", 10 ** (-TDECQ_MAX / 10), "1", 3, ["ch02.imdd.tdecq_max_100g_fr"])
oma_min = L("ch02.imdd.oma_min_100g_fr")
oma_m_tdecq = L("ch02.imdd.oma_minus_tdecq_100g_fr")
oma_at_max = oma_m_tdecq + TDECQ_MAX
r.emit("oma_at_tdecq_max", oma_at_max, "dBm", 2,
       ["ch02.imdd.oma_minus_tdecq_100g_fr", "ch02.imdd.tdecq_max_100g_fr"])
r.emit("tdecq_cross", oma_min - oma_m_tdecq, "dB", 2,
       ["ch02.imdd.oma_min_100g_fr", "ch02.imdd.oma_minus_tdecq_100g_fr"])

# extinction ratio: average power for a given OMA, P_avg = OMA (E+1) / (2 (E-1))
E = cl.db2lin(L("ch02.imdd.er_min_100g_fr"))
pavg = cl.w2dbm(cl.dbm2w(oma_at_max) * (E + 1) / (2 * (E - 1)))
r.emit("pavg_at_oma", pavg, "dBm", 2, ["ch02.imdd.er_min_100g_fr"])

# ---------------- 4. RIN penalty ----------------
RS = L("ch02.sym.lambda_pam4_rate") * 1e9
# ASSUMPTION: noise bandwidth equal to the Nyquist frequency R_s/2
BN = RS / 2
# ASSUMPTION: normalisation sigma_RIN^2 = 10^(RIN/10) * OMA^2 * B_n (RIN referred to OMA)
RIN = L("ch02.imdd.rin_oma_max_100g")
k = math.sqrt(cl.db2lin(RIN) * BN)
r.emit("bn_ghz", BN / 1e9, "GHz", 4, ["ch02.sym.lambda_pam4_rate"])
r.emit("rin_k_db", 20 * math.log10(k), "dB", 3, ["ch02.imdd.rin_oma_max_100g"])
q_rin_pam4 = 1 / (6 * k)
r.emit("q_rin_pam4", q_rin_pam4, "1", 3, ["ch02.imdd.rin_oma_max_100g"])


def rin_pen(q_req, levels, kk):
    """Optical-dB penalty: OMA_req = 2(M-1) q sigma_th / sqrt(1 - (2(M-1) q k)^2)."""
    a = 2 * (levels - 1) * q_req * kk
    if a >= 1:
        return float("inf")
    return -5 * math.log10(1 - a * a)


pen_rin4 = rin_pen(q_pam4, 4, k)
pen_rin2 = rin_pen(q_nrz, 2, k)
r.emit("rin_pen_pam4", pen_rin4, "dB", 2, ["ch02.imdd.rin_oma_max_100g", "ch02.fec.kp4_ber_limit"])
r.emit("rin_pen_nrz", pen_rin2, "dB", 2, ["ch02.imdd.rin_oma_max_100g", "ch02.fec.kp4_ber_limit"])
rin_floor = cl.lin2db(1 / (36 * q_pam4 ** 2 * BN))
r.emit("rin_floor_pam4", rin_floor, "dB/Hz", 4, ["ch02.fec.kp4_ber_limit"])
assert pen_rin2 < pen_rin4 < 3

# ---------------- 5. MPI upper bound (Bhatt) ----------------


def mpi_bound(m_levels, refl_db, er_db, discount=1.0):
    """PP = 10 log10(1/(1-x)), x = D (m-1) 4 sum_{i<j} sqrt(R_i R_j) E/(E-1).

    refl_db: list of reflectances in dB (positive numbers, i.e. -26 dB -> 26).
    sqrt(R_i R_j) is the field amplitude of the doubly reflected wave relative to
    the signal; the beat term at worst phase has peak-to-peak 4 sqrt(R_i R_j) P_top.
    """
    R = [10 ** (-x / 10) for x in refl_db]
    s = sum(math.sqrt(R[i] * R[j]) for i in range(len(R)) for j in range(i + 1, len(R)))
    Elin = cl.db2lin(er_db)
    x = discount * (m_levels - 1) * 4 * s * Elin / (Elin - 1)
    return 10 * math.log10(1 / (1 - x)), s, x


ER_B = float(cl.cond("ch02.imdd.mpi_bound_casea_2conn", "extinction_ratio_dB"))
caseA2, sA2, xA2 = mpi_bound(4, [26, 26, 26, 26], ER_B)
caseC2, _, _ = mpi_bound(4, [26, 26, 35, 35], ER_B)
caseC4, sC4, xC4 = mpi_bound(4, [26, 26, 35, 35, 35, 35], ER_B)
caseC6, _, _ = mpi_bound(4, [26, 26] + [35] * 6, ER_B)
caseA4, _, _ = mpi_bound(4, [26] * 6, ER_B)
assert abs(caseA2 - L("ch02.imdd.mpi_bound_casea_2conn")) < 0.01, caseA2
assert abs(caseC4 - L("ch02.imdd.mpi_bound_casec_4conn")) < 0.01, caseC4
assert abs(caseC2 - 0.55) < 0.01 and abs(caseC6 - 1.76) < 0.01 and abs(caseA4 - 5.24) < 0.01  # record notes/quote
insB = ["ch02.imdd.mpi_bound_casea_2conn", "ch02.imdd.mpi_bound_casec_4conn"]
r.emit("mpi_A2", caseA2, "dB", 3, insB)
r.emit("mpi_A4", caseA4, "dB", 3, insB)
r.emit("mpi_C2", caseC2, "dB", 2, insB)
r.emit("mpi_C4", caseC4, "dB", 3, insB)
r.emit("mpi_C6", caseC6, "dB", 3, insB)
r.emit("mpi_A2_sum", sA2, "1", 3, insB)
r.emit("mpi_A2_x", xA2, "1", 3, insB)
r.emit("mpi_ee1", cl.db2lin(ER_B) / (cl.db2lin(ER_B) - 1), "1", 3, insB)
caseA2_nrz, _, _ = mpi_bound(2, [26, 26, 26, 26], ER_B)
r.emit("mpi_A2_nrz", caseA2_nrz, "dB", 2, insB)
gap = 20 * math.log10(3)
assert round(gap, 1) == L("ch02.imdd.mpi_pam2_pam4_gap")
r.emit("mpi_gap", gap, "dB", 3, ["ch02.imdd.mpi_pam2_pam4_gap"])

# ---------------- 6. link budget: 100G-FR at worst-case transmitter ----------------
# ASSUMPTION: 2 km channel insertion loss including connectors (no ledger value for 100G-FR)
IL = 4.0
# ASSUMPTION: two line connectors at 35 dB return loss, Tx and Rx reflectance 26 dB (Bhatt case C)
# ASSUMPTION: discount factor 0.6 inside Bhatt's suggested 0.4-0.8 range
DISC = 0.6
mpi_disc, _, _ = mpi_bound(4, [26, 26, 35, 35], ER_B, DISC)
rx_oma = oma_at_max - IL
eff = rx_oma - TDECQ_MAX
sens_req = eff - caseC2 - pen_rin4
sens_req_disc = eff - mpi_disc - pen_rin4
r.emit("lb_il", IL, "dB", 2)
r.emit("lb_disc", DISC, "1", 1)
r.emit("lb_rx_oma", rx_oma, "dBm", 2)
r.emit("lb_eff", eff, "dBm", 2)
r.emit("lb_mpi_disc", mpi_disc, "dB", 2, insB)
r.emit("lb_sens", sens_req, "dBm", 3)
r.emit("lb_sens_disc", sens_req_disc, "dBm", 3)
# implied receiver noise: ideal eye needs sigma = OMA/(6 Qt)
# ASSUMPTION: photodiode responsivity 0.8 A/W at 1310 nm
RESP = 0.8
sig = RESP * cl.dbm2w(sens_req) / (6 * QT)
r.emit("lb_resp", RESP, "A/W", 2)
r.emit("lb_sigma_ua", sig * 1e6, "µA", 3)
r.emit("lb_in_density", sig / math.sqrt(BN) * 1e12, "pA/√Hz", 3)
# compare with a published budget structure (LPO MSA, DR 500 m): loss + MPI + TDECQ = total
lb = "ch04.lpo.power_budget"
s_lpo = float(cl.cond(lb, "channel_loss_dB")) + float(cl.cond(lb, "MPI_dB")) + float(cl.cond(lb, "TDECQ_dB"))
assert abs(s_lpo - L(lb)) < 1e-9
r.emit("lpo_total", L(lb), "dB", 2, [lb])
r.emit("lpo_loss", float(cl.cond(lb, "channel_loss_dB")), "dB", 2, [lb])
r.emit("lpo_mpi", float(cl.cond(lb, "MPI_dB")), "dB", 2, [lb])
r.emit("lpo_tdecq", float(cl.cond(lb, "TDECQ_dB")), "dB", 2, [lb])

# ---------------- figure: BER of M-PAM vs OMA/sigma ----------------
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.4, 4.0))
x_db = np.linspace(8, 26, 600)          # 10 log10(OMA/sigma), optical dB
for i, M in enumerate((2, 4, 8)):
    q = 10 ** (x_db / 10) / (2 * (M - 1))
    ber = 2 * (1 - 1 / M) * cl.qfunc(q) / math.log2(M)
    ax.semilogy(x_db, ber, color=cl.COLORS[i], label=f"PAM{M}" if M > 2 else "NRZ (PAM2)")
ax.axhline(BER_KP4, color=cl.GRAY, ls="--", lw=1)
ax.text(8.3, BER_KP4 * 1.6, "KP4 BER limit", fontsize=9)
ax.set_ylim(1e-12, 1)
ax.set_xlabel("10 log10(OMA / σ)  (optical dB)")
ax.set_ylabel("BER (Gray coding)")
ax.legend()
cl.savefig(fig, "pam_ber")
# horizontal spacing at the KP4 limit, check against 10log10(M-1) (only approximately, since
# the SER multiplier differs)
x2 = brentq(lambda xd: 2 * 0.5 * cl.qfunc(10 ** (xd / 10) / 2) - BER_KP4, 5, 30)
x4 = brentq(lambda xd: 2 * 0.75 * cl.qfunc(10 ** (xd / 10) / 6) / 2 - BER_KP4, 5, 30)
r.emit("ber_shift_24", x4 - x2, "dB", 3, ["ch02.fec.kp4_ber_limit"])
assert abs((x4 - x2) - pen_o) < 0.1

r.save()
