"""Worked example 10.4 (BOM): a bill-of-materials exposure model for a 1.6T DR8 module.

Sourced part (Chapter 4, tier B): the power breakdown of a 1.6T (8x200G)
DR8/2xFR4 module at 70 C, total below 22 W, read from a pie chart in an
IEEE 802.3df contribution (ch04.pw.1p6t_breakdown_dsp; legend order of the
non-DSP slices is the retrieval agent's inference).

Modelled part: no ledger record gives component COST shares or the origin
of each component. The cost shares c_k and the outside-China sourcing
fractions m_k below are explicit ASSUMPTIONS, chosen as round numbers to
illustrate the algebra X = sum_k c_k m_k. They are not estimates.

Draws Figure 10.4.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import re
import numpy as np
import ch10lib as cl

r = Results()
P16 = "ch04.pw.1p6t_breakdown_dsp"
others = str(cl.cond(P16, "other_shares_pct"))
pw = {k: float(v) for k, v in re.findall(r"(TEC|laser|TIA|MCU|other) ([0-9.]+)", others)}
pw["DSP"] = L(P16)
assert abs(sum(pw.values()) - 100.0) < 0.05, "power shares do not sum to 100%"
ptot = cl.qnum(P16, r"<([0-9.]+) ?W")
for k, v in pw.items():
    r.emit(f"pw_{k.lower()}_pct", v, "%", 3, [P16])
    r.emit(f"pw_{k.lower()}_w", v / 100 * ptot, "W", 2, [P16])
r.emit("pw_optics_pct", pw["laser"] + pw["TEC"], "%", 3, [P16])

# ---------------- cost-exposure model (all ASSUMPTIONS) ----------------
ASSUMPTION_COST_SHARE = {          # c_k, fraction of module material+conversion cost
    "DSP": 0.30,
    "lasers": 0.15,
    "SiPh PIC and PDs": 0.12,
    "driver and TIA": 0.08,
    "PCB, MCU, TEC, housing, fiber": 0.15,
    "assembly, test, yield": 0.20,
}
ASSUMPTION_OUTSIDE_CN = {          # m_k, fraction of each item sourced from outside mainland China
    "DSP": 1.00,                   # no domestic PAM4 DSP volume in any filing (Section 10.3)
    "lasers": 0.80,                # domestic supplier states DC laser market is overseas-dominated
    "SiPh PIC and PDs": 0.80,
    "driver and TIA": 0.90,
    "PCB, MCU, TEC, housing, fiber": 0.30,
    "assembly, test, yield": 0.00,  # done by the module maker itself
}
c = ASSUMPTION_COST_SHARE
m = ASSUMPTION_OUTSIDE_CN
assert abs(sum(c.values()) - 1.0) < 1e-12
X = sum(c[k] * m[k] for k in c)
r.emit("X_ref_pct", 100 * X, "%", 2)
r.emit("c_dsp_pct", 100 * c["DSP"], "%", 2)
r.emit("c_laser_pct", 100 * c["lasers"], "%", 2)
r.emit("c_pic_pct", 100 * c["SiPh PIC and PDs"], "%", 2)
r.emit("c_drv_pct", 100 * c["driver and TIA"], "%", 1)
r.emit("c_mech_pct", 100 * c["PCB, MCU, TEC, housing, fiber"], "%", 2)
r.emit("c_asm_pct", 100 * c["assembly, test, yield"], "%", 2)
r.emit("m_dsp_pct", 100 * m["DSP"], "%", 3)
r.emit("m_laser_pct", 100 * m["lasers"], "%", 2)
r.emit("m_pic_pct", 100 * m["SiPh PIC and PDs"], "%", 2)
r.emit("m_drv_pct", 100 * m["driver and TIA"], "%", 2)
r.emit("m_mech_pct", 100 * m["PCB, MCU, TEC, housing, fiber"], "%", 2)
# Scenario: lasers fully domestic
X_laser = X - c["lasers"] * m["lasers"]
# Scenario: lasers and PIC fully domestic, DSP unchanged
X_laser_pic = X_laser - c["SiPh PIC and PDs"] * m["SiPh PIC and PDs"]
r.emit("X_laser_pct", 100 * X_laser, "%", 2)
r.emit("X_laser_pic_pct", 100 * X_laser_pic, "%", 2)
r.emit("X_dsp_floor_pct", 100 * c["DSP"] * m["DSP"], "%", 2)
r.emit("dX_dlaser_pct", 100 * c["lasers"], "%/unit m", 2)
# Share of the remaining exposure that is DSP once optics are localized
r.emit("dsp_frac_after_pct", 100 * c["DSP"] * m["DSP"] / X_laser_pic, "%", 2)
r.save()

# ---------------- Figure 10.4 ----------------
plt = cl.setup_mpl()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10.8, 4.1))
order = ["DSP", "other", "TEC", "laser", "TIA", "MCU"]
vals = [pw[k] / 100 * ptot for k in order]
a1.barh(order[::-1], vals[::-1], color=cl.COLORS[0])
for i, v in enumerate(vals[::-1]):
    a1.text(v + 0.2, i, f"{v:.1f} W", va="center", fontsize=9.5, color=cl.GRAY)
a1.set_xlabel("power (W), module total < 22 W at 70 °C")
a1.set_title("(a) 1.6T DR8 power by block (sourced)", fontsize=11)
a1.set_xlim(0, 16)

names = list(c)
cv = np.array([c[k] for k in names]) * 100
mv = np.array([m[k] for k in names])
y = np.arange(len(names))[::-1]
a2.barh(y, cv * mv, color=cl.COLORS[1], label="outside mainland China (assumed)")
a2.barh(y, cv * (1 - mv), left=cv * mv, color=cl.COLORS[2], alpha=0.75, label="mainland China (assumed)")
a2.set_yticks(y, names, fontsize=9)
a2.set_xlabel("assumed share of module cost (%)")
a2.set_title(f"(b) assumed cost exposure: X = {100 * X:.0f}%", fontsize=11)
a2.legend(loc="upper center", bbox_to_anchor=(0.35, -0.2), ncol=2, fontsize=8.5)
a2.set_xlim(0, 34)
fig.tight_layout()
cl.savefig(fig, "bom_exposure")
