# Ch08 US network architecture: gaps and source disagreements (retrieval agent ch08)

Retrieved 2026-11-02. Ledger: `ch08.yaml` (137 records), `ch08_equations.yaml` (6 equations), `sources/ch08.yaml` (41 new sources).

## Access notes

- Direct HTTPS to `cseweb.ucsd.edu`, `arxiv.org` and similar hosts is blocked by the session proxy. Every paper was read through the Exa crawler's copy of the PDF named in the source `url`. The crawler drops typographic ligatures ("e ciency", "tra c", "ese") and breaks some words across lines ("cen ters", "dif ference"). Quotes keep the extracted text. Page numbers were not recoverable, so locators give section, figure and table.
- Source ids reused from other chapters (not redefined here): `llama3_arxiv_2024` (ch05), `msft_blog_2025_11_fairwater_atlanta` (ch05), `durairajan_sigcomm_2015` (ch09), `lumen_10k_2025` (ch09). The ch09 InterTubes entry points to the sigcomm.org PDF. I read the author-hosted copy (pages.cs.wisc.edu/~pb/tubes_final.pdf), which has the same paper and DOI.
- Shared scratchpad: other chapter agents write into the same scratchpad directory. My working files live in `scratchpad/ch08_work/`. An earlier generator file of mine in `scratchpad/gen/` was overwritten by another agent, and I regenerated it.

## Gaps (needed by the syllabus, not sourced to standard)

1. **AT&T and Verizon long-haul route miles.** Neither FY2025 10-K gives an intercity or long-haul route-mile figure. Their fiber metrics are FTTH locations and customers. The 8.1 carrier comparison is therefore Lumen (tier B, 10-K) against Zayo (tier C, press releases only, because Zayo has been private since 2020). The only pre-2016 cross-carrier view is InterTubes Table 1 (nodes and links per ISP map). An older AT&T or Verizon 10-K, or an FCC filing, might give route miles. I did not search for them.
2. **Zayo total route miles.** Zayo gives fiber miles (16.5 or 16.6 million) but no total route-mile figure in the releases I read.
3. **Lumen PCF aggregate in a tier-B filing.** The $8.5 billion figure comes only from an 8-K press exhibit (tier C) and Lightwave. The FY2025 10-K text I fetched discusses PCF but gives no aggregate dollar value. The FY2024 10-K was not checked.
4. **Meta Express Backbone 2017 engineering blog** (engineering.fb.com) could not be fetched (SOURCE_NOT_AVAILABLE). EBB facts are sourced to the peer-reviewed SIGCOMM 2023 paper instead (Denis et al.), which is better. I recorded no capacity (Tb/s) for EBB because none was found in the extracted text.
5. **Google B2/B4 optical layer.** No Google peer-reviewed paper gives B4's DWDM line-system details (spectrum, C+L deployment, margins). The closest source is Zhao et al. (IEEE Commun. Mag. 2013): 12 Tb/s per fiber pair, C+L doubles capacity. B4 papers treat links as IP capacity only. Not retrieved: the "Evolve or Die" SIGCOMM 2016 paper and Google's 2023+ optical blog posts.
6. **Filer et al. JOCN 2019 (Microsoft low-margin).** Abstract only, because the paper is paywalled. The SNR margin distributions, Q-margin targets and line-system counts inside it are not recorded. Filer et al., "Elastic optical networking in the Microsoft cloud" (JOCN 2016), was not retrieved either.
7. **"Iris" title check.** The Microsoft paper is **Dukic et al., "Beyond the mega-data center: networking multi-data center regions", SIGCOMM 2020**. Iris is the architecture's name, not the paper title. No paper titled "Iris: Optical Fabrics for Datacenter Interconnect" was found. Google's "Jupiter Evolving" (SIGCOMM 2022) covers intra-DC OCS, not WAN, and was not retrieved.
8. **SWAN LP link constraint.** The Figure 6 extraction was garbled. The capacity constraint in `ch08.eq.swan_mcf` is reconstructed from the figure structure and must be checked against the PDF.
9. **RADWAN SNR thresholds for 150/175/200 Gb/s.** These appear only as dashed lines in Fig. 1 and were not digitized. Recorded thresholds: 6.5 dB (100G), 3 dB (enough for 50G), and an illustrative 10.2 dB (150G possible).
10. **NYIIX traffic statistics** were not retrieved. No primary US IXP traffic figures from Equinix Internet Exchange were found either: the 10-K gives interconnection counts, not IX peak traffic.
11. **DE-CIX Annual Report 2025** lists US peaks (1.93 and 1.75 Tbit/s, among others), but the extracted table does not map numbers to cities unambiguously. Not recorded. The NY peak is recorded from 2024 news posts (1.68 and 1.77 Tb/s).
12. **Peering vs transit economics after 2015.** Norton's series ends in 2015 (and the 2015 value is a projection). No academic source with current US transit prices was found. Valancius et al. (SIGCOMM 2011, "How many tiers?") is a candidate that was not retrieved.
13. **Multi-datacenter training bandwidth.** No primary source gives inter-campus Tb/s or latency for Gemini, OpenAI or Microsoft Fairwater training. Gemini 1.0 says only "multiple datacenters". Microsoft discloses fiber miles but not capacity. Not retrieved: OpenAI/Stargate statements, Gemini 2.x reports, and Meta Llama 4 or Prometheus multi-building statements. Any 8.5 bandwidth estimate must therefore come from a model (`calc/ch08`) using DiLoCo or data-parallel all-reduce volumes, with explicit ASSUMPTIONs.
14. **Notation.** The equations introduce new symbols (T_be, C_peer, p_tr, a, b_{i,j}, d_i, c_l, p_l, f_l, BR). Two clash with `notation.yaml`: the B4 capacity C_i clashes with Shannon capacity C, and the RADWAN churn weight λ clashes with wavelength. The notes give suggested renames. No proposals file was written, per the task scope.

## Source disagreements (recorded as separate records)

- **RADWAN dataset size:** 8,000 links in the published paper (`ch08.radwan.links_analyzed`) against 2,000 links in the March 2018 preprint (`ch08.radwan.links_analyzed_preprint`). Use the published value.
- **Zayo fiber miles (same 21 Jan 2025 release, two copies):** zayo.com says 16.6 M fiber miles with 820,000 added in 2024. Business Wire says 16.5 M with 700,000 added.
- **Zayo Chicago-Minneapolis route length:** 521 mi in the press release against 505 mi in the company blog, both dated 15 Jul 2025.
- **One Wilshire network count:** CoreSite 2025 says more than 300 networks. The building owner page (undated) says over 250 NSPs.
- **60 Hudson carrier count:** Hudson IX says 300+ carriers and exchanges. The building owner says "more than 100" telecom companies in the meet-me room, and elsewhere on the same page "several hundred" providers.
- **Microsoft AI WAN fiber:** Guthrie's blog says "over 120,000 new fiber miles across the US last year". Microsoft Source says "deployed 120,000 miles of dedicated fiber ... increasing its overall mileage by more than 25% in one year". SDxCentral misreads this as a total of about 120,000 miles. Microsoft also does not say whether these are route or fiber miles in the Source text.
- **Lumen ILA sites:** 176 under construction (Sept 2025 press release) against 119 being built (Q2 2025, via Lightwave). These are different dates.
- **Lumen PCF book:** $8.5 B (May 2025 8-K exhibit) against "just under $9 billion" (Q2 2025 call). The second is an update, not a contradiction.
- **Norton transit series:** the 2001 decline is 40% in the 2010 white paper and 41% in the Playbook. The prices are identical.
- **Growth rates:** Zhao 2013 cites 50-60%/yr Internet growth. B4 inter-DC demand doubled every 9 months, which is about 152%/yr. These measure different traffic (public Internet against private inter-DC), and the book should say so.
