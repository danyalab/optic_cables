"""Chapter 10 helpers shared by the worked-example scripts.

This module only defines functions; running it (as `make calc` does for every
*.py in this folder) has no side effects.

* rec(), cond(), qnum(): read ledger records, their `conditions`, and numbers
  that appear verbatim in a record's `quote` or `notes` (for example the prior
  year column of a filing table), so that every input still traces to a
  ledger id.
* date helpers for the export-control timeline.
* figure style identical to Chapter 1 (transparent, mid-gray axes, no black).
"""
import datetime as _dt
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch10"


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    """A value from the `conditions` block of ledger record `rid`."""
    return rec(rid)["conditions"][key]


def qnum(rid, pattern, field="quote", group=1):
    """A number captured by regex `pattern` in the `quote` (or `notes`) of record `rid`.

    Thousands separators are removed. Used for prior-year columns that a
    filing prints on the same line as the recorded value.
    """
    text = str(rec(rid).get(field, ""))
    m = re.search(pattern, text)
    if not m:
        raise KeyError(f"pattern {pattern!r} not found in {rid}.{field}: {text!r}")
    return float(m.group(group).replace(",", "").replace(" ", ""))


def date(rid):
    """A date stored as an ISO string in the `value` of a fact record."""
    return _dt.date.fromisoformat(str(rec(rid)["value"]))


def retrieved(rid):
    v = rec(rid)["retrieved"]
    return v if isinstance(v, _dt.date) else _dt.date.fromisoformat(str(v))


def pct(x):
    return 100.0 * x


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
    fig.savefig(FIGDIR / f"{name}.svg", format="svg", bbox_inches="tight", transparent=True,
                metadata={"Date": None})
    import os
    if os.environ.get("CH10_PREVIEW"):   # optional raster preview for the author; off in `make calc`
        fig.savefig(pathlib.Path(os.environ["CH10_PREVIEW"]) / f"{name}.png", dpi=80, bbox_inches="tight")
