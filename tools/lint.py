#!/usr/bin/env python3
"""Structural checks for the book sources.

Current checks (gate G0):
  * syllabus: unique section ids, prereqs exist and precede the section in
    reading order (so the prerequisite graph is a DAG consistent with the TOC)
  * notation: unique symbols, first_defined is a real section
  * glossary: section refs are real sections, no duplicate English terms
Later gates add ledger schema, macro resolution, and bare-number checks.
"""
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent / "book"


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


def main():
    errors = []
    order = check_syllabus(errors)
    check_notation(errors, order)
    check_glossary(errors, order)
    for e in errors:
        print(e)
    print(f"lint: {len(order)} sections, {len(errors)} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
