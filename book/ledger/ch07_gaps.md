# Ch07 (Subsea systems): gaps and source disagreements

Retrieval agent ch07. Retrieved 2026-11-02. There are 99 records, 13 equations and 40 new sources. Two sources are reused from `sources/ch01_c.yaml`: `google_cloud_blog_2023_mcf` and `sumitomo_press_2026_petal`.

## Access notes

- The following hosts could not be fetched directly in this session: `www.ecfr.gov`, `www.federalregister.gov`, `www.govinfo.gov`, `docs.fcc.gov`, `www.law.cornell.edu`, `research.google`, `sumitomoelectric.com` and `arxiv.org` (PDF). All of these texts were read through the Exa crawler's copy of the official URL. For that reason, FR and eCFR locators give paragraph numbers, not page numbers.
- The Perin et al. text is the arXiv author version (via ar5iv). Its published JLT 2019 DOI was not captured.
- The Desbruslais NOC 2015 PDF is the copy hosted by Xtera. The crawler garbled Eqs. (6), (7), (13), (16) and (17), so they are not recorded. Eqs. (2), (4) and (14) were reconstructed from the structure of Eqs. (1) and (5) (see the equation notes). Recheck them against the IEEE PDF.
- The crawler garbled the column alignment of Downie 2023 Table II. The 1.6 % overall E-O efficiency is consistent with the product of the listed factors, but the factor-to-column mapping should be re-read.

## Gaps (needed by the syllabus, not sourced to standard)

1. **Dar et al., JLT 2018: abstract only.** The power-constrained capacity equations, cost model, and the "permissible MCF cost premium" numbers were not read. The capacity-under-power-constraint derivation therefore rests on Perin et al. (Eqs. 2, 3, 5), on Desbruslais (Eqs. 1, 4, 5, 14) and on maximum power transfer. Downie, "Maximum capacities in submarine cables with fixed power constraints...", JLT 36(18) 2018, was also not read.
2. **Sinkin et al., JLT 2018 and Bolshtyansky et al., JLT 2020: abstract only.** The power-efficiency metric (capacity per pump power), the optimum-SNR derivation and the pump-sharing architecture details (how many pumps are shared across how many amplifiers, redundancy) are missing. Liang/Downie/Hurley, "Repeater power conversion efficiency...", IEEE Photonics J. 2021, is relevant and was found but not read in full.
3. **Pump-sharing ("pump farming") details** come only from Google's Dunant blog (tier C) and the Papapavlou review. There is no tier-A description of a shared-pump topology with numbers.
4. **Bergano JLT 2005: abstract only.** Pilipetskii and Foursa tutorials (OFC 2015 W3G.5; OFC 2020 M3G.5 "SDM power-efficient...") are not accessible. Section 7.1 architecture facts therefore rest on ITU-T G.977, the Papapavlou review and Desbruslais.
5. **SubOptic 2019 "The subsea fiber as a Shannon channel": abstract only** (the user brief said SubOptic 2013; the paper is SubOptic 2019). No GSNR budget numbers were taken from it.
6. **G.977.1 SNR_TOT / SNR_EXT equations**: the crawler elided the middle terms. Only the GOSNR sum and the droop product rule are recorded. G.977.1 has a single edition (10/2020); I did not check whether a 2024-2026 amendment exists.
7. **Kamalov open-cable JLT / SubOptic GSNR acceptance papers** (e.g. Rivera Hartling et al., "Design, acceptance and capacity of subsea open cables", JLT 2021) were not retrieved. Acceptance-test numbers (measured GSNR in dB per fiber pair for a real open cable) are missing.
8. **TPU primary**: the FCC grant / public notice for GU Holdings (fiber-pair counts, 260 Tb/s, MCF on branches only) was not read. The values come from submarinenetworks.com (tier C). The ready-for-service date is unconfirmed: the FCC filing said May 2025 commercial service, while trade press in May 2026 still said "expected this year".
9. **Anjana / NEC 24 FP**: the FCC application was not read. RFS status as of 2026 was not confirmed.
10. **Hyperscaler share**: the EU Commission-initiated 2025 report (71 % in 2024; 90 % of transatlantic capacity) was seen only via heise (secondary) and was not recorded. ASPI 2024 (10 % to 71 %) was also not read. Caoui & Steck (tier A) is abstract only.
11. **China landing approvals in practice**: no primary source was found on PRC permit delays for SJC2, Apricot or other cables (Reuters/WSJ reporting only), and no MIIT rule on international landing stations (国际通信出入口局) was retrieved. The 1989 State Council regulation and the 1992 SOA measures are recorded, but competent-authority successors (自然资源部 since 2018) are not sourced.
12. **US actions on HMN beyond the 2021 Entity List**: the SEA-ME-WE 6 supplier switch and the US State Department "Clean Cable" statements were not sourced from primary documents.
13. **Repair statistics** (ICPC faults per year, share caused by fishing and anchors) are not sourced. The ICPC site was not read.
14. **Repeater power per unit, optical output (TOP) and NF of deployed repeaters**: no vendor datasheet was found. Model values only: NF 4.5 to 5 dB (Desbruslais, Downie), 12 dBm output (Turukhin, via Perin).
15. **Red Sea Sept 2025 cut**: Microsoft named no cables. SMW4, IMEWE and FALCON identification is press-only and was not recorded.

## Disagreements recorded

- **PFE voltage**: 12 kV "typical rating" (Desbruslais 2015), 12-18 kV with recent 20 kV (Papapavlou Sec. 6), 15-20 kV (same review, Sec. 2), 18 kV largest single-end (Downie 2023), and a 20 kV rating claimed by HMN (Hengtong AR 2025).
- **First 18 kV**: SubCom (Firmina, 2021 press) and Hengtong/HMN ("全球首个...18kV供电方案") both claim it.
- **First 16 FP repeatered system**: H2HE/HMN (review and Hengtong) versus ASN SDM1 framing.
- **Dunant capacity**: 250 Tb/s (Google) versus 300 Tb/s (Papapavlou review).
- **Grace Hopper**: 352 Tb/s (review) versus 350 Tb/s (trade press). Google gave no figure.
- **Optimal fiber-pair count**: ~50 FP minimum cost/bit (Dar 2018) versus 32 fibers (16 FP) as the practical spot (Bolshtyansky 2020). HMN offers 32/48 FP. The incumbent standard is 24 FP (Hengtong citing CAICT).
- **Optimal span**: 8-10 dB at fixed voltage for maximum capacity versus 15.1 dB for minimum voltage at optimum channel power (both Desbruslais); 40-50 km / 8.1-9.75 dB (Perin); 13 dB energy optimum (Doran & Ellis via Desbruslais); 75-100 km repeater spacing (review); "every 100 km" (Google).
- **Red Sea Feb 2024**: four cables (HGC: Seacom, TGN, AAE-1, EIG) versus three (TeleGeography via Bloomberg: TGN-Eurasia is Seacom).
- **GSNR definition**: the G.977.1 GSNR includes GAWBS, while the notation.yaml GSNR is ASE + NLI only. The prose must state which one is meant.

## Notation proposals (not written; for the orchestrator)

V (PFE/feed voltage), ρ (cable resistance per km), I (line current), R_c (total cable resistance), n_r (repeaters), P_r (electrical power per repeater), P_0 (overhead power), η_EO or η_c (E-O efficiency; avoid bare η, which is the NLI efficiency), S (spatial channels per direction), n_fp (fiber pairs), Γ (coding gap), PCE.
