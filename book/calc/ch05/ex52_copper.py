"""Worked example 5.2: passive copper reach versus lane rate.

Cable loss per metre in a low-loss TEM line: IL(f) = a sqrt(f) + b f (conductor
skin effect + dielectric). At a fixed loss budget the reach is L = B / IL(f_N),
so the local exponent p = -dlnL/dlnf_N = (1/2 + x)/(1 + x), x = (b/a) sqrt(f_N),
must lie between 1/2 and 1. We compute p between successive IEEE generations.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch05lib as cl

r = Results()

GEN = [  # (record, lane Gb/s, bits per symbol)
    ("ch05.cu.ieee_40gcr4_7m", 10, 1),
    ("ch05.cu.ieee_100gcr4_5m", 25, 1),
    ("ch05.cu.ieee_50g_cr_3m", 50, 2),
    ("ch05.cu.ieee_100g_lane_cr_2m", 100, 2),
    ("ch05.cu.ieee_200g_lane_cr_1m", 200, 2),
]
for rid, rate, _ in GEN:
    assert cl.cond(rid, "lane_rate_Gbps") == rate

# PAM4 overhead from the two records that state symbol rates
rs100 = cl.cond("ch05.cu.ieee_100g_lane_cr_2m", "symbol_rate_GBd")
rs200 = cl.cond("ch05.cu.ieee_200g_lane_cr_1m", "symbol_rate_GBd")
OH_PAM4 = rs100 / (100 / 2)
assert abs(rs200 / (200 / 2) - OH_PAM4) < 1e-12
# ASSUMPTION: the 50G PAM4 generation uses the same coding overhead as 100G and 200G lanes
# ASSUMPTION: the NRZ generations (10G, 25G) use 64b/66b line coding, overhead 66/64
OH_NRZ = 66 / 64
r.emit("oh_pam4", OH_PAM4, "", 5, ["ch05.cu.ieee_100g_lane_cr_2m"])
r.emit("oh_nrz", OH_NRZ, "", 5)

fn, reach = [], []
for rid, rate, bps in GEN:
    oh = OH_NRZ if bps == 1 else OH_PAM4
    rs = rate * oh / bps
    fn.append(rs / 2)
    reach.append(L(rid))
    r.emit(f"fn_{rate}", rs / 2, "GHz", 4, [rid])
    r.emit(f"rs_{rate}", rs, "GBd", 5, [rid])
fn = np.array(fn)
reach = np.array(reach)

# local exponents between successive generations with distinct Nyquist frequencies
pairs = [(0, 1, "10_25"), (2, 3, "50_100"), (3, 4, "100_200"), (0, 4, "10_200")]
pex = {}
for i, j, tag in pairs:
    p = math.log(reach[i] / reach[j]) / math.log(fn[j] / fn[i])
    pex[tag] = p
    r.emit(f"p_{tag}", p, "", 2, [GEN[i][0], GEN[j][0]])
assert pex["10_25"] < 0.5 < pex["50_100"] < 1.0
assert abs(pex["100_200"] - 1.0) < 1e-9
# x = (b/a) sqrt(f) implied by p = (1/2 + x)/(1 + x) for the 50 -> 100 step (constant-budget reading)
p = pex["50_100"]
x = (p - 0.5) / (1 - p)
r.emit("x_50_100", x, "", 2, [GEN[2][0], GEN[3][0]])
r.emit("fgeo_50_100", math.sqrt(fn[2] * fn[3]), "GHz", 3, [GEN[2][0], GEN[3][0]])
fc = math.sqrt(fn[2] * fn[3]) / x ** 2          # frequency where the two loss terms are equal
r.emit("fc_50_100", fc, "GHz", 2, [GEN[2][0], GEN[3][0]])

# 25G NRZ -> 50G PAM4: almost the same Nyquist frequency, shorter reach
r.emit("fn_ratio_25_50", fn[2] / fn[1], "", 3, [GEN[1][0], GEN[2][0]])
r.emit("reach_ratio_25_50", reach[2] / reach[1], "", 2, [GEN[1][0], GEN[2][0]])
pen = L("ch02.imdd.pam4_penalty_electrical")
eye = 20 * math.log10(3)                         # (N-1) = 3 for PAM4 (ch02.imdd.pamn_eye_height)
assert abs(eye - pen) < 0.05
r.emit("pam4_pen", pen, "dB", 2, ["ch02.imdd.pam4_penalty_electrical"])

# 200G: IEEE objective vs NVIDIA statement
r.emit("nv_vs_ieee", L("ch05.cu.nvidia_xdr_dac_lt_0p7m") / L("ch05.cu.ieee_200g_lane_cr_1m") * 100, "%", 2,
       ["ch05.cu.nvidia_xdr_dac_lt_0p7m", "ch05.cu.ieee_200g_lane_cr_1m"])
# If the loss per metre at 53 GHz is the same, the shorter usable length means the host/package
# take a larger share of a fixed end-to-end budget: Delta_host = (1 - 0.7) * IL_cable(1 m).
r.emit("nv_extra_frac", (1 - L("ch05.cu.nvidia_xdr_dac_lt_0p7m") / L("ch05.cu.ieee_200g_lane_cr_1m")) * 100, "%", 2,
       ["ch05.cu.nvidia_xdr_dac_lt_0p7m", "ch05.cu.ieee_200g_lane_cr_1m"])

# ---------------------------------------------------------------- energy per bit
# ASSUMPTION: 8 electrical lanes per cable end for the 800G (100G/lane) and 1.6T (200G/lane) products
LANES = 8
media = []
def add(tag, label, watts, lane_g, rid, reach_m):
    tbps = LANES * lane_g / 1e3
    pj = watts / tbps            # W per Tb/s = pJ/bit
    r.emit(f"pj_{tag}", pj, "pJ/bit", 2, [rid])
    r.emit(f"w_{tag}", watts, "W", 3, [rid])
    media.append((label, pj, reach_m))
    return pj

add("dac100", "Passive DAC, 100G/lane", cl.cond("ch05.cu.nvidia_ndr_dac_2m", "power_W_per_end"), 100,
    "ch05.cu.nvidia_ndr_dac_2m", L("ch05.cu.nvidia_ndr_dac_2m"))
add("acc100", "Linear ACC, 100G/lane", cl.cond("ch05.cu.nvidia_ndr_acc_5m", "power_W_8ch_end"), 100,
    "ch05.cu.nvidia_ndr_acc_5m", L("ch05.cu.nvidia_ndr_acc_5m", "lo"))
add("lacc200", "LACC, 200G/lane", cl.cond("ch05.cu.nvidia_aec_lacc_power", "lacc_W"), 200,
    "ch05.cu.nvidia_aec_lacc_power", L("ch05.cu.nvidia_xdr_active_reach", "lo"))
add("aec200", "DSP AEC, 200G/lane", cl.cond("ch05.cu.nvidia_aec_lacc_power", "aec_W_per_end"), 200,
    "ch05.cu.nvidia_aec_lacc_power", L("ch05.cu.nvidia_xdr_active_reach", "hi"))
add("aec100", "DSP AEC (Credo), 100G/lane", cl.cond("ch05.cu.credo_aec_800g_7m", "power_W_per_end_typ"), 100,
    "ch05.cu.credo_aec_800g_7m", L("ch05.cu.credo_aec_800g_7m"))
add("opt800", "800G 2xDR4 optics", L("ch04.pmd.800g_2xdr4_power"), 100, "ch04.pmd.800g_2xdr4_power",
    L("ch04.std.8023dj_dr_reach", "lo"))
add("opt1600", "1.6T DR8 optics", L("ch04.pmd.1p6t_dr8_power"), 200, "ch04.pmd.1p6t_dr8_power",
    L("ch04.std.8023dj_dr_reach", "lo"))
r.emit("aec_over_lacc", cl.cond("ch05.cu.nvidia_aec_lacc_power", "aec_W_per_end") /
       cl.cond("ch05.cu.nvidia_aec_lacc_power", "lacc_W"), "", 2, ["ch05.cu.nvidia_aec_lacc_power"])
r.emit("aec_over_opt1600", cl.cond("ch05.cu.nvidia_aec_lacc_power", "aec_W_per_end") /
       L("ch04.pmd.1p6t_dr8_power") * 100, "%", 2, ["ch05.cu.nvidia_aec_lacc_power", "ch04.pmd.1p6t_dr8_power"])
r.emit("dr_reach_ratio", L("ch04.std.8023dj_dr_reach", "lo") / L("ch05.cu.ieee_200g_lane_cr_1m"), "", 2,
       ["ch04.std.8023dj_dr_reach", "ch05.cu.ieee_200g_lane_cr_1m"])

# ---------------------------------------------------------------- figure
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.6))
ax.plot(fn, reach, "o-", color=cl.COLORS[0], ms=7, label="IEEE passive-twinax reach objectives")
for (rid, rate, bps), f, L_ in zip(GEN, fn, reach):
    ax.annotate(f"{rate}G {'NRZ' if bps == 1 else 'PAM4'}", (f, L_), xytext=(6, 4), textcoords="offset points", fontsize=8.5)
ff = np.geomspace(4, 70, 100)
ax.plot(ff, reach[3] * (ff / fn[3]) ** -0.5, color=cl.GRAY, ls="--", lw=1.2, label=r"$L\propto f_N^{-1/2}$ (skin effect only)")
ax.plot(ff, reach[3] * (ff / fn[3]) ** -1.0, color=cl.GRAY, ls=":", lw=1.4, label=r"$L\propto f_N^{-1}$ (dielectric only)")
ax.plot([fn[4]], [L("ch05.cu.nvidia_xdr_dac_lt_0p7m")], "v", color=cl.COLORS[1], ms=8, label="NVIDIA: usable passive DAC at 200G/lane")
ax.plot([fn[3], fn[4]], [L("ch05.cu.nvidia_ndr_acc_5m", "lo"), L("ch05.cu.nvidia_xdr_active_reach", "hi")], "s",
        color=cl.COLORS[2], ms=7, label="Active copper (ACC, AEC), vendor")
ax.plot([fn[3]], [L("ch05.cu.credo_aec_800g_7m")], "s", color=cl.COLORS[2], ms=7, mfc="none")
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel("Nyquist frequency of the lane, $f_N$ (GHz)")
ax.set_ylabel("Cable reach (m)")
ax.set_xticks([5, 10, 20, 50]); ax.set_xticklabels(["5", "10", "20", "50"])
ax.set_yticks([0.5, 1, 2, 5, 10]); ax.set_yticklabels(["0.5", "1", "2", "5", "10"])
ax.set_ylim(0.4, 12)
ax.legend(fontsize=8, loc="lower left")
ax.set_title("Ledger values with constant-budget guide lines through the 100G point", fontsize=10)
cl.savefig(fig, "copper_reach")

r.save()
