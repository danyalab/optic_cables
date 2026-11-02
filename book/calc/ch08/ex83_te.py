"""Section 8.3 worked example: max-min fair multicommodity flow over tunnels.

Toy four-site WAN (every number here is an ASSUMPTION; nothing is a sourced fact).
Compares (a) single shortest-path routing, (b) exact max-min fair (MMF)
allocation over pre-computed tunnels by progressive filling with LPs, and
(c) SWAN's banded approximation (Hong et al. 2013, Sec. 4.2, Fig. 6, as corrected
by the Chapter 8 verifier): within geometrically growing bands [U a^(k-1), U a^k]
solve  max sum_i b_i - eps sum_ij w_j b_ij  (w_j proportional to tunnel latency)
subject to  sum_ij b_ij I_jl <= min{c_l^remain, (1 - s) c_l},
freezing flows that do not reach the top of the band. s is the scratch-capacity
fraction SWAN reserves for congestion-free updates.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import Results
import numpy as np
from scipy.optimize import linprog

r = Results()
# ASSUMPTION: topology and capacities (Tb/s), directed links
CAP = {("A", "B"): 1.0, ("B", "C"): 1.0, ("A", "D"): 1.0, ("D", "C"): 1.0, ("A", "C"): 0.5, ("B", "D"): 0.5}
# ASSUMPTION: flows (src->dst), demands (Tb/s) and tunnels (shortest first)
FLOWS = [
    ("A->C", 2.0, [["A", "C"], ["A", "B", "C"], ["A", "D", "C"]]),
    ("B->C", 0.8, [["B", "C"], ["B", "D", "C"]]),
    ("A->B", 0.6, [["A", "B"]]),
    ("D->C", 0.5, [["D", "C"]]),
]
links = list(CAP)
tun = [(i, j, path) for i, (_, _, ps) in enumerate(FLOWS) for j, path in enumerate(ps)]
nv = len(tun)
nf = len(FLOWS)


def uses(path, l):
    return any((path[k], path[k + 1]) == l for k in range(len(path) - 1))


A_cap = np.array([[1.0 if uses(p, l) else 0.0 for (_, _, p) in tun] for l in links])
b_cap = np.array([CAP[l] for l in links])
A_flow = np.array([[1.0 if i == f else 0.0 for (i, _, _) in tun] for f in range(nf)])
dem = np.array([d for (_, d, _) in FLOWS])


def mmf(allowed):
    """Exact max-min fair rates by progressive filling. allowed[v]=False disables tunnel v."""
    frozen = {}
    bounds = [(0, None) if allowed[v] else (0, 0) for v in range(nv)]
    while len(frozen) < nf:
        # variables: tunnel rates x (nv) and t; maximize t
        c = np.zeros(nv + 1); c[-1] = -1
        Aub = [np.append(row, 0) for row in A_cap]; bub = list(b_cap)
        Aeq, beq = [], []
        for f in range(nf):
            if f in frozen:
                Aeq.append(np.append(A_flow[f], 0)); beq.append(frozen[f])
            else:
                Aub.append(np.append(-A_flow[f], 1)); bub.append(0)          # t <= b_f
                Aub.append(np.append(A_flow[f], 0)); bub.append(dem[f])        # b_f <= d_f
        res = linprog(c, A_ub=np.array(Aub), b_ub=bub, A_eq=np.array(Aeq) if Aeq else None,
                      b_eq=beq if beq else None, bounds=bounds + [(0, None)], method="highs")
        t = res.x[-1]
        # freeze every unfrozen flow that cannot exceed t with the others held at >= t
        for f in range(nf):
            if f in frozen:
                continue
            c2 = -np.append(A_flow[f], 0)
            Aub2 = [np.append(row, 0) for row in A_cap]; bub2 = list(b_cap)
            Aeq2, beq2 = [], []
            for g in range(nf):
                if g in frozen:
                    Aeq2.append(np.append(A_flow[g], 0)); beq2.append(frozen[g])
                else:
                    Aub2.append(np.append(-A_flow[g], 0)); bub2.append(-t + 1e-9)
                    Aub2.append(np.append(A_flow[g], 0)); bub2.append(dem[g])
            res2 = linprog(c2, A_ub=np.array(Aub2), b_ub=bub2, A_eq=np.array(Aeq2) if Aeq2 else None,
                           b_eq=beq2 if beq2 else None, bounds=bounds + [(0, 0)], method="highs")
            if -res2.fun <= t + 1e-7:
                frozen[f] = t
    # final feasible tunnel split for the frozen rates (max weighted throughput tie-break)
    w = np.array([1.0 / (len(p) - 1) for (_, _, p) in tun])
    res = linprog(-w, A_ub=A_cap, b_ub=b_cap, A_eq=A_flow, b_eq=[frozen[f] for f in range(nf)],
                  bounds=bounds, method="highs")
    return np.array([frozen[f] for f in range(nf)]), res.x


def swan(alpha, U, scratch, eps):
    """SWAN banded approximation of MMF (throughput MCF inside each band)."""
    w = np.array([float(len(p) - 1) for (_, _, p) in tun])   # latency proxy: hop count
    cost = -(1.0 - eps * w)                                    # minimize -(sum b - eps sum w b)
    frozen = {}
    lo, hi = 0.0, U
    x = None
    while len(frozen) < nf:
        Aeq, beq, Aub, bub = [], [], list(A_cap), list((1 - scratch) * b_cap)
        for f in range(nf):
            if f in frozen:
                Aeq.append(A_flow[f]); beq.append(frozen[f])
            else:
                Aub.append(-A_flow[f]); bub.append(-min(lo, dem[f]))
                Aub.append(A_flow[f]); bub.append(min(dem[f], hi))
        res = linprog(cost, A_ub=np.array(Aub), b_ub=bub, A_eq=np.array(Aeq) if Aeq else None,
                      b_eq=beq if beq else None, bounds=[(0, None)] * nv, method="highs")
        x = res.x
        rates = A_flow @ x
        for f in range(nf):
            if f not in frozen and rates[f] < min(dem[f], hi) - 1e-7:
                frozen[f] = rates[f]
            elif f not in frozen and rates[f] >= dem[f] - 1e-7:
                frozen[f] = dem[f]
        lo, hi = hi, hi * alpha
    return np.array([frozen[f] for f in range(nf)]), x


# (a) single shortest path only
single = [j == 0 for (_, j, _) in tun]
rs, xs = mmf(single)
# (b) exact MMF over all tunnels
rm, xm = mmf([True] * nv)
# (c) SWAN approximation. ASSUMPTION: alpha = 2, U = 0.1 Tb/s, eps = 1e-3 (any small
# positive value), scratch s = 0 (to compare with exact MMF) and s = 0.1 (SWAN-like reserve).
ALPHA, U0, EPS, SCR = 2.0, 0.1, 1e-3, 0.10
rw, xw = swan(ALPHA, U0, 0.0, EPS)
rw10, xw10 = swan(ALPHA, U0, SCR, EPS)

for tag, rates, x in (("sp", rs, xs), ("mmf", rm, xm), ("swan", rw, xw), ("swan10", rw10, xw10)):
    load = A_cap @ x
    assert np.all(load <= b_cap + 1e-7) and np.all(rates <= dem + 1e-7)
    r.emit(f"{tag}_total", rates.sum(), "Tb/s", 3)
    r.emit(f"{tag}_util", 100 * load.sum() / b_cap.sum(), "%", 3)
    for f, (name, _, _) in enumerate(FLOWS):
        r.emit(f"{tag}_f{f + 1}", rates[f], "Tb/s", 3)
r.emit("gain_mmf_vs_sp", 100 * (rm.sum() / rs.sum() - 1), "%", 3)
r.emit("cap_total", b_cap.sum(), "Tb/s", 2)
r.emit("dem_total", dem.sum(), "Tb/s", 2)
r.emit("into_c", sum(CAP[l] for l in links if l[1] == "C"), "Tb/s", 2)
r.emit("alpha", ALPHA, "1", 2)
r.emit("U0", U0, "Tb/s", 1)
r.emit("scratch", 100 * SCR, "%", 2)
r.emit("swan10_loss", 100 * (1 - rw10.sum() / rw.sum()), "%", 2)
assert rw10.sum() <= rw.sum() + 1e-9
for f, (name, d, _) in enumerate(FLOWS):
    r.emit(f"d{f + 1}", d, "Tb/s", 2)
# MMF check: no flow can be raised without lowering a flow that is not larger
assert abs(rm.sum() - sum(CAP[l] for l in links if l[1] == "C") - rm[2]) < 1e-6
assert rm[0] > rs[0] and abs(rm[1] - dem[1]) < 1e-6
# SWAN's rates are within a factor alpha of the MMF rates for every flow
assert np.all(rw >= rm / ALPHA - 1e-6) and np.all(rw <= rm * ALPHA + 1e-6)
r.save()
