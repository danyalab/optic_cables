# Ch. 3 (Photonic devices): gaps, disagreements, notation conflicts (retrieval agent ch03)

Retrieved 2026-11-02. Outbound access was limited. `curl` was refused by the proxy (zenodo, chalmers), and WebFetch could not resolve research.chalmers.se. Full texts were read through the Exa fetch tool. Its PDF extraction drops Greek letters, minus signs, `=` signs (sometimes printed as "5") and fraction layouts. In quotes, Greek letters and math symbols have been transcribed into ASCII ("alpha", "Delta n", "+/-", "um"). Every equation whose notes say "verify" or "reconstructed" needs a check against the PDF before it is used.

## 1. Unsourced needs (no primary source read)

1. **Coldren, Corzine & Mashanovitch, *Diode Lasers and Photonic Integrated Circuits*.** The text was not accessible, so no equation numbers from it are cited. The rate equations, threshold condition, resonance frequency, K-factor, RIN and linewidth come instead from two sources. One is Michalzik & Ebeling's VCSEL chapter (Springer 2003; author copy from Ulm). The other is Ahmed & El-Lafi (Pramana 2008). The Pramana threshold equation (Eq. 7) is dimensionally loose because it mixes a gain rate with a loss per length. The writer should give the textbook form Γg_th = α_i + (1/2L) ln(1/R₁R₂) only once a textbook page has been read, or derive it in the text.
2. **Typical α_H of InP quantum-well DFB lasers.** The only values recorded are these:
   - Henry's AlGaAs values (5.4 fitted, 4.6 and 6.2 measured);
   - the VCSEL range −2 to −7.

   No source gave the commonly quoted QW-DFB values of about 2 to 3. The paywalled Osinski & Buus overview (IEEE JQE 1987) has a table, but only its abstract was seen.
3. **Franz-Keldysh effect (bulk electroabsorption).** No primary source was read. QCSE is covered by the Miller PRL 1984 abstract only, and that abstract has no Stark-shift magnitude.
4. **Commercial or standard DML DFB bandwidth** (e.g., 25G/50G CWDM DMLs at about 20 to 30 GHz). Only the NTT membrane-laser record (108 GHz) was recorded. No commercial DML datasheet or IEEE PMD DML parameter was read.
5. **100G-per-lane (53 GBd) EML demonstrations.** Only 200G/lane and above were recorded (60 to 65 GHz bandwidth; 310 Gb/s). The 100G generation is not covered.
6. **TIA-492AAAC/AAAD/AAAE and IEC 60793-2-10.** These are paywalled. EMB values come from Parsons et al. (JLT, tier A, which quotes the standards) and from IEEE Clause 95 draft Table 95-13. Final IEEE 802.3 text for Clauses 95, 138, 150 and 167 was not read:
   - Clause 95 is the publicly posted task-force draft (tier B);
   - the SR8 and SR4.2 reaches come from TIA FOTC summaries (tier B).
7. **SWDM MSA document provenance.** The spec was read from a copy hosted by a transceiver vendor (Ascent Optics), not from swdm.org. The revision number and year (2017) are uncertain.
8. **LiNbO₃ r₃₃ (about 30.8 pm/V) and Si thermo-optic coefficient (about 1.8×10⁻⁴ /K).** Neither was sourced. Both are needed for the BTO-vs-LN comparison (3.5) and for the ring thermal-tuning derivation (3.4). Bogaerts' text mentions the "large thermo-optic response of silicon" but no number was extracted.
9. **Wavelength locking beyond Sun et al. 2015.** Padmaraju/Bergman-type dithering locks and the power cost of locking at scale were not retrieved.
10. **Heterogeneous III-V/Si laser numbers.** The Komljenovic JLT 2016 review was read only as abstract plus conclusion, so only a qualitative fact record exists. Missing: output power, threshold, Q of the Si-cavity laser, record narrow linewidth (sub-kHz), and III-V/Si taper coupling loss.
11. **Telcordia GR-468-CORE text.** The full text is paywalled. Copies of Issue 2 (2004) are hosted on unauthorized sites and were deliberately not used. The test conditions recorded here (damp heat, temperature cycling, accelerated aging, mechanical shock) come from supplier qualification reports (OZ Optics 2014, Agiltron 2021; tier B). The GR-468 clause numbers in those reports may follow older numbering. The "tier A/B test list" requested by the brief was not found in a citable public form. No DFB/EML laser FIT value from a peer-reviewed source was found; all FIT values are for 850 nm VCSELs (tier B: VI Systems report and IEEE 802.3dh contributions).
12. **Typical commercial Si MZM VπL in foundry PDKs** (about 1.5 to 2.5 V·cm at 50 GBd). Only the 2010 Kotura record (1.4 V·cm, 12 GHz) and Witzens' review statements were recorded.
13. **TIA noise, sources not read in full.** The Patel JSSC 2023 abstract and text highlights were read. The Declercq JLT 2025 value is from the abstract only.

## 2. Disagreements and caveats (recorded as separate records)

- **100GBASE-SR4 reach.**
  - IEEE Clause 95 draft Table 95-5 gives 70 m on OM3 and 100 m on OM4 (`ch03.mmf.sr4_reach_om3/om4`). Legrand, Wikipedia, CPV Micro and the 2013 ECOC Cunningham slides agree.
  - The TIA FOTC multimode-applications table lists 100 m and 150 m (`ch03.mmf.fotc_sr4_conflict_om3/om4`). This is almost certainly a copy error from the 40GBASE-SR4 row.
  - Use IEEE.
- **ITLA linewidth: spec vs product.**
  - OIF-ITLA-MSA-01.3 (2015) specifies ≤5 MHz (Application 1) and ≤10 MHz (Application 2). These figures date from direct-detection DWDM.
  - Coherent nano-ITLAs achieve <100 kHz (Furukawa, IEICE 2023) to ≤300 kHz (SEDI datasheet).
  - These are not in conflict: the OIF IA is a floor, not typical performance. Prose must not present 5 MHz as the coherent requirement.
- **VCSEL FIT, lab vs field.**
  - Lab tests give an upper bound of about 189 FIT (60 % CL; VI Systems) and <7 FIT at 105 °C (TRUMPF).
  - Field data give <1 FIT (Broadcom, >100 M channels).
  - The difference comes from limited device-hours at the low GR-468 default Ea = 0.35 eV, not from a physical disagreement.
- **VCSEL wear-out activation energy.** VI Systems measured 1.3 eV with N = 8. It quotes the literature value as about 0.7 eV with N = 2 at lower current density. TRUMPF uses 1.3 eV. The models differ by current-density regime.
- **α_H sign convention.** Henry's α = Δn′/Δn″ gives positive values (about 5). Michalzik & Ebeling give −2 to −7 for VCSELs. Prose must fix one convention and say |α_H|.
- **MCEF/D ratio.** Michalzik & Ebeling give a damping-free theory value of MCEF ≈ 1.55·D. Measured: 20.6/17.5 = 1.18 (Haglund 2015). The Pramana paper gives an alternative approximation f_3dB ≈ √3 f_r (Eq. 31) under its own assumption. The writer should derive the 1.55 factor (√(1+√2)) and note that damping and parasitics reduce it.
- **Wang et al. (Nature 2018) bandwidths.** The bandwidths were read from the authors' April 2018 preprint: >45 GHz (20 mm), 80 GHz (10 mm), 100 GHz (5 mm). The Nature version of record was not opened beyond the abstract and the Extended Data Fig. 1 caption (Vπ 1.4/2.3/4.4 V). Confirm the bandwidths before quoting.
- **Timurdogan energy typo.** The nature.com abstract reads "below 1.03 J per bit". The conclusion reads 1.03 fJ per bit. The record uses fJ.
- **Bogaerts group index.** The extracted text reads "ng 430", taken as 4.30. Verify.
- **Soref & Bennett coefficients.** These were read from Reed et al. 2010 Eqs. (1)–(4), not from the 1987 primary text (abstract only). A 2011 refit (Nedeljkovic, Soref & Mashanovich, IEEE Photonics J.) exists. It was seen only on a tier-C calculator page and is not recorded.

## 3. Notation conflicts (proposals needed; this agent may not write `book/notation/ch03_proposals.yaml`)

| Source symbol | Meaning | Clash in notation.yaml | Suggested |
|---|---|---|---|
| α (Henry) | linewidth enhancement factor | α = fibre attenuation (1.1) | α_H |
| γ | relaxation-oscillation damping rate | γ = Kerr nonlinear coefficient (1.4) | γ_d |
| ε | gain compression factor | ε = NLI accumulation exponent (1.6) | ε_c |
| G, G_th | modal gain rate, threshold gain | G = amplifier gain (1.5) | g_m, g_th |
| F(M) | APD excess noise factor | F = amplifier noise factor (1.5) | F_A |
| C | capacitance | C = Shannon capacity (1.6) | C_j |
| ν (modulation) | modulation frequency in Michalzik | ν = optical frequency (1.5) | f (1.2) |
| L (cavity / ring) | cavity or ring length | L = fibre length (1.1) | L_c, L_r |
| A (Pramana) | linear gain term | A = field envelope (1.4) | rename |
| α, β (Varshni) | band-gap fit parameters | α attenuation, β propagation constant | α_V, β_V |
| Vπ, VπL, K, D, r₄₂, R (responsivity), M (APD gain), k (ionization ratio), Q, FSR, n_g, n_eff | new | none | add |

## 4. Access notes

- Abstract-only sources (confidence med): Henry 1982, Soref 1987, Westbergh 2011, Parsons 2019, Yamaoka 2021 (plus supplementary), Uchiyama JLT 2024, Bhasker OFC 2023, Uchiyama OFC 2024, Miller 1984, Gokhale/Inoue OFC 2023, Lam/Loh Opt. Eng. 2023, Feng OE 2010 (full conference version read), Yang COL 2022, Weigel OE 2018, Ogiso JLT 2017/2020, Abel 2019, Kang 2009, McIntyre 1966, Declercq 2025.
- Some DOIs, volumes and pages were left blank where they could not be confirmed from a page that was actually read (Yang COL, Weigel OE, Ogiso 2020, Gokhale, Michalzik chapter).
- The Michalzik & Ebeling chapter is cited as the 2003 Springer book chapter from an author copy. The book DOI and page range were not confirmed.
- The Furukawa Nano-ITLA paper (IEICE Trans. C, J106-C) is in **Japanese**. The quotes are in Japanese with English glosses in `notes`. The source `language` field is set to `en` because SCHEMA allows only en|zh; the orchestrator may want to add `ja`.
