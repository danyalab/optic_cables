"""Worked example 6.1: flexgrid arithmetic, channel counts in C and C+L, spectral efficiency.

All band edges and grids come from ledger records (G.694.1, OIF 400ZR/800ZR, the
IEEE 802.3ct 400ZR baseline, WSS datasheets, Semrau 2018, Jiang 2024, China Mobile
field trials). Counts are floor(band / slot), i.e. slots placed edge to edge.
"""
import math
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import ch06lib as c6
from common import L, Results

r = Results()
h, c = c6.consts()

# ------------------------------------------------------------- G.694.1 lattice
F0 = L("ch06.grid.anchor_193p1") * 1e12              # Hz
DF_C = L("ch06.grid.flex_center_granularity") * 1e9  # 6.25 GHz
DF_S = L("ch06.grid.flex_slot_granularity") * 1e9    # 12.5 GHz
assert abs(DF_S - 2 * DF_C) < 1.0, "slot granularity must be twice the centre granularity"
r.emit("lam_anchor_nm", c / F0 * 1e9, "nm", 6, ["ch06.grid.anchor_193p1", "ch01.const.speed_of_light_c"])


def slot_edges(n, m):
    fc = F0 + n * DF_C
    w = m * DF_S
    return fc - w / 2, fc + w / 2


def on_12p5_lattice(f):
    k = (f - F0) / DF_S
    return abs(k - round(k)) < 1e-9


# Parity rule: edges of slot (n, m) are F0 + 6.25 GHz (n -/+ m); they lie on the 12.5 GHz
# lattice iff n and m have the same parity. Check by brute force.
for n in range(-20, 21):
    for m in range(1, 13):
        lo, hi = slot_edges(n, m)
        assert (on_12p5_lattice(lo) and on_12p5_lattice(hi)) == ((n - m) % 2 == 0)
# Example slots
for tag, m in (("s375", 3), ("s75", 6), ("s1125", 9), ("s150", 12)):
    r.emit(f"{tag}_m", m, "", 2)
    r.emit(f"{tag}_ghz", m * DF_S / 1e9, "GHz", 4, ["ch06.grid.flex_slot_granularity"])
# A 37.5 GHz slot (m = 3, odd) centred at n = 1, i.e. 193.10625 THz
lo, hi = slot_edges(1, 3)
r.emit("ex_fc_thz", (F0 + 1 * DF_C) / 1e12, "THz", 7, ["ch06.grid.anchor_193p1", "ch06.grid.flex_center_granularity"])
r.emit("ex_lo_thz", lo / 1e12, "THz", 7, ["ch06.grid.anchor_193p1"])
r.emit("ex_hi_thz", hi / 1e12, "THz", 7, ["ch06.grid.anchor_193p1"])
assert on_12p5_lattice(lo) and on_12p5_lattice(hi)

# ------------------------------------------------------------- C-band widths
zr_lo = L("ch06.zr.cband_191p3_196p1", "lo") * 1e12
zr_hi = L("ch06.zr.cband_191p3_196p1", "hi") * 1e12
B_C = zr_hi - zr_lo
assert abs(B_C - L("ch06.wss.finisar_cband_4p8thz", "lo") * 1e12) < 1e6, "4.8 THz C-band in two sources"
r.emit("bc_thz", B_C / 1e12, "THz", 2, ["ch06.zr.cband_191p3_196p1"])
r.emit("zr_lam_lo_nm", c / zr_hi * 1e9, "nm", 5, ["ch06.zr.cband_191p3_196p1"])
r.emit("zr_lam_hi_nm", c / zr_lo * 1e9, "nm", 5, ["ch06.zr.cband_191p3_196p1"])
itu_lo = L("ch01.amp.cband_range_itu", "lo") * 1e-9
itu_hi = L("ch01.amp.cband_range_itu", "hi") * 1e-9
B_ITU = c / itu_lo - c / itu_hi
r.emit("b_itu_thz", B_ITU / 1e12, "THz", 3, ["ch01.amp.cband_range_itu"])
r.emit("b_superc_thz", L("ch06.wss.finisar_cband_4p8thz", "hi"), "THz", 2, ["ch06.wss.finisar_cband_4p8thz"])
lum = (L("ch06.wss.lumentum_twin_1x20_range", "hi") - L("ch06.wss.lumentum_twin_1x20_range", "lo"))
r.emit("b_lumentum_thz", lum, "THz", 2, ["ch06.wss.lumentum_twin_1x20_range"])

# Channel counts in the 4.8 THz C-band
counts = {}
for sp in (50, 75, 100, 150):
    counts[sp] = math.floor(B_C / (sp * 1e9) + 1e-9)
    r.emit(f"nc_{sp}", counts[sp], "", 3, ["ch06.zr.cband_191p3_196p1"])
oif = [int(v) for v in c6.rec("ch06.zr.oif400zr_channel_plans")["value"]]
assert counts[100] == oif[0] and counts[75] == oif[1], "OIF 48x100 and 64x75 plans reproduced"
assert counts[150] == int(c6.cond("ch06.zr.oif800zr_scope", "channels")), "800ZR 32x150 reproduced"

# C+L (Semrau, ~10 THz) and super C+L (Jiang, two ~6 THz bands)
B_CL = L("ch06.cl.semrau_cl_10thz") * 1e12
sl = c6.cond("ch06.cl.super_cl_12thz_bands", "super_L_THz")
sc = c6.cond("ch06.cl.super_cl_12thz_bands", "super_C_THz")
B_sL = (sl[1] - sl[0]) * 1e12
B_sC = (sc[1] - sc[0]) * 1e12
gap = (sc[0] - sl[1]) * 1e12
r.emit("b_sl_thz", B_sL / 1e12, "THz", 3, ["ch06.cl.super_cl_12thz_bands"])
r.emit("b_sc_thz", B_sC / 1e12, "THz", 3, ["ch06.cl.super_cl_12thz_bands"])
r.emit("b_scl_thz", (B_sL + B_sC) / 1e12, "THz", 4, ["ch06.cl.super_cl_12thz_bands"])
r.emit("gap_cl_ghz", gap / 1e9, "GHz", 3, ["ch06.cl.super_cl_12thz_bands"])
r.emit("b_sc_vs_c_pct", 100 * (B_sC / B_C - 1), "%", 2, ["ch06.cl.super_cl_12thz_bands", "ch06.zr.cband_191p3_196p1"])
for sp in (50, 75, 150):
    n_cl = math.floor(B_CL / (sp * 1e9) + 1e-9)
    n_scl = math.floor(B_sL / (sp * 1e9)) + math.floor(B_sC / (sp * 1e9))
    r.emit(f"ncl_{sp}", n_cl, "", 3, ["ch06.cl.semrau_cl_10thz"])
    r.emit(f"nscl_{sp}", n_scl, "", 3, ["ch06.cl.super_cl_12thz_bands"])
    if sp == 150:
        n_scl150 = n_scl
# China Mobile 2502 km trial: 80 channels on a 150 GHz grid over C6T + L6T
cm_ch = 80
assert "80-λ" in c6.rec("ch06.cl.cmcc_c6t_l6t_2502km")["quote"]
cm_grid = c6.cond("ch06.cl.cmcc_c6t_l6t_2502km", "grid_GHz")
r.emit("cm_occupied_thz", cm_ch * cm_grid / 1e3, "THz", 3, ["ch06.cl.cmcc_c6t_l6t_2502km"])
assert abs(cm_ch * 0.4 - c6.cond("ch06.cl.cmcc_c6t_l6t_2502km", "capacity_Tbps")) < 1e-9
r.emit("cm_extra_vs_jiang", cm_ch - n_scl150, "", 2, ["ch06.cl.cmcc_c6t_l6t_2502km", "ch06.cl.super_cl_12thz_bands"])
# China Mobile C6T/L6T band edges in nm (from the claim text)
c6lo = c6.from_text("ch06.cl.cmcc_c6t_l6t_2502km", r"6 THz C \((\d+)-")
c6hi = c6.from_text("ch06.cl.cmcc_c6t_l6t_2502km", r"6 THz C \(\d+-(\d+) nm")
l6lo = c6.from_text("ch06.cl.cmcc_c6t_l6t_2502km", r"6 THz L \((\d+)-")
l6hi = c6.from_text("ch06.cl.cmcc_c6t_l6t_2502km", r"6 THz L \(\d+-(\d+) nm")
bc6 = c / (c6lo * 1e-9) - c / (c6hi * 1e-9)
bl6 = c / (l6lo * 1e-9) - c / (l6hi * 1e-9)
r.emit("cm_c6_thz", bc6 / 1e12, "THz", 3, ["ch06.cl.cmcc_c6t_l6t_2502km"])
r.emit("cm_l6_thz", bl6 / 1e12, "THz", 3, ["ch06.cl.cmcc_c6t_l6t_2502km"])
r.emit("cm_c6_lo", c6lo, "nm", 4, ["ch06.cl.cmcc_c6t_l6t_2502km"])
r.emit("cm_c6_hi", c6hi, "nm", 4, ["ch06.cl.cmcc_c6t_l6t_2502km"])
r.emit("cm_l6_lo", l6lo, "nm", 4, ["ch06.cl.cmcc_c6t_l6t_2502km"])
r.emit("cm_l6_hi", l6hi, "nm", 4, ["ch06.cl.cmcc_c6t_l6t_2502km"])

# ------------------------------------------------------------- rates and spectral efficiency
rs_zr = L("ch06.zr.oif400zr_baud") * 1e9
line = 2 * 4 * rs_zr
assert abs(line / 1e9 - 478.75) < 1e-6, "400ZR line rate in the IA quote"
r.emit("zr_line_gbps", line / 1e9, "Gb/s", 5, ["ch06.zr.oif400zr_baud"])
r.emit("zr_oh_pct", 100 * (line / 400e9 - 1), "%", 3, ["ch06.zr.oif400zr_baud"])
r.emit("zr_occ", rs_zr / 75e9, "1", 3, ["ch06.zr.oif400zr_baud", "ch06.zr.oif400zr_channel_plans"])
r.emit("se_400zr", 400e9 / 75e9, "b/s/Hz", 3, ["ch06.zr.oif400zr_channel_plans"])
r.emit("se_800zr", 800e9 / (c6.cond("ch06.zr.oif800zr_scope", "spacing_GHz") * 1e9), "b/s/Hz", 3, ["ch06.zr.oif800zr_scope"])
r.emit("cap_c_400zr", counts[75] * 0.4, "Tb/s", 3, ["ch06.zr.oif400zr_channel_plans"])
md_sp = c6.cond("ch06.coh.mardoyan_300gbd_1p6t_9075km", "spacing_GHz")
se_md = 1.6e12 / (md_sp * 1e9)
assert "1.6 Tb/s" in c6.rec("ch06.coh.mardoyan_300gbd_1p6t_9075km")["quote"]
assert abs(se_md - c6.cond("ch06.coh.mardoyan_300gbd_1p6t_9075km", "net_se_bps_per_Hz")) < 0.005
r.emit("se_mardoyan", se_md, "b/s/Hz", 3, ["ch06.coh.mardoyan_300gbd_1p6t_9075km"])
r.emit("se_cm_400g", 400e9 / (cm_grid * 1e9), "b/s/Hz", 3, ["ch06.cl.cmcc_c6t_l6t_2502km"])
cm96 = c6.cond("ch06.cl.cmcc_96tb_305km", "channels") * c6.cond("ch06.cl.cmcc_96tb_305km", "rate_per_channel_Tbps")
assert abs(cm96 - L("ch06.cl.cmcc_96tb_305km")) < 1e-9
r.emit("se_cm_96t", L("ch06.cl.cmcc_96tb_305km") / 12.0, "b/s/Hz", 3, ["ch06.cl.cmcc_96tb_305km"])
r.emit("cap_scl_800zr_grid", n_scl150 * 0.8, "Tb/s", 3, ["ch06.cl.super_cl_12thz_bands"])

# ------------------------------------------------------------- Gerstel superchannel gains
# 1 Tb/s DP-QPSK: 10 x 100G in 10 x 50 GHz = 500 GHz fixed grid, vs 190 + 10 GHz flexgrid
q_fixed, q_flex = 10 * 50, 190 + c6.cond("ch06.sc.gerstel_1t_qpsk_gain", "guard_band_GHz")
gain_q = 100 * (q_fixed / q_flex - 1)
assert abs(gain_q - L("ch06.sc.gerstel_1t_qpsk_gain")) < 1.0
s_fixed, s_flex = 2 * 50, c6.cond("ch06.sc.gerstel_400g_16qam_gain", "superchannel_bw_GHz") + \
    c6.cond("ch06.sc.gerstel_400g_16qam_gain", "guard_band_GHz")
gain_s = 100 * (s_fixed / s_flex - 1)
assert abs(gain_s - L("ch06.sc.gerstel_400g_16qam_gain")) < 1.0
r.emit("gerstel_q_gain", gain_q, "%", 3, ["ch06.sc.gerstel_1t_qpsk_gain"])
r.emit("gerstel_s_gain", gain_s, "%", 3, ["ch06.sc.gerstel_400g_16qam_gain"])
r.emit("gerstel_s_flex", s_flex, "GHz", 2, ["ch06.sc.gerstel_400g_16qam_gain"])
# Superchannel SE versus number of subcarriers (ASSUMPTION: 400ZR-like subcarriers of
# 400 Gb/s at 59.84375 GBd, packed at 62.5 GHz (m = 5) with one 12.5 GHz guard per superchannel).
SUB_SP = 62.5e9
GUARD = 12.5e9
assert SUB_SP > rs_zr
for k in (1, 2, 4, 8):
    se = k * 400e9 / (k * SUB_SP + GUARD)
    r.emit(f"se_sc_{k}", se, "b/s/Hz", 3, ["ch06.zr.oif400zr_baud"])
r.emit("se_sc_inf", 400e9 / SUB_SP, "b/s/Hz", 3, ["ch06.zr.oif400zr_baud"])
r.emit("sub_sp_ghz", SUB_SP / 1e9, "GHz", 3)
r.emit("guard_ghz", GUARD / 1e9, "GHz", 3)

r.save()
