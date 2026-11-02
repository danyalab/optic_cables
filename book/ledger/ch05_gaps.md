# Ch05 (Data center fabrics): gaps and source disagreements (retrieval agent ch05)

Retrieved 2026-11-02. 129 records, 14 equations, 52 new sources. Two sources are reused from `sources/ch04.yaml`: `ieee_p8023dj_objectives_2024` and `nvidia_cpo_blog_2025`.

## Access notes

- Direct HTTPS (curl, WebFetch) to dl.acm.org, conferences.sigcomm.org, research.google, arxiv.org and university hosts is blocked in this session. All text was read through the Exa crawler copies of the URLs listed in the sources file.
- Page numbers are approximate. Locators give section, table and figure numbers instead.
- Several quotes were normalized for crawler line-break hyphenation, for example "over subscription" and "net work". Each such case is noted in the record's `notes`.
- Some records were read only from search-engine excerpts of the full text, not a full fetch. These have `confidence: med`:
  - `ch05.ocs.jupiter_circulator_halving`
  - `ch05.ocs.lightwave_vs_static_cost`
  - `ch05.su.lightpath_32`

## Gaps (needed by the syllabus, not sourced to standard)

1. **IEEE 802.3 normative CR clauses were not read.** The documents not opened are:
   - 802.3ck Clause 162 (100GBASE-CR1)
   - 802.3df 800GBASE-CR8
   - P802.3dj Clause 179 (200GBASE-CR1)

   Copper reach per lane rate is therefore sourced to task-force objectives and contributions, all tier B. The values are 7 m at 10G, 5 m at 25G, 3 m at 50G, 2 m at 100G and 1 m at 200G per lane. No cable insertion-loss budget (dB at Nyquist) for the CR PHYs was recorded. A secondary page cites 17 dB for the cable assembly and 11.5 dB per host for 802.3dj, but it was not traced to an IEEE baseline document. The 802.3df objectives URL returned 404.
2. **Peer-reviewed paper on copper reach limits.** No tier-A paper quantifying twinax loss (dB/m vs frequency) at 53 and 106 GBd was found. The copper limit at 200G/lane rests on IEEE objectives, NVIDIA's FAQ ("under 0.7 m") and Broadcom's white paper.
3. **Jupiter Rising details.** The following were not read:
   - server count (the often-quoted "100,000 servers at 10G")
   - ToR oversubscription
   - fiber or optics counts from Sec. 3.3

   Only Table 2 and the 1.3 Pb/s sentence were captured.
4. **Jupiter Evolving OCS layer numbers.** The following were not captured:
   - number of OCSes per fabric
   - aggregation-block radix
   - CWDM4/8 optics generations (Fig. 3)
   - per-block uplink bandwidth

   The OCS hardware numbers come from Lightwave Fabrics and the Apollo preprint instead.
5. **Palomar OCS switching time.** No direct statement was found in Lightwave Fabrics. The only figure is the Apollo preprint's "commercial OCS 10-20 ms", which describes commercial devices, not Palomar. A secondary wiki says TPU v4 torus reconfiguration takes about 10 s (tier C, not recorded).
6. **Rail-optimized topology definition from NVIDIA.** The DGX SuperPOD reference architecture gives SU layout and cable counts but no formal definition paragraph. NCCL PXN documentation was not read.
7. **Transceiver-per-GPU ratios from a peer-reviewed paper.** None found. Available material:
   - Jensen Huang's "six transceivers per GPU, 180 W, $6000" (tier C, press)
   - SemiAnalysis's argument that the optics-to-GPU ratio does not fall with NVL72 (tier C, paywalled)
   - DGX SuperPOD Table 3, where cables per tier equal the GPU count (tier B). The writer can derive transceiver counts from this table with an explicit ASSUMPTION of 2 transceivers per optical link and twin-port modules.
8. **Optics power and cost share for a 100k-GPU cluster.** No primary source gives the share of cluster power or capex taken by optics for an Ethernet/IB GPU cluster. The only primary share numbers are for Google's OCS/ICI fabric:
   - TPU v4: under 5% of cost, under 3% of power
   - Lightwave: +6% cost, +1% power vs static

   xAI Colossus, Microsoft Fairwater and Meta disclose no optics counts.
9. **Pluggable 800G/1.6T transceiver power from a datasheet.** Only NVIDIA blogs give a figure (about 30 W for 1.6T). The NVIDIA MMS4X00 datasheet is in ch04 (`nvidia_mms4x00_nm_datasheet`) and was not re-read here.
10. **ConnectX-9 / 1.6T NIC.** No datasheet was found. NVIDIA LinkX page lists ConnectX-9 as compatible with CPO but gives no NIC bandwidth.
11. **UALink PHY reach.** The UALink 1.0 evaluation copy was read only for lane rate, station bandwidth and the 1024-accelerator limit. Copper reach and latency targets were not recorded.
12. **Huawei CloudMatrix384 optical module count.** Press accounts report several thousand LPO 400G modules in the UB fabric. This was not found in the arXiv text read here, so it was not recorded.
13. **Tencent Astral 3.0 (星脉3.0).** Abstract only. No numbers on optical shuffle port count, rail count or scale.
14. **Optical scale-up beyond Google.** No production deployment numbers exist outside Google OCS (TPU v4, Ironwood). Other material is proposals:
    - Broadcom CPO BiDi (vendor white paper)
    - HotNets 2024 Lightpath (prototype)
    - Lumorph and Photonic Rails (arXiv, abstract or partial)

    Peer-reviewed results on optical NVLink-class domains (for example Ayar Labs TeraPHY or Celestial AI photonic fabric) were not retrieved.
15. **Meta SIGCOMM 2024 AI Zone numbers.** The fetched text says the cross-zone layer is "oversubscribed by design" but gives no ratio. The 1:7 ratio comes from the Llama 3 paper and Meta SIGCOMM 2026.
16. **Fat-tree bisection-bandwidth formula.** Al-Fares states full bisection (rearrangeably non-blocking) qualitatively. No tier-A source with a closed-form bisection vs. tier count for a general L-tier folded Clos was read (for example Leiserson 1985). The writer must derive it, or the gap stays open.

## Source disagreements (recorded as separate records)

- **Passive copper reach at 200G/lane.** The IEEE P802.3dj objective is at least 1.0 m (`ch05.cu.ieee_200g_lane_cr_1m`). NVIDIA says passive DAC is usable to under 0.7 m at XDR 200G PAM4 and offers no passive XDR DAC (`ch05.cu.nvidia_xdr_dac_lt_0p7m`). The difference reflects host and package loss allocations. Use a contested box.
- **NVL72 copper cable count.**
  - NVIDIA OCP blog: "over 5,000" cables, which it calls "active" in one sentence and "coaxial" in another (`ch05.su.nvl72_copper_cables`).
  - SemiAnalysis: 5,184 "direct drive" cables (`ch05.su.nvl72_5184_cables`, tier C).
  - Jensen Huang's claim that an optical spine would have needed 20 kW is a keynote transcription (tier C).
- **OCS insertion-loss target.** The Apollo preprint (2022) says "ideally below 2dB". Lightwave Fabrics (SIGCOMM 2023) says "ideally below 3dB". Measured Palomar insertion loss is typically below 2 dB.
- **Cost of optical reconfigurability (Google).**
  - TPU v4 (ISCA 2023): OCS plus all optics are under 5% of system cost and under 3% of power. This is a share of total cost.
  - Lightwave Fabrics: the lightwave fabric is +6% cost and +1% power relative to a static optical fabric. This is an increment over a baseline.

  The two numbers are not contradictory, but they are easily conflated.
- **Oversubscription notation.** Al-Fares and Alibaba write host:bisection (5:1, 15:1). Meta writes the inverse (1:7, 1:2.8). Normalize in prose.
- **Vendor AEC power claims.** Credo's SPAN brief says "up to 50% less power than optical". Its SHIFT brief says "up to 75% less". The press release says "up to 14W per link". All are marketing upper bounds.
- **Per-rack vs per-GPU NVLink bandwidth.** Microsoft's Fairwater blog says a 72-GPU rack "delivers 1.8 terabytes of GPU-to-GPU bandwidth". That is NVIDIA's per-GPU figure; the rack aggregate is 130 TB/s. Flagged in `ch05.pw.fairwater_rack_bw_wording`.
- **Huawei CloudMatrix accelerator naming.** arXiv v1 says "Ascend 910", v2 says "Ascend 910C". v2 is used.

## Notation conflicts for the orchestrator

These symbols clash with `notation.yaml`:

- Collective-cost symbols from Thakur et al.: α, β, n, γ clash with attenuation, propagation constant, refractive index and nonlinear coefficient. Equations use α_c, β_c, n_B, γ_c.
- Clos n (ports per edge switch) clashes with refractive index.

Proposed new symbols:

- k: switch radix
- N_host: number of hosts
- σ: oversubscription
- B_bis: bisection bandwidth
- N_OCS: number of OCSes
- B_bus, B_alg: NCCL bus and algorithm bandwidth
