"""Worked example 2.6: FEC overheads, net coding gain from threshold BER, the
Gray 16-QAM BER formula used in Chapter 1, and required SNR/OSNR of 400ZR-class
DP-16QAM with CFEC and oFEC.

NCG_HD(p*) = 20 log10 erfcinv(2e-15) - 20 log10 erfcinv(2 p*) + 10 log10 R_c
(Zhang 2017, Eq. (2.5)): the gain in Q^2 (electrical SNR of a binary antipodal
signal) between the uncoded BER 1e-15 and the pre-FEC threshold, minus the rate loss.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import numpy as np
from scipy.optimize import brentq
from scipy.special import erfcinv
import ch02lib as cl

r = Results()
BER_OUT = 1e-15


def ncg_hd(p, rc):
    return 20 * math.log10(erfcinv(2 * BER_OUT)) - 20 * math.log10(erfcinv(2 * p)) + 10 * math.log10(rc)


def h2(p):
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


# ---------------- overheads ----------------
oh = {
    "kp4": 544 / 514 - 1,
    "stair": 255 / 239 - 1,
    "hamming": 128 / 119 - 1,
    "cfec": (255 / 239) * (128 / 119) - 1,
    "ofec": L("ch02.fec.ofec_overhead") / 100,
    "lr800": (126 / 110) * (544 / 514) - 1,
}
assert abs(100 * oh["cfec"] - L("ch02.fec.cfec_overhead")) < 0.05
assert abs(100 * oh["hamming"] - 7.56) < 0.01            # claim text of ch02.fec.cfec_hamming_gain
assert abs(100 * oh["lr800"] - float(cl.cond("ch02.fec.800lr_threshold", "overhead_pct"))) < 0.01
for k, v in oh.items():
    r.emit(f"oh_{k}", 100 * v, "%", 4)

# ---------------- NCG from threshold ----------------
cases = {
    "kp4": (L("ch02.fec.kp4_ber_limit"), oh["kp4"], ["ch02.fec.kp4_ber_limit"]),
    "stair48": (L("ch02.fec.staircase_p_operating"), oh["stair"], ["ch02.fec.staircase_p_operating"]),
    "cfec": (L("ch02.fec.cfec_ber_in"), oh["cfec"], ["ch02.fec.cfec_ber_in"]),
    "ofec": (L("ch02.fec.ofec_ber_threshold"), oh["ofec"], ["ch02.fec.ofec_ber_threshold", "ch02.fec.ofec_overhead"]),
    "lr800": (L("ch02.fec.800lr_threshold"), oh["lr800"], ["ch02.fec.800lr_threshold"]),
}
ncg = {}
for k, (p, o, ins) in cases.items():
    ncg[k] = ncg_hd(p, 1 / (1 + o))
    r.emit(f"ncg_{k}", ncg[k], "dB", 3, ins)
r.emit("q_out_db", 20 * math.log10(math.sqrt(2) * erfcinv(2 * BER_OUT)), "dB", 4)
# staircase: stated 9.41 dB; the formula at its threshold range must bracket it within 0.1 dB
# (Alvarado's 4.7e-3 belongs to a different, 6.25 %-overhead staircase code and is not used here.)
assert abs(ncg["stair48"] - L("ch02.fec.staircase_ncg")) < 0.1
assert abs(ncg["ofec"] - L("ch02.fec.ofec_ncg_qpsk")) < 0.15
r.emit("d_cfec", ncg["cfec"] - L("ch02.fec.cfec_ncg"), "dB", 2, ["ch02.fec.cfec_ncg"])
r.emit("d_ofec", ncg["ofec"] - L("ch02.fec.ofec_ncg_qpsk"), "dB", 2, ["ch02.fec.ofec_ncg_qpsk"])
# threshold implied by stated NCG (inverse), staircase and RS(255,239)
p_st = brentq(lambda p: ncg_hd(p, 1 / (1 + oh["stair"])) - L("ch02.fec.staircase_ncg"), 1e-6, 0.2)
p_rs = brentq(lambda p: ncg_hd(p, 1 / (1 + oh["stair"])) - L("ch02.fec.rs255_ncg"), 1e-8, 0.2)
r.emit("p_stair_implied", p_st, "1", 3, ["ch02.fec.staircase_ncg"])
r.emit("p_rs_implied", p_rs, "1", 3, ["ch02.fec.rs255_ncg"])

# HD (binary symmetric channel) capacity limit at rate 239/255
R239 = 239 / 255
p_cap = brentq(lambda p: 1 - h2(p) - R239, 1e-6, 0.4)
ncg_cap = ncg_hd(p_cap, R239)
r.emit("p_cap_239", p_cap, "1", 3)
r.emit("ncg_cap_239", ncg_cap, "dB", 3)
assert abs((ncg_cap - L("ch02.fec.staircase_ncg")) - L("ch02.fec.staircase_shannon_gap")) < 0.03
assert abs((ncg_cap - L("ch02.fec.rs255_ncg")) - 3.77) < 0.03            # RS gap in record quote
r.emit("stair_gap_calc", ncg_cap - L("ch02.fec.staircase_ncg"), "dB", 2, ["ch02.fec.staircase_ncg"])
r.emit("rs_gap_calc", ncg_cap - L("ch02.fec.rs255_ncg"), "dB", 3, ["ch02.fec.rs255_ncg"])

# ---------------- Gray 16-QAM BER ----------------
# Monte Carlo check of the exact expression (fixed seed)
rng = np.random.default_rng(16)
NS = 400000
snr_mc = cl.db2lin(11.0)
lv = np.array([-3.0, -1.0, 1.0, 3.0])
gray_bits = np.array([[0, 0], [0, 1], [1, 1], [1, 0]])     # Gray labels for -3, -1, 1, 3
idx = rng.integers(0, 4, size=(NS, 2))
sigma = math.sqrt(10 / snr_mc / 2)                          # Es = 10, N0 = Es/SNR, sigma^2 = N0/2
y = lv[idx] + sigma * rng.normal(size=(NS, 2))
dec = np.clip(np.round((y + 3) / 2), 0, 3).astype(int)
errs = (gray_bits[idx] != gray_bits[dec]).sum()
ber_mc = errs / (NS * 4)
ber_ex = float(cl.qam16_ber_exact(snr_mc))
assert abs(ber_mc - ber_ex) < 4 * math.sqrt(ber_ex / (NS * 4)), (ber_mc, ber_ex)
r.emit("mc_snr_db", 11.0, "dB", 3)
r.emit("mc_ber", ber_mc, "1", 3)
r.emit("ex_ber", ber_ex, "1", 3)
r.emit("ap_ber", float(cl.qam16_ber_approx(snr_mc)), "1", 3)

# Chapter 1 threshold reproduction (20 % SD-FEC threshold 2.7e-2)
ber_c1 = L("ch01.cap.soft_fec_threshold_20pct")
snr_c1 = cl.lin2db(brentq(lambda s: float(cl.qam16_ber_approx(s)) - ber_c1, 1, 100))
c1 = json.loads((pathlib.Path(__file__).resolve().parents[1] / "ch01" / "out" / "ex16_gn_optimum.json").read_text())
assert abs(snr_c1 - c1["snr_theory_db"]["value"]) < 1e-6
snr_c1_ex = cl.lin2db(brentq(lambda s: float(cl.qam16_ber_exact(s)) - ber_c1, 1, 100))
r.emit("c1_snr_approx", snr_c1, "dB", 4, ["ch01.cap.soft_fec_threshold_20pct"])
r.emit("c1_snr_exact", snr_c1_ex, "dB", 4, ["ch01.cap.soft_fec_threshold_20pct"])
r.emit("c1_ber", ber_c1, "1", 2, ["ch01.cap.soft_fec_threshold_20pct"])


def snr16(ber, exact=True):
    f = cl.qam16_ber_exact if exact else cl.qam16_ber_approx
    return cl.lin2db(brentq(lambda s: float(f(s)) - ber, 0.5, 1e4))


def snrq(ber):
    return cl.lin2db(brentq(lambda s: float(cl.qpsk_ber(s)) - ber, 0.01, 1e4))


# NCG relative to uncoded 16-QAM: SNR16(1e-15) - SNR16(p*) + 10 log10 R_c
s16_out = snr16(BER_OUT)
r.emit("s16_out", s16_out, "dB", 4)
for k in ("cfec", "ofec", "lr800"):
    p, o, ins = cases[k]
    r.emit(f"ncg16_{k}", s16_out - snr16(p) + 10 * math.log10(1 / (1 + o)), "dB", 3, ins)
ncg16_ofec = r.data["ncg16_ofec"]["value"]
# the OIF CFEC NCG is reproduced only with the 16-QAM reference curve
assert abs(r.data["ncg16_cfec"]["value"] - L("ch02.fec.cfec_ncg")) < 0.05
r.emit("d_cfec16", r.data["ncg16_cfec"]["value"] - L("ch02.fec.cfec_ncg"), "dB", 2, ["ch02.fec.cfec_ncg"])
assert abs(ncg16_ofec - L("ch02.fec.ofec_ncg_16qam")) < 0.15
r.emit("d_ofec16", ncg16_ofec - L("ch02.fec.ofec_ncg_16qam"), "dB", 2, ["ch02.fec.ofec_ncg_16qam"])
# QPSK reference NCG equals the binary formula (QPSK = two BPSK)
assert abs((snrq(BER_OUT) - snrq(cases["ofec"][0]) + 10 * math.log10(1 / (1 + oh["ofec"]))) - ncg["ofec"]) < 1e-6
# approximation error of 3/8 erfc at the CFEC threshold
r.emit("apx_err_cfec", abs(snr16(cases["cfec"][0], False) - snr16(cases["cfec"][0])), "dB", 1)

# ---------------- required SNR / OSNR, 400ZR-class DP-16QAM ----------------
c = L("ch01.const.speed_of_light_c")
lam = float(cl.cond("ch01.cd.g652_link_typ_d1550", "wavelength_nm")) * 1e-9
bref = c * L("ch01.osnr.gsup39_bref_typical") * 1e-9 / lam ** 2
RS = L("ch02.sym.400zr_symbol_rate") * 1e9
conv = 10 * math.log10(RS / bref)
r.emit("bref_ghz", bref / 1e9, "GHz", 4, ["ch01.osnr.gsup39_bref_typical"])
r.emit("osnr_conv", conv, "dB", 3, ["ch02.sym.400zr_symbol_rate", "ch01.osnr.gsup39_bref_typical"])
for k in ("cfec", "ofec", "kp4", "lr800"):
    s = snr16(cases[k][0])
    r.emit(f"snrreq_{k}", s, "dB", 4, cases[k][2])
    r.emit(f"osnrreq_{k}", s + conv, "dB", 4, cases[k][2] + ["ch02.sym.400zr_symbol_rate"])
rosnr = float(cl.cond("ch06.zr.400zr_vs_800zr_baud", "rosnr_400zr_dB"))
r.emit("rosnr_zr", rosnr, "dB", 3, ["ch06.zr.400zr_vs_800zr_baud"])
r.emit("rosnr_margin", rosnr - (r.data["snrreq_cfec"]["value"] + conv), "dB", 3, ["ch06.zr.400zr_vs_800zr_baud"])
r.emit("cfec_vs_ofec_snr", r.data["snrreq_cfec"]["value"] - r.data["snrreq_ofec"]["value"], "dB", 3)

# GMI at the CFEC threshold SNR (link to 2.5): bit per 2-D symbol and implied gap
s_cf = cl.db2lin(r.data["snrreq_cfec"]["value"])
gmi = 2 * cl.ask_gmi(4, s_cf)
r.emit("gmi_at_cfec", gmi, "bit/2D", 4)
r.emit("net_bits_cfec", 4 / (1 + oh["cfec"]), "bit/2D", 4)
r.emit("cap_at_cfec", math.log2(1 + s_cf), "bit/2D", 4)

# ---------------- figure: NCG_HD vs threshold BER for three overheads ----------------
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.4, 4.0))
pp = np.logspace(-5, math.log10(4e-2), 300)
for i, o in enumerate((oh["kp4"], oh["cfec"], oh["lr800"])):
    ax.semilogx(pp, [ncg_hd(p, 1 / (1 + o)) for p in pp], color=cl.COLORS[i], label=f"overhead {100 * o:.1f} %")
pts = [("KP4", "kp4"), ("staircase", "stair48"), ("CFEC", "cfec"), ("oFEC", "ofec"), ("800LR", "lr800")]
offs = {"kp4": (-10, 8), "stair48": (-60, 4), "cfec": (-42, 10), "ofec": (8, -12), "lr800": (6, -14)}
for lab, k in pts:
    p, o, _ = cases[k]
    ax.plot(p, ncg[k], "o", color=cl.GRAY, ms=5)
    ax.annotate(lab, (p, ncg[k]), textcoords="offset points", xytext=offs[k], fontsize=9)
ax.plot(L("ch02.fec.staircase_p_operating"), L("ch02.fec.staircase_ncg"), "s", mfc="none", color=cl.COLORS[3], ms=7,
        label="stated NCG (staircase, CFEC, oFEC)")
ax.plot(L("ch02.fec.cfec_ber_in"), L("ch02.fec.cfec_ncg"), "s", mfc="none", color=cl.COLORS[3], ms=7)
ax.plot(L("ch02.fec.ofec_ber_threshold"), L("ch02.fec.ofec_ncg_qpsk"), "s", mfc="none", color=cl.COLORS[3], ms=7)
ax.set_xlabel("pre-FEC threshold BER p*")
ax.set_ylabel("NCG at output BER 1e-15 (dB)")
ax.set_ylim(5, 12.5)
ax.legend(fontsize=8.5, loc="lower right")
cl.savefig(fig, "fec_ncg")

r.save()
