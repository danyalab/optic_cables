# Chapter 1: facts wanted but not in the ledger, and modeling assumptions

Written by the Chapter 1 writer agent. Each item says what is missing, why it was wanted, and where it would go. "Assumption" items are modeling choices made in `book/calc/ch01/*.py` and flagged in the prose with "we assume".

## A. Facts wanted but not in the ledger (priority order)

1. **Typical fusion-splice loss, line-connector loss, cable section length, and ageing/repair margin.** These are needed for the 1.1 span budget, which currently rests on assumptions (A1 to A4 below). The YOFC 2020 presentation's splice values (0.15 dB G.654.E to G.652.D; 0.022 dB self-splice) appear only in record notes, not as values. Wanted: an ITU-T G.Sup39 or G.957 or G.691 clause, or an operator design guide, giving α_s, α_c and a margin. Where: 1.1 worked example, Table 1.2.
2. **Measured implementation gap of a commercial coherent transponder (tier A).** The only number used in the main example is now a transceiver SNR *range* (Yoshida, quoting Matsushita). Rafique's 64 GBd penalty was demoted to tier C by the verifier and appears only in the 1.6 contested box. Wanted: an OFC, ECOC or JLT field or lab measurement of net rate versus GMI or Shannon at a measured SNR for a 60 to 130 GBd product. Where: 1.6, Shannon gap and required SNR.
3. **Transceiver power budgets (ZR/ZR+, 400G-LR4-10, 400G-ER4) for the unamplified case.** Without them the "unamplified" half of the 1.1 worked example can only compare loss, not close a budget. Where: 1.1 worked example (or Chapter 4).
4. **PDL magnitudes and the PDL-induced SNR penalty in coherent systems** (Mecozzi and Shtaif; Savory JSTQE 2010 for "what MIMO removes"). The 1.3 PDL discussion is qualitative only. Where: 1.3.
5. **Infrared multiphonon tail shape (exponential slope) and UV Urbach tail magnitude for silica.** Only the IR magnitude at 1550 nm is sourced. The figure uses an assumed slope (A5). Where: 1.1, loss-spectrum model and Figure 1.1.
6. **Tier-A source for the Maxwellian DGD pdf** (Foschini and Poole, JLT 1991; Karlsson JLT 2001). Currently a master's thesis (tier B). Where: 1.3.
7. **Tier-A NLSE with β3 printed, and the Manakov equation transcribed with signs** (Agrawal, *Nonlinear Fiber Optics*; Marcuse, Menyuk and Wai Eq. (12)). Both are written in the chapter as our own specializations. Where: 1.4.
8. **Measured γ for a named G.652.D and G.654.E product.** γ is computed from n2 and vendor A_eff. Where: 1.4 worked example.
9. **A resolution of the n2 spread** (for example the COST 241 intercomparison, Fellegara et al., EL 1997). The chapter offers the 8/9 polarization-average arithmetic only as a hypothesis. Where: 1.4 contested box.
10. **Long-haul in-line amplifier noise-figure datasheet** from Lumentum, Coherent or Ciena, with unambiguous typical/maximum columns. Where: 1.5.
11. **Tier-A replacement for the ASE PSD and F → 2 n_sp sources** (Desurvire's monograph; Haus, IEEE PTL 1998 / JSTQE 2000). Where: 1.5.
12. **Peer-reviewed versions of the hollow-core and SDM records** now at tier C (Chen OFC 2024 PDP full text; Luis OFC 2025 PDP full text; Gao and Ding ECOC 2025 full papers; NICT 22.9 Pb/s paper). They are presented only in the 1.7 contested box. Where: 1.7.
13. **Exact HCF group index** (about 1.001 to 1.003) from a peer-reviewed source (Trenti et al., IEEE JSTQE 2024 is suggested by the verifier). Latency figures currently use n_g = 1 from an arXiv preprint (tier B). Where: 1.7.
14. **IEEE 802.3 normative channel-dispersion values** (802.3cu, 802.3df). MSA values stand in. The verifier notes that IEEE 802.3cu changed S0 from 0.093 to 0.092; a ledger record for that would let the 1.2 contested box state it. Where: 1.2.
15. **Updated G.Sup39 (10/2025) and G.697 (newest edition) records** with the new equation numbers. The chapter cites the 2006 numbering and notes the renumbering. Where: 1.5.
16. **Hengtong and ZTT primary loss data, and a YOFC market-share percentage.** None found with a value. Where: 1.7.
17. **G.655.C/D/E in-force dispersion limits.** Only the superseded 1996 range is in the ledger. Where: 1.4.
18. **A sourced statement that the incoherent GN model often matches non-Gaussian simulations better than coherent GN** (Poggiolini 2014, Sect. V-E, noted in the gaps file but not a ledger record). It was removed from the 1.6 contested box for this reason. Where: 1.6.
19. **Explicit EGN coefficients for 16QAM** as a ledger value (they are in a record note only). Where: 1.6.

## B. Modeling assumptions (all flagged in prose with "we assume")

| ID | Assumption | Value | Script | Where used |
|---|---|---|---|---|
| A1 | Span length (syllabus choice) | 80 km | ex11, ex14, ex16, ex17 | 1.1, 1.4, 1.5, 1.6, 1.7 |
| A2 | Cable section length between splices | 4 km (19 splices per span) | ex11 | 1.1 |
| A3 | Mean splice loss; line connectors | 0.05 dB per splice; 2 connectors at 0.5 dB | ex11 | 1.1, then 1.5 and 1.6 via span loss |
| A4 | End-of-life margin | 3 dB | ex11 | 1.1, 1.5, 1.6 (EOL cases) |
| A5 | IR multiphonon tail slope b in exp(-b/λ) | 48.48 µm | ex11 | Figure 1.1 only |
| A6 | Time scale for L_D | T0 = 1/R_s | ex12 | 1.2 |
| A7 | Illustrative IM/DD lengths | 2 km and 10 km (fading); 2, 10, 40 km (PMD) | ex12, ex13 | 1.2, 1.3 |
| A8 | Practical fading criterion | abs(H(R_s/2)) ≥ 1/√2 | ex12 | 1.2 |
| A9 | Applying the G.959.1 0.3-bit-period DGD rule to the PAM4 symbol period | 0.3 T_sym | ex13 | 1.3 |
| A10 | Stricter outage target | 1e-6 | ex13 | 1.3 |
| A11 | Coherent link length for the PMD and CD problems | 1000 km | ex13, problems | 1.3, Problems 3 and 5 |
| A12 | Per-channel power for the nonlinear-phase and OSNR illustrations | 0 dBm | ex14, ex15 | 1.4, 1.5 |
| A13 | n2 used for γ | G.Sup47 pure-silica constant (lower bound for Ge-doped cores) | ex14 | 1.4, 1.6 |
| A14 | Fiber attenuation for the G.652.D NLI and ASE calculation | SMF-28 Ultra datasheet maximum | ex14, ex15, ex16 | 1.4 to 1.6 |
| A15 | Coherent symbol rate (syllabus choice) | 64 GBd | ex15, ex16, problems | 1.5, 1.6 |
| A16 | Channel grid and loading | 75 GHz grid filling the ITU C-band (58 channels) | ex16 | 1.6 |
| A17 | Channel spectrum in the GN closed form | rectangular, B_ch = R_s (validated by the reference reproduction) | ex16 | 1.6 |
| A18 | Required SNR model | Gray 16-QAM BER approximation at the 20 % SD-FEC threshold; transceiver noise added as Gaussian with SNR_TR at either end of the ledger range; main case uses the best transceiver | ex16 | 1.6 |
| A19 | ε = 0 for the main case (ε at the top of the 2014 typical range as a variant) | 0 | ex16 | 1.6 |
| A20 | G.654.E dispersion for the comparison | midpoint of ITU G.654.E bound range | ex16 | 1.6 |
| A21 | Optical frequency for all ASE and GN calculations | 1550 nm | ex15, ex16 | 1.5, 1.6 |
| A22 | Hollow-core group index | n_g = 1 (lower entry of the Antesberger record) | ex17, problems | 1.7, Problem 11 |
| A23 | Tolerance for the GN reference reproduction | 0.25 dB (rounding 0.05 + closed-form error 0.5/3 + frequency 0.02) | ex16 | 1.6 |

## C. Notation added to book/notation.yaml

A_R, L_span, T_0, f, H(f), τ_tol, Δβ, η_FWM, L_eff,a, **A** (Jones vector), S_ASE, 𝒢_WDM, 𝒢_NLI, N_ch, Φ_a, Ψ_a, SNR_req. The chapter also uses a few local symbols defined in place (κ_T compressibility, P_ref one milliwatt, μ for the GN coefficient, SNR_TR, SNR_th) that are not reused elsewhere.
