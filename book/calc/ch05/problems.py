"""Chapter 5 problem solutions."""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import ch05lib as cl

r = Results()

# P1: k = 64 fat tree
k = 64
for l in (2, 3):
    r.emit(f"p1_n{l}", cl.fattree_hosts(k, l), "hosts", 6)
    r.emit(f"p1_s{l}", cl.fattree_switches(k, l), "switches", 5)
    r.emit(f"p1_x{l}", 2 * cl.fattree_links(k, l)[1], "transceiver ports", 6)
r.emit("p1_paths", (k / 2) ** 2, "paths", 4)
assert cl.fattree_switches(64, 3) == 5 * 64 ** 2 / 4

# P2: Clos
r.emit("p2_ratio", (6 * 1000 ** 1.5 - 3 * 1000) / 1000 ** 2 * 100, "%", 3, ["ch05.clos.clos_n1000_crosspoints"])
lo, hi = 2.0, 100.0
f = lambda N: 6 * N ** 1.5 - 3 * N - N ** 2
for _ in range(200):
    mid = 0.5 * (lo + hi)
    if f(mid) > 0:
        lo = mid
    else:
        hi = mid
r.emit("p2_breakeven", lo, "inputs", 3)
assert 6 * 36 ** 1.5 - 3 * 36 < 36 ** 2 and 29 < lo < 30

# P3: oversubscription conventions
r.emit("p3_hpn", 100 / L("ch05.ai.hpn_core_oversub_15"), "%", 2, ["ch05.ai.hpn_core_oversub_15"])
r.emit("p3_meta7", 100 / L("ch05.ai.llama3_oversub_1to7"), "%", 3, ["ch05.ai.llama3_oversub_1to7"])
r.emit("p3_meta28", 100 / L("ch05.ai.meta_oversub_2p8"), "%", 3, ["ch05.ai.meta_oversub_2p8"])
r.emit("p3_gain", L("ch05.ai.llama3_oversub_1to7") / L("ch05.ai.meta_oversub_2p8"), "", 2,
       ["ch05.ai.llama3_oversub_1to7", "ch05.ai.meta_oversub_2p8"])

# P4: exponent bounds; overall 10G -> 200G exponent computed in ex52
import json
ex52 = json.loads((pathlib.Path(__file__).parent / "out" / "ex52_copper.json").read_text())
p = ex52["p_10_200"]["value"]
r.emit("p4_p", p, "", 2)
# reach at 200G predicted from 10G by the pure-skin and pure-dielectric laws
f10, f200 = ex52["fn_10"]["value"], ex52["fn_200"]["value"]
r.emit("p4_skin", L("ch05.cu.ieee_40gcr4_7m") * (f200 / f10) ** -0.5, "m", 2, ["ch05.cu.ieee_40gcr4_7m"])
r.emit("p4_diel", L("ch05.cu.ieee_40gcr4_7m") * (f200 / f10) ** -1, "m", 2, ["ch05.cu.ieee_40gcr4_7m"])

# P5: ring vs tree at Summit scale (values from ex53)
ex53 = json.loads((pathlib.Path(__file__).parent / "out" / "ex53_allreduce.json").read_text())
r.emit("p5_sstar", ex53["sstar_sum_MB"]["value"] / 1e3, "GB", 3)
r.emit("p5_ringlat", ex53["ringlat_sum_ms"]["value"], "ms", 3)
r.emit("p5_treelat_us", 2 * math.log2(ex53["n_sum"]["value"]) * ex53["tau_us"]["value"], "µs", 3)

# P6: hierarchical inter-node bytes
r.emit("p6_flat", ex53["nic_bytes_flat_GB"]["value"], "GB", 3)
r.emit("p6_hier", ex53["nic_bytes_hier_GB"]["value"], "GB", 3)
r.emit("p6_ratio", ex53["nic_bytes_flat_GB"]["value"] / ex53["nic_bytes_hier_GB"]["value"], "", 3)

# P7: pipeline bandwidth with twice as many stages
r.emit("p7_pp16", ex53["b_pp_gbps"]["value"] * 2, "Gb/s", 3)
# D halves to 96 at PP = 16: B_dp ∝ (D-1)/D / t_r and t_r doubles -> B_dp halves
r.emit("p7_dp_pp16", ex53["b_dp_gbps"]["value"] / 2 * (95 / 96) / (191 / 192), "Gb/s", 3)

# P8: TPU v4 OCS
r.emit("p8_spare_pct", (L("ch05.ocs.palomar_ports") - cl.cond("ch05.ocs.palomar_ports", "usable")) /
       L("ch05.ocs.palomar_ports") * 100, "%", 2, ["ch05.ocs.palomar_ports"])

# P9: duty cycles (from ex55)
ex55 = json.loads((pathlib.Path(__file__).parent / "out" / "ex55_ocs.json").read_text())
r.emit("p9_sir99", ex55["sir_hold99_ns"]["value"], "ns", 3)
r.emit("p9_sir99_bits", ex55["sir_hold99_ns"]["value"] * 1e-9 * 50e9 / 8 / 1e3, "kB", 3,
       ["ch05.ocs.sirius_reconfig"])

# P10: Broadcom optical scale-up, transceiver ends if every link is pluggable optics
BC = "ch05.su.broadcom_512_scaleup"
links = cl.cond(BC, "gpus") * 64
r.emit("p10_links", links, "links", 5, [BC])
r.emit("p10_ends", 2 * links, "port ends", 5, [BC])
r.emit("p10_ends_per_gpu", 2 * links / cl.cond(BC, "gpus"), "", 3, [BC])

r.save()
