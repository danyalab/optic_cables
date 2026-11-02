"""Worked example 6.2: WSS passband model, cascade narrowing and a filtering-penalty model.

Passband: ledger equation ch06.eq.wss_passband (rectangle of width B convolved with a
Gaussian of 3 dB width BW_OTF, to the power N_WSS). The equation and the example
BW_OTF = 10.4 GHz are recorded from a Politecnico di Torino MSc thesis (tier B); the
original Pulikkaseril et al. (2011) paper was not read.

Step 1  Fit (B, BW_OTF) of one commercial-class LCoS WSS to the measured -3 dB and
        -0.5 dB widths of a 50 GHz channel (Huang JLT 2023), check the -1 dB width.
Step 2  Cascade narrowing; check against Rizzelli JLT 2025 (75 GHz, 6 filters, about 63 GHz).
Step 3  Penalty model (ours): equalizer noise enhancement for a Nyquist signal,
        zero-forcing (upper bound) and linear MMSE, noise added after the filters.
Step 4  Node arithmetic for a route-and-select CDC-F ROADM built from 1x35 twin WSSs.
"""
import math
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from scipy.optimize import fsolve
import ch06lib as c6
from common import L, Results

r = Results()
HU = "ch06.wss.huang_passband_50ghz"
w3 = L(HU)
w05 = float(c6.cond(HU, "minus_0p5dB_typ_GHz"))
w1 = float(c6.cond(HU, "minus_1dB_typ_GHz"))
SLOT = 50.0

# ---------------------------------------------------------------- Step 1: fit
B_fit, bw_fit = fsolve(lambda p: [c6.bw_at(3, p[0], p[1]) - w3, c6.bw_at(0.5, p[0], p[1]) - w05], [w3, 9.0])
w1_pred = c6.bw_at(1, B_fit, bw_fit)
assert abs(c6.bw_at(3, B_fit, bw_fit) - w3) < 1e-6 and abs(c6.bw_at(0.5, B_fit, bw_fit) - w05) < 1e-6
# Independent check: the -1 dB width was not used in the fit. Huang reports it to 0.1 GHz
# resolution, and a second-order shape error of the model is plausible: allow 0.5 GHz.
assert abs(w1_pred - w1) < 0.5, "erf model must predict the measured -1 dB width"
ins1 = [HU, "ch06.wss.filter_model_bwotf"]
r.emit("w3", w3, "GHz", 3, [HU])
r.emit("w05", w05, "GHz", 3, [HU])
r.emit("w1", w1, "GHz", 3, [HU])
r.emit("b_fit", B_fit, "GHz", 3, ins1)
r.emit("bw_fit", bw_fit, "GHz", 2, ins1)
r.emit("sigma_fit", bw_fit / (2 * math.sqrt(2 * math.log(2))), "GHz", 2, ins1)
r.emit("w1_pred", w1_pred, "GHz", 3, ins1)
r.emit("deficit", SLOT - B_fit, "GHz", 2, ins1)
# Thesis example (B = 37.5 GHz, BW_OTF = 10.4 GHz): -0.5 dB width
bw_th = L("ch06.wss.filter_model_bwotf")
r.emit("th_w05", c6.bw_at(0.5, 37.5, bw_th), "GHz", 3, ["ch06.wss.filter_model_bwotf"])
r.emit("th_w3", c6.bw_at(3, 37.5, bw_th), "GHz", 3, ["ch06.wss.filter_model_bwotf"])
# Width of the transition region: -0.5 dB to -3 dB edge distance is about 1.23 sigma
r.emit("edge_05_3", (w3 - w05) / 2, "GHz", 3, [HU])

# ---------------------------------------------------------------- Step 2: cascades
for n in (2, 6, 12, 24, 48):
    r.emit(f"w3_n{n}", c6.bw_at(3, B_fit, bw_fit, n), "GHz", 3, ins1)
# Rizzelli: 75 GHz nominal, super-Gaussian order 6 <-> BW_OTF = 6.8 GHz, 6 filters,
# random centre offsets of +/-5 % of the nominal width.
bw_sg6 = c6.rec("ch06.wss.sg_order_bwotf_map")["value"][1]
nom = c6.cond("ch06.wss.rizzelli_6wss_63ghz", "nominal_GHz")
nf = int(c6.cond("ch06.wss.rizzelli_6wss_63ghz", "filters"))
w_nojit = c6.bw_at(3, nom, bw_sg6, nf)
off = 0.05 * nom
x = np.linspace(-1.2 * nom, 1.2 * nom, 48001)
H = np.prod([c6.wss_power_transfer(x - o, nom, bw_sg6) for o in [off, -off] * (nf // 2)], axis=0)
idx = np.where(H >= H.max() / 2)[0]
w_worst = x[idx[-1]] - x[idx[0]]
riz = L("ch06.wss.rizzelli_6wss_63ghz")
assert w_worst - 1.0 <= riz <= w_nojit, "Rizzelli's 63 GHz must lie between our bounds"
r.emit("riz_bw_otf", bw_sg6, "GHz", 2, ["ch06.wss.sg_order_bwotf_map"])
r.emit("riz_nojit", w_nojit, "GHz", 3, ["ch06.wss.rizzelli_6wss_63ghz", "ch06.wss.sg_order_bwotf_map"])
r.emit("riz_worst", w_worst, "GHz", 3, ["ch06.wss.rizzelli_6wss_63ghz", "ch06.wss.sg_order_bwotf_map"])
r.emit("riz_off", off, "GHz", 3, ["ch06.wss.rizzelli_6wss_63ghz"])

# ---------------------------------------------------------------- Step 3: penalties
# ASSUMPTION: the passband deficit of the fitted device (slot - B_fit) carries over to
# other slot widths (it is set by the LCoS pixel and optics, not by the slot).
DEF = SLOT - B_fit
# ASSUMPTION: Nyquist (zero roll-off) signal spectrum of width R_s; noise added after the filters.
# ASSUMPTION: SNR before equalization 15 dB for the MMSE variant.
SNR0 = 15.0
r.emit("snr0", SNR0, "dB", 2)
rs_zr = L("ch06.zr.oif400zr_baud")
rs_100g = c6.from_text("ch06.wss.filter_cascade_rahman2014", r"28-(\d+) GBd")
cases = {
    "zr75": (rs_zr, 75.0, ["ch06.zr.oif400zr_baud"]),
    "q50": (rs_100g, 50.0, ["ch06.wss.filter_cascade_rahman2014"]),
    "q375": (rs_100g, 37.5, ["ch06.wss.filter_cascade_rahman2014", "ch06.wss.filter_cascade_pan2017"]),
}
r.emit("rs_100g", rs_100g, "GBd", 2, ["ch06.wss.filter_cascade_rahman2014"])
curves = {}
NR = np.arange(0, 25)
for tag, (rs, slot, ins) in cases.items():
    zf = [c6.zf_penalty_db(rs, slot - DEF, bw_fit, 2 * k) if k else 0.0 for k in NR]
    mm = [c6.mmse_penalty_db(rs, slot - DEF, bw_fit, 2 * k, SNR0) if k else 0.0 for k in NR]
    curves[tag] = (zf, mm)
    for k in (1, 4, 8, 12, 24):
        r.emit(f"{tag}_zf_{k}", zf[k], "dB", 2, ins1 + ins)
        r.emit(f"{tag}_mm_{k}", mm[k], "dB", 2, ins1 + ins)
    # MMSE never exceeds ZF; penalties grow monotonically with the cascade
    assert all(m <= z + 1e-9 for m, z in zip(mm, zf))
    assert all(b >= a - 1e-12 for a, b in zip(zf, zf[1:]))
    # number of ROADMs at which the ZF penalty first exceeds 1 dB
    k1 = next((int(k) for k in NR if zf[k] > 1.0), None)
    r.emit(f"{tag}_n1db", k1 if k1 is not None else 99, "ROADMs", 2, ins1 + ins)
# Pan 2017 (abstract): 3 WSSs supported at 37.5 GHz without precompensation. Our model
# puts the 1 dB point inside the first two ROADMs (four WSSs) for this case.
assert curves["q375"][0][2] > 1.0
# Broadcast-and-select (one WSS per ROADM) vs route-and-select (two) at 24 ROADMs, 32 GBd, 50 GHz
r.emit("bs24_w3", c6.bw_at(3, SLOT - DEF, bw_fit, 24), "GHz", 3, ins1)
r.emit("rs24_w3", c6.bw_at(3, SLOT - DEF, bw_fit, 48), "GHz", 3, ins1)
r.emit("bs24_zf", c6.zf_penalty_db(rs_100g, SLOT - DEF, bw_fit, 24), "dB", 2, ins1)
r.emit("rs24_zf", curves["q50"][0][24], "dB", 2, ins1)
r.emit("bs24_mm", c6.mmse_penalty_db(rs_100g, SLOT - DEF, bw_fit, 24, SNR0), "dB", 2, ins1)
r.emit("rs24_mm", curves["q50"][1][24], "dB", 2, ins1)

# ---------------------------------------------------------------- Step 4: node arithmetic
IL = L("ch06.wss.huang_twin1x35_il")
r.emit("express_il", 2 * IL, "dB", 3, ["ch06.wss.huang_twin1x35_il"])
il_hi = c6.cond("ch06.wss.huang_twin1x35_il", "range_dB")[1]
r.emit("express_il_hi", 2 * il_hi, "dB", 3, ["ch06.wss.huang_twin1x35_il"])
NPORT = int(L("ch06.wss.lumentum_twin_1x35"))
# ASSUMPTION: node degree 8 (illustrative large core node)
DEG = 8
r.emit("deg", DEG, "", 2)
r.emit("ad_ports", NPORT - (DEG - 1), "", 3, ["ch06.wss.lumentum_twin_1x35"])
r.emit("wss_count", 2 * DEG, "", 2)
r.emit("lcos_granularity", L("ch06.grid.flex_center_granularity") / 2, "GHz", 4, ["ch06.grid.flex_center_granularity"])

# ---------------------------------------------------------------- figures
plt = c6.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.2))
f = np.linspace(-40, 40, 2001)
for i, n in enumerate((1, 2, 6, 24)):
    ax.plot(f, 10 * np.log10(np.maximum(c6.wss_power_transfer(f, B_fit, bw_fit, n), 1e-6)),
            color=c6.COLORS[i], label=f"{n} WSS" if n > 1 else "1 WSS (fit)")
for lvl, w in ((0.5, w05), (1.0, w1), (3.0, w3)):
    ax.plot([-w / 2, w / 2], [-lvl, -lvl], "o", color=c6.COLORS[4], ms=5)
ax.plot([], [], "o", color=c6.COLORS[4], ms=5, label="Huang 2023, measured widths")
ax.set_xlim(-35, 35)
ax.set_ylim(-12, 0.8)
ax.set_xlabel("Frequency offset from slot centre (GHz)")
ax.set_ylabel("Power transfer (dB)")
ax.set_title("Computed: erf passband fitted to a 50 GHz LCoS WSS channel, and cascades", fontsize=10)
ax.legend(fontsize=9, loc="lower center", ncol=3)
c6.savefig(fig, "wss_cascade")

fig, ax = plt.subplots(figsize=(7.2, 4.2))
labels = {"zr75": "400ZR, 59.8 GBd in 75 GHz", "q50": f"{rs_100g:.0f} GBd in 50 GHz",
          "q375": f"{rs_100g:.0f} GBd in 37.5 GHz"}
for i, tag in enumerate(("zr75", "q50", "q375")):
    zf, mm = curves[tag]
    ax.plot(NR, zf, color=c6.COLORS[i], label=labels[tag] + ", ZF")
    ax.plot(NR, mm, color=c6.COLORS[i], ls="--", lw=1.5, label="  MMSE (15 dB)")
ax.axhline(1.0, color=c6.GRAY, lw=1, ls=":")
ax.set_ylim(0, 8)
ax.set_xlim(0, 24)
ax.set_xlabel("Number of route-and-select ROADMs (2 WSS each)")
ax.set_ylabel("Equalizer SNR penalty (dB)")
ax.set_title("Computed: noise-enhancement penalty of WSS cascades (model, not measured)", fontsize=10)
ax.legend(fontsize=8.5, loc="upper right", ncol=1)
c6.savefig(fig, "filter_penalty")

r.save()
