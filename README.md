# optic_cables

A source-verified technical book on optical interconnect and networks, from fiber physics to US and China network architecture and supply chains.

## Pipeline

1. Syllabus (`book/syllabus.yaml`): table of contents, objectives, prerequisite DAG. Approved before research starts.
2. Retrieval: primary sources only, recorded in `book/ledger/chNN.yaml` with value, unit, conditions, locator, and tier.
3. Extraction: structured parameters and equations from each source.
4. Writing: `book/chapters/chNN.md`; numbers appear only as ledger or calculation macros.
5. Blind verification: an independent pass re-checks every ledger record against its source (`book/verify/`).
6. Study layer: problem sets and the 中英 glossary (`book/glossary.yaml`).

Shared conventions live in `book/notation.yaml`. Run `make check` before committing.

## Status

Gate G0: syllabus drafted, awaiting review. Pilot chapter: 1 (fiber channel physics).
