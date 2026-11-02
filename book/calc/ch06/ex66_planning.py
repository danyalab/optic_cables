"""Worked example 6.6: GSNR-based planning of a multi-span route with ROADMs,
beginning of life (BOL) versus end of life (EOL), with Pointurier's margin taxonomy.

Step 0  Pointurier's 600 km example: U + S = 10 log10(L_max / L_path); BoL total.
Step 1  Per-span GN quantities (closed form, Section 1.6) for G.652.D at 63.1 GBd.
Step 2  Route: N_s spans of 80 km, a route-and-select ROADM every 4 spans. Each ROADM
        adds an amplifier that restores the express loss (ASE, no NLI) and two WSS passes.
Step 3  Total SNR = [GSNR^-1 + SNR_TR^-1]^-1, minus the WSS-cascade penalty (MMSE model, 6.2).
Step 4  EOL: fibre ageing, amplifier NF ageing, launch power kept at the BOL optimum.
Step 5  Margin ledger for a 960 km route and maximum reach per mode.
"""
import json
import math
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ch06lib as c6
from common import L, Results

r = Results()
h, c = c6.consts()
LAM = 1550e-9                                   # ASSUMPTION (A21 of Chapter 1)
nu = c / LAM

# ---------------------------------------------------------------- Step 0
PE = "ch06.margin.pointurier_example_bol"
lmax, lpath = c6.cond(PE, "max_reach_km"), c6.cond(PE, "length_km")
us = 10 * math.log10(lmax / lpath)
us_pub = c6.cond(PE, "u_margin_dB") + c6.cond(PE, "s_margin_dB")
assert abs(us_pub + c6.cond(PE, "d_margin_dB") - L(PE)) < 0.05, "U + S + D = BoL total"
# The ledger note states U + S = 10 log10(7500/600) = 12.5 dB, but 7500/600 = 12.5 is the
# *linear* ratio; in decibels it is 10.97 dB. We report the discrepancy rather than resolve it.
r.emit("pt_us_pub", us_pub, "dB", 3, [PE])
r.emit("pt_ratio", lmax / lpath, "1", 3, [PE])
r.emit("pt_us", us, "dB", 4, [PE])
r.emit("pt_lmax_implied", lpath * 10 ** (us_pub / 10), "km", 3, [PE])
r.emit("pt_eol_used", L(PE) - c6.cond(PE, "eol_margin_dB"), "dB", 2, [PE])

# ---------------------------------------------------------------- Step 1
RS = L("ch06.openroadm.w_63p1gbd") * 1e9
DF = 75e9                                       # ASSUMPTION: 75 GHz slots (m = 6)
NCH = 64                                        # 4.8 THz / 75 GHz (Section 6.1)
SPAN = 80e3                                     # ASSUMPTION (Chapter 1, A1)
OVH = 1.95                                      # ASSUMPTION: splice + connector allowance (Chapter 1)
ALPHA = L("ch01.att.smf28ultra_max_1550")
D = L("ch01.cd.g652_link_typ_d1550")
gam = c6.gamma_from(L("ch01.kerr.n2_kato1995_smf"), L("ch01.kerr.aeff_g652d_typ"), LAM, c)
NF = L("ch01.amp.accelink_mw_nf_max")
eta1 = c6.mu_coeff(gam, ALPHA, D, SPAN, RS, DF, NCH, LAM, c) / RS ** 2
Lspan_bol = ALPHA * SPAN / 1e3 + OVH
ins1 = ["ch06.openroadm.w_63p1gbd", "ch01.att.smf28ultra_max_1550", "ch01.cd.g652_link_typ_d1550",
        "ch01.kerr.n2_kato1995_smf", "ch01.kerr.aeff_g652d_typ", "ch01.amp.accelink_mw_nf_max"]
r.emit("rs", RS / 1e9, "GBd", 3, ["ch06.openroadm.w_63p1gbd"])
r.emit("lspan_bol", Lspan_bol, "dB", 3, ["ch01.att.smf28ultra_max_1550"])
r.emit("eta1_db", 10 * math.log10(eta1), "dB(1/W²)", 4, ins1)

# ROADM node (ASSUMPTIONS): express loss = 2 x WSS insertion loss (Huang typical), restored
# by one amplifier with the line NF; ROADM every 4 spans.
IL = L("ch06.wss.huang_twin1x35_il")
NODE_LOSS = 2 * IL
SPANS_PER_ROADM = 4
r.emit("node_loss", NODE_LOSS, "dB", 3, ["ch06.wss.huang_twin1x35_il"])
r.emit("spans_per_roadm", SPANS_PER_ROADM, "", 2)

# ---------------------------------------------------------------- Pointurier S-margin items
PT = "ch06.margin.pointurier_table"
nf_age = c6.cond(PT, "nf_aging_dB")
filt_age = c6.cond(PT, "filter_aging_dB_per_filter")
trx_age = c6.cond(PT, "trx_aging_dB")
fast = c6.cond(PT, "fast_dB")
fib_age = c6.cond(PT, "fiber_aging_dB_per_km_per_year")
YEARS = 10                                      # ASSUMPTION: design life
d_span_eol = fib_age * SPAN / 1e3 * YEARS
D_MARGIN = L("ch01.gnpy.gsnr_accuracy")         # ASSUMPTION: design margin = GNPy accuracy
for k, v, u in (("nf_age", nf_age, "dB"), ("filt_age", filt_age, "dB"), ("trx_age", trx_age, "dB"),
                ("fast", fast, "dB"), ("fib_age", fib_age * 1e3, "mdB/(km·yr)")):
    r.emit(k, v, u, 2, [PT])
r.emit("years", YEARS, "yr", 2)
r.emit("d_span_eol", d_span_eol, "dB", 3, [PT])
r.emit("d_margin", D_MARGIN, "dB", 2, ["ch01.gnpy.gsnr_accuracy"])
assert abs(fib_age * 100 * 10 - 1.6) < 1e-9, "Pointurier: 1.6 dB over 10 years for 100 km spans"

# ---------------------------------------------------------------- filtering model from 6.2
ex62 = json.loads((pathlib.Path(__file__).parent / "out" / "ex62_wss_filtering.json").read_text())
DEF = ex62["deficit"]["value"]
BW = ex62["bw_fit"]["value"]
SNR0 = ex62["snr0"]["value"]

SNR_TR = L("ch01.gap.transceiver_snr_range", "hi")   # ASSUMPTION: best transceiver of the range
r.emit("snr_tr", SNR_TR, "dB", 3, ["ch01.gap.transceiver_snr_range"])


def route(ns, eol=False, popt_fixed=None):
    """Return dict for a route of ns spans (ROADM every SPANS_PER_ROADM spans)."""
    n_int = (ns - 1) // SPANS_PER_ROADM          # intermediate ROADMs
    lsp = Lspan_bol + (d_span_eol if eol else 0.0)
    F = c6.db2lin(NF + (nf_age if eol else 0.0))
    pase = ns * (F * c6.db2lin(lsp) - 1) * h * nu * RS + n_int * (F * c6.db2lin(NODE_LOSS) - 1) * h * nu * RS
    eta = ns * eta1
    popt = (pase / (2 * eta)) ** (1 / 3)
    p = popt if popt_fixed is None else popt_fixed
    gsnr = p / (pase + eta * p ** 3)
    n_wss = 2 * n_int + 2                        # add + drop + 2 per intermediate node
    pen = c6.mmse_penalty_db(RS / 1e9, 75.0 - DEF, BW, n_wss, SNR0)
    tot = 1 / (1 / gsnr + 1 / c6.db2lin(SNR_TR))
    return {"popt": popt, "gsnr": c6.lin2db(gsnr), "pen": pen, "tot": c6.lin2db(tot) - pen,
            "n_int": n_int, "n_wss": n_wss, "pase": pase}


s16 = c6.snr_at_ber_16qam(L("ch06.openroadm.ofec_threshold"))
sqp = c6.snr_at_ber_qpsk(L("ch06.openroadm.ofec_threshold"))
modes = {"m16": (c6.lin2db(s16), "400G DP-16QAM"), "mqp": (c6.lin2db(sqp), "200G DP-QPSK")}
r.emit("req_m16", modes["m16"][0], "dB", 3, ["ch06.openroadm.ofec_threshold"])
r.emit("req_mqp", modes["mqp"][0], "dB", 3, ["ch06.openroadm.ofec_threshold"])

# ---------------------------------------------------------------- Step 5: the 960 km route
NS = 12                                          # ASSUMPTION: 12 x 80 km = 960 km
bol = route(NS)
eol = route(NS, eol=True, popt_fixed=bol["popt"])
eol_re = route(NS, eol=True)
ins_r = ins1 + ["ch06.wss.huang_twin1x35_il", "ch01.gap.transceiver_snr_range", PT]
r.emit("ns", NS, "spans", 3)
r.emit("route_km", NS * SPAN / 1e3, "km", 3)
r.emit("n_int", bol["n_int"], "", 2)
r.emit("n_wss", bol["n_wss"], "", 2)
r.emit("popt_dbm", c6.w2dbm(bol["popt"]), "dBm", 3, ins_r)
r.emit("gsnr_bol", bol["gsnr"], "dB", 4, ins_r)
r.emit("gsnr_eol", eol["gsnr"], "dB", 4, ins_r)
r.emit("gsnr_eol_re", eol_re["gsnr"], "dB", 4, ins_r)
r.emit("pen", bol["pen"], "dB", 2, ins_r)
r.emit("tot_bol", bol["tot"], "dB", 4, ins_r)
r.emit("tot_eol", eol["tot"], "dB", 4, ins_r)
lin_deg = c6.lin2db(eol["pase"] / bol["pase"])
r.emit("lin_deg", lin_deg, "dB", 3, ins_r)
r.emit("gsnr_deg", bol["gsnr"] - eol["gsnr"], "dB", 3, ins_r)
r.emit("gsnr_deg_re", bol["gsnr"] - eol_re["gsnr"], "dB", 3, ins_r)
# 2/3 rule (Pointurier; Section 1.6): exact when the power is re-optimized
assert abs((bol["gsnr"] - eol_re["gsnr"]) - 2 / 3 * lin_deg) < 1e-9
assert (bol["gsnr"] - eol["gsnr"]) >= (bol["gsnr"] - eol_re["gsnr"]) - 1e-12
# ROADM ASE share at BOL
ase_node = bol["n_int"] * (c6.db2lin(NF) * c6.db2lin(NODE_LOSS) - 1) * h * nu * RS
r.emit("node_ase_pct", 100 * ase_node / bol["pase"], "%", 2, ins_r)

filt_total = filt_age * bol["n_wss"]
r.emit("filt_total", filt_total, "dB", 2, [PT])
for tag, (req, _) in modes.items():
    # S margin reserved at BOL: physical ageing (BOL - EOL of the total SNR) + filter + trx + fast
    s_res = (bol["tot"] - eol["tot"]) + filt_total + trx_age + fast
    m_bol = bol["tot"] - req
    u_bol = m_bol - s_res - D_MARGIN
    m_eol = eol["tot"] - filt_total - trx_age - req
    r.emit(f"{tag}_m_bol", m_bol, "dB", 3, ins_r)
    r.emit(f"{tag}_s_res", s_res, "dB", 3, ins_r)
    r.emit(f"{tag}_u_bol", u_bol, "dB", 3, ins_r)
    r.emit(f"{tag}_m_eol", m_eol, "dB", 3, ins_r)
    r.emit(f"{tag}_ok", 1.0 if u_bol >= 0 else 0.0, "", 1, ins_r)
    # identity: U = EOL margin - fast - D
    assert abs(u_bol - (m_eol - fast - D_MARGIN)) < 1e-9

# Maximum reach per mode: largest ns with U >= 0 (EOL feasibility), and BOL "no margin" reach
NSS = np.arange(1, 61)
curves = {"bol": [], "eol": []}
for n in NSS:
    b = route(int(n))
    e = route(int(n), eol=True, popt_fixed=b["popt"])
    curves["bol"].append(b["tot"])
    curves["eol"].append(e["tot"] - filt_age * e["n_wss"] - trx_age)
for tag, (req, _) in modes.items():
    nmax_bol = max(int(n) for n, v in zip(NSS, curves["bol"]) if v >= req)
    nmax_plan = max(int(n) for n, v in zip(NSS, curves["eol"]) if v - fast - D_MARGIN >= req)
    r.emit(f"{tag}_nmax_bol", nmax_bol, "spans", 3, ins_r)
    r.emit(f"{tag}_nmax_plan", nmax_plan, "spans", 3, ins_r)
    r.emit(f"{tag}_reach_bol", nmax_bol * SPAN / 1e3, "km", 4, ins_r)
    r.emit(f"{tag}_reach_plan", nmax_plan * SPAN / 1e3, "km", 4, ins_r)
    r.emit(f"{tag}_reach_loss_pct", 100 * (1 - nmax_plan / nmax_bol), "%", 2, ins_r)

plt = c6.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.2))
km = NSS * SPAN / 1e3
ax.plot(km, curves["bol"], color=c6.COLORS[0], label="BOL total SNR")
ax.plot(km, curves["eol"], color=c6.COLORS[1], label="EOL (ageing, filter and transceiver)")
ax.plot(km, np.array(curves["eol"]) - fast - D_MARGIN, color=c6.COLORS[1], ls="--", lw=1.4,
        label="EOL minus fast-variation and design margins")
for i, (tag, (req, lab)) in enumerate(modes.items()):
    ax.axhline(req, color=c6.COLORS[2 + i], ls=":", lw=1.3)
    ax.text(km[-1], req + 0.2, f"{lab} at oFEC threshold", fontsize=8.5, ha="right")
ax.axvline(NS * SPAN / 1e3, color=c6.GRAY, lw=0.8, ls=":")
ax.set_xlabel("Route length (km), ROADM every 320 km")
ax.set_ylabel("SNR at the decision device (dB)")
ax.set_title("Computed: 63.1 GBd over 80 km G.652.D spans, 64 x 75 GHz", fontsize=10)
ax.legend(fontsize=8.5, loc="upper right")
ax.set_ylim(4, 22)
c6.savefig(fig, "planning_bol_eol")

r.save()
