"""Worked example 2.4: complexity of the coherent DSP chain per bit.

* CD: delay spread (Chapter 1, Problem 3), FIR length from the all-pass impulse
  response (Ip 2008 form, Savory bound check), overlap-save FFT cost (derivation
  reproduces Ip's C_FD form), optimum FFT size, time- vs frequency-domain.
* 2x2 MIMO: taps needed for PMD; 4 N complex multiplications per symbol.
* Carrier recovery: Pfau linewidth tolerances at the example symbol rate.
* Totals in complex multiplications per bit, for 1000 km and for a 120 km DCI link.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import numpy as np
import ch02lib as cl

r = Results()
c = L("ch01.const.speed_of_light_c")
D = L("ch01.cd.g652_link_typ_d1550")
lam = float(cl.cond("ch01.cd.g652_link_typ_d1550", "wavelength_nm")) * 1e-9
Dsi = cl.d_si(D)
beta2 = Dsi * lam ** 2 / (2 * math.pi * c)        # |beta2| in s^2/m
r.emit("D", D, "ps/(nm·km)", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("beta2", beta2 * 1e27, "ps²/km", 3, ["ch01.cd.g652_link_typ_d1550"])

# ASSUMPTION: 64 GBd DP-16QAM, 1000 km (Chapter 1, Problem 3); 2 samples per symbol in the CD stage
RS = 64e9
LEN = 1000e3
NSS = 2.0
BITS_SYM = 8.0           # DP-16QAM gross bits per dual-pol symbol
r.emit("rs_gbd", RS / 1e9, "GBd", 3)
r.emit("len_km", LEN / 1e3, "km", 4)
r.emit("nss", NSS, "samples/symbol", 2)

# ---- CD delay spread (Chapter 1 Problem 3) ----
dtau = Dsi * LEN * lam ** 2 * RS / c
r.emit("dtau_ns", dtau * 1e9, "ns", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("dtau_sym", dtau * RS, "symbols", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("dl_ns_nm", D * LEN / 1e3 / 1e3, "ns/nm", 3, ["ch01.cd.g652_link_typ_d1550"])

# ---- FIR length: Ip N = 2 pi |beta2| L R_s^2 (M/K)^2 ----


def n_cd(b2, length, rs, nss):
    return 2 * math.pi * b2 * length * rs ** 2 * nss ** 2


N_ip = n_cd(beta2, LEN, RS, NSS)
N_ip15 = n_cd(beta2, LEN, RS, 1.5)
assert abs(N_ip - dtau * RS * NSS * NSS) / N_ip < 1e-12     # N = (spread over full sampled band)/T_sample
r.emit("ncd_2", N_ip, "taps", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("ncd_15", N_ip15, "taps", 3, ["ch01.cd.g652_link_typ_d1550", "ch02.dsp.fse_oversampling_min"])
assert L("ch02.dsp.fse_oversampling_min") == 1.5

# ---- Savory's 2.2 taps per 1000 ps/nm at 10.7 GBd ----
RS_SAV = float(cl.cond("ch02.dsp.savory_taps_per_ps_nm", "symbol_rate_GBd")) * 1e9
dl_1000 = 1000e-12 / 1e-9                         # 1000 ps/nm in s/m
full_band = dl_1000 * lam ** 2 * (NSS * RS_SAV) ** 2 / c   # spread over full sampled band / T_sample
sig_band_ratio = L("ch02.dsp.savory_taps_per_ps_nm") / full_band
r.emit("sav_fullband", full_band, "taps per 1000 ps/nm", 3, ["ch02.dsp.savory_taps_per_ps_nm"])
r.emit("sav_ratio", sig_band_ratio, "1", 3, ["ch02.dsp.savory_taps_per_ps_nm"])
r.emit("sav_bw_rs", sig_band_ratio * NSS, "R_s", 3, ["ch02.dsp.savory_taps_per_ps_nm"])
taps_sav_scaled = L("ch02.dsp.savory_taps_per_ps_nm") * (D * LEN / 1e3) / 1000 * (RS / RS_SAV) ** 2
r.emit("ncd_savory_scaled", taps_sav_scaled, "taps", 3, ["ch02.dsp.savory_taps_per_ps_nm", "ch01.cd.g652_link_typ_d1550"])

# ---- overlap-save FDE ----


def fde_cost_per_sample(n_taps, nfft):
    """Complex mults per output sample, one polarization: FFT + IFFT (radix-2: (N/2)log2 N each)
    plus N_FFT spectral multiplications, divided by the B = N_FFT - N + 1 new samples per block."""
    b = nfft - n_taps + 1
    if b <= 0:
        return float("inf")
    return nfft * (math.log2(nfft) + 1) / b


def ip_cfd_per_symbol(n_taps, b):
    """Ip 2008 form for the 2x2 FD equalizer: (N+B-1)[2 log2(N+B-1) + 4]/B per symbol."""
    nf = n_taps + b - 1
    return nf * (2 * math.log2(nf) + 4) / b


# derivation check: 2 pols x (FFT+IFFT) + 2x2 spectral butterfly == Ip's form
for nt, nf in ((101, 512), (1001, 4096)):
    b = nf - nt + 1
    mine = (2 * 2 * (nf / 2) * math.log2(nf) + 4 * nf) / b
    assert abs(mine - ip_cfd_per_symbol(nt, b)) < 1e-9

N_int = int(math.ceil(N_ip))
best = min((fde_cost_per_sample(N_int, 2 ** k), 2 ** k) for k in range(8, 20))
cost_fd_sample, NFFT = best
cost_td_sample = N_int
r.emit("nfft_opt", NFFT, "points", 5, ["ch01.cd.g652_link_typ_d1550"])
r.emit("fd_per_sample", cost_fd_sample, "mult/sample", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("td_per_sample", cost_td_sample, "mult/sample", 4, ["ch01.cd.g652_link_typ_d1550"])
r.emit("fd_td_ratio", cost_td_sample / cost_fd_sample, "1", 3, ["ch01.cd.g652_link_typ_d1550"])
# crossover length at which TD and FD cost the same (scan)
cross = None
for Lk in np.arange(1, 400, 0.5):
    n = int(math.ceil(n_cd(beta2, Lk * 1e3, RS, NSS)))
    fd = min(fde_cost_per_sample(n, 2 ** k) for k in range(4, 18))
    if n > fd:
        cross = Lk
        break
r.emit("td_fd_cross_km", cross, "km", 2, ["ch01.cd.g652_link_typ_d1550"])
cd_per_sym = 2 * NSS * cost_fd_sample      # two polarizations, NSS samples per symbol
r.emit("cd_per_sym", cd_per_sym, "mult/symbol", 3, ["ch01.cd.g652_link_typ_d1550"])

# ---- 2x2 MIMO ----
PMDQ = L("ch01.pmd.g652d_pmdq")
mean_dgd = PMDQ * math.sqrt(LEN / 1e3) * 1e-12
r.emit("dgd_mean_ps", mean_dgd * 1e12, "ps", 3, ["ch01.pmd.g652d_pmdq"])
r.emit("dgd3_sym", 3 * mean_dgd * RS, "symbols", 3, ["ch01.pmd.g652d_pmdq"])
# ASSUMPTION: 15 T/2-spaced taps per MIMO filter (PMD, residual CD, filtering), outputs at 1 per symbol
NMIMO = 15
mimo_per_sym = 4 * NMIMO                      # Ip: 4 N R_s complex mult/s
r.emit("n_mimo", NMIMO, "taps", 2)
r.emit("mimo_per_sym", mimo_per_sym, "mult/symbol", 3, ["ch02.dsp.td_fir_complexity"])
# update (LMS/CMA): one more 4N per symbol if adapted every symbol
mimo_upd_per_sym = 4 * NMIMO
r.emit("mimo_upd_per_sym", mimo_upd_per_sym, "mult/symbol", 3)

# ---- carrier recovery: Pfau tolerances ----
ins_pf = ["ch02.dsp.bps_lw_4qam", "ch02.dsp.bps_lw_16qam", "ch02.dsp.bps_lw_64qam", "ch02.dsp.bps_lw_256qam"]
for name, rid in zip(("4", "16", "64", "256"), ins_pf):
    r.emit(f"lw_{name}_mhz", L(rid) * RS / 1e6, "MHz", 3, [rid])
    r.emit(f"lw_{name}_phase_deg", math.degrees(math.sqrt(2 * math.pi * L(rid))), "°", 3, [rid])
RS_ZR = L("ch02.sym.400zr_symbol_rate") * 1e9
r.emit("lw_16_zr_mhz", L("ch02.dsp.bps_lw_16qam") * RS_ZR / 1e6, "MHz", 3,
       ["ch02.dsp.bps_lw_16qam", "ch02.sym.400zr_symbol_rate"])
ratios = [L(ins_pf[i]) / L(ins_pf[i + 1]) for i in range(3)]
r.emit("lw_ratio_4_16", ratios[0], "1", 3, ins_pf)
r.emit("lw_ratio_16_64", ratios[1], "1", 3, ins_pf)
r.emit("lw_ratio_64_256", ratios[2], "1", 3, ins_pf)
# BPS cost: ASSUMPTION B = 32 test phases (inside Pfau's 16-64), about one complex
# multiplication-equivalent per test phase per symbol per polarization
B_BPS = 32
lo, hi = L("ch02.dsp.bps_test_phases", "lo"), L("ch02.dsp.bps_test_phases", "hi")
assert lo <= B_BPS <= hi
cpr_per_sym = 2 * B_BPS
r.emit("b_bps", B_BPS, "test phases", 2, ["ch02.dsp.bps_test_phases"])
r.emit("cpr_per_sym", cpr_per_sym, "mult/symbol", 3, ["ch02.dsp.bps_test_phases"])

# ---- totals ----
tot_sym = cd_per_sym + mimo_per_sym + mimo_upd_per_sym + cpr_per_sym
r.emit("tot_per_sym", tot_sym, "mult/symbol", 3)
r.emit("tot_per_bit", tot_sym / BITS_SYM, "mult/bit", 3)
r.emit("cd_share_pct", 100 * cd_per_sym / tot_sym, "%", 2)
r.emit("tot_rate_tmult", tot_sym * RS / 1e12, "×10¹² mult/s", 3)

# DCI: ASSUMPTION 120 km (upper end of the ZR application range) at the same symbol rate
LDCI = 120e3
n_dci = int(math.ceil(n_cd(beta2, LDCI, RS, NSS)))
fd_dci = min(fde_cost_per_sample(n_dci, 2 ** k) for k in range(4, 18))
cd_dci_sym = 2 * NSS * min(fd_dci, n_dci)
tot_dci = cd_dci_sym + mimo_per_sym + mimo_upd_per_sym + cpr_per_sym
r.emit("dci_km", LDCI / 1e3, "km", 3)
r.emit("dci_ncd", n_dci, "taps", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("dci_cd_per_sym", cd_dci_sym, "mult/symbol", 3, ["ch01.cd.g652_link_typ_d1550"])
r.emit("dci_tot_per_bit", tot_dci / BITS_SYM, "mult/bit", 3)
r.emit("dci_cd_share_pct", 100 * cd_dci_sym / tot_dci, "%", 2)

# export a small table for ex27 (complexity per symbol vs length and symbol rate)
table = {}
for rs in (32e9, 64e9, 96e9, 128e9, 192e9):
    row = {}
    for Lk in (120, 1000, 3000):
        n = int(math.ceil(n_cd(beta2, Lk * 1e3, rs, NSS)))
        fd = min(fde_cost_per_sample(n, 2 ** k) for k in range(4, 20))
        row[str(Lk)] = 2 * NSS * min(fd, n) + mimo_per_sym + mimo_upd_per_sym + cpr_per_sym
    table[str(int(rs / 1e9))] = row
cl.OUT.mkdir(exist_ok=True)
(cl.OUT / "ex24_complexity_table.json.txt").write_text(json.dumps(table, indent=1))
r.save()
