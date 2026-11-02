"""Chapter 1 helpers shared by the worked-example scripts.

This module only defines functions; running it (as `make calc` does for every
*.py in this folder) has no side effects.

* rec(), cond(), parse_field(): read ledger records, their `conditions`, and
  numbers embedded in string-valued model records, so that every input still
  traces to a ledger id.
* unit conversions between the units used in the ledger and SI.
* figure style: transparent background, mid-gray axes, no pure black, so the
  SVGs read on light and dark pages.
"""
import math
import re
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch01"

LN10_10 = 10.0 / math.log(10.0)   # 4.3429...: alpha_dB = LN10_10 * alpha


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    """A value from the `conditions` block of ledger record `rid`."""
    return rec(rid)["conditions"][key]


def parse_field(rid, label, where="value"):
    """Extract a number that follows `label=` in a string-valued ledger field.

    Used for the Poggiolini 2012 reference-system record, whose value is a
    string such as 'Ls=100 km; ... D=16.5 ps/(nm·km), γ=1.3 ...'.
    """
    r = rec(rid)
    text = r["value"] if where == "value" else r["conditions"][where]
    m = re.search(re.escape(label) + r"\s*=\s*([-+0-9.eE]+)", str(text))
    if not m:
        raise KeyError(f"{label} not found in {rid}.{where}: {text!r}")
    return float(m.group(1))


# ---------- unit conversions ----------
def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


def w2dbm(p):
    return 10.0 * math.log10(p / 1e-3)


def dbm2w(p):
    return 1e-3 * 10.0 ** (p / 10.0)


def alpha_np_per_m(alpha_db_per_km):
    """dB/km -> 1/m (power attenuation coefficient)."""
    return alpha_db_per_km / LN10_10 / 1e3


def d_si(d_ps_nm_km):
    """ps/(nm·km) -> s/m^2."""
    return d_ps_nm_km * 1e-12 / (1e-9 * 1e3)


def beta2_from_d(d_ps_nm_km, lam_m, c):
    """beta2 [s^2/m] = -D lambda^2 / (2 pi c)."""
    return -d_si(d_ps_nm_km) * lam_m ** 2 / (2 * math.pi * c)


def beta2_ps2_per_km(b2_si):
    return b2_si * 1e24 * 1e3


def leff(alpha_m, length_m):
    return (1.0 - math.exp(-alpha_m * length_m)) / alpha_m


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
    fig.savefig(FIGDIR / f"{name}.svg", format="svg", bbox_inches="tight", transparent=True, metadata={"Date": None})
