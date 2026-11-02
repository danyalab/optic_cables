# Ch. 1 sections 1.4 and 1.6: gaps, disagreements, notation conflicts (agent ch01_b)

Retrieved 2026-11-02. Outbound access was limited: curl to itu.int, arxiv.org, iris.polito.it and umbc.edu was refused by the proxy. Full texts were read through the Exa fetch tool, whose PDF text extraction often drops Greek letters and fraction layouts. Every equation marked "verify" in `ch01_b_equations.yaml` needs a check against the PDF.

## 1. Unsourced needs (no primary source found or read)

1. **Scalar NLSE printed with both β2 and β3.** Agrawal JOSA B 2011 prints the general form, Eq. (7), with the sum over all orders, and the β2-only forms, Eqs. (10) and (11). The m ≤ 3 form in `ch01.eq.nlse_beta3` is DERIVED by me, not printed. The fix is to cite Agrawal, *Nonlinear Fiber Optics* (textbook, tier A), with an equation number, or another source that prints this form.
2. **Manakov equation, symbol level.** Marcuse, Menyuk & Wai 1997, Eq. (12), was located and the "8/9 factor" sentence was read. The equation glyphs were not extractable, so `ch01.eq.manakov` records the structure only. Wai & Menyuk JLT 1996 (PMD and nonlinearity) was not read.
3. **Measured γ for a named G.654.E product.** No datasheet or paper giving a measured γ (1/(W·km)) for G.654.E or G.652.D at 1550 nm was found. Vendor datasheets list Aeff only. Primary model parameters exist: Poggiolini Table I, SMF 1.3 and LPSCF 0.8. The worked example should COMPUTE γ = 2π n2/(λ Aeff) in `book/calc/` from a chosen n2 record and the Aeff records (G.652.D typ. 80 µm²; G.654.E typ. 110–125 µm², from a tier-B whitepaper). The chosen n2 must be justified because of the spread in §2.1. The Sterlite note gives γ ≈ 1.255–1.27 /W/km for G.657 (tier B, garbled, low confidence).
4. **Splett, Kurtzke, Petermann ECOC 1993.** Not available online. It is cited only as ref. [5] in Poggiolini 2012, as an early FWM-based NLI PSD. No values were taken from it.
5. **Essiambre et al. JLT 2010 headline numbers.** Only the abstract was read, so no SE-vs-distance numbers are recorded. The SSMF parameters (γ = 1.27, α = 0.22 dB/km, β2 = −21.7 ps²/km) are recorded via Poggiolini 2014 as a secondary report (`ch01.kerr.gamma_ssmf_essiambre_params`). The IEEE full text, Sect. XII, Tables I–III and Figs. 32–38, needs to be read.
6. **Implementation gap to Shannon or GMI, peer-reviewed and in dB.** The sources found are:
   - Rafique OFC 2017 (abstract): an OSNR penalty vs format theory of 2.2 dB for 16/64QAM and 1.1 dB for QPSK. This is a gap to ideal format performance, not to Shannon.
   - Yoshida ECOC 2020: SNR_TR of 14–21 dB, and a measured ROSNR gap to Shannon that appears only in Figs. 4–5. Those numbers are not extractable; read them from the figures or contact the authors.
   - Poggiolini 2014: an assumed 3 dB margin plus a 1.5 dB soft-FEC penalty. These are assumptions, not measurements.
   - ISE Magazine (tier C): an Infinera ICE6 claim of "1–2 dB from Shannon". This is a vendor claim only.

   Still needed: a tier-A measurement of a commercial or near-commercial transponder's net rate vs GMI or Shannon at a measured SNR, for example from an OFC/ECOC/JLT field-trial paper.
7. **Maximum GSNR closed form.** Poggiolini 2012 states P_ASE = 2 P_NLI at optimum and gives P_opt (Eq. 28) and N_s^max (Eq. 30). An explicit SNR_max = (2/3) P_opt/P_ASE, or SNR_max = 1/(3 (η/4)^{1/3} P_ASE^{2/3}), was NOT seen printed in the parts read. This includes 2014 Eq. (33), which gives only the dampening. The book should derive it in `book/calc/` from Eqs. (28)–(29). Do not cite it as printed.
8. **Symbol rate and NF of 2014 Fig. 11** (P_opt = −2.65 dBm over 20 × 85 km). These were not found in the extracted text, so the case cannot be reproduced without them. Prefer the 2012 check case in §4.
9. **G.655 in-force D limits (G.655.C/D/E).** Only the 1996 edition (0.1–6.0 ps/nm/km, 1530–1565 nm) and the 2009 summary were read. Sumitomo TR-22077A gives G.655.D 2.80–6.20 ps/nm/km at 1550 nm (tier B, not recorded as a separate record).
10. **FWM efficiency formula in ITU-T G.Sup47 §7.3.** The glyphs were garbled (`ch01.eq.fwm_efficiency_gsup47`, low confidence). Use the Poggiolini 2012 Eq. (2) ρ (FWM efficiency with Δβ) as the citable form. The classical source of the η formula is Inoue, JLT 1992 ("Four-wave mixing in an optical fiber in the zero-dispersion wavelength region"), cited by G.Sup47 but not read.
11. **GNPy full text.** Only the abstract was read. Per-scenario error distributions and fiber parameters are in the body (open access, JOCN 12(6) C31).
12. **Pages in published versions.** Poggiolini 2012 was read as the accepted post-print, which includes the erratum. Poggiolini 2014 was read as the PRE-REVIEW preprint, so its equation numbers (e.g. 27–29, 37, 40, 41, 51, 55, 56, 62) may differ from the published JLT 32(4). These need checking against IEEE Xplore.

## 2. Disagreements between sources

### 2.1 n2 of silica fibers (≈ 30% spread)
| Source | Fiber | n2 (10⁻²⁰ m²/W) | Method / conditions |
|---|---|---|---|
| Kato et al. OL 1995 | DSF / SMF / PSCF / DCF | 3.35 / 2.96 / 2.79 / 4.44 | XPM, depolarized pump, 1.55 µm, repeatability ±1% |
| Kim et al. OL 1994 | silica core / DSF | 2.36 / 2.52 | 1.319 µm, ±5% |
| Namihira et al. EL 1994 | DSFs | ~2.31 | SPM, random polarization, 1.55 µm, ±5% |
| Stolen et al. JLT 1998 | DSF (2 × 20 km) | 2.45 | SPM, random polarization, 1.55 µm, ±5% |
| ITU-T G.Sup47 (2025) | pure silica (formula constant) | 2.61 | empirical n2 = 0.0556·η_GeO2 + 2.61 |
| Sterlite app note (tier B) | G.657.A2/B3 | ~2.15–2.17 | cw-SPM, 1 km |

The XPM-based Kato values are systematically higher than the SPM and cw values: for DSF, 3.35 vs 2.31–2.52, about 33–45% higher. For pure silica, Kato's 2.79 vs Kim's 2.36 is about 18% higher. The sources read do not explain the difference. Possible causes are the polarization-averaging normalization (Chernikov & Taylor, OL 1996, "normalization factor of n2 for random polarization") and an electrostrictive contribution at the XPM modulation frequency. These are hypotheses that would need a source, for example the COST 241 intercomparison (Fellegara et al., EL 1997, 33(13) 1168), which was not read. The book should present n2 as a range with its method, and state which value the γ computation uses.

### 2.2 Fiber parameter tables, Poggiolini 2012 vs 2014
- SMF: D = 16.5 (2012) vs 16.7 ps/(nm·km) (2014). α = 0.2 in both (2014 §VII reference uses 0.22).
- NZDSF: α 0.2 / D 3.9 / γ 1.6 (2012) vs α 0.22 / D 3.8 / γ 1.5 (2014).
- PSCF: α 0.165 / D 20.4 (2012 "LPSCF") vs α 0.17 / D 20.1 (2014). γ = 0.8 in both.

These are not errors, just different reference fibers. Keep each check case paired with its own table.

### 2.3 NLI accumulation exponent ε
- GN-model prediction for full C-band: ε ≈ 0.035 (Nyquist) and ≈ 0.06 (50 GHz) in 2012; 0.03–0.08 in 2014.
- Experiments quoted in 2012: ε from 0 to 0.6. Some experiments (refs. [15] and part of [18] in Poggiolini 2012) report higher ε than GN predicts, and the 2012 paper itself says the matter is unsettled.
- 2014 explains part of this: the IGN model (ε = 0) often matches non-Gaussian-signal simulations better than GN, because two errors cancel (Sect. V-E).

### 2.4 GN accuracy
- GN vs pre-dispersed simulations: within 0.25 dB in maximum reach (2014).
- GN vs real-format simulations: it underestimates reach by 0.3–0.6 dB, and by up to 0.8 dB on LS fiber (EGN paper, 2014). It overestimates NLI by up to 6 dB in the first span for PM-QPSK over SMF (2014), and by 1–2 dB near maximum reach (EGN paper).
- These are consistent once the 1/3 dB-per-dB dampening (2012 Eq. 32) is applied, but the book must say which quantity, NLI or reach, each number refers to.

### 2.5 Within-source inconsistency
- Marcuse, Menyuk & Wai 1997 give the birefringence-orientation variation scale as "0.3 to 300 m" in Sect. I and "0.3–100 m" in Sect. II.
- Sterlite app note: the results section and the conclusion swap the A2 and B3 n2 values.
- Agrawal 2011 says γ is "1–10 W⁻¹/km for most silica fibers", while large-Aeff PSCF in Poggiolini uses γ = 0.8. This is a minor scope difference.

### 2.6 GN validity floor vs EGN usage
Poggiolini 2012 limits GN reliability to D ≥ 2 ps/(nm·km), Rs ≥ 28 GBd and ≥ 3 channels. The closed form, Eq. (15), additionally needs β2 ≥ 4 ps²/km and span loss ≥ 7 dB, while the 2014 tutorial asks for > 10 dB span loss for Eq. (37). The worked example must state which threshold it uses.

## 3. Notation conflicts (source vs `book/notation.yaml`)

| Source usage | Book symbol | Action |
|---|---|---|
| Poggiolini 2012/2014, GN arXiv: α = **field** loss coefficient, power ∝ e^{−2αz}; L_eff = (1−e^{−2αL_s})/(2α); L_eff,a = 1/(2α) | α = power coefficient | α_book = 2 α_Pogg. Then L_eff,a = 1/α_book. Convert every GN formula. |
| Poggiolini 2012: β2 = \|β2\| (always positive) | β2 signed | Use \|β2\| in GN closed forms. |
| G_WDM(f), G_NLI(f), G_ASE = **PSDs** (W/Hz, unilateral) | G = amplifier gain | Rename PSDs in the book (e.g. 𝒢 or S_WDM, S_NLI). Poggiolini 2014 uses Λ (Eq. 51) and Γ (Eq. 1) for amplifier gain. |
| OSNR_tot (2012) in noise bandwidth B_N; SNR, SNR_NL (2014) with B_N = R_s | OSNR in B_ref = 12.5 GHz; GSNR | The GN "OSNR" is the book's GSNR (B_N = R_s), not the book's OSNR. |
| ϵ / ε = NLI coherent-accumulation exponent of the **GN** model (2012 Eq. 7, 2014 Eqs. 16, 18) | ε "EGN coherent-accumulation exponent correction" | **CONFLICT.** In the sources, ε belongs to coherent GN vs incoherent GN (IGN), not to EGN. EGN corrects for non-Gaussian modulation (Φ_a, Ψ_a). The syllabus objective for 1.6 ("EGN correction for modulation-format dependence and coherent span accumulation (exponent 1 + ε)") merges two separate corrections. Suggest redefining ε in notation.yaml as "GN-model NLI coherent-accumulation exponent, P_NLI ∝ N_s^{1+ε}" and introducing Φ_a, Ψ_a for EGN. |
| η (Poggiolini 2014: P_NLI = η P_ch³, with η^{1 span}) | η, 1/W² | Consistent. G.Sup47 uses η for FWM efficiency (dimensionless), so the ledger renames that one η_FWM. Carena 2014 uses η for the normalized NLI variance η_NLI. |
| P_ch | P (P_ch: per channel) | Consistent. |
| Agrawal: field ∝ e^{i(β0 z − ω0 t)}, NLSE i∂A/∂z + iα/2 A − β2/2 ∂²A/∂T² + γ\|A\|²A = 0 | A, α (power), β | Consistent α. The GN literature uses the opposite Fourier sign (e^{+j...} in ρ), so state one convention in the book. |
| Marcuse et al.: u (2-vector) in the Manakov-PMD equation | A | Introduce a bold **A** or **u** for the Jones vector. |
| Carena 2014: Φ_a, Ψ_a, κ_mn | none | Add to notation.yaml for 1.6 if EGN formulas are shown. |
| Poggiolini: L_s = span length, N_s = number of spans | L, N_s | Consistent with notation.yaml (L = fiber or span length). |
| Poggiolini 2014 §VII: A_s = total span loss; K_s = Δf/R_s | none | Add if design rules (Eqs. 59–60) are used. |

## 4. Reproducible check case (recommended for the worked example)
**Poggiolini, JLT 2012, Sect. IV, Table I and Sect. XII-B (RS-SMF).**
- Inputs: SMF with α = 0.2 dB/km, D = 16.5 ps/(nm·km), γ = 1.3 1/(W·km). L_s = 100 km. EDFA NF = 6 dB.
- Inputs: R_s = 32 GBd, Δf = 50 GHz, raised-cosine roll-off 0.3, N_ch = 101 (about 5 THz). ε ≈ 0 for the P_opt calculation.
- Published result: optimum PSD 28.5 µW/GHz, which is **−0.4 dBm per channel**, about 20 dBm total.
- Published Nyquist variant (NY-SMF, 157 channels × 32 GBd): about −1 dBm per channel at 100 km spans and −2.6 dBm at 75 km spans.
- The paper does not state a maximum reach for this exact case.
- Secondary max-reach check: Poggiolini 2014 §VII-A reference simulation (9 ch PM-16QAM, 32 GBd, K_s = 1.05, SMF with 80 km spans, α = 0.22 dB/km, D = 16.7 ps/(nm·km), γ = 1.3, NF 5 dB, SNR_T = 16.85 dB) gives N_s^max = 15 spans. This is a split-step result, so a GN/IGN closed form should land near 15 but not exactly on it.
- Caveat: the 2012 example uses NF = 6 dB and the syllabus worked example uses 64 GBd DP-16QAM. Rescale using the symbol-rate independence of the optimum PSD stated in 2012 Sect. XII-B: "at least in the Nyquist-WDM case, the optimum signal PSD is independent of format, transceiver impairments and symbol rate". No published 64 GBd check value was found.
