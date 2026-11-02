"""Worked example 3.2: reach limit of a VCSEL/MMF link from effective modal bandwidth.

Gaussian link model: an impulse response of rms width sigma has |H(f)| = exp(-2 pi^2 sigma^2 f^2),
so its optical 3-dB bandwidth (|H| = 1/2) is B = sqrt(ln2 / 2) / (pi sigma) = 0.1874 / sigma.
Modal: B_m = EMB / L. Chromatic: sigma_cd = |D| L sigma_lambda.
Gaussian widths add in quadrature, so 1/B^2 = 1/B_m^2 + 1/B_cd^2.
Reach criterion (ASSUMPTION): B_total >= KAPPA * R_s.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import re
import numpy as np
import ch03lib as cl

r = Results()
G = math.sqrt(math.log(2) / 2) / math.pi          # 0.18739
assert abs(G - 0.18739) < 1e-4
r.emit("gauss_const", G, "1", 4)

# ASSUMPTION: NRZ reach criterion, end-to-end optical 3-dB bandwidth >= half the symbol rate.
KAPPA = 0.5
r.emit("kappa", KAPPA, "1", 2)

RS = float(cl.cond("ch03.mmf.swdm4_reach_om5", "lane_rate_GBd")) * 1e9
r.emit("rs", RS / 1e9, "GBd", 7, ["ch03.mmf.swdm4_reach_om5"])
emb3, emb4, emb5 = (L(x) * 1e6 * 1e3 for x in ("ch03.mmf.om3_emb", "ch03.mmf.om4_emb", "ch03.mmf.om5_emb_953"))  # Hz*m
D953 = L("ch03.mmf.om5_cd_953") * 1e-12 / (1e-9 * 1e3)   # s/m^2
sig_l = L("ch03.mmf.swdm4_rms_width") * 1e-9              # m


def btot(L_m, emb, D=0.0, sl=0.0):
    bm = emb / L_m
    if D == 0.0:
        return bm
    bcd = G / (abs(D) * L_m * sl)
    return 1 / math.sqrt(1 / bm ** 2 + 1 / bcd ** 2)


def lmax(emb, D=0.0, sl=0.0, kappa=KAPPA, rs=RS):
    return 1 / (kappa * rs * math.sqrt(1 / emb ** 2 + (abs(D) * sl / G) ** 2))


# 1. Modal bandwidth at the IEEE 100GBASE-SR4 reaches (modal only)
for tag, emb, rid in (("om3", emb3, "ch03.mmf.sr4_reach_om3"), ("om4", emb4, "ch03.mmf.sr4_reach_om4")):
    Lr = L(rid)
    bm = emb / Lr
    r.emit(f"sr4_bm_{tag}", bm / 1e9, "GHz", 3, [rid, f"ch03.mmf.{tag}_emb"])
    r.emit(f"sr4_bm_ratio_{tag}", bm / RS, "1", 3, [rid, f"ch03.mmf.{tag}_emb"])
    r.emit(f"lmax_modal_{tag}", lmax(emb), "m", 3, [f"ch03.mmf.{tag}_emb"])
r.emit("reach_ratio_ieee", L("ch03.mmf.sr4_reach_om4") / L("ch03.mmf.sr4_reach_om3"), "1", 3,
       ["ch03.mmf.sr4_reach_om3", "ch03.mmf.sr4_reach_om4"])
r.emit("emb_ratio", emb4 / emb3, "1", 3, ["ch03.mmf.om3_emb", "ch03.mmf.om4_emb"])
r.emit("reach_ratio_fotc", L("ch03.mmf.fotc_sr4_conflict_om4") / L("ch03.mmf.fotc_sr4_conflict_om3"), "1", 3,
       ["ch03.mmf.fotc_sr4_conflict_om3", "ch03.mmf.fotc_sr4_conflict_om4"])

# Power budget check: OM4 channel insertion loss = fiber attenuation + connection allocation
il_calc = L("ch03.mmf.sr4_cable_atten") * L("ch03.mmf.sr4_reach_om4") / 1e3 + \
    float(cl.cond("ch03.mmf.sr4_channel_il_om4", "connection_loss_allocation_dB"))
r.emit("sr4_il_om4_calc", il_calc, "dB", 3, ["ch03.mmf.sr4_cable_atten", "ch03.mmf.sr4_reach_om4", "ch03.mmf.sr4_channel_il_om4"])
r.emit("sr4_fiber_loss_om4", L("ch03.mmf.sr4_cable_atten") * L("ch03.mmf.sr4_reach_om4") / 1e3, "dB", 2,
       ["ch03.mmf.sr4_cable_atten", "ch03.mmf.sr4_reach_om4"])
assert abs(il_calc - L("ch03.mmf.sr4_channel_il_om4")) <= 0.06

# 2. SWDM4 lane on OM5 at the 953 nm EMB (lower bound for the long lane), with CD
L5 = L("ch03.mmf.swdm4_reach_om5")
bm5 = emb5 / L5
bcd5 = G / (abs(D953) * L5 * sig_l)
bt5 = btot(L5, emb5, D953, sig_l)
ins5 = ["ch03.mmf.om5_emb_953", "ch03.mmf.om5_cd_953", "ch03.mmf.swdm4_rms_width", "ch03.mmf.swdm4_reach_om5"]
r.emit("swdm_bm", bm5 / 1e9, "GHz", 3, ins5)
r.emit("swdm_sigcd", abs(D953) * L5 * sig_l * 1e12, "ps", 3, ins5)
r.emit("swdm_bcd", bcd5 / 1e9, "GHz", 3, ins5)
r.emit("swdm_bt", bt5 / 1e9, "GHz", 3, ins5)
r.emit("swdm_bt_ratio", bt5 / RS, "1", 3, ins5)
lm5 = lmax(emb5, D953, sig_l)
lm5_modal = lmax(emb5)
r.emit("swdm_lmax", lm5, "m", 3, ins5)
r.emit("swdm_lmax_modal", lm5_modal, "m", 3, ins5)
r.emit("swdm_cd_cost_pct", 100 * (1 - lm5 / lm5_modal), "%", 2, ins5)
assert lm5 < lm5_modal and lm5 > L5   # criterion is met at the MSA reach
# EMB needed for the MSA reach with CD included
emb_need = 1 / math.sqrt(1 / (KAPPA * RS * L5) ** 2 - (abs(D953) * sig_l / G) ** 2)
r.emit("swdm_emb_need", emb_need / 1e9, "MHz*km", 3, ins5)   # Hz*m /1e9 = MHz*km
assert emb_need < emb5

# 3. SWDM4 lane grid: lane width and the temperature span a VCSEL can drift within it
lanes = cl.cond("ch03.mmf.swdm4_wavelengths_l0", "lane_ranges_nm")
lo_, hi_ = map(float, re.match(r"\s*(\d+)-(\d+)", lanes).groups())
width = hi_ - lo_
r.emit("lane_width", width, "nm", 2, ["ch03.mmf.swdm4_wavelengths_l0"])
r.emit("lane_spacing", L("ch03.mmf.swdm4_wavelengths_l1") - L("ch03.mmf.swdm4_wavelengths_l0"), "nm", 2,
       ["ch03.mmf.swdm4_wavelengths_l0", "ch03.mmf.swdm4_wavelengths_l1"])
r.emit("lane_dT", width / L("ch03.las.vcsel_thermal_shift"), "K", 3,
       ["ch03.mmf.swdm4_wavelengths_l0", "ch03.las.vcsel_thermal_shift"])

# 4. VCSEL heat dissipation from heat-to-data ratio
for tag, rid in (("40", "ch03.vcsel.chalmers_hdr_40g"), ("50", "ch03.vcsel.chalmers_hdr_50g")):
    br = float(cl.cond(rid, "bit_rate_Gbps")) * 1e9
    r.emit(f"heat_{tag}", L(rid) * 1e-15 * br * 1e3, "mW", 3, [rid])

# ------------------------------------------------------------ figure
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.6, 4.0))
e = np.linspace(500e6 * 1e3, 6000e6 * 1e3, 300)  # Hz*m
ax.plot(e / 1e9, [lmax(x) for x in e], color=cl.COLORS[0], label="modal only")
ax.plot(e / 1e9, [lmax(x, D953, sig_l) for x in e], color=cl.COLORS[1],
        label="modal + CD (OM5 CD at 953 nm, SWDM4 width)")
for emb, name, rid, col in ((emb3, "OM3 SR4", "ch03.mmf.sr4_reach_om3", 2),
                            (emb4, "OM4 SR4", "ch03.mmf.sr4_reach_om4", 3),
                            (emb5, "OM5 SWDM4 (953 nm EMB)", "ch03.mmf.swdm4_reach_om5", 4)):
    ax.plot([emb / 1e9], [L(rid)], "o", color=cl.COLORS[col], ms=7, label=f"{name} specified reach")
ax.set_xlabel("effective modal bandwidth (MHz·km)")
ax.set_ylabel(f"reach limit at $B$ = {KAPPA}$R_s$ (m)")
ax.set_title(f"Gaussian link model, $R_s$ = {RS/1e9:.2f} GBd", fontsize=10)
ax.legend(fontsize=8)
cl.savefig(fig, "mmf_reach")
r.save()
