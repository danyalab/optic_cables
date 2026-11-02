"""Chapter 3 helpers shared by the worked-example scripts.

This module only defines functions and constants; running it (as `make calc`
does for every *.py in this folder) has no side effects.

* rec(), cond(): read ledger records and their `conditions`.
* exact SI constants that the ledger does not yet carry (see ch03_needs.md).
* unit conversions and the chapter figure style (transparent background,
  mid-gray axes, no pure black).
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger, L  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch03"

# ---------- constants ----------
H = L("ch01.const.planck_h")            # J/Hz, CODATA (ledger)
C0 = L("ch01.const.speed_of_light_c")   # m/s, CODATA (ledger)
# ASSUMPTION (needs ledger record): elementary charge, exact in the 2019 SI.
# Checked below against the ledger shot-noise RIN record (-155 dB/Hz at 1 mA).
Q_E = 1.602176634e-19                   # C
# ASSUMPTION (needs ledger record): Boltzmann constant, exact in the 2019 SI.
K_B = 1.380649e-23                      # J/K
assert abs(10 * math.log10(2 * Q_E / 1e-3) - L("ch03.las.rin_shot_limit_1ma")) < 0.1


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    """A value from the `conditions` block of ledger record `rid`."""
    return rec(rid)["conditions"][key]


def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


def w2dbm(p):
    return 10.0 * math.log10(p / 1e-3)


def dbm2w(p):
    return 1e-3 * 10.0 ** (p / 10.0)


def ev_to_nm(e_ev):
    """Photon wavelength (nm) for photon energy e_ev (eV)."""
    return H * C0 / (e_ev * Q_E) * 1e9


def qfunc(x):
    return 0.5 * math.erfc(x / math.sqrt(2.0))


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
    fig.savefig(FIGDIR / f"{name}.svg", format="svg", bbox_inches="tight",
                transparent=True, metadata={"Date": None})


# ---------- equation records ----------
def eq_record(eid):
    """An equation record from book/ledger/*_equations.yaml."""
    import yaml
    book = pathlib.Path(__file__).resolve().parents[2]
    for p in sorted((book / "ledger").glob("ch*_equations.yaml")):
        for e in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("equations") or []:
            if e["id"] == eid:
                return e
    raise KeyError(eid)


def eq_coeffs(eid):
    """Numeric coefficients written as 'a\\times10^{b}' in an equation's LaTeX, in order."""
    import re
    tex = eq_record(eid)["latex"]
    return [float(m) * 10.0 ** int(e) for m, e in re.findall(r"([0-9.]+)\\times10\^\{(-?\d+)\}", tex)]
