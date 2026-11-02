# Ch01 sections 1.1-1.3: gaps and source disagreements (retrieval agent ch01_a)

Retrieved 2026-11-02.

## Access note

- `www.itu.int` is blocked for direct fetch in this session (proxy 403 / DNS refusal). All ITU-T texts were read through the Exa crawler's copy of the official itu.int PDF and ePublication URLs. Page numbers could not be recovered, so locators give clause, table and equation numbers. Before publication, someone should open the PDFs once to confirm the table cells, especially the multi-column G.657 Table 1, where the crawler interleaved the columns. The AFL application note's G.657 table confirms the column mapping.

## Gaps (needed by the syllabus, not sourced to standard)

1. **Dispersion length L_D = T0²/|β2| and the β(ω) Taylor expansion.** No tier-A source with a verifiable locator was read. Agrawal, *Nonlinear Fiber Optics*, is the obvious source, but the text was not accessible, so I did not cite an equation number from memory. The sources found were lecture notes, a Lisbon extended abstract and a blog (all tier C). The relation D = −2πcβ2/λ² is sourced to IEEE Photon. J. 2019 Eq. (11). S(β2, β3) is sourced only to a licentiate thesis (tier B).
2. **IEEE 802.3 normative text** (802.3cu 400GBASE-FR4/LR4-6, 802.3cd/cu 100GBASE-FR1/LR1, 802.3df 800G). The text is paywalled and was not read. I used the 100G Lambda MSA public specs (tier B) instead. The MSA 400G-FR4 grid matches the IEEE 802.3 100G_OPTX Mar-2019 baseline slide (Liu), but IEEE channel-dispersion values are not recorded. I did not retrieve the 100G-LR1 or 800G-FR4 MSA specs.
3. **Maxwellian DGD pdf from a tier-A source.** Foschini & Poole (JLT 1991) and Karlsson (JLT 2001) are paywalled. The pdf equation is sourced to a Waterloo M.Sc. thesis (tier B). The mean/RMS relation is tier A (G.650.2 Eq. 3-3), and so are the tail probabilities (G.959.1 Table 8-3). G.650.2 Appendix IV (PMD statistics, Monte Carlo PMDQ/DGDmax) was not in the fetched text. I also did not check whether a G.650.2 edition newer than 08/2015 exists.
4. **PDL.** No values or sources were recorded for PDL (component PDL magnitudes, PDL-induced OSNR penalty). The same is true for the statement of what 2×2 MIMO coherent DSP removes: it removes PMD of all orders within the equalizer length, but not PDL-induced SNR loss. This needs, for example, Mecozzi & Shtaif on PDL, or Savory's 2010 JSTQE "Digital coherent optical receivers".
5. **Hengtong (亨通) / ZTT (中天) ULL datasheets.** Not findable as primary PDFs. The only hits were a 2015 Hengtong press release (G.654-135, "170 % effective area", no loss number) and a 2016 brokerage report (tier C, garbled table: 亨通 G654-135 0.165 dB, 153 µm²?). Neither was recorded. YOFC is covered only by a 2020 corporate presentation (zh, tier B), not a current datasheet.
6. **Intrinsic loss minimum of silica.** No authoritative "theoretical minimum" value was found. The only primary number is Khrapko 2024's model projection of 0.1325 dB/km for their draw conditions. Kanamori cites a Saito estimate of below 0.141 dB/km with annealing (not recorded separately).
7. **UV Urbach-tail magnitude.** Kanamori says only that it is "negligible" for SiO2 at telecom wavelengths. No numbers were recorded.
8. **Group index from a standard.** No ITU-T fibre Recommendation specifies n_g. Group index comes only from vendor sheets: SMF-28 Ultra 1.4682 and Vascade 1.4634 at 1550 nm. The R&M G.657 sheet lists 1.468 (not recorded).
9. **Tamura 2018 and Sato 2024: abstract only.** Loss spectra, fictive-temperature values and Rayleigh coefficients inside these papers were not read.
10. **G.691 Appendix I (PMD penalty discussion)** was not read. G.959.1 refers to it.
11. **Corning Vascade EX2500 / TXF** (terrestrial G.654.E). The selection guide lists EX2500 at 0.148 dB/km nominal and 125 µm², but I did not open the product sheet, so nothing was recorded.

## Source disagreements (each recorded as separate records)

- **Record-low silica fibre loss after 2018.** Two 2024 claims exist:
  - Sato et al. (Sumitomo), OFC 2024 Tu2E.1: 0.1397 dB/km at 1566 nm, Ge-free silica-core single-mode fibre (`ch01.rec.sato_ofc2024_1566`).
  - Khrapko et al. (Corning), IEEE PTL 2024: 0.1400 dB/km at 1560 nm, *quasi*-single-mode fibre, with half-lengths averaging 0.1395 dB/km (`ch01.rec.khrapko_ptl2024_qsmf`).

  Both call their result a record. The difference is mostly fibre class (SMF vs QSMF) and wavelength. Tamura 2018 (0.1419 dB/km) is superseded. The hollow-core DNANF (0.091 dB/km, Petrovich 2025) is a different waveguide class and is recorded separately.
- **Vascade EX2000 attenuation.** The Corning PI1440 sheet (2023) gives 0.149 dB/km nominal. The PI1445 family sheet (2020) gives 0.152 dB/km typical. These are likely product-generation differences.
- **S0max for O-band PMDs.** G.652.D allows 0.092 ps/(nm²·km), and the 400G-LR4-10 MSA uses 0.092. The 400G-FR4 MSA Table 5-1 uses 0.093, the IEEE legacy B1.1/B1.3 value.
- **G.654.E Note 1 cut-off.** The 2024 edition says the cable cut-off should be "less than 1527 nm" for G.698.2 use at 1527.8-1530 nm. The 2020 edition text reads "less than 1527.8 nm".
- **Kanamori 2021 internal inconsistency.** The text says fibre Rayleigh coefficients are 0.8-0.9 dB/(km·µm⁴), but its own Fig. 4 example for a typical SMF gives 0.93. Sakr 2020 gives about 0.75 for record pure-silica-core fibre and about 1 for high-volume Ge-doped fibre.
- **Z-PLUS 150 loss.** The datasheet gives 0.144 dB/km typical (ULL). The Sumitomo 2024 press release rounds this to "0.14 dB/km" (tier C).

## Notes for the writer

- G.652 2024 (latest edition) did not change any G.652.D Table 2 value compared with the 2016 edition. It added Appendix I.6.2 (statistical O-band CD for M = 1-16 cables) and I.6.3 (PMDQ vs M).
- G.657 2024 lists only the A1, A2 and B3 subcategories (B2 no longer appears). B3 has PMDQ 0.50 ps/√km and λ0 1250-1350 nm.
- Vendor PMD link design values are not always on the ITU M=20, Q=0.01 % basis. Vascade EX2000 uses IEC m=24, Q=0.1 %.
- zh terminology encountered: 衰减系数 (attenuation coefficient), 低水峰 (low water peak), 模场直径 (MFD), 光缆截止波长 (cable cut-off wavelength), 宏弯损耗 (macrobend loss), 有效面积 (effective area), 成缆后 (after cabling), 超低衰减/超低损耗 (ultra-low attenuation/loss), 截止波长位移单模光纤 (cut-off-shifted SMF, G.654), 弯曲损耗不敏感单模光纤 (bend-insensitive SMF, G.657), 零色散波长 (zero-dispersion wavelength), 偏振模色散 (PMD), 微分群时延 (DGD), 一级干线/一干 (level-1 national trunk), 空芯光纤 (hollow-core fibre), 假想温度 (fictive temperature), 群折射率 (group index).
