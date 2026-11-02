#!/usr/bin/env python3
"""Structural checks for the book sources.

Current checks (gate G0):
  * syllabus: unique section ids, prereqs exist and precede the section in
    reading order (so the prerequisite graph is a DAG consistent with the TOC)
  * notation: unique symbols, first_defined is a real section
  * glossary: section refs are real sections, no duplicate English terms
Later gates add ledger schema, macro resolution, and bare-number checks.
"""
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent / "book"
PARSE_ERRORS = []


def load(name):
    with open(ROOT / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_syllabus(errors):
    syl = load("syllabus.yaml")
    order = {}
    for ch in syl["chapters"]:
        for sec in ch["sections"]:
            sid = sec["id"]
            if sid in order:
                errors.append(f"syllabus: duplicate section id {sid}")
            if not sid.startswith(f"{ch['id']}."):
                errors.append(f"syllabus: section {sid} filed under chapter {ch['id']}")
            for p in sec.get("prereqs", []):
                if p not in order:
                    errors.append(f"syllabus: {sid} prereq {p} is unknown or does not precede it")
            if not sec.get("objectives") and not sec.get("contested"):
                errors.append(f"syllabus: {sid} has no objectives")
            order[sid] = len(order)
    return order


def check_notation(errors, order):
    seen = {}
    for s in load("notation.yaml")["symbols"]:
        sym = s["symbol"]
        if sym in seen and seen[sym] != s["meaning"]:
            errors.append(f"notation: {sym} redefined ({seen[sym]!r} vs {s['meaning']!r})")
        seen[sym] = s["meaning"]
        if s["first_defined"] not in order:
            errors.append(f"notation: {sym} first_defined {s['first_defined']} is not a section")


def check_glossary(errors, order):
    seen = set()
    for t in load("glossary.yaml")["terms"]:
        if t["en"] in seen:
            errors.append(f"glossary: duplicate term {t['en']}")
        seen.add(t["en"])
        if t["section"] not in order:
            errors.append(f"glossary: {t['en']} refers to unknown section {t['section']}")


LEDGER_REQUIRED = ("id", "section", "claim", "value", "unit", "kind", "source_id",
                   "locator", "quote", "retrieved", "tier", "confidence")
KINDS = {"spec_max", "spec_min", "spec_typ", "measured", "record", "constant", "model_param", "fact"}
TIERS = {"A", "B", "C"}
CONFIDENCE = {"high", "med", "low"}
ID_RE = re.compile(r"^ch\d{2}\.[a-z0-9_.]+$")


def load_all(subdir, pattern, key):
    out = []
    for path in sorted((ROOT / subdir).glob(pattern)):
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError as e:
            PARSE_ERRORS.append(f"{path.name}: YAML parse error: {str(e).splitlines()[0]}")
            continue
        for rec in data.get(key) or []:
            out.append((path.name, rec))
    return out


def check_ledger(errors, order):
    sources = {}
    for fname, s in load_all("sources", "*.yaml", "sources"):
        sid = s.get("id")
        if sid in sources:
            errors.append(f"{fname}: duplicate source id {sid}")
        sources[sid] = s
        if s.get("tier") not in TIERS:
            errors.append(f"{fname}: source {sid} has bad tier {s.get('tier')!r}")

    ids = set()
    for fname, r in load_all("ledger", "ch*[!s].yaml", "records"):
        rid = r.get("id", "?")
        for k in LEDGER_REQUIRED:
            if k == "unit" and r.get("kind") == "fact":
                continue
            if r.get(k) in (None, ""):
                errors.append(f"{fname}: {rid} missing {k}")
        if not ID_RE.match(str(rid)):
            errors.append(f"{fname}: bad id {rid}")
        if rid in ids:
            errors.append(f"{fname}: duplicate record id {rid}")
        ids.add(rid)
        if r.get("section") not in order:
            errors.append(f"{fname}: {rid} unknown section {r.get('section')}")
        if r.get("kind") not in KINDS:
            errors.append(f"{fname}: {rid} bad kind {r.get('kind')!r}")
        if r.get("tier") not in TIERS:
            errors.append(f"{fname}: {rid} bad tier {r.get('tier')!r}")
        if r.get("confidence") not in CONFIDENCE:
            errors.append(f"{fname}: {rid} bad confidence {r.get('confidence')!r}")
        if r.get("source_id") not in sources:
            errors.append(f"{fname}: {rid} cites unknown source {r.get('source_id')}")
        if len(str(r.get("quote", "")).split()) > 40:
            errors.append(f"{fname}: {rid} quote longer than 40 words")

    eq_ids = set()
    for fname, e in load_all("ledger", "*_equations.yaml", "equations"):
        eid = e.get("id", "?")
        if eid in eq_ids:
            errors.append(f"{fname}: duplicate equation id {eid}")
        eq_ids.add(eid)
        for k in ("latex", "source_id", "locator", "section"):
            if not e.get(k):
                errors.append(f"{fname}: {eid} missing {k}")
        if e.get("source_id") and e["source_id"] not in sources:
            errors.append(f"{fname}: {eid} cites unknown source {e['source_id']}")
    return len(ids), len(eq_ids), len(sources)


def main():
    errors = []
    order = check_syllabus(errors)
    check_notation(errors, order)
    check_glossary(errors, order)
    n_rec, n_eq, n_src = check_ledger(errors, order)
    check_chapters(errors)
    errors.extend(sorted(set(PARSE_ERRORS)))
    print(f"ledger: {n_rec} records, {n_eq} equations, {n_src} sources")
    for e in errors:
        print(e)
    print(f"lint: {len(order)} sections, {len(errors)} error(s)")
    return 1 if errors else 0



UNIT_RE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?\s?(?:dBm|dB/km|dB|km|nm|ps|GHz|THz|GBd|Gb/s|Tb/s|µm|um|mW|W)\b")


def check_chapters(errors):
    """Bare numbers with units outside macros and math; tier-C records outside contested boxes."""
    recs = {}
    for _, r in load_all("ledger", "ch*[!s].yaml", "records"):
        recs[r["id"]] = r
    for path in sorted((ROOT / "chapters").glob("ch[0-9][0-9].md")):
        text = path.read_text(encoding="utf-8")
        in_contested = False
        for n, line in enumerate(text.splitlines(), 1):
            if line.startswith(":::"):
                in_contested = "contested" in line
            stripped = re.sub(r"\{\{[^}]*\}\}", "", line)
            stripped = re.sub(r"\$\$.*?\$\$|\$[^$]*\$", "", stripped)
            stripped = re.sub(r"\{[^}]*\}", "", stripped)          # pandoc attributes
            for m in UNIT_RE.finditer(stripped):
                errors.append(f"{path.name}:{n}: bare number with unit '{m.group(0)}'")
            if not in_contested:
                for rid in re.findall(r"\{\{[LQ]:([A-Za-z0-9_.\-]+)", line):
                    if recs.get(rid, {}).get("tier") == "C":
                        errors.append(f"{path.name}:{n}: tier-C record {rid} outside a contested box")


if __name__ == "__main__":
    sys.exit(main())
