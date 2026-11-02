"""Chapter 6 helpers shared by the worked-example scripts.

Defines functions only; running it (as `make calc` does for every *.py in this
folder) has no side effects.

* Reuses the Chapter 1 helpers (ledger access, unit conversions) read-only.
* GN-model coefficient (closed form, Poggiolini 2012 Eq. (15)), copied from
  book/calc/ch01/ex16_gn_optimum.py so that Chapter 6 scripts can evaluate
  multi-span routes with ROADMs.
* WSS passband model (rectangle convolved with a Gaussian, raised to the
  number of cascaded filters), ledger equation ch06.eq.wss_passband.
* Figure style identical to Chapter 1, saved to book/figs/ch06/.
"""
import math
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))           # book/calc  (common.py)
sys.path.insert(0, str(HERE.parent / "ch01"))  # book/calc/ch01 (ch01lib.py, read-only)

import ch01lib as cl  # noqa: E402
from common import L, _ledger  # noqa: E402

FIGDIR = HERE.parents[1] / "figs" / "ch06"

db2lin, lin2db, w2dbm, dbm2w = cl.db2lin, cl.lin2db, cl.w2dbm, cl.dbm2w
alpha_np_per_m, leff, beta2_from_d = cl.alpha_np_per_m, cl.leff, cl.beta2_from_d
LN10_10 = cl.LN10_10


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    return rec(rid)["conditions"][key]


def from_text(rid, pattern, field="claim"):
    """Extract a number from a ledger text field with a regex having one group."""
    text = str(rec(rid)[field])
    m = re.search(pattern, text)
    if not m:
        raise KeyError(f"{pattern!r} not found in {rid}.{field}: {text!r}")
    return float(m.group(1))


# ---------------------------------------------------------------- constants
def consts():
    h = L("ch01.const.planck_h")
    c = L("ch01.const.speed_of_light_c")
    return h, c


# ---------------------------------------------------------------- GN model
def mu_coeff(gamma, alpha_db, D, Lspan_m, Rs, Df, Nch, lam, c, Bch=None):
    """Closed-form GN coefficient mu [Hz^2/W^2], G_NLI(0) = mu G_WDM^3 for one span.

    gamma in 1/(W m), alpha_db in dB/km, D in ps/(nm km), lengths in m, rates in Hz.
    """
    Bch = Rs if Bch is None else Bch
    a = alpha_np_per_m(alpha_db)
    le = leff(a, Lspan_m)
    lea = 1.0 / a
    b2 = abs(beta2_from_d(D, lam, c))
    arg = (math.pi ** 2 / 2) * b2 * lea * Bch ** 2 * Nch ** (2 * Bch / Df)
    return (8.0 / 27.0) * gamma ** 2 * le ** 2 * math.asinh(arg) / (math.pi * b2 * lea)


def gamma_from(n2, aeff_um2, lam, c):
    """gamma = n2 omega / (c A_eff) in 1/(W m)."""
    return n2 * 2 * math.pi * (c / lam) / (c * aeff_um2 * 1e-12)


# ---------------------------------------------------------------- WSS model
def wss_power_transfer(f, B, bw_otf, n=1):
    """Ledger eq. ch06.eq.wss_passband: rect(B) * Gaussian(BW_OTF), to the power n.

    f, B, bw_otf in the same unit (GHz). Normalised to unit peak for B >> sigma.
    """
    from scipy.special import erf
    import numpy as np
    s = bw_otf / (2 * math.sqrt(2 * math.log(2)))
    single = 0.5 * (erf((B / 2 - np.asarray(f)) / (math.sqrt(2) * s))
                    - erf((-B / 2 - np.asarray(f)) / (math.sqrt(2) * s)))
    return single ** n


def bw_at(level_db, B, bw_otf, n=1):
    """Full width (same unit as B) at which the cascade transfer is level_db below peak."""
    from scipy.optimize import brentq
    peak = float(wss_power_transfer(0.0, B, bw_otf, n))
    target = peak * 10 ** (-level_db / 10)
    x = brentq(lambda f: float(wss_power_transfer(f, B, bw_otf, n)) - target, 0.0, B)
    return 2 * x


def zf_penalty_db(Rs, B, bw_otf, n, npts=4001):
    """Zero-forcing noise-enhancement penalty for a Nyquist (zero roll-off) signal.

    Penalty = 10 log10 < 1/|H(f)|^2 > over |f| <= Rs/2, with |H|^2 = power transfer.
    Assumes all noise is added after the filters (upper bound for a linear equalizer).
    """
    import numpy as np
    f = np.linspace(-Rs / 2, Rs / 2, npts)
    h2 = wss_power_transfer(f, B, bw_otf, n)
    return 10 * math.log10(float(np.mean(1.0 / h2)))


# ---------------------------------------------------------------- QAM thresholds
def snr_at_ber_16qam(ber):
    """SNR (linear) where Gray 16-QAM BER ~ (3/8) erfc(sqrt(SNR/10)) equals ber (Section 1.6)."""
    from scipy.optimize import brentq
    from scipy.special import erfc
    return brentq(lambda s: 3 / 8 * erfc(math.sqrt(s / 10)) - ber, 0.5, 200.0)


def snr_at_ber_qpsk(ber):
    """SNR (linear, per symbol, both quadratures) where Gray QPSK BER = (1/2) erfc(sqrt(SNR/2))."""
    from scipy.optimize import brentq
    from scipy.special import erfc
    return brentq(lambda s: 0.5 * erfc(math.sqrt(s / 2)) - ber, 0.1, 200.0)


# ---------------------------------------------------------------- figures
GRAY = cl.GRAY
COLORS = cl.COLORS


def setup_mpl():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        "figure.facecolor": "none",
        "axes.facecolor": "none",
        "svg.hashsalt": "optic_cables",
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
    fig.savefig(FIGDIR / f"{name}.svg", format="svg", bbox_inches="tight", transparent=True,
                metadata={"Date": None})
