"""Section 4.6: coherent pluggables table and the 800ZR reach margin from the GN model.

Part 1 checks line rates R_line = 2 R_s log2 M (eq. ch04.eq.coherent_bitrate) and the
800LR expansion (eq. ch04.eq.800lr_expansion), and computes energy per bit.

Part 2 (worked example): one amplified span carrying a full 800ZR grid. The GN model of
Section 1.6 (Poggiolini 2012, closed form) gives the optimum launch power and maximum
OSNR in the 0.1 nm reference bandwidth versus span length; comparing with the 800ZR OSNR
requirement gives the reach margin.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import math
import re
import numpy as np
from scipy.optimize import brentq
from scipy.special import erfc
import ch04lib as cl

r = Results()
BITS_DP16QAM = 2 * math.log2(16)       # two polarizations x 4 bits

# ================================================================ Part 1: table
rs400 = L("ch04.coh.400zr_baud")
rs_ozr = cl.cond("ch04.coh.openzrplus_ofec", "baud_GBd")
rs800 = L("ch04.coh.800zr_baud")
rs800p = cl.cond("ch04.coh.800zrplus_nokia_31w", "baud_GBd")
rs_lr = L("ch04.coh.800lr_baud")
line1600 = cl.cond("ch04.coh.1600zr_ia", "line_bit_rate_Gbps")
rs1600 = line1600 / BITS_DP16QAM
assert abs(rs400 * BITS_DP16QAM - cl.cond("ch04.coh.400zr_baud", "line_rate_Gbps")) < 1e-6
assert abs(rs800 * BITS_DP16QAM - cl.cond("ch04.coh.800zr_baud", "line_rate_Gbps")) < 0.05
assert abs(rs_lr * BITS_DP16QAM - cl.cond("ch04.coh.800lr_baud", "line_rate_Gbps")) < 0.01
r.emit("rs400", rs400, "GBd", 6, ["ch04.coh.400zr_baud"])
r.emit("rs_ozr", rs_ozr, "GBd", 4, ["ch04.coh.openzrplus_ofec"])
r.emit("rs800", rs800, "GBd", 4, ["ch04.coh.800zr_baud"])
r.emit("rs800p", rs800p, "GBd", 4, ["ch04.coh.800zrplus_nokia_31w"])
r.emit("rs_lr", rs_lr, "GBd", 6, ["ch04.coh.800lr_baud"])
r.emit("rs1600", rs1600, "GBd", 4, ["ch04.coh.1600zr_ia"])
r.emit("line400", rs400 * BITS_DP16QAM, "Gb/s", 5, ["ch04.coh.400zr_baud"])
r.emit("line800", rs800 * BITS_DP16QAM, "Gb/s", 4, ["ch04.coh.800zr_baud"])
r.emit("line_lr", rs_lr * BITS_DP16QAM, "Gb/s", 5, ["ch04.coh.800lr_baud"])
r.emit("line1600", line1600, "Gb/s", 6, ["ch04.coh.1600zr_ia"])
# 800LR expansion: 850 Gb/s RS-coded client x 126/110 x 64/63 / 8
eqs = json.dumps(__import__("yaml").safe_load((pathlib.Path(__file__).resolve().parents[2] / "ledger" / "ch04_equations.yaml").read_text()))
client = float(re.search(r"([0-9.]+) Gb/s RS-coded client", eqs).group(1))
rs_lr_calc = client / 8 * 126 / 110 * 64 / 63
assert abs(rs_lr_calc - rs_lr) < 1e-3
r.emit("lr_client", client, "Gb/s", 3, ["ch04.coh.800lr_baud"])
r.emit("lr_rs_calc", rs_lr_calc, "GBd", 6, ["ch04.coh.800lr_baud"])
r.emit("client_oh_pct", 100 * (client / 800 - 1), "%", 3, ["ch04.coh.800lr_baud"])
r.emit("ofec_oh_pct", 100 * 17 / 111, "%", 3, ["ch04.coh.openzrplus_ofec"])
r.emit("ofec_rate", 111 / 128, "1", 3, ["ch04.coh.openzrplus_ofec"])
assert cl.cond("ch04.coh.openzrplus_ofec", "overhead").startswith("17/111")
# energy per bit
for tag, rid, rate in (("400zr", "ch04.coh.400zr_module_power", 400), ("400zr_t", "ch04.coh.400zr_15w_target", 400),
                       ("800zr", "ch04.coh.800zr_module_power", 800), ("800zrp", "ch04.coh.800zrplus_nokia_31w", 800),
                       ("1600zr", "ch04.ff.osfpxd_40w_target", 1600)):
    r.emit(f"eb_{tag}", cl.pj_per_bit(L(rid), rate), "pJ/bit", 3, [rid])
r.emit("p400_over_target", L("ch04.coh.400zr_module_power") - L("ch04.coh.400zr_15w_target"), "W", 2,
       ["ch04.coh.400zr_module_power", "ch04.coh.400zr_15w_target"])
r.emit("p400_typ", cl.cond("ch04.coh.400zr_module_power", "typical_W"), "W", 2, ["ch04.coh.400zr_module_power"])
r.emit("p800_typ", cl.cond("ch04.coh.800zr_module_power", "typical_W"), "W", 2, ["ch04.coh.800zr_module_power"])
# grid and capacity per fibre for 800ZR
grid = cl.cond("ch04.coh.800zr_reach", "grid")
NCH, DF_GHZ = [float(x) for x in re.search(r"(\d+) x (\d+) GHz", grid).groups()]
r.emit("zr_nch", NCH, "", 2, ["ch04.coh.800zr_reach"])
r.emit("zr_df", DF_GHZ, "GHz", 3, ["ch04.coh.800zr_reach"])
r.emit("zr_band", NCH * DF_GHZ / 1e3, "THz", 2, ["ch04.coh.800zr_reach"])
r.emit("zr_cap", NCH * 0.8, "Tb/s", 3, ["ch04.coh.800zr_reach"])
r.emit("zr_se", 800 / DF_GHZ, "b/s/Hz", 3, ["ch04.coh.800zr_reach"])
r.emit("zr_rolloff_room", DF_GHZ / rs800, "1", 3, ["ch04.coh.800zr_reach", "ch04.coh.800zr_baud"])
# 800LR loss budgets vs 10 km of datasheet fibre (ch01 records)
lr_km = cl.cond("ch04.coh.800lr_loss_budget", "reach_km")
a1310, a1550 = L("ch01.att.smf28ultra_max_1310"), L("ch01.att.smf28ultra_max_1550")
r.emit("lr_o_margin", cl.cond("ch04.coh.800lr_loss_budget", "O_band_dB") - a1310 * lr_km, "dB", 2,
       ["ch04.coh.800lr_loss_budget", "ch01.att.smf28ultra_max_1310"])
r.emit("lr_c_margin", cl.cond("ch04.coh.800lr_loss_budget", "C_band_dB") - a1550 * lr_km, "dB", 2,
       ["ch04.coh.800lr_loss_budget", "ch01.att.smf28ultra_max_1550"])
r.emit("lr_o_fiber", a1310 * lr_km, "dB", 2, ["ch01.att.smf28ultra_max_1310"])
r.emit("lr_c_fiber", a1550 * lr_km, "dB", 2, ["ch01.att.smf28ultra_max_1550"])

# ================================================================ Part 2: required SNR and implementation gap
bref = L("ch01.osnr.bref_0p1nm_equals_12p5ghz")          # GHz
osnr800 = L("ch04.coh.800zr_osnr")
osnr400 = L("ch04.coh.400zr_osnr_26")
snr800 = osnr800 + cl.lin2db(bref / rs800)
snr400 = osnr400 + cl.lin2db(bref / rs400)
r.emit("bref", bref, "GHz", 3, ["ch01.osnr.bref_0p1nm_equals_12p5ghz"])
r.emit("snr800_req", snr800, "dB", 3, ["ch04.coh.800zr_osnr", "ch04.coh.800zr_baud"])
r.emit("snr400_req", snr400, "dB", 3, ["ch04.coh.400zr_osnr_26", "ch04.coh.400zr_baud"])
r.emit("baud_ratio_db", cl.lin2db(rs800 / rs400), "dB", 3, ["ch04.coh.800zr_baud", "ch04.coh.400zr_baud"])


def snr_th(ber):
    """Gray 16-QAM per-symbol SNR at BER (Section 1.6): BER = (3/8) erfc(sqrt(SNR/10))."""
    return brentq(lambda s: 3 / 8 * erfc(math.sqrt(s / 10)) - ber, 1.0, 100.0)


# ASSUMPTION: 800ZR's OFEC has the OpenZR+ OFEC pre-FEC threshold (same code; the 800ZR IA table was not read).
ber800 = L("ch04.coh.openzrplus_ofec")
ber400 = L("ch04.coh.400zr_cfec")
th800, th400 = cl.lin2db(snr_th(ber800)), cl.lin2db(snr_th(ber400))
r.emit("ber800", ber800, "1", 2, ["ch04.coh.openzrplus_ofec"])
r.emit("ber400", ber400, "1", 3, ["ch04.coh.400zr_cfec"])
r.emit("snr800_th", th800, "dB", 3, ["ch04.coh.openzrplus_ofec"])
r.emit("snr400_th", th400, "dB", 3, ["ch04.coh.400zr_cfec"])
r.emit("gap800", snr800 - th800, "dB", 2, ["ch04.coh.800zr_osnr", "ch04.coh.openzrplus_ofec"])
r.emit("gap400", snr400 - th400, "dB", 2, ["ch04.coh.400zr_osnr_26", "ch04.coh.400zr_cfec"])
assert snr800 - th800 < snr400 - th400

# ================================================================ Part 2: GN-model reach of one span
h = L("ch01.const.planck_h")
c = L("ch01.const.speed_of_light_c")
lam = float(cl.cond("ch01.osnr.gsup39_58db_constant", "wavelength_nm")) * 1e-9
nu = c / lam
ex14 = json.loads((pathlib.Path(__file__).resolve().parents[1] / "ch01" / "out" / "ex14_nonlinear_lengths.json").read_text())
gamma = ex14["gamma_g652"]["value"] * 1e-3                  # 1/(W m), from n2 and A_eff ledger records
D = L("ch01.cd.g652_link_typ_d1550")
NF = L("ch01.amp.accelink_mw_nf_max")
F = cl.db2lin(NF)
RS = rs800 * 1e9
DF = DF_GHZ * 1e9
BREF = bref * 1e9
OSNR_REQ = cl.db2lin(osnr800)
ba_max = float(re.search(r"([0-9.]+) \(BA", cl.cond("ch01.amp.accelink_mw_nf_max", "output_power_dBm")).group(1))
GN_IN = ["ch01.cd.g652_link_typ_d1550", "ch01.kerr.n2_pure_silica_gsup47", "ch01.kerr.aeff_g652d_typ",
         "ch01.amp.accelink_mw_nf_max", "ch01.const.planck_h", "ch01.const.speed_of_light_c",
         "ch04.coh.800zr_baud", "ch04.coh.800zr_reach", "ch04.coh.800zr_osnr"]
r.emit("nf", NF, "dB", 2, ["ch01.amp.accelink_mw_nf_max"])
r.emit("gamma", gamma * 1e3, "1/(W·km)", 3, ["ch01.kerr.n2_pure_silica_gsup47", "ch01.kerr.aeff_g652d_typ"])
r.emit("ba_max", ba_max, "dBm", 2, ["ch01.amp.accelink_mw_nf_max"])
r.emit("ba_per_ch", ba_max - cl.lin2db(NCH), "dBm", 3, ["ch01.amp.accelink_mw_nf_max", "ch04.coh.800zr_reach"])


def span(alpha_db_km, Lkm, p_cap_dbm=None):
    """Return (P_opt [W], OSNR_max [lin], eta [1/W^2], P_ASE in B_ref [W]) for one span."""
    mu, b2 = cl.mu_coeff(gamma, alpha_db_km, D, Lkm * 1e3, RS, DF, NCH, lam, c)
    eta = mu / RS ** 2                                     # P_NLI = eta P^3 in B_N = R_s
    G = cl.db2lin(alpha_db_km * Lkm)
    pase_rs = (F * G - 1) * h * nu * RS                    # both polarizations, B_N = R_s
    popt = (pase_rs / (2 * eta)) ** (1 / 3)
    if p_cap_dbm is not None:
        popt = min(popt, cl.dbm2w(p_cap_dbm))
    snr = popt / (pase_rs + eta * popt ** 3)
    return popt, snr * RS / BREF, eta, pase_rs * BREF / RS


# ASSUMPTION: cases for the fibre loss coefficient: uncabled datasheet maximum (optimistic) and
# the ITU typical cabled link value, which already includes cabling effects. No extra connector loss.
FIB = {"dsfib": L("ch01.att.smf28ultra_max_1550"), "itulink": L("ch01.att.g652_link_typ_cband")}
FIB_IN = {"dsfib": ["ch01.att.smf28ultra_max_1550"], "itulink": ["ch01.att.g652_link_typ_cband"]}
L_lo, L_hi = L("ch04.coh.800zr_reach", "lo"), L("ch04.coh.800zr_reach", "hi")
for tag, a in FIB.items():
    ins = GN_IN + FIB_IN[tag]
    r.emit(f"alpha_{tag}", a, "dB/km", 3, FIB_IN[tag])
    for Lk in (L_lo, L_hi):
        po, osnr, eta, pase = span(a, Lk)
        k = int(Lk)
        r.emit(f"popt_{tag}_{k}", cl.w2dbm(po), "dBm", 3, ins)
        r.emit(f"ptot_{tag}_{k}", cl.w2dbm(po * NCH), "dBm", 3, ins)
        r.emit(f"osnr_{tag}_{k}", cl.lin2db(osnr), "dB", 3, ins)
        r.emit(f"margin_{tag}_{k}", cl.lin2db(osnr / OSNR_REQ), "dB", 2, ins)
        r.emit(f"lspan_{tag}_{k}", a * Lk, "dB", 3, FIB_IN[tag])
        # with booster output capped at the datasheet value
        po_c, osnr_c, *_ = span(a, Lk, ba_max - cl.lin2db(NCH))
        r.emit(f"osnrcap_{tag}_{k}", cl.lin2db(osnr_c), "dB", 3, ins + ["ch01.amp.accelink_mw_nf_max"])
        r.emit(f"margincap_{tag}_{k}", cl.lin2db(osnr_c / OSNR_REQ), "dB", 2, ins + ["ch01.amp.accelink_mw_nf_max"])
        if k == int(L_hi):
            r.emit(f"eta_{tag}_db", cl.lin2db(eta), "dB(1/W²)", 4, ins)
            r.emit(f"pase_ref_{tag}_dbm", cl.w2dbm(pase), "dBm", 4, ins)
    # maximum span length meeting the OSNR requirement (GN optimum and capped launch)
    Lmax = brentq(lambda Lk: cl.lin2db(span(a, Lk)[1] / OSNR_REQ), 20, 400)
    Lmax_c = brentq(lambda Lk: cl.lin2db(span(a, Lk, ba_max - cl.lin2db(NCH))[1] / OSNR_REQ), 20, 400)
    r.emit(f"lmax_{tag}", Lmax, "km", 3, ins)
    r.emit(f"lmaxcap_{tag}", Lmax_c, "km", 3, ins + ["ch01.amp.accelink_mw_nf_max"])
    r.emit(f"lmax_loss_{tag}", a * Lmax, "dB", 3, ins)
    r.emit(f"lmaxcap_loss_{tag}", a * Lmax_c, "dB", 3, ins)
    # 26 dB (module EOL spec) instead of 27 dB
    Lmax26 = brentq(lambda Lk: cl.lin2db(span(a, Lk, ba_max - cl.lin2db(NCH))[1]) - osnr400, 20, 400)
    r.emit(f"lmaxcap26_{tag}", Lmax26, "km", 3, ins)

# Consistency with the 58 dB rule (ASE only, at the capped launch, ITU link fibre, 120 km)
p_ch = ba_max - cl.lin2db(NCH)
osnr58 = L("ch01.osnr.gsup39_58db_constant") + p_ch - NF - FIB["itulink"] * L_hi
r.emit("osnr58_itulink_120", osnr58, "dB", 3, ["ch01.osnr.gsup39_58db_constant", "ch01.att.g652_link_typ_cband"])
_, osnr_chk, eta_chk, _ = span(FIB["itulink"], L_hi, p_ch)
assert abs(osnr58 - cl.lin2db(osnr_chk)) < 1.0     # NLI small at the capped launch -> close to the rule

# ---------------- figure: OSNR_max vs span length
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.4))
Ls = np.linspace(40, 200, 161)
for j, (tag, a) in enumerate(FIB.items()):
    lab = "datasheet fibre" if tag == "dsfib" else "ITU typical cabled link"
    ax.plot(Ls, [cl.lin2db(span(a, Lk)[1]) for Lk in Ls], color=cl.COLORS[j * 2], lw=2.2,
            label=f"{lab}, {a} dB/km, GN optimum")
    ax.plot(Ls, [cl.lin2db(span(a, Lk, p_ch)[1]) for Lk in Ls], color=cl.COLORS[j * 2], lw=1.4, ls="--",
            label=f"{lab}, booster-limited launch")
ax.axhline(osnr800, color=cl.COLORS[1], lw=1.2, ls=":")
ax.text(42, osnr800 - 1.6, "800ZR OSNR requirement", ha="left", fontsize=8.5, color=cl.COLORS[1])
ax.axvspan(L_lo, L_hi, color=cl.GRAY, alpha=0.12, lw=0)
ax.text(0.5 * (L_lo + L_hi), 15.5, "800ZR target\nspan range", ha="center", fontsize=8.5)
ax.set_xlabel("Span length (km)")
ax.set_ylabel("OSNR in 0.1 nm (dB)")
ax.set_ylim(14, 46)
ax.legend(fontsize=8, loc="upper right")
ax.set_title(f"Computed (GN model): {int(NCH)} x {rs800} GBd DP-16QAM on {int(DF_GHZ)} GHz, NF {NF:g} dB", fontsize=10)
cl.savefig(fig, "zr800_osnr")

r.save()
