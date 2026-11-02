"""Worked example 7.1: electrical power budget of a repeatered cable.

Series constant-current line (G.977: stabilized current through the cable
conductor with sea return). With PFE voltage V, conductor resistance
R_c = R' L and N_r identical repeaters, each dropping V_r = P_rep / I_f:

    V = I_f R_c + N_r P_rep / I_f                  (Desbruslais Eq. (1))
    P_e(I_f) = I_f (V - I_f R_c)                    power reaching repeaters
    max at I_f = V/(2 R_c):  P_e,max = V^2/(4 R_c)  (Perin, after Eq. (1))

Reference link: Perin et al. 2019 (12 kV, 1 ohm/km, 287 spans of 50 km).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from common import L, Results
import ch07lib as cl

r = Results()
FEED = "ch07.power.perin_feed_voltage_resistance"
LINK = "ch07.power.perin_link_reference"
PTOT = "ch07.power.perin_total_electrical_power"

V = L(FEED) * 1e3                                 # V
Rp = float(cl.cond(FEED, "rho_ohm_per_km"))       # ohm/km
Lkm = L(LINK)                                     # km
N_s = int(cl.cond(LINK, "N_s"))
span = float(cl.cond(LINK, "span_km"))
assert abs(N_s * span - Lkm) < 1e-6
Rc = Rp * Lkm
ins = [FEED, LINK]

r.emit("V_kv", V / 1e3, "kV", 2, [FEED])
r.emit("rprime", Rp, "Ω/km", 2, [FEED])
r.emit("L_km", Lkm, "km", 5, [LINK])
r.emit("N_s", N_s, "", 3, [LINK])
r.emit("span_km", span, "km", 2, [LINK])
r.emit("Rc_kohm", Rc / 1e3, "kΩ", 4, ins)

Pmax = cl.max_power_transfer(V, Rc)
Iopt = V / (2 * Rc)
r.emit("Pmax_kw", Pmax / 1e3, "kW", 3, ins)
r.emit("Pmax_pub_kw", L(PTOT), "kW", 2, [PTOT])
assert abs(Pmax / 1e3 - L(PTOT)) / L(PTOT) < 0.01, "Perin's 2.5 kW not reproduced"
r.emit("Iopt_a", Iopt, "A", 3, ins)
r.emit("Ploss_kw", Iopt ** 2 * Rc / 1e3, "kW", 3, ins)
assert abs(Iopt ** 2 * Rc - Pmax) < 1e-6 * Pmax       # half the PFE power heats the conductor
r.emit("Ppfe_kw", V * Iopt / 1e3, "kW", 3, ins)

# per repeater (N_r = N_s powered repeaters, Perin Eq. (2) convention)
N_r = N_s
P_rep = Pmax / N_r
V_rep = P_rep / Iopt
r.emit("Prep_w", P_rep, "W", 3, ins)
r.emit("Vrep_v", V_rep, "V", 3, ins)
r.emit("Vrep_total_kv", N_r * V_rep / 1e3, "kV", 3, ins)
# consistency with Desbruslais Eq. (1)
assert abs(cl.pfe_voltage(Iopt, Rc, N_r, P_rep) - V) < 1e-6 * V
# Desbruslais Eq. (4): minimum voltage for given load equals V at the optimum
assert abs(2 * (Rc * N_r * P_rep) ** 0.5 - V) < 1e-6 * V

# flatness of the optimum: P_e(I)/P_max = 1 - (I/I_opt - 1)^2
for tag, f in (("80", 0.8), ("120", 1.2)):
    frac = cl.repeater_power(f * Iopt, V, Rc) / Pmax
    assert abs(frac - (1 - (f - 1) ** 2)) < 1e-12
    r.emit(f"Pfrac_{tag}_pct", 100 * frac, "%", 3, ins)

# higher voltage and lower-resistance conductor (Downie 2023 modelling values)
V18 = L("ch07.arch.max_single_end_voltage_18kv") * 1e3
R07 = L("ch07.arch.cable_resistance_low_end")
P18 = cl.max_power_transfer(V18, R07 * Lkm)
ins18 = ["ch07.arch.max_single_end_voltage_18kv", "ch07.arch.cable_resistance_low_end", LINK]
r.emit("P18_kw", P18 / 1e3, "kW", 3, ins18)
r.emit("P18_ratio", P18 / Pmax, "", 3, ins18 + ins)
r.emit("P18_vratio_sq", (V18 / V) ** 2, "", 3, ins18 + ins)
r.emit("P18_rratio", Rp / R07, "", 3, ins18 + ins)
assert abs(P18 / Pmax - (V18 / V) ** 2 * Rp / R07) < 1e-9

# double-end feeding: PFEs of +V and -V in series across the line
P2 = cl.max_power_transfer(2 * V, Rc)
r.emit("Pdouble_kw", P2 / 1e3, "kW", 3, ins)
assert abs(P2 / Pmax - 4) < 1e-12

# a shorter (7,000 km, Downie 2023 MCF study) cable at 18 kV, 0.7 ohm/km
L7 = float(cl.cond("ch07.sdm.mcedfa_capacity_gain_no_fifo", "L_km"))
P7 = cl.max_power_transfer(V18, R07 * L7)
r.emit("L7_km", L7, "km", 2, ["ch07.sdm.mcedfa_capacity_gain_no_fifo"])
r.emit("P7_kw", P7 / 1e3, "kW", 3, ins18 + ["ch07.sdm.mcedfa_capacity_gain_no_fifo"])

# cable / joint voltage rating (Desbruslais) vs PFE ranges
r.emit("Vrating_kv", L("ch07.arch.cable_joint_voltage_rating_12kv"), "kV", 2,
       ["ch07.arch.cable_joint_voltage_rating_12kv"])

# reliability: G.977 'fewer than three' cable-ship repairs in a 25-year life
life = L("ch07.arch.design_life_25y")
nrep = L("ch07.arch.reliability_lt3_ship_repairs")
lam_yr = nrep / life
HOURS_PER_YEAR = 365.25 * 24
# ASSUMPTION (illustrative upper bound): the whole repair budget is assigned to repeater
# failures, spread over the N_r repeaters of the reference link.
fit = nrep / (life * HOURS_PER_YEAR * N_r) * 1e9
relins = ["ch07.arch.design_life_25y", "ch07.arch.reliability_lt3_ship_repairs"]
r.emit("rel_rate_per_yr", lam_yr, "per year", 2, relins)
r.emit("rel_fit_per_rep", fit, "FIT", 2, relins + [LINK])

# ---------------------------------------------------------------- figure
plt = cl.setup_mpl()
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0), gridspec_kw={"width_ratios": [1.6, 1]})
# (a) conductor potential vs distance
x, v = cl.voltage_profile(V, Iopt, Rp, Lkm, N_r, P_rep)
ax1.plot(x, v / 1e3, color=cl.COLORS[0], label="single-end, +12 kV / sea earth")
ax1.plot(x, (v - V / 2) / 1e3, color=cl.COLORS[1], label="double-end, +6 kV and -6 kV")
x2, v2 = cl.voltage_profile(2 * V, 2 * Iopt, Rp, Lkm, N_r, cl.max_power_transfer(2 * V, Rc) / N_r)
ax1.plot(x2, (v2 - V) / 1e3, color=cl.COLORS[2], ls="--", label="double-end, +12 kV and -12 kV (4x power)")
ax1.axhline(0, color=cl.GRAY, lw=0.8)
ax1.set_xlabel("distance from the first PFE (km)")
ax1.set_ylabel("conductor potential to sea (kV)")
ax1.legend(fontsize=8.5, loc="lower left")
ax1.set_title("(a) potential along the reference link", fontsize=10)
# inset zoom on a few repeaters
ins_ax = ax1.inset_axes([0.62, 0.58, 0.35, 0.36])
m = x < 4 * span
ins_ax.plot(x[m], v[m] / 1e3, color=cl.COLORS[0], lw=1.4)
ins_ax.set_xlabel("km", fontsize=7)
ins_ax.tick_params(labelsize=7)
ins_ax.set_title("first spans", fontsize=7)
# (b) delivered power vs current
f = np.linspace(0, 2, 201)
ax2.plot(f, [cl.repeater_power(ff * Iopt, V, Rc) / Pmax for ff in f], color=cl.COLORS[0],
         label="to repeaters")
ax2.plot(f, [(ff * Iopt) ** 2 * Rc / Pmax for ff in f], color=cl.COLORS[1], label="heat in conductor")
ax2.set_xlabel(r"line current $I_{\mathrm{f}}/I_{\mathrm{opt}}$")
ax2.set_ylabel(r"power $/ P_{\mathrm{e,max}}$")
ax2.set_ylim(0, 4.1)
ax2.legend(fontsize=8.5)
ax2.set_title("(b) maximum power transfer", fontsize=10)
fig.tight_layout()
cl.savefig(fig, "voltage_profile")

r.save()
