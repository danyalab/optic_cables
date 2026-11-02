# Ledger, source, and equation schemas

Every number that appears in the book must trace to one ledger record, or be computed by a script in `book/calc/` from ledger records. The writer may not assert anything that is not here.

## Ledger record (`book/ledger/chNN*.yaml`)

```yaml
records:
  - id: ch01.att.g652d_max_1550       # ch<NN>.<topic>.<slug>, unique, lowercase, [a-z0-9_.]
    section: "1.1"                     # syllabus section id
    claim: "Maximum cabled attenuation coefficient of G.652.D fiber at 1550 nm"
    value: 0.3                         # number, or [lo, hi] for a range, or a string only for non-numeric facts
    unit: "dB/km"                      # SI or field-standard unit; "1" for dimensionless
    kind: spec_max                     # spec_max | spec_min | spec_typ | measured | record | constant | model_param | fact
    conditions:                        # everything needed to interpret the number
      wavelength_nm: 1550
      fiber: "G.652.D"
      note: "cabled fiber, table attribute"
    source_id: itu_t_g652_2016         # key into book/sources/chNN*.yaml
    locator: "Table 2, row 'Attenuation coefficient', p. 9"   # page / table / figure / equation number
    quote: "verbatim excerpt, at most 25 words, from the source text that contains the value"
    retrieved: 2026-11-02
    tier: A                            # see tiers below
    confidence: high                   # high: read in full text; med: abstract/figure readout/datasheet; low: indirect
    notes: ""                          # optional: caveats, disagreements between sources, digitized-from-figure, etc.
```

## Source record (`book/sources/chNN*.yaml`)

```yaml
sources:
  - id: itu_t_g652_2016
    type: standard                     # standard | journal | conference | datasheet | whitepaper | book | thesis | press | report
    title: "Characteristics of a single-mode optical fibre and cable"
    authors: "ITU-T Study Group 15"
    venue: "ITU-T Recommendation G.652"
    year: 2016
    doi: ""                            # if any
    url: "https://www.itu.int/rec/T-REC-G.652"
    access: open                       # open | paywalled | abstract_only
    language: en                       # en | zh
    tier: A
    retrieved: 2026-11-02
```

## Equation record (`book/ledger/chNN*_equations.yaml`)

```yaml
equations:
  - id: ch01.eq.gn_popt
    section: "1.6"
    latex: "P_{\\mathrm{opt}} = \\left(\\frac{P_{\\mathrm{ASE}}}{2\\eta}\\right)^{1/3}"
    symbols: ["P_{\\mathrm{ASE}}", "\\eta"]   # must match book/notation.yaml where possible
    source_id: poggiolini_jlt_2012
    locator: "Eq. (13)"
    notes: "source uses different symbols: ... (map them here)"
```

## Tiers

- **A**: peer-reviewed journal or conference paper (JLT, OE, PTL, Nature Photonics, OFC, ECOC), ITU-T/IEEE/OIF standard, textbook, CODATA constant.
- **B**: vendor datasheet or application note, operator or CAICT white paper, company annual report.
- **C**: news, press release, market research, blog, Wikipedia. Allowed in the ledger only to record a claim that is itself the subject of discussion (e.g. a press-release record claim in a "contested" box), with `confidence: low`. Never the sole support for a technical value in prose.

## Hard rules for retrieval agents

1. A value must be read from the source document itself (full text, datasheet, or at minimum the abstract). Never from memory, never from a secondary summary. If you could only see the abstract, set `confidence: med` and `access: abstract_only`.
2. The quote must be verbatim and must contain the value or the sentence that states it.
3. If two primary sources disagree, record both as separate records and note the disagreement.
4. If you cannot find a primary source for something the syllabus needs, do not invent a record; list it in the gaps file instead.
