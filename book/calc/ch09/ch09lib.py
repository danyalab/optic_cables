"""Chapter 9 helpers shared by the worked-example scripts.

This module only defines functions; running it (as `make calc` does for every
*.py in this folder) has no side effects.

* rec(), cond(), parse_num(): read ledger records, their `conditions`, and
  numbers embedded in string fields, so that every input still traces to a
  ledger id.
* unit conversions (dB, dBm, attenuation, dispersion) and the Chapter 1
  closed-form GN model (Section 1.6), re-implemented here so that Chapter 9
  results do not depend on Chapter 1 output files.
* figure style identical to Chapter 1 (transparent, mid-gray axes, no black).
"""
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger, L  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch09"
OUT = pathlib.Path(__file__).resolve().parent / "out"


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    """A value from the `conditions` block of ledger record `rid`."""
    return rec(rid)["conditions"][key]


def num(x):
    """Float from a ledger field that may be a string such as '3.691e7'."""
    return float(x)


def parse_num(rid, pattern, field="notes"):
    """First number captured by regex `pattern` in a string field of `rid`."""
    text = str(rec(rid)[field] if field in ("notes", "quote", "claim", "value")
               else rec(rid)["conditions"][field])
    m = re.search(pattern, text)
    if not m:
        raise KeyError(f"{pattern!r} not found in {rid}.{field}: {text!r}")
    return float(m.group(1).replace(",", ""))


# ---------- constants from the ledger ----------
def c_light():
    return L("ch01.const.speed_of_light_c")


def h_planck():
    return L("ch01.const.planck_h")


# ---------- unit conversions ----------
LN10_10 = 10.0 / math.log(10.0)


def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


def w2dbm(p):
    return 10.0 * math.log10(p / 1e-3)


def dbm2w(p):
    return 1e-3 * 10.0 ** (p / 10.0)


def alpha_np_per_m(alpha_db_per_km):
    return alpha_db_per_km / LN10_10 / 1e3


def leff(alpha_m, length_m):
    return (1.0 - math.exp(-alpha_m * length_m)) / alpha_m


def beta2_abs(d_ps_nm_km, lam_m):
    """|beta2| [s^2/m] from D [ps/(nm km)]: |beta2| = D lambda^2 / (2 pi c)."""
    d_si = d_ps_nm_km * 1e-12 / (1e-9 * 1e3)
    return d_si * lam_m ** 2 / (2 * math.pi * c_light())


def bref_hz(lam_m, dlam_m):
    """OSNR reference bandwidth in Hz for a wavelength interval dlam at lam."""
    return c_light() * dlam_m / lam_m ** 2


# ---------- GN model (Chapter 1, Section 1.6) ----------
def gn_mu(gamma_per_w_m, alpha_db_km, d_ps_nm_km, span_m, bch_hz, df_hz, nch, lam_m):
    """mu [Hz^2/W^2] with G_NLI(0) = mu * G_WDM^3 for one span (closed form,
    Poggiolini 2012 Eq. (15) in book notation)."""
    a = alpha_np_per_m(alpha_db_km)
    le = leff(a, span_m)
    lea = 1.0 / a
    b2 = beta2_abs(d_ps_nm_km, lam_m)
    arg = (math.pi ** 2 / 2) * b2 * lea * bch_hz ** 2 * nch ** (2 * bch_hz / df_hz)
    mu = (8.0 / 27.0) * gamma_per_w_m ** 2 * le ** 2 * math.asinh(arg) / (math.pi * b2 * lea)
    return mu, arg


def gn_span_optimum(mu, g_ase_w_per_hz):
    """Optimum PSD [W/Hz] and one-span maximum GSNR (linear) in the PSD form:
    G_opt = (G_ASE / (2 mu))^(1/3), SNR_max = (2/3) G_opt / G_ASE."""
    g_opt = (g_ase_w_per_hz / (2 * mu)) ** (1.0 / 3.0)
    return g_opt, (2.0 / 3.0) * g_opt / g_ase_w_per_hz


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
        "svg.hashsalt": "optic_cables_ch09",
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
