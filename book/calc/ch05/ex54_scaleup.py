"""Worked example 5.4: scale-up versus scale-out bandwidth, NVL72 cable arithmetic,
and the optical-spine power estimate.

All NVLink and ICI figures in the sources are bidirectional totals; we convert to
per-direction rates before comparing with NIC rates, which are per direction.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import ch05lib as cl

r = Results()

# ------------------------------------------------ NVLink generations
gens = (("4", "ch05.su.nvlink4_900", "ch05.ai.cx7_400g"),
        ("5", "ch05.su.nvlink5_1800", "ch05.ai.cx8_800g"),
        ("6", "ch05.su.nvlink6_3000", "ch05.ai.cx8_800g"))
for g, rid, nic in gens:
    bidir = L(rid)                                 # GB/s
    links = cl.cond(rid, "links")
    per_dir_gbps = bidir / 2 * 8
    r.emit(f"nvl{g}_dir_tbps", per_dir_gbps / 1e3, "Tb/s", 3, [rid])
    r.emit(f"nvl{g}_link_GBps", bidir / links, "GB/s", 3, [rid])
    r.emit(f"nvl{g}_links", links, "links", 2, [rid])
    r.emit(f"nvl{g}_ratio", per_dir_gbps / L(nic), "", 3, [rid, nic])
# tier-C cross-check (contested box only): the switch-tray port rate equals the per-link rate
assert L("ch05.su.nvlink5_1800") / cl.cond("ch05.su.nvlink5_1800", "links") == cl.cond("ch05.su.nvl72_switch_tray", "port_rate_GBps")

# ------------------------------------------------ NVL72
TRAY = "ch05.su.nvl72_switch_tray"
gpus = cl.cond("ch05.su.nvl72_130tbs", "gpus")
trays = cl.cond(TRAY, "trays")
gpu_links = cl.cond(TRAY, "gpu_links")
assert trays * L(TRAY) == gpus * gpu_links
agg = gpus * cl.cond("ch05.su.nvl72_130tbs", "per_gpu_TBps")
assert abs(agg / L("ch05.su.nvl72_130tbs") - 1) < 0.005
r.emit("nvl72_ports", trays * L(TRAY), "ports", 4, [TRAY])
r.emit("nvl72_agg", agg, "TB/s", 4, ["ch05.su.nvl72_130tbs"])
r.emit("nvl72_gpus", gpus, "GPUs", 2, ["ch05.su.nvl72_130tbs"])
# cable arithmetic for the contested count
c_sa = L("ch05.su.nvl72_5184_cables")
per_link = c_sa / (gpus * gpu_links)
assert per_link == 4
r.emit("cables_per_link", per_link, "", 1, ["ch05.su.nvl72_5184_cables"])
link_dir_gbps = L("ch05.su.nvlink5_1800") / cl.cond("ch05.su.nvlink5_1800", "links") / 2 * 8   # Gb/s per direction per link
# ASSUMPTION (box): one differential pair (one cable) per lane per direction
lanes_per_dir = per_link / 2
r.emit("link_dir_gbps", link_dir_gbps, "Gb/s", 3, ["ch05.su.nvlink5_1800"])
r.emit("lane_gbps", link_dir_gbps / lanes_per_dir, "Gb/s", 3, [TRAY, "ch05.su.nvl72_5184_cables"])
assert link_dir_gbps / lanes_per_dir == cl.cond("ch05.cu.ieee_200g_lane_cr_1m", "lane_rate_Gbps")   # 200G-class lane
# optical-spine power check against the 20 kW claim
spine_tbps = gpus * L("ch05.su.nvlink5_1800") / 2 * 8 / 1e3       # Tb/s per direction, GPU side
xcvr_tbps = cl.cond("ch05.pw.transceiver_1p6t_30w", "rate_Tbps")
assert xcvr_tbps == 1.6
n_x = 2 * spine_tbps / xcvr_tbps                                   # both ends of every link
p_kw = n_x * L("ch04.pmd.1p6t_dr8_power") / 1e3                    # 1.6T DR8 datasheet maximum
p_kw_blog = n_x * L("ch05.pw.transceiver_1p6t_30w") / 1e3          # tier-C blog figure
r.emit("spine_kw_blog", p_kw_blog, "kW", 3, ["ch05.pw.transceiver_1p6t_30w"])
r.emit("spine_vs_claim_blog", p_kw_blog / L("ch05.su.nvl72_optics_20kw_claim") * 100, "%", 2,
       ["ch05.su.nvl72_optics_20kw_claim"])
r.emit("spine_tbps", spine_tbps, "Tb/s", 4, ["ch05.su.nvlink5_1800"])
r.emit("spine_xcvr", n_x, "transceivers", 3, ["ch05.su.nvlink5_1800"])
r.emit("spine_kw", p_kw, "kW", 3, ["ch05.su.nvlink5_1800", "ch04.pmd.1p6t_dr8_power"])
r.emit("spine_vs_claim", p_kw / L("ch05.su.nvl72_optics_20kw_claim") * 100, "%", 2,
       ["ch05.su.nvl72_optics_20kw_claim"])
BCP = "ch04.pw.broadcom_pluggable_14w_800g"
cpo_ratio = L(BCP) / float(cl.cond(BCP, "comparison").split()[1].rstrip("W/800G"))
r.emit("cpo_ratio_bcm", cpo_ratio, "", 3, [BCP])
r.emit("spine_kw_cpo", p_kw / cpo_ratio, "kW", 2, [BCP, "ch04.pmd.1p6t_dr8_power"])
r.emit("spine_w_per_gpu", p_kw * 1e3 / gpus, "W", 3, ["ch04.pmd.1p6t_dr8_power"])
assert 0.75 < p_kw / L("ch05.su.nvl72_optics_20kw_claim") < 1.0

# ------------------------------------------------ UALink
UA = "ch05.su.ualink_lane_rate"
assert L(UA) * cl.cond(UA, "max_link_width") == L("ch05.su.ualink_station_800g")
ua_oh = cl.cond(UA, "signaling_GTps") / L(UA)
ex52 = json.loads((pathlib.Path(__file__).parent / "out" / "ex52_copper.json").read_text())
assert abs(ua_oh - ex52["oh_pam4"]["value"]) < 1e-12        # same overhead as the IEEE 200G lane
assert 2 ** 10 == L("ch05.su.ualink_1024")
r.emit("ua_oh", ua_oh, "", 5, [UA])
r.emit("ua_station", L("ch05.su.ualink_station_800g"), "Gb/s", 3, ["ch05.su.ualink_station_800g"])
r.emit("ua_stations_for_nvl5", L("ch05.su.nvlink5_1800") / 2 * 8 / L("ch05.su.ualink_station_800g"), "stations", 2,
       ["ch05.su.ualink_station_800g", "ch05.su.nvlink5_1800"])

# ------------------------------------------------ Ironwood
IW = "ch05.su.ironwood_ici"
assert cl.cond(IW, "links") * cl.cond(IW, "per_link_GBps") == L(IW)
assert cl.cond("ch05.su.ironwood_9216", "cubes") * cl.cond("ch05.su.ironwood_9216", "chips_per_cube") == L("ch05.su.ironwood_9216")
iw_dir = L(IW) / 2 * 8
r.emit("iw_dir_tbps", iw_dir / 1e3, "Tb/s", 3, [IW])
r.emit("iw_ratio", iw_dir / L("ch05.su.ironwood_dcn_100g"), "", 3, [IW, "ch05.su.ironwood_dcn_100g"])

# ------------------------------------------------ CloudMatrix384
CM = "ch05.su.cloudmatrix_ub_bw"
per_die = cl.cond(CM, "transceivers_per_die") * cl.cond(CM, "transceiver_Gbps")
assert abs(per_die / 8 - L(CM) / 2) < 1e-9
cm_dir = L(CM) * 8
cm_out = 2 * cl.cond(CM, "rdma_per_die_Gbps")
r.emit("cm_die_gbps", per_die, "Gb/s", 4, [CM])
r.emit("cm_dir_tbps", cm_dir / 1e3, "Tb/s", 3, [CM])
r.emit("cm_out_gbps", cm_out, "Gb/s", 3, [CM])
r.emit("cm_ratio", cm_dir / cm_out, "", 3, [CM])

# ------------------------------------------------ Broadcom optical scale-up
BC = "ch05.su.broadcom_512_scaleup"
n_g = cl.cond(BC, "gpus")
n_sw = cl.cond(BC, "switches")
tot = n_g * L(BC)
assert tot / 102.4 == n_sw
link = float(cl.cond(BC, "link").split()[0])
r.emit("bc_links_per_gpu", L(BC) * 1e3 / link, "links", 2, [BC])
r.emit("bc_tot_pbps", tot / 1e3, "Pb/s", 3, [BC])
assert L(BC) * 1e3 / link == n_sw

# ------------------------------------------------ latency
r.emit("lat_ratio", cl.cond("ch05.ai.tencent_nvlink_roce_latency", "roce_us") * 1e3 /
       cl.cond("ch05.ai.tencent_nvlink_roce_latency", "nvlink_ns"), "", 2, ["ch05.ai.tencent_nvlink_roce_latency"])
# TP requirement of Section 5.3 against NVLink 4 per direction
ex53 = json.loads((pathlib.Path(__file__).parent / "out" / "ex53_allreduce.json").read_text())
r.emit("tp_vs_nvl4", ex53["b_tp_gbps"]["value"] / (L("ch05.su.nvlink4_900") / 2 * 8) * 100, "%", 2,
       ["ch05.su.nvlink4_900"])

r.save()
