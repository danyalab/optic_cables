"""Worked example 3.6: Ge photodiode efficiency, bandwidth, and PAM4 receiver sensitivity.

PAM4 sensitivity (thermal-noise-limited, Gray coding): adjacent levels are separated by
d = R * OMA / 3 in photocurrent. With Gaussian noise sigma and decision thresholds midway,
SER = (3/2) Q(d / (2 sigma)) for equiprobable levels, so the required OMA is
OMA = 6 Q_t sigma / R, with Q_t the argument that meets the target SER (Section 2.2).
APD: signal x M, shot noise 2 q I M^2 F_A(M) B, F_A from McIntyre.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import re
import numpy as np
from scipy.optimize import brentq, minimize_scalar
import ch03lib as cl

r = Results()

# ------------------------------------------------------------ band gaps
lam_d = cl.ev_to_nm(L("ch03.ge.direct_gap"))
lam_i = cl.ev_to_nm(float(cl.cond("ch03.ge.direct_gap", "indirect_gap_eV")))
assert abs(lam_d - 1550) / 1550 < 0.01
r.emit("lam_direct", lam_d, "nm", 4, ["ch03.ge.direct_gap"])
r.emit("lam_indirect", lam_i, "nm", 4, ["ch03.ge.direct_gap"])


# ------------------------------------------------------------ responsivity -> quantum efficiency
def eta(R, lam_nm):
    return R * cl.H * cl.C0 / (cl.Q_E * lam_nm * 1e-9)


r.emit("r_ideal_1550", cl.Q_E * 1550e-9 / (cl.H * cl.C0), "A/W", 3)
r.emit("eta_imec", eta(L("ch03.pd.imec_responsivity_1550"), 1550), "1", 3, ["ch03.pd.imec_responsivity_1550"])
# ASSUMPTION: the imec O-band value refers to 1310 nm
r.emit("eta_imec_o", eta(float(cl.cond("ch03.pd.imec_responsivity_1550", "o_band_value_A_W")), 1310), "1", 3,
       ["ch03.pd.imec_responsivity_1550"])
eta240 = eta(L("ch03.pd.lischke_responsivity"), 1550)
bw240 = float(re.search(r"(\d+) GHz", cl.rec("ch03.pd.lischke_responsivity")["claim"]).group(1))
bep = eta240 * bw240
assert abs(bep - L("ch03.pd.lischke_bep")) / L("ch03.pd.lischke_bep") < 0.02
r.emit("eta_240", eta240, "1", 3, ["ch03.pd.lischke_responsivity"])
r.emit("bep_calc", bep, "GHz", 3, ["ch03.pd.lischke_responsivity"])
r.emit("eta_265", eta(float(cl.cond("ch03.pd.lischke_265g", "internal_responsivity_A_W")), 1550), "1", 3,
       ["ch03.pd.lischke_265g"])
r.emit("bep_265", eta(0.3, 1550) * L("ch03.pd.lischke_265g"), "GHz", 3, ["ch03.pd.lischke_265g"])
assert float(cl.cond("ch03.pd.lischke_265g", "internal_responsivity_A_W")) == 0.3
r.emit("bep_imec", eta(L("ch03.pd.imec_responsivity_1550"), 1550) * L("ch03.pd.imec_bw"), "GHz", 3,
       ["ch03.pd.imec_responsivity_1550", "ch03.pd.imec_bw"])
# grating-coupler loss implied by external/internal responsivity
r.emit("gc_loss", 10 * math.log10(L("ch03.pd.lischke_responsivity") / float(cl.cond("ch03.pd.lischke_responsivity", "external_A_W"))),
       "dB", 2, ["ch03.pd.lischke_responsivity"])

# ------------------------------------------------------------ RC vs transit
RLOAD = 50.0   # ASSUMPTION: 50 ohm load
r.emit("rload", RLOAD, "Ω", 2)
for tag, rid in (("lis", "ch03.pd.lischke_265g"), ("imec", "ch03.pd.imec_bw")):
    C = float(cl.cond(rid, "capacitance_fF")) * 1e-15
    frc = 1 / (2 * math.pi * RLOAD * C)
    r.emit(f"frc_{tag}", frc / 1e9, "GHz", 3, [rid])
    if tag == "lis":
        f3 = L(rid) * 1e9
        ftr = 1 / math.sqrt(1 / f3 ** 2 - 1 / frc ** 2)
        r.emit("ftr_lis", ftr / 1e9, "GHz", 3, [rid])

# ------------------------------------------------------------ PIN + TIA sensitivity
nd = L("ch03.tia.patel_noise") * 1e-12           # A/sqrt(Hz)
B = float(cl.cond("ch03.tia.patel_noise", "bandwidth_GHz")) * 1e9
sig = nd * math.sqrt(B)
assert abs(sig - 3.0e-6) < 0.05e-6                # ledger note: 3.0 uA rms
Qt = L("ch02.imdd.tdecq_qt")
ser = L("ch02.imdd.tdecq_target_ser")
assert abs(1.5 * cl.qfunc(Qt) - ser) / ser < 0.05      # Q_t reproduces the target SER
R = L("ch03.pd.imec_responsivity_1550")   # ASSUMPTION: Patel's co-packaged PD has the imec responsivity
oma = 6 * Qt * sig / R
inst = ["ch03.tia.patel_noise", "ch02.imdd.tdecq_qt", "ch03.pd.imec_responsivity_1550"]
r.emit("sigma_th", sig * 1e6, "µA", 3, ["ch03.tia.patel_noise"])
r.emit("qt", Qt, "1", 4, ["ch02.imdd.tdecq_qt"])
r.emit("ser_check", 1.5 * cl.qfunc(Qt), "1", 2, ["ch02.imdd.tdecq_qt"])
r.emit("oma_req_uw", oma * 1e6, "µW", 3, inst)
r.emit("oma_req_dbm", cl.w2dbm(oma), "dBm", 3, inst)
gap = L("ch03.tia.patel_noise") * 0 + float(cl.cond("ch03.tia.patel_noise", "sensitivity_dBm_OMA")) - cl.w2dbm(oma)
assert 0 < gap < 4
r.emit("patel_sens", float(cl.cond("ch03.tia.patel_noise", "sensitivity_dBm_OMA")), "dBm", 3, ["ch03.tia.patel_noise"])
r.emit("gap_db", gap, "dB", 2, inst)
# shot noise at that OMA (ASSUMPTION: infinite extinction ratio, P_avg = OMA/2)
iavg = R * oma / 2
sshot = math.sqrt(2 * cl.Q_E * iavg * B)
r.emit("sigma_shot", sshot * 1e6, "µA", 2, inst)
r.emit("shot_var_frac", 100 * sshot ** 2 / sig ** 2, "%", 2, inst)
r.emit("dark_frac", 100 * L("ch03.pd.lischke_dark", "hi") * 1e-9 / iavg, "%", 2, inst + ["ch03.pd.lischke_dark"])
RS = L("ch02.sym.lambda_pam4_rate") * 1e9
r.emit("tia_bw_ratio", B / RS, "1", 2, ["ch03.tia.patel_noise", "ch02.sym.lambda_pam4_rate"])
# Declercq: noise at twice the bandwidth
nd2 = L("ch03.tia.declercq_noise") * 1e-12
B2 = float(cl.cond("ch03.tia.declercq_noise", "bandwidth_with_GePD_GHz")) * 1e9
r.emit("sigma_declercq", nd2 * math.sqrt(B2) * 1e6, "µA", 3, ["ch03.tia.declercq_noise"])
r.emit("oma_declercq_dbm", cl.w2dbm(6 * Qt * nd2 * math.sqrt(B2) / R), "dBm", 3,
       ["ch03.tia.declercq_noise", "ch02.imdd.tdecq_qt", "ch03.pd.imec_responsivity_1550"])

# ------------------------------------------------------------ APD gain optimization
k = L("ch03.apd.kang_keff")
gbp = L("ch03.apd.kang_gbp") * 1e9


def FA(M):
    return k * M + (1 - k) * (2 - 1 / M)


# check McIntyre closed form against the M^3 bracket of the abstract
for M in (2.0, 10.0):
    bracket = M ** 3 * (1 - (1 - k) * ((M - 1) / M) ** 2)
    assert abs(bracket - M ** 2 * FA(M)) < 1e-9


def oma_apd(M, Bw=B):
    """Required OMA (W) with APD gain M, thermal noise sig at bandwidth Bw, shot noise at the
    mean current R*OMA/2 (ASSUMPTION: infinite ER; noise of the mean level used for all levels)."""
    st2 = (nd ** 2) * Bw
    f = lambda P: R * M * P / 3 - 2 * Qt * math.sqrt(st2 + 2 * cl.Q_E * R * (P / 2) * M ** 2 * FA(M) * Bw)
    return brentq(f, 1e-9, 1e-2)


o1 = oma_apd(1.0)
r.emit("fa10", FA(10), "1", 3, ["ch03.apd.kang_keff"])
r.emit("fa10_db", 10 * math.log10(FA(10)), "dB", 3, ["ch03.apd.kang_keff"])
res = minimize_scalar(lambda M: oma_apd(M), bounds=(1.0, 60.0), method="bounded")
Mopt = res.x
Mcap = gbp / B
insa = ["ch03.apd.kang_keff", "ch03.apd.kang_gbp", "ch03.tia.patel_noise", "ch02.imdd.tdecq_qt", "ch03.pd.imec_responsivity_1550"]
r.emit("apd_mopt", Mopt, "1", 3, insa)
r.emit("apd_mcap", Mcap, "1", 3, ["ch03.apd.kang_gbp", "ch03.tia.patel_noise"])
r.emit("apd_oma_m1_dbm", cl.w2dbm(o1), "dBm", 3, insa)
r.emit("apd_gain_opt_db", cl.lin2db(o1 / oma_apd(Mopt)), "dB", 3, insa)
Muse = min(Mopt, Mcap)
r.emit("apd_muse", Muse, "1", 3, insa)
r.emit("apd_gain_use_db", cl.lin2db(o1 / oma_apd(Muse)), "dB", 3, insa)
r.emit("apd_oma_use_dbm", cl.w2dbm(oma_apd(Muse)), "dBm", 3, insa)
assert abs(cl.w2dbm(o1) - cl.w2dbm(oma)) < 0.2       # M = 1 reproduces the PIN result (small shot term)

# ------------------------------------------------------------ figure
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(6.4, 4.0))
Ms = np.linspace(1, 40, 200)
for i, kk in enumerate((k, 0.3, 0.5)):
    def FAk(M, kk=kk):
        return kk * M + (1 - kk) * (2 - 1 / M)

    def om(M, kk=kk):
        st2 = nd ** 2 * B
        f = lambda P: R * M * P / 3 - 2 * Qt * math.sqrt(st2 + 2 * cl.Q_E * R * (P / 2) * M ** 2 * FAk(M) * B)
        return brentq(f, 1e-9, 1e-2)
    lab = f"$k$ = {kk:g}" + (" (Ge/Si SACM)" if kk == k else "")
    ax.plot(Ms, [cl.w2dbm(om(M)) for M in Ms], color=cl.COLORS[i], label=lab)
ax.axvline(Mcap, color=cl.GRAY, ls="--", lw=1)
ax.annotate("gain-bandwidth limit\nat the TIA bandwidth", (Mcap, cl.w2dbm(o1) - 1), xytext=(6, 0),
            textcoords="offset points", fontsize=8, color=cl.GRAY)
ax.set_xlabel("APD multiplication gain $M$")
ax.set_ylabel("required OMA (dBm)")
ax.set_title("PAM4 sensitivity vs APD gain (computed)", fontsize=10)
ax.legend(fontsize=8)
cl.savefig(fig, "apd_gain")
r.save()
