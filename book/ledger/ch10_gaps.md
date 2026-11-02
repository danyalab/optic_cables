# ch10 gaps, disagreements, and proposals (Supply chain and geopolitics)

Retrieved 2026-11-02. Network note: direct curl to federalregister.gov and govinfo.gov was refused by the egress proxy, and WebFetch could not resolve govinfo.gov. All reading went through Exa fetch/search. Full-text extracts were used where Exa returned them. Chinese annual-report tables came from cninfo/SZSE PDF text extraction, where columns are sometimes split. Spot-check those against the PDFs (Eoptolink capacity row; Eoptolink Thailand subsidiary row).

## Reused source ids (not redefined in sources/ch10.yaml)

- `yofc_ar_2025` (ch01_c), `innolight_ar_2025`, `eoptolink_ar_2025`, `accelink_ar_2025`, `hgtech_ar_2025` (ch04), `nvidia_photonics_press_2025`, `nvidia_cpo_blog_2025` (ch04), `bis_entity_list_2021_12_17` (ch07; same document as 86 FR 71557).
- `accelink_ar_2025` in ch04 points to cninfo 1225148212. Our reading used the Sina/hibor full-text mirrors of the same report.

## Unsourced or under-sourced needs

1. **Per-tier market shares and HHI inputs.** No primary (tier A/B) source publishes vendor shares for EMLs, PAM4 DSPs, modules or optical transport. All shares are market research (LightCounting, Omdia, Dell'Oro, Yole, ICC, Cignal AI) and are tier C. This includes the free Dell'Oro release, which gives a ranking but no percentages. A computed HHI per tier can therefore only appear inside a contested box, or be built from filings as revenue-based concentration among *listed* firms (Innolight + Eoptolink + Coherent Networking + Lumentum C&N + Accelink...). That second option is not a market share. **CR_n (n-firm concentration ratio) has no tier-A source in the ledger.** Only HHI is sourced (DOJ/FTC 2023 Guidelines).
2. **Broadcom optical revenue.** The Broadcom 10-K does not break out optical components. Only facility facts are recorded (InP wafers sole-sourced at Breinigsville; III-V fabs in US and Singapore). Broadcom DSP (Sian) revenue is also not disclosed.
3. **Lumentum C&N value from the 10-K itself.** The 1,410.8 MUSD figure comes from the earnings release (8-K exhibit). The 10-K MD&A table was not captured verbatim. A secondary summary gives a +325.9 MUSD C&N increase, which is consistent.
4. **Huawei optical / HiSilicon.** Huawei does not disclose optical transport revenue or HiSilicon DSP/laser output. No primary statement was found on Huawei in-house PAM4 or coherent DSP or EML supply. The 2025 annual report only mentions 800G and OXC solutions. HiSilicon's internal capability claims in the press were not recorded.
5. **Domestic PAM4 DSP.** Only tier-C items were found: 橙科微 interview, planned 400G/800G PAM4 DSP mass production in 2025. No confirmation of mass production, no filing. 达发科技 (Airoha, Taiwan) 400G DSP is in news only. No primary source was found for ZTE Microelectronics or HiSilicon datacom PAM4 DSP. 盛科 (Centec) makes Ethernet switch silicon, not optical DSP, so it is not relevant to 10.3.
6. **Yuanjie 招股说明书 (2022 STAR IPO prospectus).** Not read. The 2025 annual report and the 2026 HK listing document were used instead. Rates and products are covered.
7. **Accelink EML volumes / in-house chip ratio.** These are not disclosed. Only a capability statement is recorded. The **华工正源** chip ratio is likewise only an IR claim.
8. **长光华芯 (Everbright Photonics) 100G EML mass production.** Only a press report (STCN) was found. Check its 2025 annual report.
9. **Mitsubishi Electric EML capacity numbers.** The company web page says capacity will more than triple from FY2026 to FY2030. The trade press says 3x from FY2024 to FY2028, with 1.5x by FY2026 and 2x by FY2028. The Integrated Report / securities report wording was not captured. Recorded as disagreement.
10. **Sumitomo Electric capacity multiples.** The 2025 "Growth strategy for data center-related business" deck shows InP substrate and intra-DC optical device capacity multiples (2.4x, 12x, 4x, 2x, 1.4x across 2023-2028). Text extraction could not attach the numbers to their bars, so no record was made. Read the PDF figure directly.
11. **InP substrate market structure.** The main suppliers are Sumitomo Electric, AXT/Tongmei and JX Metals. There is no primary share data. JX Metals' roughly 20% capacity increase appears only in trade press (sangyo-times) and was not recorded.
12. **Primary texts not retrieved:**
   - MOFCOM 2025 Nos. 55-58, 61 and 62 (Oct 2025 rare-earth, extraterritorial and technology measures). Only their suspension (No. 70) was read.
   - US Supreme Court IEEPA tariff decision (20 Feb 2026) and the CBP termination notice. These are known only via the AXT 10-K.
   - The formal BIS FR rescission of the AI Diffusion rule. Only the press release was read.
   - The FR page citation of BIS doc 2025-02655.
   - The SME IFR 88 FR 73424 (Oct 2023), cited but not read.
   - USTR List 4A notice for HTS 8517.62.00. The 7.5% rate comes from a CBP ruling mirror.
   - Laser diodes (HTS 8541.41): coverage under Section 301 lists was not checked.
   - IEEPA "fentanyl"/"reciprocal" tariff executive orders and the Nov 2025 US-China arrangement.
13. **Entity List checks.**
   - **No evidence** was found that YOFC, Accelink, Innolight, Eoptolink, HGTECH or Yuanjie are on the BIS Entity List. The Dec 2024 list of 140 entities was not checked line by line.
   - Innolight is on the **DoD 1260H list** (June 2026), which is not an export control.
   - FiberHome Technologies Group has been listed since June 2020 (Xinjiang basis). Its aliases include FiberHome Telecommunication Technologies Co., Ltd.
   - Hengtong Optic-Electric, Hengtong Marine, ZTT Submarine and HMN International have been listed since Dec 2021.
   - Whether Accelink (a FiberHome/CICT group company) would be captured by the 50% Affiliates rule depends on ownership. The rule is stayed until 9 Nov 2026. Not verified.
14. **Affiliates-rule stay ends 9 Nov 2026 and MOFCOM No. 72 ends 27 Nov 2026,** both just after the retrieval date. Re-check before the chapter is finalized.
15. **Thai and Malaysian footprint.** Eoptolink's annual report mentions China and Thailand only. **No Malaysia plant statement was found in the Eoptolink 2025 report**, so the task premise "Eoptolink Thailand/Malaysia" is unverified. The Innolight Thailand plant start year was not cleanly extracted. The ESG timeline shows "泰国生产基地正式投产" but the extracted year ordering was scrambled.
16. **Cisco/Acacia.** No Cisco 10-K optical (Acacia) revenue statement was retrieved. Cisco does not appear to break it out. Only the Dell'Oro ranking (tier C) places Cisco fifth.

## Disagreements recorded

- China ≥25G optical (laser) chip localization: 4% (中商产业研究院 via Kaiyuan broker report) vs 41% in 2025 (EET-China blog, unsourced). Both are tier C.
- China share of ≥25G optical electrical chips: 7% (ICC 2025 forecast) vs about 8% for ≥25G TIAs (ICC) vs <5% in 2023 (ICC). The scopes and years differ.
- Mitsubishi EML capacity plan: different baselines in the company web page and the trade press.
- NVIDIA CPO efficiency: 3.5x (Mar 2025 press release, Aug 2025 blog) vs 5x (later product page, ch04 `nvidia_siph_page_2026`). Quantum-X availability moved from "later this year" (2025) to "early 2026".
- Broadcom TH6-Davisson release says both "now shipping" and "currently sampling".
- Yuanjie (domestic supplier, tier B) says "数据中心市场仍以海外供应商为主" (the data center market is still dominated by overseas suppliers), and its 200G EML is only in customer validation. HGTECH says its high-end optical chips reach in-house scale production in 2026. 长光华芯 (press) says its 100G EML is shipping in volume. This is the core of the 10.7 contested box on the self-sufficiency timeline.

## Notation proposals (for book/notation/ch10_proposals.yaml; not written, outside allowed files)

- `\mathrm{HHI}`: Herfindahl-Hirschman index, shares in percent, unit 1, first_defined 10.1
- `s_i`: market share of firm i (percent), first_defined 10.1. Check for a clash with existing `s`.
- `N`: number of firms in a supply-chain tier, first_defined 10.1. Check for a clash.
- `\mathrm{TPP}`, `\mathrm{MacTOPS}`, `b_{\mathrm{op}}`, `\mathrm{PD}`, `A_{\mathrm{die}}`: BIS 3A090 metrics, first_defined 10.6

## Glossary candidates (Chinese at first use)

出口管制 (export control); 两用物项 (dual-use items); 实体清单 (Entity List); 国产化率 (localization rate); 磷化铟 (indium phosphide); 电吸收调制激光器 EML; 光芯片 / 电芯片 (optical / electrical chips); 共封装光学 CPO (光电共封装).

## Format notes for the orchestrator

- The ledger contains one `language: ja` source (`sangyo_times_2025_09_optical`). The schema lists only en|zh.
- Several value fields are strings for dates or names (kind: fact). Ranges use [lo, hi], or pairs as noted in conditions.
