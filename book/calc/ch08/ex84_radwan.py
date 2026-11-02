"""Section 8.4 worked example: SNR margin -> capacity, and the RADWAN fleet figures.

Constant-gap Shannon model (Chapter 2 AWGN capacity, Chapter 1 GSNR):
  net rate per polarization  eta(R) = R / (2 R_s)  [bit/symbol]
  SNR_req(R) = Gamma (2^eta - 1)
Gamma is calibrated on one ledger point (100 Gb/s QPSK at 6.5 dB); the other
ledger points (50 Gb/s at 3 dB is 'enough'; 10.2 dB supports 150 Gb/s) are checks.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch08lib as cl

r = Results()
S100, S50, S150 = "ch08.radwan.snr_req_100g", "ch08.radwan.snr_req_50g", "ch08.radwan.snr_150g_example"
# ASSUMPTION: 15 % soft-decision FEC overhead (the ledger note on ch08.radwan.snr_req_100g states
# the transceivers use 15 % SD-FEC); framing overhead ignored.
assert "15% soft-decision FEC" in cl.rec(S100)["notes"]
OH = 0.15
R100 = 100e9
eta100 = 2 / (1 + OH)                   # QPSK: 2 coded bits per symbol per polarization
Rs = R100 / (2 * eta100)
r.emit("oh_pct", 100 * OH, "%", 2)
r.emit("eta100", eta100, "bit/symbol", 3)
r.emit("rs_gbd", Rs / 1e9, "GBd", 4)
snr100 = cl.db2lin(L(S100))
gamma = snr100 / (2 ** eta100 - 1)
r.emit("shannon100_db", cl.lin2db(2 ** eta100 - 1), "dB", 3, [S100])
r.emit("gap_db", cl.lin2db(gamma), "dB", 3, [S100])


def snr_req_db(R):
    return cl.lin2db(gamma * (2 ** (R / (2 * Rs)) - 1))


def rate(snr_db):
    return 2 * Rs * math.log2(1 + cl.db2lin(snr_db) / gamma)


th = {}
for R in (50, 150, 175, 200):
    th[R] = snr_req_db(R * 1e9)
    r.emit(f"th{R}", th[R], "dB", 3, [S100])
    r.emit(f"m{R}", th[R] - L(S100), "dB", 3, [S100])
th[100] = L(S100)
assert th[50] <= L(S50), "model must say 3 dB is enough for 50 Gb/s"
assert th[150] <= L(S150), "model must say 10.2 dB supports 150 Gb/s"
r.emit("step_100_150", th[150] - th[100], "dB", 3, [S100])
r.emit("step_150_175", th[175] - th[150], "dB", 3, [S100])
r.emit("step_175_200", th[200] - th[175], "dB", 3, [S100])
r.emit("rate_at_102", rate(L(S150)) / 1e9, "Gb/s", 3, [S100, S150])
r.emit("rate_at_3", rate(L(S50)) / 1e9, "Gb/s", 3, [S100, S50])

# marginal value of SNR: dR/dSNR_dB = 2 R_s (ln10/10)/ln2 * x/(1+x), x = SNR/Gamma
k = 2 * Rs * (math.log(10) / 10) / math.log(2)
x100 = snr100 / gamma
r.emit("dRdB_hi", k / 1e9, "Gb/s per dB", 3)
r.emit("dRdB_100", k * x100 / (1 + x100) / 1e9, "Gb/s per dB", 3, [S100])
r.emit("db_per_bit", 10 * math.log10(2), "dB", 4)

# Margins of a static 100G design (Chapter 6.6, Pointurier): what rate would the margin buy?
PB = "ch06.margin.pointurier_example_bol"
bol = L(PB)
eol = cl.cond(PB, "eol_margin_dB")
dmar = cl.cond(PB, "d_margin_dB")
r.emit("pt_bol", bol, "dB", 3, [PB])
r.emit("pt_eol", eol, "dB", 2, [PB])
r.emit("pt_len", cl.cond(PB, "length_km"), "km", 2, [PB])
r.emit("pt_dmargin", dmar, "dB", 2, [PB])
# keep the D-margin, spend the rest (EoL basis); model rate (uncapped)
r.emit("pt_rate_eol", rate(L(S100) + eol - dmar) / 1e9, "Gb/s", 3, [PB, S100])
r.emit("pt_rate_bol", rate(L(S100) + bol - dmar) / 1e9, "Gb/s", 3, [PB, S100])

# ---------- reach check: GSNR at optimum launch ~ 1/N_s (Chapter 1, eps = 0)
RQ, R8, R16 = "ch08.radwan.reach_qpsk", "ch08.radwan.reach_8qam", "ch08.radwan.reach_16qam"
for tag, rid, R in (("8qam", R8, 150), ("16qam", R16, 200)):
    implied = 10 * math.log10(L(RQ) / L(rid))
    r.emit(f"implied_step_{tag}", implied, "dB", 3, [RQ, rid])
    r.emit(f"model_step_{tag}", th[R] - th[100], "dB", 3, [S100])
    r.emit(f"model_reach_{tag}", L(RQ) * 10 ** (-(th[R] - th[100]) / 10), "km", 3, [RQ, S100])

# ---------- fleet: the 75 Gb/s and 134 Tb/s figures
F64, G134, N8, N2 = ("ch08.radwan.upgradable_fraction", "ch08.radwan.capacity_gain",
                     "ch08.radwan.links_analyzed", "ch08.radwan.links_analyzed_preprint")
F95 = "ch08.radwan.above_100g_threshold"
assert "175" in cl.rec(F95)["notes"]
dR75 = 175 - 100          # 175 Gb/s minus 100 Gb/s, the two rates named in the records
r.emit("dR75", dR75, "Gb/s", 2, [F64, F95])
f64, f95 = L(F64) / 100, L(F95) / 100
per_lo = f64 * dR75                              # only the 64 % gain, each by exactly 75
per_hi = f64 * 100 + (f95 - f64) * 50            # 64 % reach 200 G, the rest above threshold reach 150 G
r.emit("per_link_lo", per_lo, "Gb/s", 3, [F64])
r.emit("per_link_hi", per_hi, "Gb/s", 3, [F64, F95])
for tag, nid in (("2k", N2), ("8k", N8)):
    r.emit(f"fleet_lo_{tag}", L(nid) * per_lo / 1e3, "Tb/s", 3, [nid, F64])
    r.emit(f"fleet_hi_{tag}", L(nid) * per_hi / 1e3, "Tb/s", 3, [nid, F64, F95])
n_implied = L(G134) * 1e3 / per_lo
r.emit("n_implied", n_implied, "links", 3, [G134, F64])
r.emit("n_implied_hi", L(G134) * 1e3 / per_hi, "links", 3, [G134, F64, F95])
assert L(N2) * per_lo / 1e3 <= L(G134) <= L(N2) * per_hi / 1e3, "134 Tb/s is bracketed by the 2,000-link fleet"
assert L(N8) * per_lo / 1e3 > L(G134), "8,000 links x 64 % x 75 Gb/s exceeds 134 Tb/s"
# average gain per analysed link implied by each count
r.emit("avg_gain_2k", L(G134) * 1e3 / L(N2), "Gb/s", 3, [G134, N2])
r.emit("avg_gain_8k", L(G134) * 1e3 / L(N8), "Gb/s", 3, [G134, N8])

# ---------- churn of a reconfiguration
RC, RF = "ch08.radwan.reconfig_latency", "ch08.radwan.reconfig_fast"
for tag, R in (("100", 100e9), ("175", 175e9)):
    r.emit(f"churn_gb_{tag}", R * L(RC) / 8 / 1e9, "GB", 3, [RC])
    r.emit(f"churn_fast_gb_{tag}", R * L(RF) * 1e-3 / 8 / 1e9, "GB", 3, [RF])
r.emit("churn_ratio", L(RC) / (L(RF) * 1e-3), "1", 3, [RC, RF])
# a 2 dB weekly SNR swing compared with the threshold steps
W = "ch08.radwan.snr_weekly_variation"
assert "2 dB" in cl.rec(W)["quote"]
r.emit("swing_db", 2.0, "dB", 1, [W])
assert 2.0 > th[175] - th[150] and 2.0 < th[150] - th[100]

# ---------- figure: rate vs SNR
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.4))
s = np.linspace(-2, 16, 600)
ax.plot(s, [2 * Rs * math.log2(1 + cl.db2lin(v)) / 1e9 for v in s], color=cl.GRAY, ls="--", lw=1.4,
        label=f"Shannon, 2 pol at {Rs/1e9:.2f} GBd (no gap)")
ax.plot(s, [rate(v) / 1e9 for v in s], color=cl.COLORS[0], lw=2.0,
        label=f"constant gap {cl.lin2db(gamma):.2f} dB (calibrated at 100 Gb/s)")
steps = [(th[50], 50), (th[100], 100), (th[150], 150), (th[175], 175), (th[200], 200)]
xs, ys = [-2], [0]
for t, R in steps:
    xs += [t, t]; ys += [ys[-1], R]
xs.append(16); ys.append(200)
ax.plot(xs, ys, color=cl.COLORS[1], lw=2.2, label="BVT rate (model thresholds)")
pts = [(L(S50), 50, "3 dB: enough for 50G"), (L(S100), 100, "6.5 dB: 100G required"),
       (L(S150), 150, "10.2 dB: 150G possible")]
for x, y, lab in pts:
    ax.plot([x], [y], "o", color=cl.COLORS[2], ms=7)
    ax.annotate(lab, (x, y), xytext=(x + 0.4, y - 22), fontsize=8.5)
ax.set_xlabel("SNR (dB)")
ax.set_ylabel("Net line rate (Gb/s)")
ax.set_xlim(-2, 16)
ax.set_ylim(0, 300)
ax.legend(fontsize=8.5, loc="upper left")
ax.set_title("Computed: RADWAN ledger thresholds (points) and constant-gap model", fontsize=10)
cl.savefig(fig, "radwan_rate_snr")
r.save()
