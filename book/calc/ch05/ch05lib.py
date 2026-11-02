"""Chapter 5 helpers shared by the worked-example scripts.

Defines functions only; running it (as `make calc` does for every *.py in this
folder) has no side effects.

* rec(), cond(): ledger records and their `conditions` blocks (any chapter).
* Folded-Clos (fat-tree) counting functions used in Sections 5.1 and 5.6.
* Collective-communication cost models used in Sections 5.3 and 5.4.
* Figure style identical to Chapter 1 (transparent, mid-gray axes).
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch05"


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    return rec(rid)["conditions"][key]


# ---------------------------------------------------------------- Clos counting
def fattree_hosts(k, tiers, sigma=1.0):
    """Hosts of an l-tier folded Clos of radix-k switches.

    Full bisection above the leaf; the leaf splits its k ports into
    d = k*sigma/(1+sigma) host ports and u = k/(1+sigma) uplinks.
    sigma = 1 gives the k-ary fat tree, N = 2 (k/2)^l.
    """
    return 2 * (k / 2) ** tiers * 2 * sigma / (1 + sigma)


def fattree_switches(k, tiers, sigma=1.0):
    """Switch count. Full fat tree (sigma = 1): (2l - 1) (k/2)^(l-1).

    With leaf oversubscription the leaf count is N/d and every upper tier
    carries the N/sigma leaf uplinks, so each upper non-top tier has
    (N/sigma)/(k/2) switches and the top tier (N/sigma)/k.
    """
    n = fattree_hosts(k, tiers, sigma)
    d = k * sigma / (1 + sigma)
    up = n / sigma
    if tiers == 1:
        return 1
    return n / d + (tiers - 2) * up / (k / 2) + up / k


def fattree_links(k, tiers, sigma=1.0):
    """(host links, switch-to-switch links)."""
    n = fattree_hosts(k, tiers, sigma)
    return n, (tiers - 1) * n / sigma


def tiers_needed(n_hosts, k):
    """Smallest l with 2 (k/2)^l >= n_hosts."""
    l = 1
    while 2 * (k / 2) ** l < n_hosts:
        l += 1
    return l


# ------------------------------------------------------------ collective costs
def t_ring(n, size, bw, lat):
    """Ring all-reduce: 2(N-1) steps of size/N bytes."""
    return 2 * (n - 1) * lat + 2 * (n - 1) / n * size / bw


def t_rabenseifner(n, size, bw, lat):
    """Reduce-scatter by recursive halving + all-gather by recursive doubling (Thakur 2005),
    reduction cost neglected."""
    return 2 * math.log2(n) * lat + 2 * (n - 1) / n * size / bw


def t_recursive_doubling(n, size, bw, lat):
    return math.log2(n) * (lat + size / bw)


def t_binomial_allreduce(n, size, bw, lat):
    """Binomial-tree reduce followed by a binomial broadcast."""
    return 2 * math.ceil(math.log2(n)) * (lat + size / bw)


def t_hier(n_nodes, g, size, bw_in, bw_out, lat_in, lat_out):
    """Hierarchical all-reduce: intra-node reduce-scatter, inter-node ring on size/g
    along the rail, intra-node all-gather."""
    t_in = 2 * (g - 1) * lat_in + 2 * (g - 1) / g * size / bw_in
    t_out = t_ring(n_nodes, size / g, bw_out, lat_out)
    return t_in + t_out, t_in, t_out


# ---------------------------------------------------------------- figure style
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
