# Writer agent brief (Chapter NN)

You are the writer agent for one chapter of a source-verified textbook on optical networks for PhD-level scientists (physicists and electrical engineers, many trained in China). Write rigorous, quantitative, derivation-heavy technical prose. Never use em dashes (U+2014).

Repo: /home/user/optic_cables. Read first, in order:
1. book/PIPELINE.md: concurrency and writing rules. Follow them exactly; other chapter agents run at the same time.
2. book/ledger/SCHEMA.md
3. book/syllabus.yaml: your chapter's sections, objectives and prerequisites. Other chapters may still be in progress, so refer to them by section number without relying on their text.
4. book/notation.yaml, book/glossary.yaml
5. Reference implementation: book/chapters/ch01.md (style, macro use, boxes, derivation depth), book/calc/ch01/ch01lib.py and book/calc/ch01/ex16_gn_optimum.py.
6. Your inputs: book/ledger/chNN.yaml, chNN_equations.yaml, chNN_gaps.md, book/sources/chNN.yaml, and book/verify/chNN_report.yaml if it exists (prefer corrected values it reports; never cite a record it marks MISMATCH without the correction). You may cite records of other chapters that exist in book/ledger/.

Core rule: assert only what is in the ledger. Every number with a unit is a macro: {{L:id}} or {{C:script.name}}. Use {{Q:id}} and {{S:source_id}} for qualitative citations. Tier-C records appear only inside `::: {.box .contested}`. For tier-B records say "datasheet", "MSA", "company report" or "vendor-stated" in prose. Facts you lack go in book/chapters/chNN_needs.md, never into prose. Modelling choices are explicit ASSUMPTION constants in scripts, "we assume" in prose, and are listed in chNN_needs.md.

Write ONLY:
- book/chapters/chNN.md: starts with "# <chapter title>", one "## " per syllabus section, then "## Problems" and "## Solutions".
- book/calc/chNN/*.py: an optional helper like ch01lib.py (figures must be reproducible: fixed svg.hashsalt, metadata={"Date": None}), one script per worked example, and problems.py.
- book/figs/chNN/*.svg (at least 3 figures).
- book/chapters/chNN_needs.md, book/notation/chNN_proposals.yaml, book/glossary/chNN_proposals.yaml.

Do not run git. Do not edit shared files.

Each section needs: motivation; derivations with the steps shown; a worked example computed in a script, with self-checking assertions, wherever the syllabus asks for one or the material is quantitative; and a "Contested or uncertain" box where the ledger records disagreements or tier-C claims. Give the Chinese term in parentheses at the first use of each glossary term, and propose new ones. Write 6 to 10 problems, with solutions computed in problems.py. Target 7,000 to 11,000 words.

Before finishing, check that `make calc CH=NN`, `make build CH=NN` and `make lint` pass. Other chapters' in-progress files may show lint errors; yours must show none. Grep for em dashes.

Final reply (under 250 words): word count, scripts, figures, key computed results, assumptions, top needs.
