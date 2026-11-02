"""Section 4.4: what linear drive (LPO) and half-retimed (LRO) modules save and cost.

Reconciles the disagreeing LPO savings estimates by what each one includes:
module only (Eoptolink, Bechtolsheim module), module plus analog upgrades
(Marvell), and switch level (Bechtolsheim system, Evans).
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent)); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch04lib as cl

r = Results()

# ------------------------------------------------ module-level: removing the DSP
P0 = cl.cond_num("ch04.lpo.eoptolink_40pct", "from_W")             # 14 W retimed 800G
P1 = cl.cond_num("ch04.lpo.eoptolink_40pct", "to_W")               # <8 W linear 800G
EO = ["ch04.lpo.eoptolink_40pct"]
r.emit("eo_from", P0, "W", 3, EO)
r.emit("eo_to", P1, "W", 2, EO)
r.emit("eo_saving_pct", 100 * (1 - P1 / P0), "%", 3, EO)
r.emit("eo_eb_from", cl.pj_per_bit(P0, 800), "pJ/bit", 3, EO)
r.emit("eo_eb_to", cl.pj_per_bit(P1, 800), "pJ/bit", 3, EO)
assert abs(100 * (1 - P1 / P0) - L("ch04.lpo.eoptolink_40pct")) < 5     # 'around 40 %'

s_dsp = L("ch04.pw.dsp_half_module") / 100
# Ideal LPO: delete the DSP and change nothing else -> saving equals the DSP share
r.emit("ideal_saving_pct", 100 * s_dsp, "%", 2, ["ch04.pw.dsp_half_module"])
# Eoptolink numbers imply extra analog power for linear drivers / CTLE
extra = P1 - (1 - s_dsp) * P0
r.emit("eo_implied_extra", extra, "W", 2, EO + ["ch04.pw.dsp_half_module"])
r.emit("eo_implied_extra_pct", 100 * extra / ((1 - s_dsp) * P0), "%", 2, EO + ["ch04.pw.dsp_half_module"])
assert extra > 0

# Marvell (Patra): only ~20 %, because components need 25-50 % more bandwidth and 25 % more swing.
s_marv = L("ch04.lpo.marvell_20pct") / 100
# Saving S = s_dsp - x  ->  extra analog/host power x as a fraction of the retimed module
x_marv = s_dsp - s_marv
r.emit("marv_extra_frac", 100 * x_marv, "%", 2, ["ch04.lpo.marvell_20pct", "ch04.pw.dsp_half_module"])
r.emit("marv_extra_w", x_marv * P0, "W", 2, ["ch04.lpo.marvell_20pct", "ch04.pw.dsp_half_module"] + EO)
# ASSUMPTION (illustrative): driver power scales with the square of the output swing at fixed
# load; a 25 % swing increase then raises driver power by 1.25^2.
SWING = 1.25
r.emit("swing_factor", SWING ** 2, "1", 3)

# ------------------------------------------------ system level
s_mod_b = L("ch04.lpo.bechtolsheim_50pct") / 100
s_sys_b = cl.cond("ch04.lpo.bechtolsheim_50pct", "system_pct") / 100
frac_opt = s_sys_b / s_mod_b          # optics share of system power implied by the two numbers
r.emit("bech_optics_share", 100 * frac_opt, "%", 2, ["ch04.lpo.bechtolsheim_50pct"])
# Evans 102.4T switch: DSP vs LPO
ev = "ch04.cpo.evans_switch_power"
dsp_tot, lpo_tot, cpo_tot = (cl.cond(ev, k) for k in ("DSP_W", "LPO_W", "CPO_W"))
o_dsp, o_lpo, o_cpo = (cl.cond(ev, k) for k in ("optics_DSP_W", "optics_LPO_W", "optics_CPO_W"))
r.emit("ev_opt_saving_lpo", 100 * (1 - o_lpo / o_dsp), "%", 3, [ev])
r.emit("ev_sw_saving_lpo", 100 * (1 - lpo_tot / dsp_tot), "%", 3, [ev])
r.emit("ev_optics_share_dsp", 100 * o_dsp / dsp_tot, "%", 3, [ev])
r.emit("ev_lpo_module_w", o_lpo / 128, "W", 3, [ev])
r.emit("ev_dsp_module_w", o_dsp / 128, "W", 3, [ev])
r.emit("ev_eb_lpo", cl.pj_per_bit(o_lpo, 102400), "pJ/bit", 3, [ev])
r.emit("ev_eb_dsp", cl.pj_per_bit(o_dsp, 102400), "pJ/bit", 3, [ev])
# the Evans switch-level saving exceeds optics-delta / total because cooling and PSU scale too
r.emit("ev_direct_only", 100 * (o_dsp - o_lpo) / dsp_tot, "%", 3, [ev])
# Bechtolsheim projection at 200G/lane (tier C), Eoptolink annual-report target (tier B)
r.emit("eo_ar_eb", cl.pj_per_bit(L("ch04.lpo.eoptolink_lpo_lt11w"), 800), "pJ/bit", 3, ["ch04.lpo.eoptolink_lpo_lt11w"])

# Multimode: MACOM data cited by Innolight (>13 W with DSP, <4 W linear)
mm_lo, mm_hi = L("ch04.pw.macom_800g_mm", "lo"), L("ch04.pw.macom_800g_mm", "hi")
r.emit("mm_saving_pct", 100 * (1 - mm_lo / mm_hi), "%", 2, ["ch04.pw.macom_800g_mm"])

# ------------------------------------------------ LRO: keep only the transmit-path DSP
# ASSUMPTION: DSP power divides equally between the transmit (host-to-line) and receive
# (line-to-host) paths. No ledger source gives the split.
F_RX = 0.5
r.emit("lro_saving_pct", 100 * s_dsp * F_RX, "%", 2, ["ch04.pw.dsp_half_module"])
r.emit("lro_frx", 100 * F_RX, "%", 2)

# ------------------------------------------------ LPO optical link budget (LPO MSA Table 15)
budget = L("ch04.lpo.power_budget")
parts = [cl.cond("ch04.lpo.power_budget", k) for k in ("channel_loss_dB", "MPI_dB", "TDECQ_dB")]
assert abs(sum(parts) - budget) < 1e-9
r.emit("lpo_chan", parts[0], "dB", 2, ["ch04.lpo.power_budget"])
r.emit("lpo_mpi", parts[1], "dB", 1, ["ch04.lpo.power_budget"])
r.emit("lpo_tdecq", parts[2], "dB", 2, ["ch04.lpo.power_budget"])
r.emit("lpo_tdecq_frac", 100 * parts[2] / budget, "%", 2, ["ch04.lpo.power_budget"])
pmin = L("ch04.lpo.tx_launch_power_min")
r.emit("lpo_rx_min", pmin - parts[0], "dBm", 2, ["ch04.lpo.tx_launch_power_min", "ch04.lpo.power_budget"])
r.emit("lpo_tx_max", cl.cond("ch04.lpo.tx_launch_power_min", "max_dBm"), "dBm", 2, ["ch04.lpo.tx_launch_power_min"])
host_max = L("ch04.lpo.host_loss", "hi")
r.emit("host_max", host_max, "dB", 2, ["ch04.lpo.host_loss"])
# host loss as a linear amplitude ratio at Nyquist
r.emit("host_amp_ratio", 10 ** (host_max / 20), "1", 3, ["ch04.lpo.host_loss"])
import re
rs_lpo = float(re.search(r"([0-9.]+) GBd", cl.cond("ch04.lpo.spec_rev1_date", "scope")).group(1))
r.emit("lpo_rs", rs_lpo, "GBd", 5, ["ch04.lpo.spec_rev1_date"])
r.emit("lpo_nyq", rs_lpo / 2, "GHz", 4, ["ch04.lpo.spec_rev1_date"])

r.save()
