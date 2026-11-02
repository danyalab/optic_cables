"""Worked example 10.7: CPO claims put on a common footing.

(a) An "N-times power efficiency" claim and a "P% power reduction" claim are
    the same quantity in different form: N = 1 / (1 - P/100). Convert each
    sourced claim and note the boundary (optics only, or whole switch) that
    it uses. Tier-C inputs are for the contested box only.
(b) NVIDIA's 22 dB -> 4 dB electrical-loss claim and its '63x signal
    integrity' claim are the same number in dB and linear form.
(c) CW laser power for CPO: Yuanjie's 300 mW development target relative to
    its 70 mW volume product, against Sumitomo's 'over four times'.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import ch10lib as cl

r = Results()


def n_from_p(p_pct):
    return 1.0 / (1.0 - p_pct / 100.0)


# (a) boundary-dependent multiples
NV, BD = "ch10.open.nvidia_cpo_efficiency", "ch10.open.broadcom_th6_davisson"
META, BAILLY = "ch04.cpo.meta_65pct", "ch04.cpo.bailly_70pct_claim"
EV = "ch04.cpo.evans_switch_power"
r.emit("nv_n", L(NV), "x", 2, [NV])
r.emit("nv_p_pct", 100 * (1 - 1 / L(NV)), "%", 3, [NV])
r.emit("bd_n", n_from_p(100 * L(BD)), "x", 3, [BD])
r.emit("meta_n", n_from_p(L(META)), "x", 3, [META])
r.emit("bailly_n", n_from_p(L(BAILLY)), "x", 3, [BAILLY])
ev_opt_dsp = float(cl.cond(EV, "optics_DSP_W"))
ev_opt_cpo = float(cl.cond(EV, "optics_CPO_W"))
r.emit("ev_opt_n", ev_opt_dsp / ev_opt_cpo, "x", 3, [EV])
r.emit("ev_sw_n", L(EV, "hi") / L(EV, "lo"), "x", 3, [EV])
r.emit("ev_sw_p_pct", 100 * (1 - L(EV, "lo") / L(EV, "hi")), "%", 2, [EV])
assert ev_opt_dsp / ev_opt_cpo > L(EV, "hi") / L(EV, "lo")    # optics-only multiple exceeds switch-level multiple

# (b) electrical loss
NL = "ch10.open.nvidia_cpo_loss"
# value = [pluggable, CPO]; L(..., "lo") returns the first element, "hi" the second.
dl = L(NL, "lo") - L(NL, "hi")
assert dl > 0
lin = 10 ** (dl / 10)
r.emit("nv_dloss", dl, "dB", 2, [NL])
r.emit("nv_lin", lin, "x", 2, [NL])
q63 = cl.qnum(NV, r"([0-9]+)x greater signal integrity")
assert abs(lin - q63) / q63 < 0.01, "63x and 22->4 dB should be the same ratio"
r.emit("nv_q63", q63, "x", 2, [NV])

# (c) CW laser power
CW70, CW300, SUMI = "ch10.inp.yuanjie_cw70_mass", "ch10.open.yuanjie_cw300_dev", "ch10.open.sumitomo_cpo_cw_power"
ratio = L(CW300) / L(CW70)
assert ratio > L(SUMI)
r.emit("cw_ratio", ratio, "x", 3, [CW70, CW300])
r.emit("cw_ratio_db", 10 * math.log10(ratio), "dB", 3, [CW70, CW300])
r.emit("sumi_x", L(SUMI), "x", 1, [SUMI])
# Laser sharing in the Bailly system (Meta, tier A): one pluggable laser source feeds 8 x 400G ports
PLS = "ch04.cpo.meta_pls_8ports"
r.emit("pls_ports", L(PLS), "ports", 1, [PLS])
r.save()
