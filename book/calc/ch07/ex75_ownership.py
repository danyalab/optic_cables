"""Section 7.5: numbers quoted from regulations and reports, plus simple checks.

No modelling; values are echoed from ledger records (some held in `conditions`)
so the prose can cite them as macros.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1])); sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from common import L, Results
import ch07lib as cl

r = Results()
EO = "ch07.own.eo13913_review_periods"
r.emit("eo_initial_days", L(EO), "days", 3, [EO])
r.emit("eo_secondary_days", float(cl.cond(EO, "secondary_assessment_days")), "days", 2, [EO])
r.emit("eo_total_days", L(EO) + float(cl.cond(EO, "secondary_assessment_days")), "days", 3, [EO])

PRC = "ch07.own.prc_route_application_lead_time"
r.emit("prc_lead_days", L(PRC), "days", 2, [PRC])
r.emit("prc_reply_days", float(cl.cond(PRC, "authority_reply_days")), "days", 2, [PRC])
# survey application and laying application each 60 days ahead; minimum calendar time
# from first application to laying if the survey itself took zero time
r.emit("prc_min_two_step_days", 2 * L(PRC), "days", 3, [PRC])

SH = "ch07.own.caict_supplier_share_2018_2022"
shares = {k: float(cl.cond(SH, k)) for k in ("SubCom_pct", "ASN_pct", "HMN_pct", "NEC_pct")}
for k, v in shares.items():
    r.emit("share_" + k.split("_")[0].lower(), v, "%", 2, [SH])
r.emit("share_sum", sum(shares.values()), "%", 2, [SH])
r.emit("share_systems", float(cl.cond(SH, "systems")), "", 3, [SH])
r.emit("share_other", 100 - sum(shares.values()), "%", 1, [SH])
assert 90 <= sum(shares.values()) <= 100

CP = "ch07.own.content_provider_share_2021"
r.emit("cp_2005_pct", float(cl.cond(CP, "share_2005_pct")), "%", 1, [CP])
r.emit("cp_growth_factor", L(CP) / float(cl.cond(CP, "share_2005_pct")), "", 2, [CP])

HMN = "ch07.own.hmn_projects_km"
r.emit("hmn_projects", float(cl.cond(HMN, "projects")), "", 3, [HMN])
# average contracted length per project
r.emit("hmn_km_per_project", L(HMN) / float(cl.cond(HMN, "projects")), "km", 2, [HMN])

r.save()
