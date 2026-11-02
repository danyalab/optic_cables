"""Worked example 6.4: ZR versus ZR+ (FEC threshold to reach), coherent-engine
bits per symbol, and a transceiver-count model of hop-by-hop IP-over-DWDM versus
optical express (ROADM bypass).

Part A  Required SNR of DP-16QAM at the CFEC (400ZR) and oFEC (OpenROADM / ZR+) thresholds,
        and the ASE-limited reach ratio. 400ZR ROSNR converted to SNR.
Part B  Net bits per dual-polarization symbol and the Shannon SNR floor of three engines.
Part C  Chain of K nodes, uniform all-to-all demand d per node pair, wavelength capacity C:
        transceivers and transit router ports, hop-by-hop with grooming versus express.
"""
import math
import itertools
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
import ch06lib as c6
from common import L, Results

r = Results()

# ---------------------------------------------------------------- Part A
ber_c = L("ch06.zr.cfec_threshold")
ber_o = L("ch06.openroadm.ofec_threshold")
s_c = c6.snr_at_ber_16qam(ber_c)
s_o = c6.snr_at_ber_16qam(ber_o)
r.emit("snr_cfec", c6.lin2db(s_c), "dB", 3, ["ch06.zr.cfec_threshold"])
r.emit("snr_ofec", c6.lin2db(s_o), "dB", 3, ["ch06.openroadm.ofec_threshold"])
d_db = c6.lin2db(s_c / s_o)
r.emit("d_fec_db", d_db, "dB", 2, ["ch06.zr.cfec_threshold", "ch06.openroadm.ofec_threshold"])
# ASE-limited at optimum power, eps = 0: N_max proportional to 1/SNR_req (Section 1.6)
r.emit("reach_ratio_fec", s_c / s_o, "1", 3, ["ch06.zr.cfec_threshold", "ch06.openroadm.ofec_threshold"])
r.emit("reach_ratio_fec_pct", 100 * (s_c / s_o - 1), "%", 2, ["ch06.zr.cfec_threshold", "ch06.openroadm.ofec_threshold"])
# QPSK at the oFEC threshold (for the 6.6 planning example and comparison)
s_q = c6.snr_at_ber_qpsk(ber_o)
r.emit("snr_ofec_qpsk", c6.lin2db(s_q), "dB", 3, ["ch06.openroadm.ofec_threshold"])
# 400ZR ROSNR (OIF presentation, draft) -> SNR in R_s, both polarizations (Section 1.5)
rec = "ch06.zr.400zr_vs_800zr_baud"
rosnr = c6.cond(rec, "rosnr_400zr_dB")
rs_zr = L("ch06.zr.oif400zr_baud") * 1e9
BREF = 12.5e9   # 0.1 nm reference bandwidth (Chapter 1 record ch01.osnr.bref_0p1nm_equals_12p5ghz)
assert abs(L("ch01.osnr.bref_0p1nm_equals_12p5ghz") * 1e9 - BREF) < 1
snr_ros = rosnr - c6.lin2db(rs_zr / BREF)
r.emit("rosnr_400zr", rosnr, "dB", 2, [rec])
r.emit("snr_from_rosnr", snr_ros, "dB", 3, [rec, "ch06.zr.oif400zr_baud"])
r.emit("rosnr_gap", snr_ros - c6.lin2db(s_c), "dB", 2, [rec, "ch06.zr.cfec_threshold"])
r.emit("osnr_to_snr_zr", c6.lin2db(rs_zr / BREF), "dB", 3, ["ch06.zr.oif400zr_baud"])
rs800 = L(rec) * 1e9
r.emit("snr_from_rosnr_800", c6.cond(rec, "rosnr_800zr_dB") - c6.lin2db(rs800 / BREF), "dB", 3, [rec])
r.emit("rs_ratio_800_400", rs800 / rs_zr, "1", 4, [rec, "ch06.zr.oif400zr_baud"])

# ---------------------------------------------------------------- Part B
eng = {
    "wl6e": (c6.cond("ch06.coh.wl6e_200gbd_1p6t", "max_rate_Tbps"), L("ch06.coh.wl6e_200gbd_1p6t"),
             ["ch06.coh.wl6e_200gbd_1p6t"]),
    "pse6s": (c6.cond("ch06.coh.pse6s_130gbd_1p2t", "max_rate_Tbps"), L("ch06.coh.pse6s_130gbd_1p2t"),
              ["ch06.coh.pse6s_130gbd_1p2t"]),
    "ice7": (c6.cond("ch06.coh.ice7_148gbd", "max_rate_Tbps"), L("ch06.coh.ice7_148gbd"), ["ch06.coh.ice7_148gbd"]),
    "mard": (1.6, c6.cond("ch06.coh.mardoyan_300gbd_1p6t_9075km", "symbol_rate_GBd"),
             ["ch06.coh.mardoyan_300gbd_1p6t_9075km"]),
}
for tag, (rate, rs, ins) in eng.items():
    b = rate * 1e3 / rs                         # net bits per dual-pol symbol
    snr_sh = 2 ** (b / 2) - 1                   # Shannon, per polarization
    r.emit(f"{tag}_rate", rate, "Tb/s", 2, ins)
    r.emit(f"{tag}_bits", b, "bit/symbol", 3, ins)
    r.emit(f"{tag}_snr_sh", c6.lin2db(snr_sh), "dB", 3, ins)
r.emit("pse6s_vs_wl6e_db", r.data["pse6s_snr_sh"]["value"] - r.data["wl6e_snr_sh"]["value"], "dB", 2,
       ["ch06.coh.pse6s_130gbd_1p2t", "ch06.coh.wl6e_200gbd_1p6t"])
r.emit("pse6s_se", r.data["pse6s_rate"]["value"] * 1e3 / c6.cond("ch06.coh.pse6s_130gbd_1p2t", "spacing_GHz"),
       "b/s/Hz", 3, ["ch06.coh.pse6s_130gbd_1p2t"])
r.emit("wl6e_rs_ratio", L("ch06.coh.wl6e_200gbd_1p6t") / L("ch06.coh.pse6s_130gbd_1p2t"), "1", 3,
       ["ch06.coh.wl6e_200gbd_1p6t", "ch06.coh.pse6s_130gbd_1p2t"])
# Mardoyan's net SE check: 1.6 Tb/s / 306.25 GHz
assert abs(1600 / c6.cond("ch06.coh.mardoyan_300gbd_1p6t_9075km", "spacing_GHz")
           - c6.cond("ch06.coh.mardoyan_300gbd_1p6t_9075km", "net_se_bps_per_Hz")) < 0.01

# ---------------------------------------------------------------- Part C
# ASSUMPTIONS: chain of K = 5 nodes, one router per node, uniform all-to-all demand d per
# unordered node pair, 400 Gb/s per wavelength (400ZR), every path within optical reach
# (no regeneration) and no protection.
K = 5
CAP = 400.0


def hop_by_hop(d, k=K):
    """Transceivers (one per wavelength end) and transit router ports, grooming at every node."""
    loads = [d * i * (k - i) for i in range(1, k)]            # link i <-> i+1
    w = [math.ceil(x / CAP - 1e-12) for x in loads]
    trx = 2 * sum(w)
    # transit traffic terminates on routers at intermediate nodes; port count = transceivers
    # (every wavelength ends on a router). Transit share of router capacity:
    transit = sum(d * (i * (k - 1 - i)) for i in range(1, k - 1))  # traffic passing through node i
    return trx, transit


def express(d, k=K):
    pairs = k * (k - 1) // 2
    return 2 * pairs * math.ceil(d / CAP - 1e-12), 0.0


def brute_hbh(d, k=K):
    load = [0.0] * (k - 1)
    for a, b in itertools.combinations(range(k), 2):
        for l in range(a, b):
            load[l] += d
    return 2 * sum(math.ceil(x / CAP - 1e-12) for x in load)


for d in (50, 100, 200, 300, 400, 800):
    assert hop_by_hop(d)[0] == brute_hbh(d)
ds = np.arange(25, 825, 25)
hb = [hop_by_hop(d)[0] for d in ds]
ex = [express(d)[0] for d in ds]
for d in (100, 200, 400, 800):
    r.emit(f"hbh_{d}", hop_by_hop(d)[0], "", 3)
    r.emit(f"exp_{d}", express(d)[0], "", 3)
    r.emit(f"transit_{d}", hop_by_hop(d)[1] / 1e3, "Tb/s", 3)
cross = next(int(d) for d, a, b in zip(ds, hb, ex) if b <= a)
r.emit("crossover_d", cross, "Gb/s", 3)
r.emit("k_nodes", K, "", 2)
r.emit("cap_gbps", CAP, "Gb/s", 3)
r.emit("pairs", K * (K - 1) // 2, "", 2)
r.emit("exp_saving_400_pct", 100 * (1 - express(400)[0] / hop_by_hop(400)[0]), "%", 2)
# general result at d = C: hop-by-hop 2 * sum i(K-i) = K(K^2-1)/3, express K(K-1)
assert hop_by_hop(CAP)[0] == K * (K ** 2 - 1) // 3 and express(CAP)[0] == K * (K - 1)

plt = c6.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 3.9))
ax.step(ds, hb, where="mid", color=c6.COLORS[0], label="hop-by-hop (router at every node, grooming)")
ax.step(ds, ex, where="mid", color=c6.COLORS[1], label="optical express (ROADM bypass)")
ax.axvline(cross, color=c6.GRAY, ls=":", lw=1)
ax.set_xlabel("Demand per node pair, d (Gb/s)")
ax.set_ylabel("Coherent transceivers")
ax.set_title(f"Computed: {K}-node chain, all-to-all demand, 400 Gb/s per wavelength", fontsize=10)
ax.legend(fontsize=9, loc="upper left")
c6.savefig(fig, "ipodwdm_count")

r.save()
