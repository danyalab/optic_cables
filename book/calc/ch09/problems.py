"""Numerical answers for the Chapter 9 problem set."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import re
import ch09lib as cl

r = Results()
c = cl.c_light()
NG = "ch01.fiber.smf28ultra_group_index_1550"
ng = L(NG)
km_per_ms = c / ng / 1e6

# P1: the 1/5/20 ms circles read as round-trip
TC = "ch09.dsxs.latency_circles_1_5_20"
for t in cl.rec(TC)["value"]:
    r.emit(f"p1_ow_{t}", t * km_per_ms, "km", 3, [TC, NG])
    r.emit(f"p1_rtt_{t}", t / 2 * km_per_ms, "km", 3, [TC, NG])

# P2: 1.5x theoretical latency and the Beijing-Inner Mongolia route
FL1 = "ch09.l400.cmcc_first_link_2024"
TH = "ch09.dsxs.latency_1p5x_theory"
geo_min = L(FL1) / L(TH)
r.emit("p2_geo_min", geo_min, "km", 3, [FL1, TH])
r.emit("p2_tau", L(FL1) / km_per_ms, "ms", 3, [FL1, NG])
r.emit("p2_tau_theory_min", geo_min / km_per_ms, "ms", 3, [FL1, TH, NG])

# P3: PCS-16QAM alternative in the same 12 THz
Q = "ch09.l400.cmcc_qpsk_130gbd_150ghz"
CCSA = "ch09.l400.ct_ccsa_400g_qpsk_params"
CAP = "ch09.l400.cmcc_capacity_32t"
alt = cl.cond(CCSA, "pcs16qam_alt")
rs_p = float(re.search(r"~(\d+) GBaud", alt).group(1)) * 1e9
df_p = float(re.search(r"(\d+) GHz", alt).group(1)) * 1e9
rnet = float(cl.cond(CAP, "rate_Gbps")) * 1e9
B = float(cl.cond(Q, "channels")) * float(cl.cond(Q, "grid_GHz")) * 1e9
nch = int(round(B / df_p))
bits = rnet / (2 * rs_p)
r.emit("p3_nch", nch, "", 3, [Q, CCSA])
r.emit("p3_cap", nch * rnet / 1e12, "Tb/s", 2, [Q, CCSA, CAP])
r.emit("p3_se", rnet / df_p, "b/(s·Hz)", 2, [CCSA, CAP])
r.emit("p3_bits", bits, "bit", 3, [CCSA, CAP])
r.emit("p3_shannon", cl.lin2db(2 ** bits - 1), "dB", 3, [CCSA, CAP])

# P4: SRS tilt for C4.8T+L4.8T at (a) fixed per-channel PSD, (b) fixed total power
SRS, SRSB = "ch09.l400.srs_power_transfer_7db", "ch09.l400.srs_peak_13p4"
b_cu = 9.6e12  # C4.8T + L4.8T, from ch09.l400.cu_400g_cl_1650km conditions
assert "C4.8THz+L4.8THz" == cl.cond("ch09.l400.cu_400g_cl_1650km", "band")
ratio = b_cu / (L(SRSB) * 1e12)
r.emit("p4_fixed_psd", L(SRS) * ratio ** 2, "dB", 3, [SRS, SRSB, "ch09.l400.cu_400g_cl_1650km"])
r.emit("p4_fixed_ptot", L(SRS) * ratio, "dB", 3, [SRS, SRSB, "ch09.l400.cu_400g_cl_1650km"])

# P5: L-band noise figure and the 2/3 rule
NFR = "ch09.l400.ecoc2023_edfa_nf"
dnf = float(cl.cond(NFR, "L_band_NF_max_dB")) - float(cl.cond(NFR, "C_band_NF_max_dB"))
pen = 2 / 3 * dnf
r.emit("p5_dnf", dnf, "dB", 2, [NFR])
r.emit("p5_pen", pen, "dB", 3, [NFR])
r.emit("p5_reach_frac", 100 * 10 ** (-pen / 10), "%", 2, [NFR])

# P6: exit bandwidth growth
X22 = "ch09.intl.exit_bw_2022"
series = {int(y): float(v.replace(",", "")) for y, v in re.findall(r"(20\d\d) ([0-9,]{9,})", cl.rec(X22)["notes"])}
cagr = (series[2022] / series[2018]) ** (1 / 4) - 1
r.emit("p6_cagr", 100 * cagr, "%", 3, [X22])
r.emit("p6_double", math.log(2) / math.log(1 + cagr), "yr", 2, [X22])
r.emit("p6_yrs_to_fiber", math.log(L(CAP) * 1e6 / series[2022]) / math.log(1 + cagr), "yr", 2, [X22, CAP])

# P7: gigabit users per 10G-PON port
GU, P10 = "ch09.acc.gigabit_users_2025", "ch09.acc.10gpon_ports_2025"
k = cl.num(L(GU)) / cl.num(L(P10))
# ASSUMPTION: 10 Gb/s nominal downstream per 10G-PON port (class name)
r.emit("p7_k", k, "", 3, [GU, P10])
r.emit("p7_share", 10e9 / k / 1e6, "Mb/s", 3, [GU, P10])

# P8: group index from the Ningbo-Gui'an loop
FT, FLT = "ch09.l400.field_5616km", "ch09.l400.field_5616km_latency"
ng_i = L(FLT) * 1e-3 * c / (L(FT) * 1e3)
r.emit("p8_ng", ng_i, "", 5, [FT, FLT])
r.emit("p8_us_per_km", L(FLT) * 1e3 / L(FT), "µs/km", 4, [FT, FLT])
r.emit("p8_dkm", L(FT) * (1 - ng_i / ng), "km", 2, [FT, FLT, NG])

# P9: China Telecom OA sites per ROADM link for nodal degree 4
ROADM = "ch09.op.ct_allotical_backbone_scale_2023"
for deg in (3, 4):
    links = L(ROADM) * deg / 2
    spans = float(cl.cond(ROADM, "oa_nodes_lower_bound")) / links + 1
    r.emit(f"p9_spans_d{deg}", spans, "", 3, [ROADM])
    r.emit(f"p9_km_d{deg}", spans * 80, "km", 3, [ROADM])

# P10: capacity needed at CN2 light loading vs B4 average utilization
U1, U2 = "ch09.op.cn2_light_loading_50pct", "ch08.b4.avg_util"
r.emit("p10_ratio", L(U2) / L(U1), "", 2, [U1, U2])
r.emit("p10_extra_pct", 100 * (L(U2) / L(U1) - 1), "%", 2, [U1, U2])
r.save()
