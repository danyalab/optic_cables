"""Chapter 4 helpers shared by the worked-example scripts.

This module only defines functions; running it (as `make calc` does for every
*.py in this folder) has no side effects.

* rec(), cond(), cond_num(): read ledger records and numbers stored in their
  `conditions` block, so that every input still traces to a ledger id.
* GN-model coefficient (Poggiolini 2012, eq. (15), book notation), reused from
  Section 1.6 for the coherent-pluggable reach example.
* figure style identical to Chapter 1 (transparent, mid-gray axes, no black).
"""
import math
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch04"


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    """A value from the `conditions` block of ledger record `rid`."""
    return rec(rid)["conditions"][key]


def cond_num(rid, key):
    """First number inside a (possibly string-valued) condition, e.g. '53.125 GBd PAM4' -> 53.125."""
    v = cond(rid, key)
    if isinstance(v, (int, float)):
        return float(v)
    m = re.search(r"[-+]?[0-9]*\.?[0-9]+(?:[eE][-+]?[0-9]+)?", str(v))
    if not m:
        raise KeyError(f"no number in {rid}.conditions.{key}: {v!r}")
    return float(m.group(0))


def cond_pairs(rid, key):
    """Parse 'A 1.0, B 2.0, ...' or 'A=1, B=2' strings into a dict of floats."""
    out = {}
    for part in str(cond(rid, key)).split(","):
        m = re.search(r"([A-Za-z_0-9/]+?)\s*[= ]\s*([0-9.]+)\s*$", part.strip().split("(")[0].strip())
        if m:
            out[m.group(1)] = float(m.group(2))
    return out


def year_frac(datestr):
    """'2017-12-06' -> 2017.93; '2017-12' -> 2017.96; '2025-Q2' -> 2025.375."""
    s = str(datestr)
    m = re.match(r"(\d{4})-Q(\d)", s)
    if m:
        return int(m.group(1)) + (int(m.group(2)) - 1) / 4 + 0.125
    parts = [int(p) for p in s.split("-")]
    y = parts[0]
    mo = parts[1] if len(parts) > 1 else 7
    d = parts[2] if len(parts) > 2 else 15
    return y + (mo - 1) / 12 + (d - 1) / 365


# ---------- unit conversions ----------
def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


def w2dbm(p):
    return 10.0 * math.log10(p / 1e-3)


def dbm2w(p):
    return 1e-3 * 10.0 ** (p / 10.0)


def pj_per_bit(watts, gbps):
    """W / (Gb/s) = nJ/bit; times 1000 gives pJ/bit."""
    return watts / gbps * 1e3


# ---------- GN model (Section 1.6) ----------
def mu_coeff(gamma, alpha_db_km, D_ps_nm_km, Lspan_m, Rs, Df, Nch, lam, c):
    """Coefficient mu [Hz^2/W^2] with G_NLI = mu * G_WDM^3 for one span (Poggiolini 2012 eq. 15)."""
    a = alpha_db_km / (10.0 / math.log(10.0)) / 1e3
    le = (1.0 - math.exp(-a * Lspan_m)) / a
    lea = 1.0 / a
    b2 = abs(D_ps_nm_km * 1e-6 * lam ** 2 / (2 * math.pi * c))
    arg = (math.pi ** 2 / 2) * b2 * lea * Rs ** 2 * Nch ** (2 * Rs / Df)
    return (8.0 / 27.0) * gamma ** 2 * le ** 2 * math.asinh(arg) / (math.pi * b2 * lea), b2


# ---------- figure style ----------
GRAY = "#8a8a8a"
COLORS = ["#2f7fd8", "#e2622c", "#1a9f73", "#7a64dc", "#d2477a", "#b08600", "#5b8a99"]


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
