"""Worked example 9.6: US and China on matched metrics.

Inputs are ledger records of Chapter 9 and of Chapter 8 (US) that existed when
this script was written. Values are only put side by side when the basis can
be stated; conversions (one-way vs round-trip, miles vs km, ports vs passings)
are explicit.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch09lib as cl

r = Results()
n = cl.num
c = cl.c_light()
NG = "ch01.fiber.smf28ultra_group_index_1550"
km_per_ms = c / L(NG) / 1e6

# ---------------- latency on a common basis ---------------------------------------
T20 = "ch09.dsxs.cluster_latency_20ms"
VZ = "ch09.cmp.us_verizon_na_latency"
lo, hi = (float(v) for v in cl.cond(VZ, "measured_range_ms"))
r.emit("cn_ow", L(T20), "ms", 2, [T20])
r.emit("cn_rtt", 2 * L(T20), "ms", 2, [T20])
r.emit("us_rtt", L(VZ), "ms", 2, [VZ])
r.emit("us_ow", L(VZ) / 2, "ms", 3, [VZ])
r.emit("us_meas_ow_lo", lo / 2, "ms", 3, [VZ])
r.emit("us_meas_ow_hi", hi / 2, "ms", 3, [VZ])
r.emit("cn_L", L(T20) * km_per_ms, "km", 3, [T20, NG])
r.emit("us_L", L(VZ) / 2 * km_per_ms, "km", 3, [VZ, NG])
r.emit("us_cn_rtt_ratio", L(VZ) / (2 * L(T20)), "", 3, [VZ, T20])
r.emit("bead_lat", L("ch09.cmp.us_bead_latency_100ms"), "ms", 3, ["ch09.cmp.us_bead_latency_100ms"])

# ---------------- long-haul footprint ----------------------------------------------------
# ASSUMPTION: 1 international mile = 1.609344 km (exact by the 1959 definition of the
# international yard; not a ledger record).
MILE_KM = 1.609344
LU = "ch09.cmp.us_lumen_route_miles"
LH = "ch09.acc.cable_split_2025"
lumen_km = L(LU) * MILE_KM
r.emit("mile_km", MILE_KM, "km", 7)
r.emit("lumen_kkm", lumen_km / 1e3, "thousand km", 3, [LU])
r.emit("cn_lh_kkm", n(L(LH)) / 1e3, "thousand km", 4, [LH])
r.emit("cn_lh_over_lumen", n(L(LH)) / lumen_km, "", 2, [LH, LU])
r.emit("cu_88_over_lumen", n(L("ch09.op.cu_new_88_total_198k")) / lumen_km, "", 2,
       ["ch09.op.cu_new_88_total_198k", LU])
IT = "ch09.cmp.us_longhaul_map"
r.emit("it_conduits", L(IT), "", 3, [IT])
r.emit("it_nodes", float(cl.cond(IT, "nodes")), "", 3, [IT])
r.emit("it_links", float(cl.cond(IT, "links")), "", 4, [IT])
r.emit("it_share_ge2", L("ch08.intertubes.share_ge2"), "%", 4, ["ch08.intertubes.share_ge2"])

# ---------------- fiber access ----------------------------------------------------
UP = "ch09.cmp.us_fiber_passings_2025"
us_pass, us_conn = n(L(UP)), n(cl.cond(UP, "connected_households"))
FT = "ch09.acc.ftth_ports_2025"
NFB = "ch09.op.national_fixed_bb_users_2025"
r.emit("us_pass_m", us_pass / 1e6, "million", 3, [UP])
r.emit("us_conn_m", us_conn / 1e6, "million", 2, [UP])
r.emit("us_take_pct", 100 * us_conn / us_pass, "%", 3, [UP])
r.emit("cn_ftth_b", n(L(FT)) / 1e9, "billion", 3, [FT])
r.emit("cn_port_use_pct", 100 * n(L(NFB)) / n(cl.cond(FT, "total_ports")), "%", 3, [FT, NFB])
r.emit("oecd_fibre_pct", L("ch09.cmp.oecd_fibre_share_2024"), "%", 2, ["ch09.cmp.oecd_fibre_share_2024"])
r.emit("cn_ftth_share", float(cl.cond(FT, "share_pct")), "%", 3, [FT])
r.emit("bead_busd", L("ch09.cmp.us_bead_42p45b"), "billion USD", 4, ["ch09.cmp.us_bead_42p45b"])

# ---------------- utilization policy ----------------------------------------------
r.emit("cn2_load", L("ch09.op.cn2_light_loading_50pct"), "%", 2, ["ch09.op.cn2_light_loading_50pct"])
r.emit("b4_util", L("ch08.b4.avg_util"), "%", 2, ["ch08.b4.avg_util"])
r.emit("wan_util_lo", L("ch08.b4.typical_wan_util", "lo"), "%", 2, ["ch08.b4.typical_wan_util"])
r.emit("wan_util_hi", L("ch08.b4.typical_wan_util", "hi"), "%", 2, ["ch08.b4.typical_wan_util"])
r.emit("swan_lo", L("ch08.swan.busy_link_util", "lo"), "%", 2, ["ch08.swan.busy_link_util"])
r.emit("swan_hi", L("ch08.swan.busy_link_util", "hi"), "%", 2, ["ch08.swan.busy_link_util"])
r.emit("chisel_free", L("ch08.chisel.unused_spectrum"), "%", 2, ["ch08.chisel.unused_spectrum"])
# Capacity needed for the same carried traffic at the two utilization levels
r.emit("cn2_vs_b4_capacity", L("ch08.b4.avg_util") / L("ch09.op.cn2_light_loading_50pct"), "", 2,
       ["ch08.b4.avg_util", "ch09.op.cn2_light_loading_50pct"])

# ---------------- per-fiber capacity and format reach ------------------------------
CAP = "ch09.l400.cmcc_capacity_32t"
GO = "ch08.google_optical.fiber_pair_capacity"
IR = "ch08.iris.dc_capacity_example"
iris_tb, iris_pairs = (float(v) for v in cl.rec(IR)["value"])
r.emit("cmcc_cap", L(CAP), "Tb/s", 2, [CAP])
r.emit("google13_cap", L(GO), "Tb/s", 2, [GO])
r.emit("iris_cap", iris_tb / iris_pairs, "Tb/s", 2, [IR])
r.emit("cmcc_over_google", L(CAP) / L(GO), "", 3, [CAP, GO])
r.emit("google_cl", L("ch08.google_optical.cl_band"), "", 1, ["ch08.google_optical.cl_band"])
r.emit("radwan_qpsk", L("ch08.radwan.reach_qpsk"), "km", 2, ["ch08.radwan.reach_qpsk"])
r.emit("radwan_8qam", L("ch08.radwan.reach_8qam"), "km", 2, ["ch08.radwan.reach_8qam"])
r.emit("radwan_16qam", L("ch08.radwan.reach_16qam"), "km", 2, ["ch08.radwan.reach_16qam"])
r.emit("cmcc_reach", L("ch09.l400.reach_1500_g652d_edfa"), "km", 2, ["ch09.l400.reach_1500_g652d_edfa"])
r.emit("chisel_austin_nyc", L("ch08.chisel.austin_nyc_reach"), "km", 2, ["ch08.chisel.austin_nyc_reach"])
r.emit("chisel_austin_nyc_ms", L("ch08.chisel.austin_nyc_reach") / km_per_ms, "ms", 3,
       ["ch08.chisel.austin_nyc_reach", NG])

# ---------------- ownership ----------------------------------------------------------
r.emit("cmcc_state", L("ch09.op.cmcc_ownership_2025"), "%", 3, ["ch09.op.cmcc_ownership_2025"])
r.emit("ct_state", L("ch09.op.ct_ownership_2025"), "%", 3, ["ch09.op.ct_ownership_2025"])

# ---------------- tier-C US records used only in the contested box ---------------------
LU4 = "ch08.carrier.lumen_400g_route_miles"
r.emit("lumen_400g_kkm", L(LU4) * MILE_KM / 1e3, "thousand km", 3, [LU4])
r.emit("lumen_400g_mi", L(LU4), "route-mi", 3, [LU4])
r.emit("lumen_400g_frac", 100 * L(LU4) / L(LU), "%", 2, [LU4, LU])

# ---------------- compute bases --------------------------------------------------------
MI = "ch09.dsxs.racks_2025_06"
CA = "ch09.dsxs.caict_device_compute_962"
r.emit("miit_fp16", float(cl.cond(MI, "intelligent_compute_EFLOPS_FP16")), "EFLOPS", 3, [MI])
r.emit("caict_fp32_ai", float(cl.cond(CA, "intelligent_EFLOPS_FP32")), "EFLOPS", 3, [CA])
r.emit("caict_fp32_tot", L(CA), "EFLOPS", 3, [CA])
r.emit("caict_basic", float(cl.cond(CA, "basic_EFLOPS_FP32")), "EFLOPS", 3, [CA])
r.save()
