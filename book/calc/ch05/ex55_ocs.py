"""Worked example 5.5: OCS arithmetic (Palomar, TPU v4, Jupiter) and the
reconfiguration-time duty cycle."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import json
import ch05lib as cl

r = Results()

# ------------------------------------------------ Palomar
PP = "ch05.ocs.palomar_ports"
ports, spares = L(PP), cl.cond(PP, "spares")
usable = ports - spares
assert usable == cl.cond(PP, "usable")
r.emit("pal_usable", usable, "ports", 3, [PP])
r.emit("pal_yield", ports / L("ch05.ocs.palomar_mirrors") * 100, "%", 3, [PP, "ch05.ocs.palomar_mirrors"])
w_port = L("ch05.ocs.palomar_power") / ports
w_usable = L("ch05.ocs.palomar_power") / usable
r.emit("pal_w_port", w_port, "W", 2, ["ch05.ocs.palomar_power", PP])
r.emit("pal_w_usable", w_usable, "W", 2, ["ch05.ocs.palomar_power", PP])
# An electrical hop removed from a path removes two transceiver ports (one module per side
# for a single-port module). Compare with the 800G twin-port module of Chapter 4.
x800 = L("ch04.pmd.800g_2xdr4_power")
r.emit("pal_vs_2x800", w_usable / (2 * x800) * 100, "%", 2, ["ch04.pmd.800g_2xdr4_power"])
r.emit("pal_unavail_min", (1 - L("ch05.ocs.palomar_availability") / 100) * 365.25 * 24 * 60, "min/yr", 2,
       ["ch05.ocs.palomar_availability"])
r.emit("rl_margin", L("ch05.ocs.palomar_rl", "lo") * -1 - L("ch05.ocs.palomar_rl", "hi") * -1, "dB", 2,
       ["ch05.ocs.palomar_rl"])
r.emit("il_diff", L("ch05.ocs.il_target_lightwave") - L("ch05.ocs.il_target_apollo"), "dB", 2,
       ["ch05.ocs.il_target_lightwave", "ch05.ocs.il_target_apollo"])
r.emit("il_ratio_lin", 10 ** ((L("ch05.ocs.il_target_lightwave") - L("ch05.ocs.il_target_apollo")) / 10), "", 3,
       ["ch05.ocs.il_target_lightwave", "ch05.ocs.il_target_apollo"])

# ------------------------------------------------ TPU v4
chips = L("ch05.ocs.tpuv4_chips")
cubes = cl.cond("ch05.ocs.tpuv4_48_ocs", "cubes")
per_cube = cl.cond("ch05.ocs.tpuv4_48_ocs", "links_per_cube")
cube_side = round((chips / cubes) ** (1 / 3))
assert cube_side ** 3 * cubes == chips
assert 6 * cube_side ** 2 == per_cube
assert cubes * per_cube == L("ch05.ocs.tpuv4_6144_links")
assert 6 * 16 / 2 == L("ch05.ocs.tpuv4_48_ocs")
ppo = L("ch05.ocs.tpuv4_6144_links") / L("ch05.ocs.tpuv4_48_ocs")
assert ppo == cl.cond("ch05.ocs.tpuv4_48_ocs", "ports_used") == usable
r.emit("v4_cube_side", cube_side, "", 1, ["ch05.ocs.tpuv4_chips"])
r.emit("v4_cubes", cubes, "cubes", 2, ["ch05.ocs.tpuv4_48_ocs"])
r.emit("v4_ports_per_ocs", ppo, "ports", 3, ["ch05.ocs.tpuv4_6144_links", "ch05.ocs.tpuv4_48_ocs"])
r.emit("v4_links_per_chip", L("ch05.ocs.tpuv4_6144_links") / chips, "", 2, ["ch05.ocs.tpuv4_6144_links"])
r.emit("v4_ends_per_chip", 2 * L("ch05.ocs.tpuv4_6144_links") / chips, "", 2, ["ch05.ocs.tpuv4_6144_links"])
r.emit("v4_ocs_kw", L("ch05.ocs.tpuv4_48_ocs") * L("ch05.ocs.palomar_power") / 1e3, "kW", 3,
       ["ch05.ocs.tpuv4_48_ocs", "ch05.ocs.palomar_power"])
r.emit("v4_ocs_w_chip", L("ch05.ocs.tpuv4_48_ocs") * L("ch05.ocs.palomar_power") / chips, "W", 3,
       ["ch05.ocs.tpuv4_48_ocs", "ch05.ocs.palomar_power"])

# ------------------------------------------------ Lightwave vs static vs EPS
LW = "ch05.ocs.lightwave_vs_static_cost"
c_lw, p_lw = 1 + cl.cond(LW, "cost_pct") / 100, 1 + cl.cond(LW, "power_pct") / 100
c_eps, p_eps = 1 + cl.cond(LW, "eps_cost_pct") / 100, 1 + cl.cond(LW, "eps_power_pct") / 100
r.emit("v4_cost_pct", L("ch05.ocs.tpuv4_cost_share", "lo"), "%", 1, ["ch05.ocs.tpuv4_cost_share"])
r.emit("v4_power_pct", L("ch05.ocs.tpuv4_cost_share", "hi"), "%", 1, ["ch05.ocs.tpuv4_cost_share"])
for key in ("cost_pct", "power_pct", "eps_cost_pct", "eps_power_pct"):
    r.emit(f"lw_{key}", cl.cond(LW, key), "%", 2, [LW])
r.emit("rl_typ", L("ch05.ocs.palomar_rl", "lo"), "dB", 2, ["ch05.ocs.palomar_rl"])
r.emit("rl_spec", L("ch05.ocs.palomar_rl", "hi"), "dB", 2, ["ch05.ocs.palomar_rl"])
r.emit("lumorph_coll", L("ch05.su.lumorph_speedup", "lo"), "%", 2, ["ch05.su.lumorph_speedup"])
r.emit("lumorph_train", L("ch05.su.lumorph_speedup", "hi"), "", 2, ["ch05.su.lumorph_speedup"])
r.emit("sir_gen1_guard", 100, "ns", 3, ["ch05.ocs.sirius_reconfig"])
assert "100 ns guardband" in cl.rec("ch05.ocs.sirius_reconfig")["notes"]
r.emit("lw_vs_eps_cost", (1 - c_lw / c_eps) * 100, "%", 3, [LW])
r.emit("lw_vs_eps_power", (1 - p_lw / p_eps) * 100, "%", 2, [LW])

# ------------------------------------------------ Jupiter
JP = "ch05.ocs.jupiter_pathlen"
f_dir = cl.cond(JP, "direct_traffic_pct") / 100
assert abs(f_dir * 1 + (1 - f_dir) * 2 - L(JP)) < 1e-12
r.emit("jp_transit", (1 - f_dir) * 100, "%", 2, [JP])
r.emit("jp_ports_both", L("ch05.ocs.jupiter_circulator_halving") ** 2 * 100, "%", 2, ["ch05.ocs.jupiter_circulator_halving"])
# Clos spine path: every inter-block path crosses the spine, block-level length 2
r.emit("jp_vs_clos", (1 - L(JP) / 2) * 100, "%", 2, [JP])

# ------------------------------------------------ reconfiguration duty cycle
def hold_for(eff, t_sw):
    return eff / (1 - eff) * t_sw

for tag, t in (("lo", L("ch05.ocs.commercial_switch_time", "lo") * 1e-3),
               ("hi", L("ch05.ocs.commercial_switch_time", "hi") * 1e-3)):
    r.emit(f"mems_hold99_{tag}", hold_for(0.99, t), "s", 2, ["ch05.ocs.commercial_switch_time"])
t_s = L("ch05.ocs.sirius_reconfig") * 1e-9
rate = cl.cond("ch05.ocs.sirius_reconfig", "line_rate_Gbps") * 1e9
r.emit("sir_guard_bits", t_s * rate, "bits", 3, ["ch05.ocs.sirius_reconfig"])
r.emit("sir_hold90_ns", hold_for(0.90, t_s) * 1e9, "ns", 3, ["ch05.ocs.sirius_reconfig"])
r.emit("sir_hold99_ns", hold_for(0.99, t_s) * 1e9, "ns", 3, ["ch05.ocs.sirius_reconfig"])
r.emit("sir_vs_mems", L("ch05.ocs.commercial_switch_time", "lo") * 1e-3 / t_s, "", 2,
       ["ch05.ocs.commercial_switch_time", "ch05.ocs.sirius_reconfig"])
# ring step of the Section 5.3 example
ex53 = json.loads((pathlib.Path(__file__).parent / "out" / "ex53_allreduce.json").read_text())
step = ex53["s_grad_GB"]["value"] * 1e9 / ex53["dp"]["value"] / (ex53["bw_GBps"]["value"] * 1e9)
r.emit("ring_step_ms", step * 1e3, "ms", 3)
r.emit("ring_step_vs_mems", L("ch05.ocs.commercial_switch_time", "lo") * 1e-3 / step, "", 2,
       ["ch05.ocs.commercial_switch_time"])
r.emit("fiber_vs_free", L("ch05.ocs.fiber_latency") / cl.cond("ch05.ocs.fiber_latency", "free_space_ns_per_m"), "", 3,
       ["ch05.ocs.fiber_latency"])

r.save()
