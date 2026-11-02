# Ch. 2: gaps, disagreements, notation conflicts (retrieval agent ch02)

Retrieved 2026-11-02. Direct `curl` and WebFetch to most publisher and university hosts (ee.stanford.edu, ieee.org, optica.org) were refused by the session proxy. Everything was read through the Exa search and fetch tools. Their PDF text extraction often drops square roots, fraction bars and Greek letters, so equation records marked "verify" need a check against the PDF. Counts: 110 ledger records, 28 equations, 41 sources (one, `savory_jstqe_2010`, is listed but not cited because only its abstract was seen).

## 1. Unsourced or weakly sourced needs

### 2.1 Signal space and Nyquist shaping
1. **Bit-rate identity R_b = N_pol R_s log2(M) R_c.** This identity is not printed verbatim in any source I read. `ch02.eq.bit_rate` derives it from Cho & Winzer Eq. (5) and checks it against 400ZR (59.84375 GBd x 8 = 478.75 Gb/s). Kikuchi 2016 or Winzer & Essiambre should print a citable form.
2. **Raised-cosine source.** The only raised-cosine source is Ishihara et al., IEEE Access 2021, a tier-A general comms review. No optics-specific peer-reviewed statement of (1+ρ)R_s was read in full text. Candidates are Bosco et al. JLT 2011 (Nyquist-WDM) and Schmogrow et al. OE 2012 ("Error vector magnitude...") or JLT 2013. Only the Bosco OFC 2012 slides were seen.
3. **Kikuchi 2016 Sect. IV.** I did not capture the photon-number SNR expressions for heterodyne, homodyne and phase-diversity detection, or the "x photons per bit" sensitivities. Only Eqs. (1)-(24) and (31)-(36) were seen.

### 2.2 IM/DD metrics
4. **IEEE 802.3bs/cd/ck/df published clauses** (121-124, 138-140, 151, 167) were not read; the standard is paywalled to this session. All 802.3 values here come from task-force contributions (tier B). This affects:
   - the 400GBASE-DR4 TDECQ max (expected 3.4 dB), OMAouter min and RIN21.4OMA;
   - 400GBASE-FR4 / 100GBASE-DR values;
   - 802.3ck/df 200G-per-lane TDECQ and the TECQ limits.

   100G Lambda MSA 100G-FR/LR values (TDECQ 3.4 dB, RIN -136 dB/Hz) are recorded instead. **RIN21.4OMA for 400GBASE-DR4 is a gap.**
5. **TDECQ formula.** The draft (King 2016) gives R = (Ceq σG² + σS²)^½. The published form quoted by Cole 2019 is R = sqrt(σG² + σS²), with Ceq handled separately. Verify against IEEE 802.3-2022 Eq. (121-12).
6. **PAM4 9.5 dB penalty.** The electrical-domain 9.5 dB comes from a circuits paper (Lu et al., ISLPED 2018), and the optical-domain 4.8 dB is in Cole 2014 (tier B). Pang et al. JLT 2020 gives the (N-1) eye-height factor. No optics journal paper read here states "9.5 dB" with the equal-peak-power derivation explicitly. The derivation (20log10 3) should be done in calc.
7. **MPI.** The sources are task-force contributions (Bhatt 2016, Mazzini 2015, Zhang 2022) plus the Fei et al. JLT 2025 abstract. A peer-reviewed closed-form MPI penalty for PAM4 was not read in full. A classic candidate is Gimlett & Cheung JLT 1989 for NRZ.

### 2.4 DSP chain
8. **Savory CD tap formula N = 2⌊|D|λ²z/(2cT²)⌋+1** and the CMA update equations (Savory OE 2008 / JSTQE 2010; Kikuchi OE 2011). These were seen only in secondary transcriptions: a 2013 thesis and a vendor blog reproducing a book chapter. They were NOT recorded. The equivalent primary form from Ip et al. 2008 is recorded as `ch02.eq.cd_taps_ip`.

   Still needed:
   - CMA: ε = 1 − |x_out|², h ← h + μ ε x_out y*;
   - the decision-directed LMS update;
   - the CD all-pass G(z,ω) = exp(−j D λ² z ω²/(4πc)).
9. **Viterbi-Viterbi 4th-power estimator** (Viterbi & Viterbi, IEEE Trans. Inf. Theory 1983) and **BPS equations** (Pfau Eqs. 7-10). Only Pfau's abstract numbers and text were extracted; the equation glyphs were lost.
10. **Gardner TED equation.** Only the abstract was read (two samples per symbol).
11. **Complexity per bit.** Ip 2008 gives multiplications per second (recorded). The Table 7 tap counts and the Sect. 7 single-carrier vs OFDM comparison were not extracted. Spinnler JSTQE 2010 ("Equalizer design and complexity for digital coherent receivers") is the standard source for multiplications per bit and was not read.

### 2.5 Information rates
12. **Forney et al. 1984 / Ungerboeck / Kschischang & Pasupathy 1993** were not read; the 1.53 dB comes via Böcherer 2015 Sect. III-D. Cho & Winzer was read via the IEEE open text, but no explicit 1.53 dB sentence was captured there.
13. **Gap of uniform 16QAM/64QAM to Shannon** is recorded only through Böcherer Table I (per-dimension ASK, MI-based): about 0.35 dB at 2 b/2D and 0.86 dB at 4 b/2D. A GMI-based (BICM) gap at the operating SNR of 400ZR/800ZR is not recorded. Alvarado 2018 Table I gives GMI thresholds for DVB-S2 LDPC plus staircase but was not extracted.

### 2.6 FEC
14. **KP4 RS(544,514) NCG and latency.** Neither was found as a stated number. NCG should be computed with `ch02.eq.ncg_hd` at p* = 2.4e-4 (R = 514/544), noting that the Ethernet target is an FLR, not BER 1e-15. RS(544,514) latency (~100 ns class) is unsourced.
15. **Staircase pre-FEC threshold.** Smith et al. do not state it in the text I extracted; 4.8e-3 is their error-floor operating point. Alvarado uses 4.7e-3, and ITU-T G.709.2 / OIF statements of the staircase threshold were not read.
16. **CFEC and staircase latency** are unsourced. **oFEC and CFEC power** are unsourced (only an 802.3df IM/DD FEC power of ~0.2 W/800G at 5 nm).
17. **Concatenated SD codes beyond 800LR** (e.g. 800ZR oFEC vs 800LR CFEC-like, ITU-T G.709.3 FlexO-LR) are not covered. The OIF 800LR and 800ZR IAs were not read directly; numbers come via Nagarajan JLT 2024.

### 2.7 DSP power
18. **Pillai et al. JLT 2014.** Only the abstract was read. The per-block pJ/bit at 40 nm and the node-scaling assumptions were seen only in a secondary UCL conference paper (CD 162 pJ/bit at 40 nm vs 81 at 20 nm for 2400 km PM-QPSK) and were NOT recorded.
19. **Laperle & O'Sullivan JLT 2014.** Not read (paywalled, abstract only, which has no numbers).
20. **Vendor ISSCC coherent DSP power by node** (e.g. 16 nm, 7 nm, 5 nm, 3 nm in W at stated baud) was not found with full numbers. The records available are:
    - the 7 nm module at 40-60 pJ/bit (Puttegowda, abstract);
    - the 22 nm 400G receiver units at 5 W (Fougstedt, abstract);
    - the 5 nm 200 GS/s ADC at 20 fJ/conv-step (Nguyen ISSCC 2024, abstract);
    - the 40 nm 25 GS/s ADC at 0.4 pJ/conversion (Crivelli).

    The generation table by node and baud (Acacia Jannu 5 nm 136 GBd, Ciena WL6e 3 nm 200 GBd, etc.) exists only in a market-analyst blog (tier C, not recorded). Vendor datasheets would be needed for tier B. A pJ/bit vs node model will need explicit ASSUMPTION constants, e.g. a per-node energy scaling factor.

## 2. Disagreements between sources

| Quantity | Source A | Source B | Note |
|---|---|---|---|
| CFEC pre-FEC BER | OIF 400ZR IA 01.0/02.0/03.0: 1.25E-2 | CableLabs blog (tier C, not recorded): 1.22E-2 | Use 1.25e-2 |
| oFEC enc+dec latency | OpenROADM 6.0: < 2 µs at 800G | OpenZR+ and CableLabs: < 3 µs | Rate-dependent; both recorded |
| PAS gap to capacity | Böcherer IEEE TCOM abstract: < 1.1 dB | arXiv abstract: < 1 dB | Both recorded; use published |
| TDECQ noise term R | King draft 2016: (Ceq σG² + σS²)^½ | Cole 2019 quoting 121-11: sqrt(σG² + σS²) | Use published; verify |
| Staircase threshold | Smith 2012 operating point p = 4.8e-3 | Alvarado 2018: 4.7e-3 | Small; neither is an explicit threshold statement in the extracted text |
| oFEC overhead | Nagarajan JLT 2024: 15.32% | CableLabs PHYv2.0: "15. %" (garbled) | Use 15.32% |
| ADC FOM units | Crivelli: 0.4 pJ/conversion | Nguyen: 20 fJ/conversion-step | Different FOM definitions possible; do not compare directly without checking |

## 3. Notation conflicts (to propose in `book/notation/ch02_proposals.yaml`; not written by this agent)

- **Roll-off.** Sources use β, which clashes with the propagation constant β. Use ρ (per syllabus).
- **MB rate parameter.** ν (Böcherer) clashes with optical frequency ν, and λ (Cho & Winzer) with wavelength. Propose κ or λ_MB.
- **R.** Responsivity (Kikuchi), FEC code rate (Smith, Zhang) and reflectance product (Bhatt) all use R. Propose R for responsivity, R_c for code rate, and r_MPI for reflectance.
- **M.** Constellation order vs M/K oversampling ratio in Ip 2008. Propose n_ss for samples per symbol.
- **N and B.** N for FIR taps vs N coded bits vs N interferer pairs, and B for block length (Ip) vs noise bandwidth (Kikuchi) vs occupied bandwidth.
- **New symbols needed:** R_b, R_c, N_pol, M, m, P_LO, P_s, I_I, I_Q, Q_t, OMA_outer, C_eq, σ_G, σ_S, H(X), IR, G (GMI), NCG, OH.
