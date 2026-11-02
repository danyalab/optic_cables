# Ch04 Transceivers, 2016 to 2026: gaps and source disagreements (retrieval agent ch04)

Retrieved 2026-11-02. Direct HTTP fetch was blocked for most hosts (proxy 403, DNS refusals for qsfp-dd.com and osfpmsa.org), so all documents were read through the Exa crawler. Page numbers are often missing; locators give section and table numbers instead. Two source ids were reused from chapter 2: `oif_400zr_01_2020` and `lambda_msa_100g_fr_lr_rev2`. One was reused from chapter 1: `lambda_msa_400g_fr4_r2p0_2018`.

## Gaps (needed by the syllabus, not sourced to standard)

1. **IEEE 802.3 normative PMD tables.** The 802.3bs, cd, cu, ck and df clauses were not read, so per-PMD reach, wavelength, TDECQ and power-budget values from IEEE text are missing. Only the standards' approval dates (from IEEE SA pages) and the P802.3dj objectives are recorded. PMD optical values come from the 100G Lambda MSA and the LPO MSA (tier B). The 802.3df/dj texts are free through IEEE GET but could not be downloaded.
2. **IEEE P802.3dj final approval.** As of 2026-11-02 the project has conditional approval to go to RevCom (6 Oct 2026; 97 % recirculation approval). The IEEE-SA board approval date is not yet known. Re-check in Dec 2026.
3. **OIF CEI-224G IA.** No CEI-224G implementation agreement appears in OIF's published IA list (latest electrical IA: CEI-05.3, July 2025). The CEI-224G-VSR, MR, LR, XSR and Linear projects are still listed as current work. The CEI-112G-VSR 16 dB Nyquist-loss figure is available only from an OIF press release (tier C, not recorded). It should be read from OIF-CEI-05.1 clause 25.
4. **400ZR IA optical tables.** The receiver OSNR tolerance (Table 13.1.3, application code 0x01) and the 0x02 unamplified loss budget were not read from the IA itself. The OSNR of 26 dB comes from a Juniper module spec. The 11 dB unamplified budget is in the OIF press release (not recorded). The IA does not state a power class; the 15 W target is sourced from the OpenZR+ white paper.
5. **800ZR IA expansion table and OSNR.** IA Table 20 (symbol rate) and Table 22 (OSNR) were not read. The 118.2 GBd value comes from a Juniper spec and the ECOC 2024 market-focus slides. The 1600ZR symbol rate was not stated in the text read; about 236 GBd is derived from the 1891.25 Gb/s line rate.
6. **Component-level 1.6T power budget from a tier-A source.** Nagarajan (IEEE 2024, read from an IEEE Xplore excerpt) gives the DSP share as about 50 % and the overhead as 10 to 15 %. The only per-component split (TEC, laser, DSP, TIA, MCU) for 1.6T and 800G is the Chang and Yu IEEE 802.3df pie chart (tier B). Its percentage-to-legend mapping was inferred and must be checked on the slide image. No tier-A driver or TIA wattage was found. The Nagarajan paper's venue (JLT?) and issue are unverified.
7. **LPO measured interoperability data.** No peer-reviewed OFC or ECOC paper with multi-vendor LPO BER statistics or measured module power was retrieved. The DesignCon 2024 paper (Signal Integrity Journal) was seen but not recorded. The LPO MSA interop results are self-reported (tier C), and the LPO MSA 400G-FR4-LPO spec was not read.
8. **Ayar Labs energy efficiency.** No pJ/bit figure is published for the 8 Tb/s TeraPHY; only a relative claim ("4x to 8x") was found. Ayar's own product page is internally inconsistent: it gives "8 Tbps bi-directional" and also "4 Tbps per chiplet" (consistent only if 4 Tb/s is per direction).
9. **CPO shipments in 2026.** Volume shipment status of NVIDIA Quantum-X and Spectrum-X Photonics, and of Broadcom TH6-Davisson CPO, was not verified from primary sources. The Broadcom TH6 102.4T CPO (2025) was not searched.
10. **COBO.** The COBO on-board optics spec (power classes) was not retrieved. COBO appears only as a mention in Minkenberg 2021.
11. **First shipments of 100G/400G/800G.** There are no reliable primary dates for first volume shipments of 400G (around 2019) or 800G (around 2022 to 2023). Only Innolight's 800G launch (4 Dec 2020) and its 1.6T first shipments (Q2 2025, via a news report of an IR record) are recorded. LightCounting and Cignal AI data are paywalled.
12. **Microsoft CPO reliability study.** Not found. The Meta ECOC 2025 paper and a news report of a Meta PECC 2025 talk are recorded.
13. **HG Genuine (华工正源) datasheets.** No product datasheet with W values was found. Only HG Tech annual-report and board-report statements are recorded. The 400k-unit 1.6T order figure appears only in a third-party IR summary and was not recorded.
14. **OSFP power-class table (Rev 5.x Table 15-8)** was not read. The power ceilings come from the Rev 4.0 summary table and the Rev 5.2 revision history.

## Disagreements recorded as separate records

- **802.3df approval date.** The IEEE SA page says 2024-02-15; the task-force page says 16 Feb 2024 (`ch04.std.8023df_approval_sa` / `_tf`).
- **CEI-4.0 date.** The OIF IA list says December 2017; Lightwave says "released in 2018" (noted, not recorded separately).
- **CPO power saving vs pluggables.** Claims range from 65 % (Meta measured, ECOC 2025) to 70 % (Broadcom press 2024). NVIDIA gives 3.5x (2025) in one place and 5x (2026 product page) in another. Evans (JLT 2026) gives 67 % at transceiver level and 36 % at switch level. Baselines differ.
- **LPO power saving.** Estimates are 20 % (Marvell/Patra, via LightCounting), about 40 % (Eoptolink), and 50 % for the module and up to 25 % for the system (Bechtolsheim, OFC 2023).
- **800ZR OSNR.** 27.0 dB/0.1 nm (van den Borne ECOC 2024, the IA-level figure) differs from 26 dB worst-case EOL (Juniper module) and <25.5 dB (O-Net OFC 2026 material, not recorded).
- **"Industry first" claims.** Eoptolink claims first LPO in mass production. Innolight claims first 1.6T DR8 OSFP224 LPO and first 800G. HG Tech claims first 3.2T CPO/NPO. All are self-claims.
- **NVIDIA CPO availability slipped.** In March 2025, Quantum-X was due "later this year" (2025). By August 2025 the dates were early 2026 for Quantum-X and 2H 2026 for Spectrum-X.
- **CPO timing outlook.** Innolight (2025 annual report) is cautious: standards still need time and it treats NPO as the nearer step. HG Tech, citing LightCounting, expects CPO ramp in 2026 to 2027. Minkenberg (2021) says the hurdle is industry inertia, not technology.

## Notes for the writer

- The brief's "Minkenberg, JOCN 2021" is actually published in **IET Optoelectronics** 15(2):77-91, DOI 10.1049/ote2.12020.
- Derived numbers flagged in notes (not to be cited as source values): 14 W/800G = 17.5 pJ/bit; 5.5 W/800G = 6.9 pJ/bit; Evans optics energy 20.6/9.0/5.0 pJ/bit; QSFP-DD Class 8 12 A x 3.3 V of about 40 W; 1600ZR about 236 GBd. Compute these in `book/calc/ch04/`.
- Proposed notation (for `book/notation/ch04_proposals.yaml`, not written by this agent): E_b (energy per bit, pJ/bit), P_mod (module power), R_b (lane bit rate), R_mod (aggregate module rate), N_lambda (lane count), M (modulation levels), n_FEC/k_FEC (code lengths; avoid clash with refractive index n).
