"""Worked example 9.1: scale ratios of the Chinese operator backbones.

All inputs are ledger records; the outputs are ratios that the ledger does not
state directly. Assumptions are named ASSUMPTION constants.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import ch09lib as cl

r = Results()

# --- China Telecom all-optical backbone: OA nodes per ROADM node --------------
ROADM = "ch09.op.ct_allotical_backbone_scale_2023"
n_roadm = L(ROADM)                                  # lower bound, 500+
n_oa = float(cl.cond(ROADM, "oa_nodes_lower_bound"))  # lower bound, 2000+
ratio = n_oa / n_roadm
r.emit("ct_roadm", n_roadm, "", 3, [ROADM])
r.emit("ct_oa", n_oa, "", 4, [ROADM])
r.emit("ct_oa_per_roadm", ratio, "", 2, [ROADM])
# ASSUMPTION: mean ROADM nodal degree 3 (a typical national mesh value; not sourced).
DEG = 3.0
# ASSUMPTION: each OA node serves exactly one ROADM-to-ROADM link (in-line site).
links = n_roadm * DEG / 2
oa_per_link = n_oa / links
spans_per_link = oa_per_link + 1
r.emit("deg_assumed", DEG, "", 1)
r.emit("ct_links", links, "", 3, [ROADM])
r.emit("ct_oa_per_link", oa_per_link, "", 2, [ROADM])
r.emit("ct_spans_per_link", spans_per_link, "", 2, [ROADM])
# ASSUMPTION: 80 km spans (the CCSA 22 dB reference span at the ITU typical G.652
# link coefficient, Section 9.3).
SPAN_KM = 80.0
r.emit("span_km", SPAN_KM, "km", 2)
r.emit("ct_link_km", spans_per_link * SPAN_KM, "km", 2, [ROADM])
assert 3.0 < ratio < 5.0

# --- China Mobile: inter-provincial bandwidth vs per-fiber capacity ----------
BW = "ch09.op.cmcc_interprovincial_bw_2025"
CAP = "ch09.l400.cmcc_capacity_32t"
fib_eq = L(BW) / L(CAP)
r.emit("cmcc_bw_tbps", L(BW), "Tb/s", 4, [BW])
r.emit("cmcc_fiber_equiv", fib_eq, "", 3, [BW, CAP])
r.emit("cmcc_400g_waves_equiv", L(BW) * 1e3 / float(cl.cond(CAP, "rate_Gbps")), "", 3, [BW, CAP])
assert 30 < fib_eq < 40

# --- Cable length shares (sheath / route km) --------------------------------
SH = "ch09.op.cmcc_cable_sheath_km_2025"
NAT = "ch09.acc.cable_length_2025"
r.emit("cmcc_sheath_mkm", cl.num(L(SH)) / 1e6, "million km", 4, [SH])
r.emit("nat_cable_mkm", cl.num(L(NAT)) / 1e6, "million km", 4, [NAT])
share = cl.num(L(SH)) / cl.num(L(NAT))
r.emit("cmcc_share_pct", 100 * share, "%", 3, [SH, NAT])
assert 0.4 < share < 0.6

# --- China Unicom new 八纵八横 backbone ---------------------------------------
ADD = "ch09.op.cu_new_88_cable_2025"
TOT = "ch09.op.cu_new_88_total_198k"
r.emit("cu_total_kkm", cl.num(L(TOT)) / 1e3, "thousand km", 3, [TOT])
r.emit("cu_added_km", L(ADD), "km", 2, [ADD])
r.emit("cu_added_pct", 100 * L(ADD) / cl.num(L(TOT)), "%", 2, [ADD, TOT])

# --- Ownership and users ----------------------------------------------------
r.emit("cmcc_state_pct", L("ch09.op.cmcc_ownership_2025"), "%", 3, ["ch09.op.cmcc_ownership_2025"])
r.emit("ct_state_pct", L("ch09.op.ct_ownership_2025"), "%", 3, ["ch09.op.ct_ownership_2025"])
NFB = "ch09.op.national_fixed_bb_users_2025"
CTU = "ch09.op.ct_users_2025"
r.emit("nat_fbb_m", cl.num(L(NFB)) / 1e6, "million", 3, [NFB])
r.emit("ct_fbb_m", cl.num(L(CTU)) / 1e6, "million", 3, [CTU])
r.emit("ct_fbb_share_pct", 100 * cl.num(L(CTU)) / cl.num(L(NFB)), "%", 3, [CTU, NFB])
ct_gig = cl.num(L(CTU)) * float(cl.cond(CTU, "gigabit_penetration_pct")) / 100
r.emit("ct_gig_m", ct_gig / 1e6, "million", 3, [CTU])
r.emit("ct_gig_pen_pct", float(cl.cond(CTU, "gigabit_penetration_pct")), "%", 3, [CTU])
CMG = "ch09.op.cmcc_gigabit_users_2025"
r.emit("cmcc_gig_m", cl.num(L(CMG)) / 1e6, "million", 3, [CMG])
NG = "ch09.acc.gigabit_users_2025"
r.emit("nat_gig_m", cl.num(L(NG)) / 1e6, "million", 3, [NG])
r.emit("ct_cm_gig_share_pct", 100 * (ct_gig + cl.num(L(CMG))) / cl.num(L(NG)), "%", 3, [CTU, CMG, NG])
r.emit("cbn_5g_m", cl.num(L("ch09.op.cbn_5g_users_2025")) / 1e6, "million", 2, ["ch09.op.cbn_5g_users_2025"])

# --- CN2 and CU numbers used in the table -----------------------------------
r.emit("cn2_pop_223", L("ch09.op.cn2_domestic_pop_coverage"), "cities", 3, ["ch09.op.cn2_domestic_pop_coverage"])
r.emit("cn2_pop_161", L("ch09.op.cn2_dual_pop_161"), "cities", 3, ["ch09.op.cn2_dual_pop_161"])
r.emit("cmcc_intl_tbps", L("ch09.intl.cmcc_intl_2025"), "Tb/s", 3, ["ch09.intl.cmcc_intl_2025"])
r.save()
