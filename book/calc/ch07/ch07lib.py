"""Chapter 7 helpers shared by the worked-example scripts.

This module only defines functions; running it (as `make calc` does for every
*.py in this folder) has no side effects.

* rec(), cond(): read ledger records and their `conditions` blocks, so that
  every input still traces to a ledger id.
* the electrical power-feed model of Section 7.1 (series constant-current line,
  maximum power transfer);
* the power-limited capacity model of Section 7.2 (fixed electrical power shared
  by N_fp fiber pairs, Chapter 1 ASE and GN results per fiber);
* figure style identical to Chapter 1 (transparent, mid-gray axes).

Notation (book symbols, see book/notation/ch07_proposals.yaml):
  V_PFE   PFE voltage [V]           R'   cable resistance per length [ohm/km]
  R_c     total conductor resistance  I_f  line (feed) current [A]
  P_e     electrical power delivered to all repeaters [W]
  N_fp    fiber pairs               N_s  amplified spans (= amplifiers per fiber)
  P_0     overhead electrical power per amplifier [W]
  eta_EO  overall electrical-to-optical efficiency (signal output / electrical)
  Gamma   coding gap (linear)
"""
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import _ledger, L  # noqa: E402

FIGDIR = pathlib.Path(__file__).resolve().parents[2] / "figs" / "ch07"
LN10_10 = 10.0 / math.log(10.0)


def rec(rid):
    return _ledger()[rid]


def cond(rid, key):
    return rec(rid)["conditions"][key]


def db2lin(x):
    return 10.0 ** (x / 10.0)


def lin2db(x):
    return 10.0 * math.log10(x)


def w2dbm(p):
    return 10.0 * math.log10(p / 1e-3)


def dbm2w(p):
    return 1e-3 * 10.0 ** (p / 10.0)


# ---------------------------------------------------------------- constants
def h_nu(lam_m=1550e-9):
    h = L("ch01.const.planck_h")
    c = L("ch01.const.speed_of_light_c")
    return h * c / lam_m


def cband_hz():
    """ITU C-band width in Hz (G.Sup39 Table 5-1 band edges)."""
    c = L("ch01.const.speed_of_light_c")
    lo = L("ch01.amp.cband_range_itu", "lo") * 1e-9
    hi = L("ch01.amp.cband_range_itu", "hi") * 1e-9
    return c / lo - c / hi


# ---------------------------------------------------------------- 7.1 power feed
def max_power_transfer(V, Rc):
    """Maximum electrical power deliverable to the repeater chain, V^2/(4 R_c)."""
    return V ** 2 / (4.0 * Rc)


def repeater_power(I, V, Rc):
    """Power delivered to the repeaters at line current I: I (V - I R_c)."""
    return I * (V - I * Rc)


def pfe_voltage(I, Rc, n_r, P_r):
    """Desbruslais Eq. (1): V = I R_c + n_r P_r / I."""
    return I * Rc + n_r * P_r / I


def voltage_profile(V_top, I, r_per_km, L_km, n_r, P_r, npts_per_span=20):
    """Conductor potential along the cable, single-end feed.

    The PFE holds the shore end at V_top; the conductor loses I r per km, and
    each repeater (equally spaced) drops P_r / I. Returns (x_km, v) arrays.
    """
    import numpy as np
    span = L_km / (n_r + 1)
    xs, vs = [], []
    v = V_top
    for k in range(n_r + 1):
        x0 = k * span
        x = np.linspace(x0, x0 + span, npts_per_span)
        seg = v - I * r_per_km * (x - x0)
        xs.append(x)
        vs.append(seg)
        v = seg[-1]
        if k < n_r:
            xs.append(np.array([x0 + span]))
            v = v - P_r / I
            vs.append(np.array([v]))
    return np.concatenate(xs), np.concatenate(vs)


# ---------------------------------------------------------------- 1.5/1.6 per-fiber noise
def noise_factor(n_sp, G):
    """Chapter 1: F = 2 n_sp (G - 1)/G + 1/G."""
    return 2.0 * n_sp * (G - 1.0) / G + 1.0 / G


def ase_psd_chain(N_s, F, G, hnu):
    """Accumulated ASE PSD, both polarizations: N_s h nu (F G - 1) [W/Hz]."""
    return N_s * hnu * (F * G - 1.0)


def beta2_abs(D_ps_nm_km, lam_m=1550e-9):
    c = L("ch01.const.speed_of_light_c")
    d_si = D_ps_nm_km * 1e-12 / (1e-9 * 1e3)
    return d_si * lam_m ** 2 / (2 * math.pi * c)


def gn_eta1(gamma_per_W_km, alpha_db_km, D, span_km, Rs, Df, Nch):
    """One-span NLI efficiency eta^(1) [1/W^2] from the Chapter 1 closed form
    (Poggiolini 2012 Eq. (15), B_ch = R_s, NLI integrated over R_s)."""
    a = alpha_db_km / LN10_10 / 1e3
    Ls = span_km * 1e3
    le = (1 - math.exp(-a * Ls)) / a
    lea = 1 / a
    b2 = beta2_abs(D)
    gam = gamma_per_W_km * 1e-3
    arg = (math.pi ** 2 / 2) * b2 * lea * Rs ** 2 * Nch ** (2 * Rs / Df)
    mu = (8 / 27) * gam ** 2 * le ** 2 * math.asinh(arg) / (math.pi * b2 * lea)
    return mu / Rs ** 2


# ---------------------------------------------------------------- 7.2 capacity model
class PowerLimitedCable:
    """Fixed electrical power P_e shared by N_fp fiber pairs.

    Per amplifier (2 N_fp amplifiers per repeater, N_s repeaters):
        P_el = P_e / (2 N_fp N_s)
        P_sig = eta_EO (P_el - P_0)            (Desbruslais Eq. 5 / Perin Eq. 2 form)
    Per fiber, flat over bandwidth B with N_ch = B / R_s Nyquist channels,
        P_ch = min(P_sig / N_ch, P_opt)       (GN: never launch above optimum)
        GSNR = P_ch / (N_s P_ASE1 + N_s eta1 P_ch^3)
        C_fp = 2 B log2(1 + Gamma GSNR)       (both polarizations, one direction)
    Cable capacity per direction: N_fp C_fp.
    """

    def __init__(self, P_e, N_s, span_loss_db, n_sp, eta_EO, P_0, B, Rs, Gamma,
                 eta1=None, hnu=None):
        self.P_e, self.N_s, self.eta_EO, self.P_0 = P_e, N_s, eta_EO, P_0
        self.B, self.Rs, self.Gamma = B, Rs, Gamma
        self.G = db2lin(span_loss_db)
        self.F = noise_factor(n_sp, self.G)
        self.hnu = h_nu() if hnu is None else hnu
        self.Nch = B / Rs
        self.S_ase = ase_psd_chain(N_s, self.F, self.G, self.hnu)      # W/Hz
        self.P_ase_ch = self.S_ase * Rs                                  # W in R_s
        self.eta = None if eta1 is None else eta1 * N_s                  # incoherent GN
        self.P_opt = None if self.eta is None else (self.P_ase_ch / (2 * self.eta)) ** (1 / 3)
        # linear-regime constants of Section 7.2
        self.p = P_e / (2 * N_s)                       # W per amplifier x N_fp
        self.k = Gamma * eta_EO / (self.S_ase * B)     # 1/W: gap-scaled SNR per watt of electrical
        self.q = self.k * P_0                          # overhead SNR

    def p_sig(self, N_fp):
        return max(self.eta_EO * (self.p / N_fp - self.P_0), 0.0)

    def p_ch(self, N_fp):
        pc = self.p_sig(N_fp) / self.Nch
        if self.P_opt is not None:
            pc = min(pc, self.P_opt)
        return pc

    def gsnr(self, N_fp):
        pc = self.p_ch(N_fp)
        nli = 0.0 if self.eta is None else self.eta * pc ** 3
        return pc / (self.P_ase_ch + nli)

    def c_fp(self, N_fp):
        return 2 * self.B * math.log2(1 + self.Gamma * self.gsnr(N_fp))

    def capacity(self, N_fp):
        return N_fp * self.c_fp(N_fp)

    def c_inf(self):
        """Wideband (P_0 = 0, N_fp -> infinity) limit: 2 B k p / ln 2."""
        return 2 * self.B * self.k * self.p / math.log(2)

    def optimum_linear(self):
        """Closed-form optimum of the linear-regime model with overhead.

        x* solves ln(1 + x) = (x + q)/(1 + x); N_fp* = k p/(x* + q);
        C* = C_inf/(1 + x*).
        """
        from scipy.optimize import brentq
        q = self.q
        if q <= 0:
            return 0.0, math.inf, self.c_inf()
        f = lambda x: math.log1p(x) - (x + q) / (1 + x)
        x = brentq(f, 1e-12, 1e6)
        n = self.k * self.p / (x + q)
        return x, n, self.c_inf() / (1 + x)


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
    import os
    if os.environ.get("CH07_PNG"):
        fig.savefig(pathlib.Path(os.environ["CH07_PNG"]) / f"{name}.png", dpi=80)
