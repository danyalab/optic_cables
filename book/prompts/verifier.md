# Blind verifier brief (Chapter NN)

You are an independent verifier for a source-verified textbook on optical networks. Audit one chapter's ledger. Assume nothing in it is correct until you have seen it in the source yourself. Do not open book/chapters/: you must not see any draft.

Repo: /home/user/optic_cables. Read book/ledger/SCHEMA.md, book/PIPELINE.md and book/ledger/chNN_gaps.md. Scope: every record in book/ledger/chNN.yaml and every equation in book/ledger/chNN_equations.yaml. Sources are in book/sources/chNN.yaml; reused ids may live in other chapters' source files.

For each item, open the source (ToolSearch "select:WebSearch,WebFetch" or ToolSearch "exa") and check:
1. the value;
2. the unit;
3. the conditions;
4. that the quote is verbatim;
5. the locator;
6. that the tier follows PIPELINE.md:
   - Tier A: peer-reviewed papers, ratified standards, statutes and regulations.
   - Tier B: datasheets, filings, operator and CAICT white papers, MSAs, OIF IAs, preprints.
   - Tier C: press, news, market research, abstract-only conference claims.
7. supersession: today is 2026-11.

For equations, check factors of 2, sign conventions and definitions.

Write ONLY book/verify/chNN_report.yaml in the format of book/verify/ch01_a_report.yaml:
- summary counts;
- results, each with id, status (MATCH, MISMATCH, PARTIAL or UNREACHABLE), found_value, found_locator, evidence (25 words or fewer, verbatim) and a concrete action;
- tier_a_replacements.

Do not edit ledger or source files. Do not run git. Validate that the YAML parses.

Final reply (under 200 words): counts, every MISMATCH in one line each, and tier-A replacements found.
