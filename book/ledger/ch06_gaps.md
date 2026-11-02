# ch06 gaps, disagreements, and proposals (sections 6.1-6.6)

Retrieval date 2026-11-02. Network note: direct curl and WebFetch to oiforum.com (and most publisher hosts) were refused by the session proxy; all reading was through Exa search highlights and Exa fetch. Abstract-only items are marked `confidence: med`, `access: abstract_only`. Counts: 85 ledger records, 14 equations, 60 new sources (plus reused ids `oif_400zr_01_2020`, `oif_400zr_03_2024` and `openroadm_msa6_wport_2023` from ch02, `oif_800zr_ia_2024` and `oif_ia_list_2026` from ch04, and `zuo_ecoc_2023_2502km` from ch09).

Chapter 1 material is referenced, not duplicated: GN model and NLI (`ch01.eq.gn_*`, `ch01.gn.*`), ASE and OSNR (`ch01.eq.ase_*`, `ch01.eq.osnr_*`), GNPy accuracy from Ferrari JOCN 2020 (`ch01.gnpy.gsnr_accuracy`, `ch01.gnpy.popt_accuracy`), G.654.E fibre attributes (`ch01.att.g654e_*`, `ch01.kerr.aeff_g654e_typ`, `ch01.fact.zte_g654e_a130_backbone`, `ch01.att.zte_g654e_vs_g652d_80km`), and C/L band edges (`ch01.amp.cband_range_itu`, `ch01.amp.lband_range_itu`).

## Unsourced or under-sourced needs

1. **Per-ROADM filtering penalty from a peer-reviewed full text.** The only numbers per cascade length are (a) the 24-ROADM penalties of 1.6 dB (R&S) and about 1 dB (B&S), read only as a secondary citation in a Queen's MSc thesis (`ch06.wss.cascade_bw_narrowing_24roadm`, tier B, low), and (b) abstract-level results from Pan & Tibuleac JPhot 2017 and Rahman PTL 2014. Still needed: Gringeri et al., ECOC 2010 ("127-Gb/s PM-QPSK over 1000 km NDSF with >10 cascaded 50 GHz ROADMs"), Filer & Tibuleac JLT 28(4) 2010 (full text), Hsueh et al. JLT 2012, and a 2020s result at 64-130 GBd. Then the textbook can quote "dB per pass" from a primary source.
2. **Pulikkaseril et al., Opt. Express 19(9) 8458 (2011)** could not be fetched. The erf passband equation (`ch06.eq.wss_passband`) and BW_OTF = 10.4 GHz come from a Politecnico di Torino MSc thesis (tier B). Rizzelli JLT 2025 (tier A, open access) confirms the model and gives the BW_OTF to super-Gaussian mapping. Read the OE paper (open access on Optica) to confirm the equation number, the normalisation and the typical BW_OTF (often quoted as 8-11 GHz).
3. **Superchannel spectral efficiency, beyond Gerstel 2012 Table 1.** No source states the commercial C-band channel count directly (e.g. 96 x 50 GHz, 64 x 75 GHz, 32 x 150 GHz). These are derived from the 4.8 THz range (400ZR, Finisar WSS) and the OIF channel plans, so a calc script should derive them. A tier-A source on guard-band overheads for Nyquist superchannels (e.g. Chandrasekhar & Liu, or Infinera ICE superchannel papers) was not retrieved.
4. **OIF 400ZR channel tables.** The 191.4-196.1 THz (48 x 100 GHz) and 191.375-196.1 THz (64 x 75 GHz) tables were seen only in a vendor datasheet that reproduces them. The IA PDF (sections 15.1-15.2) needs to be read for direct records. The 400ZR ROSNR (26 dB) is from an OFC 2023 OIF slide, not the IA table.
5. **OIF-1600ZR-01.0 (September 2026)** is listed on the OIF site, but its baud rate, reach and modulation were not read. **OpenZR+ MSA** (ZR400-OFEC-16QAM) specs were seen only via an analyst report; the MSA spec itself is needed.
6. **Coherent vendor datasheets.** Ciena WL6e (200 GBd, 1.6T, 3 nm) and Nokia PSE-6s (130+ GBd, 1.2T, 5 nm) have tier-B pages. **Infinera ICE7** has no datasheet: 148 GBd comes from trade press and "140+ GBaud" from a press release (both tier C). Nokia absorbed Infinera in 2025, and the old datasheets may be offline. No peer-reviewed field trial at 200 GBd / 1.6T was found; only operator press releases (AT&T 296 km, Arelion 470 km, Verizon 118 km with 9 ROADMs). The lab state of the art is Mardoyan ECOC 2024 (300 GBd optical slicing, tier A).
7. **G.654.E figure of merit (FOM) equation.** Corning's Chinese article (Makovejs et al.) contains a FOM formula with A_eff, n2, attenuation, L_eff and D terms weighted 2/3 and 1/3. The PDF text extraction was too garbled to transcribe, so no equation record was made. Read the PDF or an English peer-reviewed version (Makovejs et al. or Downie et al., OFC/ECOC 2016-2018, "Fiber figure of merit") and add `ch06.eq.g654e_fom`.
8. **G.654.E total deployed length in China.** Only tender volumes (China Mobile 2134, 8463 and 22,900 cable-km in 2022, 2023-24 and 2025-27; China Telecom about 3621 cable-km in 2022; China Unicom 4.365 M fiber-km in 2024) and a 2024 "58,000 cable-km built by three operators" figure (not clearly all G.654.E) are recorded. No CAICT or operator statement of cumulative installed G.654.E km was found. The 2025 《G.654.E光纤技术应用报告》 (three operators, State Grid, YOFC, May 2025) probably contains it but was not located online. The China Telecom 2022 tender figure (3621 cable-km, 0.61 M fiber-km) appears only in a C114 secondary article and was not recorded.
9. **G.654.E terrestrial system-gain studies, peer-reviewed full text.** Downie SPIE 2018 (at least 55% reach) and Shen et al. (China Unicom) OFC 2017 were read as abstracts only. The China Telecom "+3.5 dB OSNR" is from a SASAC republication (tier B). Wang et al. ICICN 2024 (C4.8T+L4.8T, G.654.E vs G.652.D, China Unicom) was seen as an abstract only, with no numbers.
10. **Raman gain coefficient, tier-A full text.** Bromage JLT 2004 is paywalled. The SSMF peak gain efficiency 0.4 /(W km) comes from Kjaer's DTU PhD thesis (tier B); peak g_R = 5.4e-14 m/W comes from Andre et al. Optica Applicata 2003 (OCR text). Stolen & Ippen APL 1973 / Agrawal *Nonlinear Fiber Optics* (g_R ~ 1e-13 m/W at 1 um) were not retrieved. No Raman on-off gain equation was recorded, because the Andre Eq. (21) OCR was ambiguous about the polarization factor.
11. **Christodoulides & Jander PTL 1996** (original SRS tilt formula) was not retrieved. The tilt equation is recorded from Semrau JLT 2019 Eq. (3), which cites Semrau OE 2017.
12. **S-band TDFA performance (gain, NF) and a commercial S+C+L system** were not sourced. Only the NICT press release (tier C) says TDFAs were used for S-band in the 402 Tb/s experiment. The 402 Tb/s paper itself is abstract-only.
13. **Open line systems (OLS).** No tier-A definition or deployment-scale paper on OLS (e.g. Microsoft/Facebook OLS papers, TIP OOPT) was recorded. OpenROADM facts are recorded instead. Filer et al. JLT 2018 covers the Microsoft OLS testbed in an abstract only.
14. **Margins in operator practice.** Pointurier JOCN 2017 (full text) gives typical values. No operator document (e.g. China Mobile/Telecom design rule "OSNR margin x dB" or Telcordia) was found. The Chinese articles refer to "标准OSNR余量" (standard OSNR margin) without a number. Search CCSA YD/T 5092 / YD/T 1960 for the Chinese engineering OSNR margin.
15. **GNPy accuracy beyond C-band** (GNPy with ISRS / C+L validation, e.g. Ferrari or D'Amico JOCN 2022) was not retrieved.
16. **Year/venue checks:** `zuo_ecoc_2023_2502km` venue (reused from ch09) was inferred from the copyright line "©2023"; `makovejs_corning_cn_g654e` year (2018) is approximate; `acg_cisco_wp_400g_ip_transport` year (2020) is approximate; `polito_thesis_2018_scm_filtering` author name was not captured.

## Disagreements and contested items (each side recorded separately)

### (a) IP-over-DWDM economics
- **Pro (vendor/analyst, tier C):** ACG for Cisco claims 46% TCO, 35% CapEx and 57% OpEx savings (`ch06.ipodwdm.acg_tco_46pct`). Heavy Reading (Juniper-sponsored) relays Arelion's reported 64% CapEx and 76% OpEx savings (`ch06.ipodwdm.arelion_capex64`).
- **Skeptical / conditional (tier A):** BT (Davey JOCN 2023) finds hop-by-hop ZR cheapest at low traffic, but "optical express" via ROADMs becomes cheaper as traffic grows from 28 to 220 Tb/s (`ch06.ipodwdm.davey_express_cheaper`). Gumaste JOCN 2022 finds that flexponders need 75% and 51% fewer transceivers than ZR+ designs (`ch06.ipodwdm.gumaste_transceiver_count`).

### (b) "200 GBd / 1.6T per wave" is not industry-wide
The task brief groups WL6e, PSE-6s and ICE7 as about 200 GBd / 1.6 Tb/s. The sources disagree: only Ciena WL6e is 200 GBd / 1.6T (3 nm). Nokia PSE-6s is 130+ GBd / 1.2T (5 nm), and Infinera ICE7 is 140-148 GBd / 1.2T (5 nm). The prose must not generalise.

### (c) 400ZR symbol rate
The IA gives 59.84375 GBd (`ch06.zr.oif400zr_baud`). An OIF OFC 2023 slide gives 59.87 GBd (`ch06.zr.400zr_vs_800zr_baud`). Use the IA value.

### (d) G.654.E in China: how much, and does the 400G backbone need it?
- **Pro:** China Unicom (Wang Guangquan) calls G.654.E "the first choice for 400G backbone", with 800G reach of 1100 km vs 600 km on G.652.D. China Telecom reports +3.5 dB OSNR in a live comparison. China Mobile's 2016 trial claims -20% system build cost. China Mobile's tenders grew 10x from 2022 to 2025-27.
- **Counter:** China Mobile (Zhang Dechao, 2025) says its 400G backbone "mostly chose G.652.D, with some G.654.E", relying on 130 GBd QPSK + C6T/L6T instead (`ch06.coh.cmcc_400g_130gbd_qpsk`). The 2502 km C6T+L6T 400G field trial was on G.652.D. Unicom says G.654.E raises total build cost by 10-20%.
- **Inconsistent numbers:** the Shanghai-Guangzhou route is 1970 km (SASAC, completed route) vs 2029 km of new cable (2019 tender). The State Grid unrepeated span is 467 km (CWW) vs 460 km (eefocus repost).
- **Vendor-reported reach gains:** Corning +55% (SPIE abstract), +60% (Chinese article) and +60-100% (Optical Connections). FOM gains are 2.2-3.2 dB, depending on the reference fibre and span length.

### (e) 402 Tb/s amplifier count
The Optica abstract says "6 doped-fiber amplifier variants", while the Aston repository abstract says "5".

### (f) Raman gain slope
Andre et al. say their measured local Raman gain slope is 49.6% higher than an earlier SRS-tilt-based value for SMF; the window matters. C_r = 0.028 /(W km THz) (Semrau JOCN 2020) is a regression over 0-14 THz and should be used for the tilt formula.

### (g) C+L total bandwidth
"About 10 THz" for full C+L (Semrau 2018, conventional C4.8T+L4.8T = 9.6 THz in Chinese trials) vs "12 THz" for super C+L (C6T+L6T, China Mobile; Jiang et al. 2024 says 20-30% more than earlier C+L). Specify which in prose.

## Notation proposals (orchestrator to merge into notation.yaml)
- `f_c` slot nominal central frequency (THz), first_defined 6.1; `\Delta f_{\mathrm{slot}}` slot width (GHz), 6.1. The flexgrid integer `m` collides with the PCS bits-per-symbol `m` in `ch06.eq.net_rate_pcs`; suggest `m_c` for the latter.
- `B_{\mathrm{tot}}` total WDM bandwidth (THz), 6.3; `P_{\mathrm{tot}}` total launch power (W), 6.3; `C_r` Raman gain slope (1/(W km THz)), 6.3; `\rho(z,f)` normalised signal power profile, 6.3.
- Span loss: notation.yaml uses `L` for length. Suggest `A_{\mathrm{span}}` (linear span loss) instead of Pelouch's `L_span`.
- `\mathrm{BW}_{\mathrm{OTF}}` WSS optical transfer function 3 dB bandwidth (GHz), 6.2; `N_{\mathrm{WSS}}` number of cascaded WSS filters, 6.2.
- Margins `M_U`, `M_S`, `M_D` (dB), 6.6.

## Glossary candidates (with Chinese)
flexible grid / flexgrid (灵活栅格); frequency slot (频隙); superchannel (超级信道); wavelength selective switch, WSS (波长选择开关); colorless-directionless-contentionless, CDC (无色无向无竞争); route-and-select / broadcast-and-select (路由选择 / 广播选择); passband narrowing (通带窄化); inter-channel stimulated Raman scattering, ISRS (信道间受激拉曼散射); distributed Raman amplification (分布式拉曼放大); thulium-doped fibre amplifier, TDFA (掺铥光纤放大器); IP over DWDM (IP over DWDM / 光电协同); open line system (开放光线路系统); unallocated / system / design margin (未分配 / 系统 / 设计余量); sheath-km (皮长公里) vs fiber-km (芯公里); unregenerated reach (无电中继传输距离).
