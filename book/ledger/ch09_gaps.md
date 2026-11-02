# Chapter 9 retrieval gaps (retrieved 2026-11-02)

Network note: in this session WebFetch and direct curl could not reach gov.cn, miit.gov.cn, or cnnic.net.cn (proxy 403 / DNS). Pages were read through the Exa fetch/search service instead, which returns extracted text. A few tables (MIIT gigabit-city criteria, the China Unicom ESG report) came through with columns out of order. Those records are marked `confidence: med` and need checking against the PDF layout.

## Not found / not sourced (no record made)

1. **China Mobile 400G backbone total route length (km).** No primary source states it, and the task brief's figure could not be confirmed. What we do have: 711 km for the first link (Beijing to Inner Mongolia), 1900+ OTN sets in 135 cities, 11000+ ports, 30 provinces, and a "400,000 km commissioning distance" (C114, a tier-C test-effort metric, not route length). Also missing is a commissioned-link count by hub pair.
2. **Latest international exit bandwidth (国际出口带宽).** The newest official value is Dec 2022 (18,469,972 Mb/s, CNNIC 52nd report). CNNIC 53rd to 57th reports (2024-03 to 2026-02) have no such section. Neither the MIIT bulletin nor the CNNIC 58th (if published) was found with a newer value. Operator-level figures (CMCC 406 Tb/s international transmission, CU 6.7 Tb/s international interconnect) are different metrics.
3. **ChinaNet (163, AS4134) architecture from a tier-A/B Chinese source**, for example the number of core nodes or the 3-centre structure (Beijing, Shanghai, Guangzhou plus 8 core cities). Only tier-C sources were found (Wikipedia zh, a GitHub README). China Telecom 163 backbone capacity was not found either.
4. **China Unicom "A网" (AS9929, CUII) naming from a Unicom primary source.** Unicom Global calls it the "premium bearer network (AS9929)". The labels "A网/工业互联网骨干网" appear only in tier-C sources and in registry names (APNIC: "CHINA UNICOM Industrial Internet Backbone").
5. **CMNet current architecture** (core node count, the "9 core nodes / 22 access nodes" claim, backbone bandwidth "181T"). These appear only in tier-C blogs. China Mobile's own 2025 report gives only inter-provincial transport bandwidth (1,098 Tb/s).
6. **China Broadnet backbone.** No primary source describes CBN's national IP/optical backbone (the 国家文化专网, the "一省一网" integration of cable operators) with numbers. CBN is unlisted, so there is no annual report. The NRTA 2025 bulletin confirms that 一省一网 integration is complete and gives 5G users (近4200万), but nothing on the backbone.
7. **China Telecom 400G QPSK deployment scale** (route km, node count, completion date). CT's 400G is in tier-C news only (800G/400G trials, extended C+L module). CT's 2025 annual report says only "400G 全光省际骨干网发展持续深化" at the industry level.
8. **Peer-reviewed China Telecom 400G long-haul paper.** None was retrieved. Candidates to look for: OFC/ECOC 2024-2025 papers by CT Research Institute (Li Junjie, Huo Xiaoli) on extended C+L ROADM.
9. **The Nature Reviews EE (2026) review by Li et al.** was read only at the abstract/key-points level. Its benchmark table of field trials, which could anchor 9.3, has not been extracted.
10. **US fibre route-km, national total.** None exists from FCC or NTIA. We have InterTubes (2015: 542 conduits, no total km) and Lumen (340,000 route miles, a single carrier, global). FCC National Broadband Map fiber availability by location was not retrieved.
11. **US share of fibre in fixed broadband (OECD).** Only a secondary article (ITPro, 24.5% as of June 2024) was seen. The OECD spreadsheet "Percentage of fibre connections in total broadband" was not fetched, so no record was made.
12. **Matched backbone latency metric.** China's targets (709号: 20 ms one-way within clusters; 1779号 and CMCC: 1/5/20 ms, direction unspecified) and Verizon's (45 ms round-trip SLA, about 33-36 ms measured) are not comparable without a convention. No Chinese operator publishes monthly measured backbone latency.
13. **2025 gigabit-city count as a number.** The 2024 count is 207. For 2025 CNNIC gives only "2/3 of prefecture cities".
14. **The 14th FYP target value for 10G PON ports** (implied to be about 1200万 by "2.6倍"). The 十四五信息通信行业发展规划 text was not retrieved.
15. **MIIT primary table for the trunk 400G port count** (14060 at June 2025). Only Xinhua (tier C) has it.
16. **The MIIT 2025 bulletin interpretation (解读)**, the primary source for 94.4 EFLOPS schedulable compute, 553.4 Mb/s per household and 117.9 per 100 households. These were read second-hand in China Telecom's annual report.
17. **Cross-border terrestrial cables, current status** (count, capacity after 2018). The latest numbers are CAICT (undated, about 2018: 12 countries, 17 crossings, 70 TB+) and ITU 2015 (19 stations, 11 countries, 7.6 Tb/s).
18. **The 2024 national 算力 implementation document.** Only the 2023 1779号 opinions and the 2025 算力互联互通行动计划 were retrieved. Other candidates (2024 数据中心绿色低碳发展专项行动计划 with PUE targets; NDRC 2024 东数西算 progress notes) were not pursued.

## Disagreements recorded (both sides in the ledger)

- **CN2 dual-PoP city count:** 223 (CT Asia Pacific page, about 2019) vs 161 (CT Americas page, 2023). Both are undated marketing pages.
- **China Unicom 10G PON share 2025:** 86% (business section) vs 85% (core-competitiveness section) in the same annual report.
- **东数西算 trunk cables:** 234 (digitalchina.gov.cn, Dec 2025) vs "超过250条" (ncsti, Sept 2025). Both tier C.
- **National compute scale:** MIIT infrastructure-side intelligent compute is 788 EFLOPS FP16 (June 2025) and 1053 EFLOPS FP16 (Sept 2025). CAICT device-side is 962 EFLOPS FP32 total, of which 782 EFLOPS FP32-converted is intelligent (June 2025). The bases differ (in-DC vs shipped devices, FP16 vs FP32), so the values must not be mixed.
- **China Telecom intelligent compute:** 91 EFLOPS (own plus connected, annual report) vs 46 EFLOPS (self-owned, results release).
- **QPSK vs PCS-16QAM back-to-back OSNR:** CMRI 2023 slide gives QPSK 15.8 dB, 1 dB better than PCS. The CMRI 2024 article gives PCS-16QAM at 17.5 dB (a gap of about 1.7 dB, possibly from a different hardware generation).
- **SRS power transfer per 80 km span (C6T+L6T):** the 2024 article says up to 7 dB. The 2023 slide says about 8 dB simulated and +3/-4.3 dB measured (tilt split across band edges).
- **Cross-border cables:** 19 stations / 11 countries (ITU 2015) vs 17 border crossings / 12 countries (CAICT, about 2018). The definitions differ.
- **US fibre passings:** 84.6M unique homes vs 98.3M passings including overlaps (FBA).
- **Unit gloss error:** China Telecom's annual report glosses EFLOPS as "每秒万亿亿次" (1e20), but 1 EFLOPS = 1e18 FLOP/s (百亿亿次). People's Daily and MOFCOM use 百亿亿次.

## Caveats for the writer

- Every 2025 MIIT bulletin value is preliminary (注释1).
- 光缆线路长度 (national, 7499万 km) is cable-route length summed over operators, not fibre-km. China Mobile's 3,691万 km is in 皮长公里 (sheath km).
- FTTH/O 96.8% is a share of **ports**, not subscribers.
- 400G "无中继" in China Mobile documents means no electrical regeneration; optical amplifiers are present.
- 709号 latency targets are explicitly **one-way** (单向). Verizon SLAs are **round-trip**.
- Tier-C records (14 + 2) are for provenance or contested boxes only.
