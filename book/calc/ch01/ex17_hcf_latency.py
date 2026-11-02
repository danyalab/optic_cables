"""Section 1.7: latency of hollow-core vs solid-core fibre from group indices.

t/L = n_g / c. Latency reduction = 1 - n_g,HCF/n_g,SMF; speed-up = n_g,SMF/n_g,HCF - 1.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch01lib as cl

r = Results()
c = L("ch01.const.speed_of_light_c")
ng_smf = L("ch01.fiber.smf28ultra_group_index_1550")
ng_hcf = L("ch01.hcf.ng_nanf_vs_smf28", "lo")        # pair [NANF, SMF-28]; 'lo' is the NANF entry
ins = ["ch01.fiber.smf28ultra_group_index_1550", "ch01.hcf.ng_nanf_vs_smf28", "ch01.const.speed_of_light_c"]

t_smf = ng_smf / c * 1e3 * 1e6        # µs/km
t_hcf = ng_hcf / c * 1e3 * 1e6
r.emit("t_smf", t_smf, "µs/km", 4, ins)
r.emit("t_hcf", t_hcf, "µs/km", 4, ins)
r.emit("dt", t_smf - t_hcf, "µs/km", 3, ins)
red = 100 * (1 - ng_hcf / ng_smf)
spd = 100 * (ng_smf / ng_hcf - 1)
r.emit("lat_red_pct", red, "%", 3, ins)
r.emit("speedup_pct", spd, "%", 3, ins)
# Consistency: the quoted latency figures straddle the computed value
quoted = [L("ch01.hcf.petrovich2025_latency_30pct"), L("ch01.hcf.yofc_ar2025_latency_31pct"),
          L("ch01.hcf.msft_latency_33pct"), L("ch01.hcf.latency_reduction_antesberger")]
assert min(quoted) <= red <= max(quoted)
# Poletti 2013: 1.54 µs/km faster at 99.7 % of c (n_g = 1/0.997)
r.emit("dt_poletti_check", t_smf - (1 / 0.997) / c * 1e9, "µs/km", 3, ins)
assert abs((t_smf - (1 / 0.997) / c * 1e9) - L("ch01.hcf.poletti2013_speed_997pct")) < 0.03

# Plausibility of the (tier C) Dongguan-Hong Kong round-trip figure: 100 km HCF + 10 km SMF
hcf_km = float(cl.cond("ch01.hcf.ctel_hk_link_latency", "hollow_core_length_km"))
tot_km = float(cl.cond("ch01.hcf.ctel_hk_link_latency", "cable_length_km"))
rtt = 2 * (hcf_km * t_hcf + (tot_km - hcf_km) * t_smf) / 1e3   # ms
r.emit("hk_rtt_fibre_ms", rtt, "ms", 3, ins + ["ch01.hcf.ctel_hk_link_latency"])
r.emit("hk_rtt_allsmf_ms", 2 * tot_km * t_smf / 1e3, "ms", 3, ins + ["ch01.hcf.ctel_hk_link_latency"])

# Hero vs batch ratio for YOFC ST-HCF (ECOC 2025)
r.emit("yofc_batch_over_hero", L("ch01.hcf.ding2025_yofc_batch_avg") / L("ch01.hcf.ding2025_yofc_sthcf_005"), "1", 3,
       ["ch01.hcf.ding2025_yofc_batch_avg", "ch01.hcf.ding2025_yofc_sthcf_005"])
# Petrovich HCF1 method spread ratio
r.emit("hcf1_spread_ratio", L("ch01.hcf.petrovich2025_hcf1_method_spread", "hi") /
       L("ch01.hcf.petrovich2025_hcf1_method_spread", "lo"), "1", 2, ["ch01.hcf.petrovich2025_hcf1_method_spread"])
# Loss of an 80 km span of record DNANF vs record silica
r.emit("span_hcf_db", 80 * L("ch01.hcf.petrovich2025_loss_1550"), "dB", 3, ["ch01.hcf.petrovich2025_loss_1550"])
r.emit("span_silica_db", 80 * L("ch01.ull.sato2025_record_1550"), "dB", 3, ["ch01.ull.sato2025_record_1550"])
r.save()
