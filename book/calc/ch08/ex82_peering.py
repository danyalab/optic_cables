"""Section 8.2: IXP traffic arithmetic and a peering-vs-transit cost model.

Cost model (monthly, 95th-percentile billing):
  all transit:            C_tr  = p T
  peer a fraction phi:    C_mix = p (1 - phi) T + C_peer * ceil(phi T / T_eff)
Break-even (one port):    T_be  = C_peer / p          (Norton; ch08.eq.peering_breakeven)
Peering beats transit at full port load only if p > C_peer / T_eff.
"""
import sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from common import L, Results
import math
import numpy as np
import ch08lib as cl

r = Results()
DAY = 86400.0
YEAR = 365 * DAY

# ---------- Ager et al. (tier A)
M, PL, VOL, SF = ("ch08.ixp.ager_members", "ch08.ixp.ager_peering_links",
                  "ch08.ixp.ager_daily_volume", "ch08.ixp.ager_sflow_sampling")
n = L(M)
pairs = n * (n - 1) / 2
r.emit("ager_pairs", pairs, "AS pairs", 4, [M])
r.emit("ager_links_from_pct", pairs * L(PL, "hi") / 100, "links", 3, [M, PL])
assert pairs * L(PL, "hi") / 100 >= L(PL, "lo"), "67% of possible pairs must exceed 50,000"
r.emit("ager_avg_tbps", L(VOL) * 1e15 * 8 / DAY / 1e12, "Tb/s", 3, [VOL])
r.emit("ager_eb_yr", L(VOL) * 365 / 1e3, "EB/yr", 3, [VOL])
r.emit("ager_per_member_gbps", L(VOL) * 1e15 * 8 / DAY / n / 1e9, "Gb/s", 2, [VOL, M])

# ---------- DE-CIX (tier C; contested box)
NY, NYP, NA, GL, GP = ("ch08.ixp.decix_ny_annual_2025", "ch08.ixp.decix_ny_peak_2024",
                       "ch08.ixp.decix_na_annual_2025", "ch08.ixp.decix_global_annual_2025",
                       "ch08.ixp.decix_global_peak_2025")
ny_avg = L(NY) * 1e18 * 8 / YEAR / 1e12
gl_avg = L(GL) * 1e18 * 8 / YEAR / 1e12
r.emit("ny_avg_tbps", ny_avg, "Tb/s", 3, [NY])
r.emit("ny_peak_over_avg", L(NYP) / ny_avg, "1", 2, [NY, NYP])
r.emit("na_avg_tbps", L(NA, "hi") * 1e18 * 8 / YEAR / 1e12, "Tb/s", 3, [NA])
r.emit("na_growth_pct", 100 * (L(NA, "hi") / L(NA, "lo") - 1), "%", 2, [NA])
r.emit("gl_avg_tbps", gl_avg, "Tb/s", 3, [GL])
r.emit("gl_peak_over_avg", L(GP) / gl_avg, "1", 2, [GL, GP])
pk_dec = cl.verifier_number(GP, r"reached ([0-9.]+) terabits", "evidence")
r.emit("gl_peak_dec", pk_dec, "Tb/s", 4, [GP])
r.emit("gl_peakdec_over_avg", pk_dec / gl_avg, "1", 3, [GP, GL])
r.emit("ny_share_pct", 100 * L(NY) / L(GL), "%", 2, [NY, GL])
r.emit("ny_over_ager", L(NY) / (L(VOL) * 365 / 1e3), "1", 2, [NY, VOL])

# ---------- Equinix (tier B)
EQ, EC = "ch08.ixp.equinix_interconnections_ar", "ch08.ixp.equinix_customers"
r.emit("eq_dcs", cl.cond(EQ, "data_centers"), "data centers", 3, [EQ])
r.emit("eq_markets", cl.cond(EQ, "markets"), "markets", 2, [EQ])
r.emit("eq_per_dc", L(EQ) / cl.cond(EQ, "data_centers"), "interconnections per DC", 3, [EQ])
r.emit("eq_per_customer", L(EQ) / L(EC, "lo"), "interconnections per customer", 2, [EQ, EC])

# ---------- carrier hotels (tier C; contested box)
r.emit("ow_ratio", L("ch08.hotel.one_wilshire_networks_coresite") / L("ch08.hotel.one_wilshire_networks_owner"),
       "1", 2, ["ch08.hotel.one_wilshire_networks_coresite", "ch08.hotel.one_wilshire_networks_owner"])
r.emit("sh_ratio", L("ch08.hotel.sixty_hudson_hudsonix") / L("ch08.hotel.sixty_hudson_owner"), "1", 2,
       ["ch08.hotel.sixty_hudson_hudsonix", "ch08.hotel.sixty_hudson_owner"])

# ---------- transit prices (Norton, tier B)
P98, P10, P15 = ("ch08.peering.transit_price_1998", "ch08.peering.transit_price_2010",
                 "ch08.peering.transit_price_2015")
dec_98_10 = 1 - (L(P10) / L(P98)) ** (1 / 12)
dec_10_15 = 1 - (L(P15) / L(P10)) ** (1 / 5)
r.emit("decl_98_10", 100 * dec_98_10, "%/yr", 3, [P98, P10])
r.emit("decl_10_15", 100 * dec_10_15, "%/yr", 3, [P10, P15])
r.emit("price_ratio_98_15", L(P98) / L(P15), "1", 3, [P98, P15])
# Norton's table lists 33 % for the 2015 step; our geometric mean 2010-2015 should be close
assert abs(100 * dec_10_15 - 33) < 2

CP, BE, TE = "ch08.peering.cost_assumption", "ch08.peering.breakeven_2010", "ch08.peering.effective_10g_bw"
Cp, Teff = L(CP), L(TE)
for tag, pid in (("98", P98), ("10", P10), ("15", P15)):
    r.emit(f"tbe_{tag}", Cp / L(pid), "Mb/s", 3, [CP, pid])
assert abs(Cp / L(P10) - L(BE)) < 1e-9, "Norton's 2010 break-even must follow from C_peer/p"
p_star = Cp / Teff
r.emit("p_star", p_star, "USD/(Mb/s·month)", 3, [CP, TE])
r.emit("peer_unit_cost", p_star, "USD/(Mb/s·month)", 3, [CP, TE])
assert L(P15) < p_star < L(P10)
# Year at which the geometric 2010-2015 interpolation crosses p_star (model, not data)
t_star = 2010 + 5 * math.log(L(P10) / p_star) / math.log(L(P10) / L(P15))
r.emit("t_star", t_star, "year", 5, [P10, P15, CP, TE])
r.emit("tbe15_over_teff", (Cp / L(P15)) / Teff, "1", 3, [CP, P15, TE])

# ---------- worked example
# ASSUMPTION: an access network with 95th-percentile outbound traffic T = 20 Gb/s.
T = 20000.0
# ASSUMPTION: 40 % of that traffic can be exchanged with peers present at one IXP.
PHI = 0.40
# ASSUMPTION: each additional 10G port costs the full Norton bundle (port + colo + transport);
# this overstates the cost of the second port and is conservative for peering.
r.emit("ex_T", T / 1e3, "Gb/s", 2)
r.emit("ex_phi", 100 * PHI, "%", 2)
ports = math.ceil(PHI * T / Teff)
r.emit("ex_ports", ports, "ports", 1, [TE])
r.emit("ex_peered", PHI * T / 1e3, "Gb/s", 2)
for tag, pid in (("10", P10), ("15", P15)):
    p = L(pid)
    c_tr = p * T
    c_mix = p * (1 - PHI) * T + Cp * ports
    r.emit(f"ex_ctr_{tag}", c_tr, "USD/month", 3, [pid])
    r.emit(f"ex_cmix_{tag}", c_mix, "USD/month", 3, [pid, CP, TE])
    r.emit(f"ex_save_{tag}", c_tr - c_mix, "USD/month", 3, [pid, CP, TE])
assert L(P10) * PHI * T > Cp * ports and L(P15) * PHI * T < Cp * ports

# ---------- figure
plt = cl.setup_mpl()
fig, ax = plt.subplots(figsize=(7.2, 4.2))
tp = np.linspace(0, 30000, 1201)
for pid, col, lab in ((P10, cl.COLORS[0], "transit at 2010 price"), (P15, cl.COLORS[1], "transit at 2015 price")):
    ax.plot(tp / 1e3, L(pid) * tp / 1e3, color=col, label=lab)
ax.step(tp / 1e3, Cp * np.ceil(np.maximum(tp, 1) / Teff) / 1e3, where="post", color=cl.COLORS[2],
        label="peering, 10G ports at the assumed bundle cost")
ax.axvline(Cp / L(P10) / 1e3, color=cl.GRAY, ls=":", lw=1)
ax.text(Cp / L(P10) / 1e3 + 0.3, 125, "break-even\n2010", fontsize=8.5)
ax.set_xlabel("Traffic moved from transit to peering, 95th percentile (Gb/s)")
ax.set_ylabel("Monthly cost (thousand USD)")
ax.set_ylim(0, 160)
ax.set_xlim(0, 30)
ax.legend(fontsize=9, loc="upper left")
ax.set_title("Computed: Norton transit prices and peering-cost assumption", fontsize=10)
cl.savefig(fig, "peering_cost")
r.save()
