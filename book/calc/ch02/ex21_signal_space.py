"""Worked example 2.1: bit-rate bookkeeping and raised-cosine occupied bandwidth.

R_b = N_pol R_s log2(M) (gross, before removing FEC and pilot overhead); occupied
bandwidth (1 + rho) R_s.  Checks: 400ZR line rate (OIF IA), 100G-FR PAM4 lane,
CableLabs 200G DP-QPSK with oFEC.  Also verifies numerically that the raised-cosine
spectrum satisfies the Nyquist ISI-free criterion (folded spectrum is flat) and
draws Figure 2.1.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch02lib as cl

r = Results()

# ---------------- 400ZR ----------------
RS = L("ch02.sym.400zr_symbol_rate")           # GBd
BPS = L("ch02.sym.400zr_bits_per_symbol")      # bit per dual-pol symbol
NPOL, M = 2, 16
assert BPS == NPOL * math.log2(M)
rb_gross = NPOL * RS * math.log2(M)
assert abs(rb_gross - L("ch02.sym.400zr_line_rate")) < 1e-9, "400ZR line rate not reproduced"
ins = ["ch02.sym.400zr_symbol_rate", "ch02.sym.400zr_line_rate", "ch02.sym.400zr_bits_per_symbol"]
r.emit("zr_rb_gross", rb_gross, "Gb/s", 5, ins)
r.emit("zr_rs", RS, "GBd", 7, ins)
pil = L("ch02.sym.400zr_pilot_period")
r.emit("zr_pilot_oh_pct", 100 / pil, "%", 3, ["ch02.sym.400zr_pilot_period"])
rb_nopilot = rb_gross * (1 - 1 / pil)
r.emit("zr_rb_nopilot", rb_nopilot, "Gb/s", 4, ins + ["ch02.sym.400zr_pilot_period"])
# CFEC = staircase (255,239) outer x Hamming (128,119) inner; ledger states ~14.8 % total
cfec_oh_exact = (255 / 239) * (128 / 119) - 1
assert abs(100 * cfec_oh_exact - L("ch02.fec.cfec_overhead")) < 0.05
rb_after_fec = rb_nopilot / (1 + cfec_oh_exact)
r.emit("zr_rb_after_fec", rb_after_fec, "Gb/s", 4, ins + ["ch02.fec.cfec_overhead"])
r.emit("zr_residual_pct", 100 * (rb_after_fec / 400 - 1), "%", 2, ins)
assert 400 < rb_after_fec < 410

# ASSUMPTION: roll-off factor of the transmit pulse (no ledger value for 400ZR)
RHO = 0.1
b_occ = (1 + RHO) * RS
r.emit("rho_assumed", RHO, "1", 2)
r.emit("zr_bocc", b_occ, "GHz", 4, ins)
r.emit("zr_se_net", 400 / b_occ, "bit/s/Hz", 3, ins)
r.emit("zr_se_gross", rb_gross / b_occ, "bit/s/Hz", 3, ins)

# ---------------- 100G-FR PAM4 lane ----------------
RS_FR = L("ch02.sym.lambda_pam4_rate")
rb_fr = 1 * RS_FR * math.log2(4)
r.emit("fr_rs", RS_FR, "GBd", 5, ["ch02.sym.lambda_pam4_rate"])
r.emit("fr_rb_gross", rb_fr, "Gb/s", 5, ["ch02.sym.lambda_pam4_rate"])
kp4 = 514 / 544
r.emit("fr_rb_after_kp4", rb_fr * kp4, "Gb/s", 5, ["ch02.sym.lambda_pam4_rate"])
r.emit("kp4_oh_pct", 100 * (544 / 514 - 1), "%", 3)

# ---------------- CableLabs 200G DP-QPSK with oFEC ----------------
RS_P2 = L("ch02.sym.p2pco_200g_qpsk_rate")
rb_p2 = 2 * RS_P2 * 2
ofec = L("ch02.fec.ofec_overhead") / 100
r.emit("p2_rs", RS_P2, "GBd", 6, ["ch02.sym.p2pco_200g_qpsk_rate"])
r.emit("p2_rb_gross", rb_p2, "Gb/s", 5, ["ch02.sym.p2pco_200g_qpsk_rate"])
r.emit("p2_rb_after_fec", rb_p2 / (1 + ofec), "Gb/s", 4,
       ["ch02.sym.p2pco_200g_qpsk_rate", "ch02.fec.ofec_overhead"])

# ---------------- spectral efficiency history ----------------
r.emit("kikuchi_se", L("ch02.sym.kikuchi_40g_16ghz"), "bit/s/Hz", 2, ["ch02.sym.kikuchi_40g_16ghz"])
r.emit("binary_se", L("ch02.sym.binary_se_limit"), "bit/s/Hz", 2, ["ch02.sym.binary_se_limit"])


# ---------------- raised cosine: Nyquist criterion and figure ----------------
def h_rc(f, rho, T=1.0):
    f = np.abs(f)
    f1 = (1 - rho) / (2 * T)
    f2 = (1 + rho) / (2 * T)
    out = np.zeros_like(f)
    out[f <= f1] = T
    if rho > 0:
        m = (f > f1) & (f <= f2)
        out[m] = T / 2 * (1 + np.cos(np.pi * T / rho * (f[m] - f1)))
    return out


def g_rc(t, rho, T=1.0):
    t = np.asarray(t, float)
    den = 1 - (2 * rho * t / T) ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        g = np.sinc(t / T) * np.cos(np.pi * rho * t / T) / den
    sing = np.isclose(den, 0)
    if rho > 0:
        g[sing] = np.pi / 4 * np.sinc(1 / (2 * rho))
    return g


f = np.linspace(-0.5, 0.5, 2001)[1:-1]   # open interval: the rho = 0 edges are a set of measure zero
for rho in (0.0, 0.1, 0.5, 1.0):
    folded = sum(h_rc(f + k, rho) for k in range(-3, 4))
    assert np.allclose(folded, 1.0, atol=1e-12), "RC spectrum violates Nyquist criterion"
    k = np.arange(-20, 21)
    gk = g_rc(k.astype(float), rho)
    assert abs(gk[20] - 1) < 1e-12 and np.allclose(np.delete(gk, 20), 0, atol=1e-12)

# fraction of RC energy beyond the Nyquist frequency 1/(2T)
ff = np.linspace(0, 1.0, 200001)
for rho, name in ((RHO, "efrac_out_rho"), (0.5, "efrac_out_05")):
    H2 = h_rc(ff, rho) ** 2
    frac = np.trapezoid(H2[ff > 0.5], ff[ff > 0.5]) / np.trapezoid(H2, ff)
    r.emit(name, 100 * frac, "%", 2)

plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(9.5, 3.6))
fp = np.linspace(-1.1, 1.1, 1201)
tp = np.linspace(-5, 5, 2001)
for i, rho in enumerate((0.0, 0.1, 0.5, 1.0)):
    a1.plot(fp, h_rc(fp, rho), color=cl.COLORS[i], label=f"ρ = {rho:g}")
    a2.plot(tp, g_rc(tp, rho), color=cl.COLORS[i], label=f"ρ = {rho:g}")
a1.axvline(0.5, color=cl.GRAY, lw=0.8, ls="--")
a1.axvline(-0.5, color=cl.GRAY, lw=0.8, ls="--")
a1.set_xlabel("frequency f T")
a1.set_ylabel("H(f) / T")
a1.set_title("spectrum")
a2.plot(np.arange(-5, 6), np.zeros(11), "o", color=cl.GRAY, ms=3)
a2.set_xlabel("time t / T")
a2.set_ylabel("g(t)")
a2.set_title("impulse response")
a2.legend(fontsize=9)
fig.tight_layout()
cl.savefig(fig, "raised_cosine")

r.save()
