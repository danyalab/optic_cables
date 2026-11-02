# Pipeline instructions for chapter agents

Read with `book/ledger/SCHEMA.md` (record formats) and `book/syllabus.yaml` (scope). Chapter 1 is the reference implementation: `book/chapters/ch01.md`, `book/calc/ch01/`, `book/ledger/ch01_*.yaml`.

## Shared files and concurrency

Several chapter agents run at the same time. To avoid write conflicts:

- Write only files carrying your own chapter number `NN` (e.g. `book/ledger/ch05.yaml`, `book/sources/ch05.yaml`, `book/calc/ch05/`, `book/figs/ch05/`, `book/chapters/ch05*.md`, `book/verify/ch05_report.yaml`).
- Never edit `book/notation.yaml`, `book/glossary.yaml`, `book/syllabus.yaml`, other chapters' files, or `tools/`. Propose additions in your own files instead:
  - new symbols: `book/notation/chNN_proposals.yaml`, same format as `notation.yaml` entries;
  - new glossary terms: `book/glossary/chNN_proposals.yaml`, same format as `glossary.yaml` entries.
  The orchestrator merges these and resolves conflicts.
- Source ids are global. Before creating a source, search `book/sources/*.yaml` for the same DOI or URL and reuse the existing id. For a new source, prefix nothing; use a descriptive id (`firstauthor_venue_year`).
- Do not run git.

## Retrieval rules (summary of SCHEMA.md)

- Values are read from the document itself, with a verbatim quote (25 words or fewer) and a locator.
- Tier A: peer-reviewed papers, standards (ITU-T, IEEE, OIF, IEC, MSA specifications count as B unless ratified by a standards body), textbooks, government statutes and regulations (Federal Register, MOFCOM announcements, NDRC notices). Tier B: datasheets, company annual reports and 10-K filings, operator/CAICT white papers, unrefereed preprints. Tier C: press releases, news, market research, abstract-only conference claims, Wikipedia. Tier C is recorded only for claims that are themselves the subject of a contested box.
- Chinese-language primary sources are expected for China topics; quote in Chinese and gloss in `notes`.
- List what you could not source in `book/ledger/chNN_gaps.md`. Never invent a record.

## Writing rules (summary)

- Every number with a unit in prose is a macro: `{{L:id}}`, `{{C:script.name}}`; qualitative citations `{{Q:id}}`, `{{S:source_id}}`. `make lint` fails on bare numbers with units and on tier-C records outside `::: {.box .contested}`.
- Derivations, not just statements. One worked example per section where the syllabus asks for one, computed in `book/calc/chNN/*.py` from ledger inputs (`from common import L, Results`), with self-checking assertions. Modelling assumptions are explicit `ASSUMPTION` constants and are said as "we assume" in prose.
- Each section may assume only material from its syllabus prerequisites and earlier sections. Refer back to Chapter 1 symbols and results by section number.
- Contested or uncertain boxes present both sides with sources.
- Chinese term in parentheses at first use of each glossary term.
- No em dashes (U+2014) anywhere.
- Figures: matplotlib, Agg, reproducible SVG (`rcParams["svg.hashsalt"]` fixed, `savefig(..., metadata={"Date": None})`) to `book/figs/chNN/`, transparent background, mid-gray axes, no pure black; captions say computed or redrawn.
- End with `## Problems` and `## Solutions` (answers from `book/calc/chNN/problems.py`).
- Check: `make calc CH=NN`, `make build CH=NN`, `make lint` all pass.
