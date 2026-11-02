"""Section 8.4: Microsoft regional design (Dukic et al. 2020) and CHISEL spectrum.

Latency: one-way t = n_g L / c with the Chapter 1 group index of standard SMF.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import re
import ch08lib as cl

r = Results()
tkm = cl.us_per_km()
ins = [cl.NG_ID, cl.C_ID]
r.emit("ng", L(cl.NG_ID), "1", 5, [cl.NG_ID])
r.emit("us_per_km", tkm, "µs/km", 4, ins)
r.emit("km_per_ms_rtt", 1e3 / (2 * tkm), "km", 3, ins)
DMAX, RTT = "ch08.iris.max_dc_distance", "ch08.iris.rtt_example"
ow = L(DMAX) * tkm / 1e3
r.emit("ow_120", ow, "ms", 3, ins + [DMAX])
r.emit("rtt_120", 2 * ow, "ms", 3, ins + [DMAX])
r.emit("rtt_dev_pct", 100 * (2 * ow - L(RTT)) / L(RTT), "%", 2, ins + [DMAX, RTT])
assert abs(2 * ow - L(RTT)) / L(RTT) < 0.05, "120 km of SMF must give the paper's ~1.2 ms RTT"
r.emit("d_from_rtt", L(RTT) * 1e3 / (2 * tkm), "km", 3, ins + [RTT])
r.emit("hub_km", L(DMAX) / 2, "km", 2, [DMAX])
# vacuum (c) comparison: the same RTT budget in free space / hollow core (n_g ~ 1)
r.emit("d_vacuum", L(RTT) * 1e-3 / 2 * L(cl.C_ID) / 1e3, "km", 3, [RTT, cl.C_ID])
r.emit("rtt_120_vac", 2 * L(DMAX) * 1e3 / L(cl.C_ID) * 1e3, "ms", 3, [DMAX, cl.C_ID])

# Unamplified reach and loss
UR = "ch08.iris.unamplified_reach"
a = cl.cond(UR, "fiber_loss_dB_per_km")
r.emit("alpha_iris", a, "dB/km", 2, [UR])
r.emit("loss_80", a * L(UR), "dB", 3, [UR])
r.emit("loss_120", a * L(DMAX), "dB", 3, [UR, DMAX])
r.emit("loss_extra", a * (L(DMAX) - L(UR)), "dB", 2, [UR, DMAX])
r.emit("osnr_tol", L("ch08.iris.osnr_penalty_tolerance"), "dB", 2, ["ch08.iris.osnr_penalty_tolerance"])

# Fiber pairs for 160 Tb/s per DC
DC = "ch08.iris.dc_capacity_example"
q = cl.rec(DC)["quote"]
gbps = float(re.search(r"With ([0-9]+) Gbps", q).group(1))
nwl = float(re.search(r"each of ([0-9]+) wavelengths", q).group(1))
per_pair = gbps * nwl / 1e3
r.emit("wl_rate", gbps, "Gb/s", 3, [DC])
r.emit("wl_count", nwl, "wavelengths", 2, [DC])
r.emit("per_pair", per_pair, "Tb/s", 3, [DC])
r.emit("pairs", L(DC, "lo") / per_pair, "fiber pairs", 2, [DC])
assert abs(L(DC, "lo") / per_pair - L(DC, "hi")) < 1e-9

# CHISEL: unused spectrum
CU = "ch08.chisel.unused_spectrum"
note = cl.rec(CU)["notes"]
m = re.search(r"([0-9,]+)-([0-9,]+) GHz discretized into ([0-9]+) pixels of ([0-9.]+) GHz", note)
f_lo, f_hi = (float(x.replace(",", "")) for x in m.group(1, 2))
npx, wpx = float(m.group(3)), float(m.group(4))
band = (f_hi - f_lo) / 1e3
r.emit("chisel_band", band, "THz", 2, [CU])
r.emit("chisel_px", npx, "pixels", 3, [CU])
r.emit("chisel_pxw", wpx, "GHz", 3, [CU])
assert abs(npx * wpx / 1e3 - band) < 1e-9
ZR = "ch06.zr.cband_191p3_196p1"
assert abs((L(ZR, "hi") - L(ZR, "lo")) - band) < 1e-9, "same 4.8 THz C-band as the 400ZR plan of Chapter 6"
free = band * L(CU) / 100
r.emit("free_thz", free, "THz", 2, [CU])
r.emit("free_px", npx * L(CU) / 100, "pixels", 2, [CU])
# ASSUMPTION: 100 Gb/s QPSK channels on a 50 GHz grid for a 2,800 km path (RADWAN reach table:
# QPSK reaches 3,000 km, 8QAM 2,100 km), i.e. 2 b/s/Hz
SE_LONG = 100 / 50
AU = "ch08.chisel.austin_nyc_reach"
assert L("ch08.radwan.reach_8qam") < L(AU) < L("ch08.radwan.reach_qpsk")
r.emit("se_long", SE_LONG, "b/s/Hz", 2)
r.emit("free_cap_long", free * SE_LONG, "Tb/s", 2, [CU])
# 400ZR plan (Chapter 6): 64 channels of 75 GHz, 400G each -> SE (short reach only)
r.emit("se_zr", 400 / 75, "b/s/Hz", 3, ["ch06.zr.oif400zr_channel_plans"])
r.emit("free_cap_zr", free * 400 / 75, "Tb/s", 3, [CU, "ch06.zr.oif400zr_channel_plans"])
r.emit("austin_ow_ms", L(AU) * tkm / 1e3, "ms", 3, [AU] + ins)
r.save()
