"""Chapter 2 helpers shared by the worked-example scripts.

This module only defines functions; running it (as `make calc` does for every
*.py in this folder) has no side effects.

* rec(), cond(): read ledger records and their `conditions`.
* Q-function, PAM/QAM error-rate formulas.
* Information rates of ASK/QAM on the AWGN channel by Gauss-Hermite
  quadrature (deterministic, so results are reproducible to all digits):
  mutual information (MI), bit-wise GMI with Gray labels, Maxwell-Boltzmann
  (MB) distributions.
* figure style: transparent background, mid-gray axes, no pure black.
"""
import math
import pathlib
import sys

import numpy as np
from scipy.special import erfc, erfcinv

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch02"
OUT = pathlib.Path(__file__).resolve().parent / "out"


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    return rec(rid)["conditions"][key]


# ---------- conversions ----------
def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


def w2dbm(p):
    return 10.0 * math.log10(p / 1e-3)


def dbm2w(p):
    return 1e-3 * 10.0 ** (p / 10.0)


def d_si(d_ps_nm_km):
    """ps/(nm km) -> s/m^2."""
    return d_ps_nm_km * 1e-12 / (1e-9 * 1e3)


# ---------- error-rate formulas ----------
def qfunc(x):
    return 0.5 * erfc(np.asarray(x) / math.sqrt(2.0))


def qinv(p):
    return math.sqrt(2.0) * erfcinv(2.0 * p)


def pam_ser(M, snr):
    """SER of equiprobable M-PAM, levels +-1, +-3, ..., SNR = E[x^2]/sigma^2."""
    es = (M * M - 1) / 3.0           # mean energy of levels +-1, ..., +-(M-1)
    sigma = np.sqrt(es / np.asarray(snr))
    return 2.0 * (1.0 - 1.0 / M) * qfunc(1.0 / sigma)


def qam16_ber_approx(snr):
    """Gray 16-QAM, nearest-neighbour approximation: (3/8) erfc(sqrt(SNR/10))."""
    return 3.0 / 8.0 * erfc(np.sqrt(np.asarray(snr) / 10.0))


def qam16_ber_exact(snr):
    """Exact Gray 16-QAM BER: per-quadrature Gray 4-PAM, x = sqrt(SNR/5)."""
    x = np.sqrt(np.asarray(snr) / 5.0)
    return 0.75 * qfunc(x) + 0.5 * qfunc(3 * x) - 0.25 * qfunc(5 * x)


def qpsk_ber(snr):
    return 0.5 * erfc(np.sqrt(np.asarray(snr) / 2.0))


# ---------- information rates (1-D ASK, AWGN) ----------
_GH_T, _GH_W = np.polynomial.hermite.hermgauss(160)


def ask_points(M):
    return np.arange(-(M - 1), M, 2, dtype=float)


def gray(i):
    return i ^ (i >> 1)


def mb_probs(M, lam):
    """Maxwell-Boltzmann distribution on M-ASK points (unit spacing 2), P ∝ exp(-lam x^2)."""
    x = ask_points(M)
    p = np.exp(-lam * x * x)
    return p / p.sum()


def entropy(p):
    p = np.asarray(p)
    p = p[p > 0]
    return float(-(p * np.log2(p)).sum())


def _likelihood_terms(x, p, snr):
    """Return scaled points, sigma, and quadrature noise samples."""
    pw = float((p * x * x).sum())
    xs = x / math.sqrt(pw)                # unit average power
    sigma = math.sqrt(1.0 / snr)
    z = math.sqrt(2.0) * sigma * _GH_T     # quadrature abscissae for N(0, sigma^2)
    w = _GH_W / math.sqrt(math.pi)
    return xs, sigma, z, w


def ask_mi(M, snr, p=None):
    """I(X;Y) in bit per real dimension, M-ASK with probabilities p, SNR = P/sigma^2."""
    x = ask_points(M)
    p = np.full(M, 1.0 / M) if p is None else np.asarray(p, float)
    xs, sigma, z, w = _likelihood_terms(x, p, snr)
    mi = 0.0
    for i in range(M):
        d = xs[i] - xs                       # (M,)
        # log p(y|x_j)/p(y|x_i) with y = x_i + z
        expo = -((d[None, :] + z[:, None]) ** 2 - z[:, None] ** 2) / (2 * sigma ** 2)
        mx = expo.max(axis=1, keepdims=True)
        s = np.log2((p[None, :] * np.exp(expo - mx)).sum(axis=1)) + mx[:, 0] / math.log(2)
        mi -= p[i] * float((w * s).sum())
    return mi


def ask_gmi(M, snr, p=None):
    """Bit-wise GMI sum_k I(B_k;Y) for binary-reflected Gray-labelled M-ASK, bit per dimension."""
    m = int(round(math.log2(M)))
    x = ask_points(M)
    p = np.full(M, 1.0 / M) if p is None else np.asarray(p, float)
    xs, sigma, z, w = _likelihood_terms(x, p, snr)
    labels = np.array([gray(i) for i in range(M)])
    bits = (labels[:, None] >> np.arange(m)[None, :]) & 1   # (M, m)
    total = 0.0
    for i in range(M):
        y = xs[i] + z                                    # (Q,)
        lik = p[None, :] * np.exp(-((y[:, None] - xs[None, :]) ** 2) / (2 * sigma ** 2))  # (Q, M)
        den = lik.sum(axis=1)
        for k in range(m):
            b = bits[i, k]
            mask = bits[:, k] == b
            pb = p[mask].sum()
            num = lik[:, mask].sum(axis=1)
            total += p[i] * float((w * np.log2(num / (pb * den))).sum())
    return total


def awgn_cap_1d(snr):
    return 0.5 * math.log2(1.0 + snr)


def snr_for_rate(fun, rate, lo_db=-10.0, hi_db=40.0):
    """SNR (dB) at which fun(snr_lin) == rate, by bisection (fun increasing)."""
    from scipy.optimize import brentq
    return brentq(lambda s: fun(db2lin(s)) - rate, lo_db, hi_db, xtol=1e-7)


# ---------- figure style ----------
GRAY = "#8a8a8a"
COLORS = ["#2f7fd8", "#e2622c", "#1a9f73", "#7a64dc", "#d2477a", "#b08600"]


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "svg.hashsalt": "optic_cables_ch02",
        "savefig.facecolor": "none",
        "savefig.transparent": True,
        "axes.edgecolor": GRAY,
        "axes.labelcolor": GRAY,
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "text.color": GRAY,
        "axes.titlecolor": GRAY,
        "grid.color": GRAY,
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "axes.grid": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "legend.frameon": False,
        "lines.linewidth": 2.0,
        "font.size": 11,
        "svg.fonttype": "none",
    })
    FIGDIR.mkdir(parents=True, exist_ok=True)
    return plt


def savefig(fig, name):
    FIGDIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGDIR / f"{name}.svg", format="svg", bbox_inches="tight",
                transparent=True, metadata={"Date": None})


# ---------- DSP complexity model (Section 2.4), shared with the power model ----------
def n_cd_taps(beta2_abs, length_m, rs, nss):
    """FIR length 2 pi |beta2| L R_s^2 nss^2 (Ip et al. 2008)."""
    return 2 * math.pi * beta2_abs * length_m * rs ** 2 * nss ** 2


def fde_cost_per_sample(n_taps, nfft):
    b = nfft - n_taps + 1
    if b <= 0:
        return float("inf")
    return nfft * (math.log2(nfft) + 1) / b


def ops_per_symbol(beta2_abs, length_m, rs, nss=2.0, n_mimo=15, b_bps=32):
    """Complex multiplications per dual-pol symbol: CD (FD or TD, cheaper), MIMO + update, BPS."""
    n = int(math.ceil(n_cd_taps(beta2_abs, length_m, rs, nss)))
    fd = min(fde_cost_per_sample(n, 2 ** k) for k in range(4, 20))
    return 2 * nss * min(fd, n) + 4 * n_mimo + 4 * n_mimo + 2 * b_bps
