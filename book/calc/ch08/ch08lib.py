"""Chapter 8 helpers shared by the worked-example scripts.

This module only defines functions and constants; running it (as `make calc`
does for every *.py in this folder) has no side effects.

* rec(), cond(): read ledger records and their `conditions`.
* unit conversions (statute mile, dB), fiber latency from the Chapter 1 group index.
* figure style: same as Chapter 1 (transparent background, mid-gray axes, no
  pure black, fixed svg.hashsalt, no date metadata).
"""
import math
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger, L  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch08"

# DEFINITION (not a measured value): the international statute mile is exactly
# 1609.344 m (international yard of 0.9144 m, 1760 yd per mile). No ledger record
# exists; listed in chapters/ch08_needs.md.
MI_KM = 1.609344


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    return rec(rid)["conditions"][key]


def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


NG_ID = "ch01.fiber.smf28ultra_group_index_1550"
C_ID = "ch01.const.speed_of_light_c"


def us_per_km():
    """One-way group delay per km of standard SMF at 1550 nm, in microseconds."""
    return L(NG_ID) / L(C_ID) * 1e3 * 1e6


# ---------- figure style (identical to Chapter 1) ----------
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
    fig.savefig(FIGDIR / f"{name}.svg", format="svg", bbox_inches="tight", transparent=True,
                metadata={"Date": None})
