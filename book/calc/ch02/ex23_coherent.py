"""Worked example 2.3: 90-degree hybrid, balanced detection, LO shot-noise limit.

1. Numerical check of the 2x4 hybrid + balanced detector algebra.
2. Shot-noise-limited SNR of a phase-diversity receiver, SNR = eta P_s/(h nu R_s),
   i.e. eta times the number of photons per symbol.
3. Sensitivity of DP-QPSK at the HD-FEC threshold, LO power needed to swamp
   thermal noise, and why amplified links are ASE-limited (LO-ASE >> LO shot).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
from scipy.optimize import brentq
import ch02lib as cl

r = Results()
h = L("ch01.const.planck_h")
c = L("ch01.const.speed_of_light_c")
lam = float(cl.cond("ch01.cd.g652_link_typ_d1550", "wavelength_nm")) * 1e-9
nu = c / lam
# ASSUMPTION: elementary charge (exact SI value; no ledger record yet, see needs file)
QE = 1.602176634e-19
r.emit("lam_nm", lam * 1e9, "nm", 4, ["ch01.cd.g652_link_typ_d1550"])
r.emit("photon_e", h * nu * 1e19, "×10⁻¹⁹ J", 4, ["ch01.const.planck_h", "ch01.const.speed_of_light_c"])

# ---------------- 1. hybrid algebra, random fields ----------------
rng = np.random.default_rng(2)
Rr = 0.8
for _ in range(20):
    Es = rng.normal() + 1j * rng.normal()
    Elo = 3 * (rng.normal() + 1j * rng.normal())
    E = [(Es + Elo) / 2, (Es - Elo) / 2, (Es + 1j * Elo) / 2, (Es - 1j * Elo) / 2]
    Pk = [abs(e) ** 2 for e in E]
    assert abs(sum(Pk) - abs(Es) ** 2 - abs(Elo) ** 2) < 1e-12        # lossless
    iI = Rr * (Pk[0] - Pk[1])
    iQ = Rr * (Pk[2] - Pk[3])
    Ps, Plo = abs(Es) ** 2, abs(Elo) ** 2
    dth = np.angle(Es) - np.angle(Elo)
    assert abs(iI - Rr * math.sqrt(Ps * Plo) * math.cos(dth)) < 1e-12
    # |a+b|^2 - |a-b|^2 = 4 Re(a b*), with b = i E_LO/2: Im(Es E_LO*) = sqrt(Ps Plo) sin(dth)
    assert abs(iQ - Rr * math.sqrt(Ps * Plo) * math.sin(dth)) < 1e-12

# ---------------- 2. shot-noise-limited SNR ----------------
# ASSUMPTION: symbol rate 64 GBd (same as the Chapter 1 coherent example)
RS = 64e9
# ASSUMPTION: photodiode quantum efficiency 0.8 for practical numbers; 1 for the quantum limit
ETA = 0.8
resp = ETA * QE / (h * nu)
r.emit("rs_gbd", RS / 1e9, "GBd", 3)
r.emit("eta", ETA, "1", 2)
r.emit("resp", resp, "A/W", 3, ["ch01.const.planck_h", "ch01.const.speed_of_light_c"])


def snr_shot(ps, plo, eta=1.0, bn=RS / 2):
    """Complex-baseband SNR, two balanced pairs each seeing P_LO/2 of LO power."""
    rr = eta * QE / (h * nu)
    sig = rr ** 2 * ps * plo                       # |I_c|^2
    s_two_sided = QE * rr * plo / 2                # per balanced pair (Ip: q R P'_LO with P'_LO = P_LO/2)
    noise = 2 * s_two_sided * 2 * bn               # two quadratures, two-sided bandwidth 2 B_n
    return sig / noise


ps_test = 1e-6
for plo in (1e-3, 1e-2):
    assert abs(snr_shot(ps_test, plo) - ps_test / (h * nu * RS)) / snr_shot(ps_test, plo) < 1e-12

# ---------------- 3. DP-QPSK sensitivity at the HD threshold ----------------
BER_HD = L("ch02.ir.hd_threshold_4p7e3")
snr_req = brentq(lambda s: cl.qpsk_ber(s) - BER_HD, 0.5, 100)
r.emit("qpsk_snr_req_db", cl.lin2db(snr_req), "dB", 3, ["ch02.ir.hd_threshold_4p7e3"])
r.emit("np_sym_ideal", snr_req, "photons/symbol", 3, ["ch02.ir.hd_threshold_4p7e3"])
r.emit("np_bit_ideal", snr_req / 2, "photons/bit", 3, ["ch02.ir.hd_threshold_4p7e3"])
p_pol_ideal = snr_req * h * nu * RS
p_pol = p_pol_ideal / ETA
r.emit("sens_pol_ideal_dbm", cl.w2dbm(p_pol_ideal), "dBm", 3, ["ch02.ir.hd_threshold_4p7e3"])
r.emit("sens_dp_ideal_dbm", cl.w2dbm(2 * p_pol_ideal), "dBm", 3, ["ch02.ir.hd_threshold_4p7e3"])
r.emit("sens_dp_eta_dbm", cl.w2dbm(2 * p_pol), "dBm", 3, ["ch02.ir.hd_threshold_4p7e3"])
# BPSK with single-quadrature homodyne gains 3 dB (ledger); check: SNR_hom = 2 SNR_het for one quadrature
r.emit("hom_gain", L("ch02.coh.single_quadrature_homodyne_gain"), "dB", 1,
       ["ch02.coh.single_quadrature_homodyne_gain"])

# LO power for shot noise to exceed thermal noise by 10 dB
# ASSUMPTION: input-referred thermal noise current density of the TIA, one-sided
ITH = 20e-12
plo_min = 10 * ITH ** 2 / (QE * resp)
r.emit("ith_pa", ITH * 1e12, "pA/√Hz", 2)
r.emit("plo_min_dbm", cl.w2dbm(plo_min), "dBm", 3)
r.emit("plo_min_mw", plo_min * 1e3, "mW", 3)

# ---------------- 4. amplified links: LO-ASE vs LO-shot ----------------
NF = L("ch01.amp.accelink_mw_nf_max")
# ASSUMPTION: amplifier gain 20 dB (span loss of order the Chapter 1 example)
G_DB = 20.0
G = cl.db2lin(G_DB)
F = cl.db2lin(NF)
nsp = (F * G - 1) / (2 * (G - 1))
ratio = ETA * nsp * (G - 1)          # SNR_shot / SNR_ASE = eta S_ASE / (h nu), S_ASE = nsp h nu (G-1)
r.emit("amp_g_db", G_DB, "dB", 2)
r.emit("amp_nf", NF, "dB", 2, ["ch01.amp.accelink_mw_nf_max"])
r.emit("amp_nsp", nsp, "1", 3, ["ch01.amp.accelink_mw_nf_max"])
r.emit("ase_over_shot_db", cl.lin2db(ratio), "dB", 3, ["ch01.amp.accelink_mw_nf_max"])
assert ratio > 10

r.save()
