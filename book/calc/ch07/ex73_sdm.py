"""Worked example 7.3: capacity per cable versus fiber-pair count, multicore
fiber with fan-in/fan-out, and pump sharing.

Uses the Section 7.2 model (ch07lib.PowerLimitedCable) with the same amplifier
assumptions as ex72 (eta_EO, absolute overhead P_0 per amplifier, 50 GBd
Nyquist C-band, Perin fiber and span parameters).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import json
import math
from common import L, Results
import ch07lib as cl

r = Results()
HERE = pathlib.Path(__file__).parent
ex72 = json.loads((HERE / "out" / "ex72_power_limited.json").read_text())
FEED = "ch07.power.perin_feed_voltage_resistance"
LINK = "ch07.power.perin_link_reference"
EO = "ch07.arch.pce_typical_5pct"
V18 = "ch07.arch.max_single_end_voltage_18kv"
R07 = "ch07.arch.cable_resistance_low_end"
MCF = "ch07.sdm.mcedfa_capacity_gain_no_fifo"
FIFO = "ch07.sdm.fifo_loss_xt"

span_km = float(cl.cond(LINK, "span_km"))
span_db = float(cl.cond(LINK, "span_att_dB"))
alpha = float(cl.cond(LINK, "alpha_dB_per_km"))
n_sp = float(cl.cond(LINK, "n_sp"))
gamma = float(cl.cond(LINK, "gamma_per_W_km"))
D = float(cl.cond(LINK, "D_ps_nm_km"))
Gamma = cl.db2lin(float(cl.cond(LINK, "coding_gap_dB")))
eta_EO = L(EO) / 100
RS = ex72["rs_gbd"]["value"] * 1e9
NCH = int(ex72["nch"]["value"])
B = NCH * RS
P_0 = ex72["P0_mw"]["value"] * 1e-3      # ASSUMPTION carried from ex72 (absolute, per amplifier)
ins = [FEED, LINK, EO, V18, R07, MCF, "ch07.power.desbruslais_span_loss_min_voltage",
       "ch07.power.desbruslais_8fp_example", "ch01.amp.cband_range_itu"]


def cable(P_e, Lkm, extra_loss_db=0.0, P0=P_0):
    N_s = round(Lkm / span_km)
    e1 = cl.gn_eta1(gamma, alpha, D, span_km, RS, RS, NCH)
    return cl.PowerLimitedCable(P_e, N_s, span_db + extra_loss_db, n_sp, eta_EO, P0, B, RS, Gamma, eta1=e1)


# ---------------------------------------------------------------- two cables
L_tp = L(LINK)
L_ta = float(cl.cond(MCF, "L_km"))
Pe_tp = cl.max_power_transfer(L(FEED) * 1e3, float(cl.cond(FEED, "rho_ohm_per_km")) * L_tp)
Pe_ta = cl.max_power_transfer(L(V18) * 1e3, L(R07) * L_ta)
tp, ta = cable(Pe_tp, L_tp), cable(Pe_ta, L_ta)
r.emit("ta_L_km", L_ta, "km", 2, [MCF])
r.emit("ta_Ns", ta.N_s, "", 3, [MCF, LINK])
r.emit("ta_Pe_kw", Pe_ta / 1e3, "kW", 3, [V18, R07, MCF])
for tag, m in (("tp", tp), ("ta", ta)):
    x, n, c = m.optimum_linear()
    r.emit(f"{tag}_nopt", n, "", 3, ins)
    r.emit(f"{tag}_copt", c / 1e12, "Tb/s", 3, ins)
    r.emit(f"{tag}_seopt", 2 * math.log2(1 + x), "b/s/Hz", 3, ins)
    r.emit(f"{tag}_q", m.q, "", 3, ins)
    for nfp in (8, 12, 16, 24, 32, 48):
        r.emit(f"{tag}_c{nfp}", m.capacity(nfp) / 1e12, "Tb/s", 3, ins)
        r.emit(f"{tag}_fp{nfp}", m.c_fp(nfp) / 1e12, "Tb/s", 3, ins)
        r.emit(f"{tag}_se{nfp}", 2 * math.log2(1 + Gamma * m.gsnr(nfp)), "b/s/Hz", 3, ins)
# on the shorter, higher-voltage cable N_s is halved and P_e is ~6.6x: q falls by ~2 (fewer
# spans per fiber -> less ASE), N* grows
assert ta.optimum_linear()[1] > tp.optimum_linear()[1]
r.emit("ta_over_tp_pe", Pe_ta / Pe_tp, "", 3, ins)
# fiber-pair count below which each fiber can be driven to its GN optimum (power not binding)
for tag, m in (("tp", tp), ("ta", ta)):
    knee = m.p / (m.P_opt * NCH / eta_EO + P_0)
    r.emit(f"{tag}_knee", knee, "", 3, ins)
    r.emit(f"{tag}_gsnr_max_db", cl.lin2db(m.P_opt / (1.5 * m.P_ase_ch)), "dB", 3, ins)

# ---------------------------------------------------------------- 24 FP -> 48 core pairs
# Doubling spatial channels at fixed electrical power: 2-core MCF in the same 24-FP cable.
fifo_db = L(FIFO)
xt_db = float(cl.cond(FIFO, "crosstalk_dB"))
r.emit("fifo_db", fifo_db, "dB", 2, [FIFO])
r.emit("xt_db", xt_db, "dB", 2, [FIFO])
# ASSUMPTION: an SC-EDFA MCF repeater needs one fan-out before and one fan-in after each
# amplifier, both inside the span loss budget (2 x FIFO loss per span); crosstalk of the
# 2 N_s devices adds incoherently as Gaussian noise relative to the signal.
for tag, m, Lk in (("tp", tp, L_tp), ("ta", ta, L_ta)):
    N_s = m.N_s
    xt_tot = 2 * N_s * cl.db2lin(xt_db)
    r.emit(f"{tag}_xt_tot_db", cl.lin2db(xt_tot), "dB", 3, ins + [FIFO])
    Pe = m.P_e
    c24 = m.capacity(24)
    mf = cable(Pe, Lk, extra_loss_db=2 * fifo_db)
    def cap_xt(mm, n):
        g = mm.gsnr(n)
        g_tot = 1 / (1 / g + xt_tot)
        return n * 2 * B * math.log2(1 + Gamma * g_tot)
    c48_fifo = cap_xt(mf, 48)
    c48_ideal = m.capacity(48)
    r.emit(f"{tag}_c24", c24 / 1e12, "Tb/s", 3, ins)
    r.emit(f"{tag}_c48_ideal", c48_ideal / 1e12, "Tb/s", 3, ins)
    r.emit(f"{tag}_c48_fifo", c48_fifo / 1e12, "Tb/s", 3, ins + [FIFO])
    r.emit(f"{tag}_mcf_gain_pct", 100 * (c48_fifo / c24 - 1), "%", 2, ins + [FIFO])
    r.emit(f"{tag}_fifo_removal_pct", 100 * (c48_ideal / c48_fifo - 1), "%", 2, ins + [FIFO])
    # ASSUMPTION: an integrated two-core MC-EDFA shares control and supervisory electronics
    # between the two cores, so the overhead per core path is P_0/2, with no FIFOs.
    mi = cable(Pe, Lk, P0=P_0 / 2)
    r.emit(f"{tag}_c48_mcedfa", mi.capacity(48) / 1e12, "Tb/s", 3, ins)
    r.emit(f"{tag}_mcedfa_gain_pct", 100 * (mi.capacity(48) / c24 - 1), "%", 2, ins)
    # crosstalk alone vs loss alone
    r.emit(f"{tag}_xt_only_pct", 100 * (1 - cap_xt(m, 48) / c48_ideal), "%", 2, ins + [FIFO])
# Downie's comparison: 16 FP of 4-core MCF (64 cores per direction) at 7,000 km
cores = int(cl.cond(MCF, "cores"))
nfp_d = int(cl.cond(MCF, "fiber_pairs"))
npaths = cores * nfp_d
xt_tot = 2 * ta.N_s * cl.db2lin(xt_db)
mf = cable(Pe_ta, L_ta, extra_loss_db=2 * fifo_db)
g = 1 / (1 / mf.gsnr(npaths) + xt_tot)
c_fifo = npaths * 2 * B * math.log2(1 + Gamma * g)
c_nofifo = ta.capacity(npaths)
r.emit("downie_paths", npaths, "", 2, [MCF])
r.emit("downie_case_gain_pct", 100 * (c_nofifo / c_fifo - 1), "%", 2, ins + [FIFO])
r.emit("downie_pub_gain_pct", L(MCF), "%", 1, [MCF])
r.emit("downie_case_c_fifo", c_fifo / 1e12, "Tb/s", 3, ins + [FIFO])

# ---------------------------------------------------------------- pump sharing
# M pumps combined and split over K amplifiers: one pump failure removes 1/M of the pump
# power of all K amplifiers at that repeater. In the linear regime (signal output ∝ pump
# above threshold) the outputs fall by delta = -10 log10(1 - 1/M) dB; with constant-output
# amplifiers downstream, that repeater's successor sees its input lowered by delta, so its
# ASE contribution relative to signal grows by 10^(delta/10).
N_s = tp.N_s
for M in (2, 4, 8):
    delta = -cl.lin2db(1 - 1 / M)
    pen = cl.lin2db((N_s - 1 + cl.db2lin(delta)) / N_s)
    r.emit(f"share_M{M}_drop_db", delta, "dB", 3)
    r.emit(f"share_M{M}_pen_db", pen, "dB", 2, [LINK])
assert cl.lin2db((N_s - 1 + 2) / N_s) < 0.05

r.save()
