# ch01_c gaps, disagreements, and glossary proposals (sections 1.5, 1.7)

Retrieval date 2026-11-02. Network note: WebFetch and direct curl could not reach nature.com, arxiv.org, physics.nist.gov or perso.telecom-paristech.fr from this session (proxy refusal); all reading was through Exa fetch/search highlights. Several items are therefore abstract-only (`confidence: med`).

## Unsourced or under-sourced needs

1. **ASE PSD and F -> 2 n_sp from a telecom-grade tier-A text.** The equations are recorded from Carney et al., Opt. Express 2013 (SOA paper, generic formula) and Desurvire's Scholarpedia article (tier B). Better primary sources were not reachable: Desurvire, *Erbium-Doped Fiber Amplifiers* (Wiley 1994); Agrawal, *Fiber-Optic Communication Systems*; Haus, "The noise figure of optical amplifiers," IEEE PTL 10(11) 1998; Essiambre et al., JLT 28(4) 2010. One of these should replace or back up Carney before the prose is written.
2. **Baney et al. 2000, Eqs. (13)-(14)** (F_sig-sp = 2 rho_ASE/(h nu G) + 1/G, the IEC optical-method NF). The fetch was cut off before these equations, so only Eqs. (3)-(4) are recorded.
3. **Caves 1982** was read from the abstract only. The F >= 2 (3 dB) statement in optical-NF terms comes from Desurvire and Carney. Haus 2000 (IEEE JSTQE 6(2), "Noise figure definition valid from RF to optical frequencies") was not retrieved.
4. **Essiambre et al. JLT 2010** (the original OSNR to SNR relation) is paywalled. The relation is recorded from Essiambre and Tkach, Proc. IEEE 2012, Eq. (11), which is full text.
5. **Lumentum EDFA datasheet with NF values.** Only the portfolio page was found, with no numbers. **O-Net** was not found. The NF values we have come from Accelink (3 sheets), Coherent (a pluggable POLS, not a line amplifier) and VIAVI (a test instrument). A long-haul line-amplifier datasheet from Lumentum, Coherent or Ciena is still needed for a "typical ILA NF 4.5-5.5 dB" statement. The Accelink L-band NF could not be assigned to a table column.
6. **Accelink and Coherent table column ambiguity.** Text extraction scrambled the min/typ/max columns, so the NF values are marked `spec_max` with `confidence: med`. Check them against the PDF layout.
7. **G.Sup39 Eq. (9-17)** was reconstructed from garbled text. It is consistent with the stated special cases, but check it against the PDF. The 10/2025 edition's clause 9.5 was not read; it may have renumbered the equations.
8. **Microsoft Ignite 2024 keynote primary source** (15,000 km HCF plan, with a timeframe of "coming months" or "24 months" depending on the press account). Only secondary press was available.
9. **Antesberger et al. (arXiv 2308.01337) and Gao et al. (arXiv 2409.13332): published venues are not verified.** Find the journal versions (possibly Optica Quantum / Phys. Rev. Applied, and Opt. Express / JLT) and update the source records.
10. **Petrovich 2025 ref. 32** (the "other team" with a 4-tube DNANF at 0.1-0.13 dB/km): almost certainly Gao et al., but the reference list could not be fetched.
11. **Corning 0.1400 dB/km quasi-single-mode fiber** (Khrapko et al., IEEE PTL 36(8), 539-542, 2024): seen only as a title in a reference list, so no record was made. Needed for the 1.1/1.7 ULL contested box. The Corning result is quasi-single-mode, while Sumitomo's 0.1397 dB/km is single-mode, so this is a definitional disagreement to note.
12. **ZTT (中天科技) ULL record value:** none found with a number. **Hengtong hollow-core loss values:** not found (only exhibition mentions).
13. **YOFC global market-share percentage.** YOFC documents say "first place since 2016" without a percentage. The 11.30% (2023) figure comes from a broker report (Dongguan Securities) citing 网络电信 (tier C), so it is not recorded. The underlying CRU report is paywalled. A preform share figure is also missing.
14. **China Mobile / China Telecom G.654.E deployment statements** (for example, the 400G inter-provincial backbone) come only via broker reports. Operator primary sources are not found. Defer to ch6/ch9.
15. **The NICT 22.9 Pb/s peer-reviewed paper** (probably ECOC 2023 PDP) is not located; recorded from the press release only (tier C).
16. **Values inside the Puttnam et al. Optica 2021 review** (record tables, MIMO-DSP complexity) were not extracted. Only the abstract classification is recorded. Hayashi's reviews were not retrieved.
17. **First commercial MCF subsea cable in-service date** (Google TPU) is not confirmed from a primary source.
18. **YOFC "0.04 dB/km" (2025 annual report):** no wavelength, length or method, and no peer-reviewed counterpart found.
19. **HCF standards:** ITU-T SG15 mentions only a "potential technical report on hollow core fibers" (Oct 2025). No IEC/ITU HCF specification exists yet. Recorded under ch01.sdm.itu_sg15_2025_two_mcf_recs.

## Disagreements and contested items (each side recorded separately)

### (a) Hollow-core deployment timing / scope
- **Pro / near-term:** Microsoft says it has deployed since 2023 in multiple Azure regions, has a 15,000 km plan, and has >1,200 km carrying live traffic (all tier C). YOFC's annual report calls 2025 the "first year of HCF commercialization", with >10 projects and a 100 km Guangdong-Hong Kong link (tier B). Deployed cabled loss of 0.065 dB/km in China Mobile's network is peer reviewed (JLT 2026).
- **Skeptic:** Wei Leping (former China Telecom) says the cost is about 2500x G.652.D per core-km and that HCF will not become general network fiber (tier C). Andrew Lord (BT) says HCF is a niche with no wholesale swap-out (tier C). CAICT (Ao Li) says the next 3-5 years are the key window and that geometry standardization and process stability remain unsolved (tier C).

### (b) Reported vs reproduced loss records
- Peer-reviewed journal record: **0.091 dB/km** at 1550 nm in 15 km, from four cutbacks plus OTDR (Petrovich, Nat. Photon. 2025).
- On the short HCF1 fibre from the same group, the method spread was **0.055-0.11 dB/km**. The authors say "considerably longer fibres are needed for accurate measurements."
- Lower values in **conference abstracts only**: 0.052 dB/km over 40 km (Linfiber, ECOC 2025) and 0.05 ± 0.01 dB/km over 9.1 km (YOFC, ECOC 2025). The **company claim** of 0.04 dB/km (YOFC annual report 2025) has no stated method.
- Hero sample vs production: the YOFC batch average was **0.147 dB/km** over 733.3 km (ECOC 2025), while trade press reports a "scale production average" of **0.12 dB/km**. The two differ, and their dates and batches are unknown.
- Older internal inconsistency: Jasion OFC 2020 gives the fibre length as 1.7 km in the abstract and 2.8 km (1.2 km measured) in the conclusion. Short cutbacks gave 0.60 dB/km against 0.28 dB/km for the 500 m cutback (HOM bias).

### Latency / speed figures disagree in rounding
Reported latency reductions are 30% (Petrovich conclusion; Poggiolini Sec. II), 31% (YOFC; Poletti 2013 "31% slower"), 33% (Microsoft) and 34% (Antesberger, measured with unequal lengths). Reported speed-ups are 45% (Petrovich abstract), 47% (Microsoft, YOFC) and 50% (Poggiolini). Recommendation: compute both in book/calc from n_g(SMF-28 Ultra, 1550 nm) = 1.4682 and n_g(HCF) ≈ 1.00 (Antesberger; an exact HCF n_g of about 1.001-1.003 is needed). With n_g(HCF) = 1, the results are 1 - 1/1.4682 = 31.9% latency reduction and a 46.8% speed-up.

### Minor
- Petrovich 2025 states that silica has 26 THz of bandwidth below 0.2 dB/km in the abstract and 25 THz in the conclusion.
- Two companies both claim to have supplied the fibre for the China Mobile 2024 800G Shenzhen-Dongguan HCF trial: Linfiber/Jinan University (with 特发信息) per JNU news, and YOFC per YOFC news. They may have supplied different segments.
- Vendor C-band ranges (1528-1562, 1528-1564 and 1528-1569 nm) extend beyond the ITU discussion band of 1530-1565 nm.

## Proposed glossary corrections and additions (book/glossary.yaml)

| en | current zh | proposal | source |
|---|---|---|---|
| hollow-core fiber | 空芯光纤 | keep; add a sub-entry "anti-resonant hollow-core fiber (AR-HCF/HC-ARF) 反谐振空芯光纤 (YOFC: 空芯反谐振光纤)" | YOFC 2025 annual report, definitions table: "空芯光纤 指 空芯反谐振光纤（HC-ARF）"; JNU/SASAC news use "反谐振空芯光纤" |
| nested antiresonant nodeless fiber (NANF) | 嵌套反谐振无节点光纤 | acceptable; add DNANF = "双层嵌套反谐振无节点光纤" and note the Chinese industry term "双层嵌套" | JNU press 2024: "四单元截断型双层嵌套结构" |
| noise figure | 噪声系数 | keep 噪声系数 as primary, add the alias 噪声指数 (used in some vendor sheets) | Amonics Chinese datasheet uses "噪声指数"; Accelink Chinese marketing uses 噪声系数 (not verified verbatim). Low confidence; check GB/T or YD/T EDFA standard wording |
| spontaneous emission factor (n_sp) | (missing) | add "自发辐射因子" (also 粒子数反转因子) | needs a Chinese textbook citation; not verified |
| weakly-coupled multicore fiber | (missing) | add "弱耦合多芯光纤" | Hengtong press 2024: "超低损耗四芯弱耦合光纤" |
| space-division multiplexing fiber | (missing) | add "空分复用光纤" | YOFC 2024 annual report: "多芯、少模等空分复用光纤" |
| ultra-low-loss fiber | 超低损耗光纤 | keep; add the variant "超低衰减" (YOFC product naming) | YOFC annual report definition of G.654.E: "超强超低衰减大有效面积光纤" |
| support-tube hollow-core fiber (ST-HCF) | (missing) | add "支撑管结构空芯光纤" | YOFC OFC 2025 news; CWW 2025 |

## Notation proposals (book/notation.yaml, for the lead to decide)
- Add `S_{\mathrm{ASE}}` (or reuse `N_{\mathrm{ASE}}` as in Essiambre-Tkach) for the ASE PSD per polarization in W/Hz. notation.yaml currently has only P_ASE (power).
- G.Sup39 uses `L` for span loss in dB, which clashes with notation `L` (length in km). The prose should use `L_{\mathrm{span}}` in dB, as the syllabus does.
