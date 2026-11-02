#!/usr/bin/env python3
"""Build a chapter: resolve macros, number citations, render HTML with pandoc.

Macros in book/chapters/chNN.md:
  {{L:id}}      ledger value with unit and citation, e.g. "0.18 dB/km [3]"
  {{L:id|v}}    ledger value only (no unit, still cited)
  {{C:s.name}}  calc result s.name with unit (from book/calc/chNN/out/s.json)
  {{C:s.name|v}} calc result value only
  {{S:source_id}} bare citation to a source (for equations and qualitative claims)
  {{Q:id}}      citation only for a ledger record (qualitative 'fact' records)

Usage: tools/build.py 01
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BOOK = ROOT / "book"
DIST = ROOT / "dist"
MACRO = re.compile(r"\{\{([LCSQ]):([A-Za-z0-9_.\-]+)(?:\|(v))?\}\}")
KATEX = "https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/"


def load_ledger(ch):
    recs, srcs = {}, {}
    for p in sorted((BOOK / "ledger").glob(f"ch{ch}*.yaml")):
        if not p.name.endswith("_equations.yaml"):
            for r in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("records") or []:
                recs[r["id"]] = r
    for p in sorted((BOOK / "sources").glob(f"ch{ch}*.yaml")):
        for s in (yaml.safe_load(p.read_text(encoding="utf-8")) or {}).get("sources") or []:
            srcs[s["id"]] = s
    return recs, srcs


def load_calc(ch):
    out = {}
    for p in sorted((BOOK / "calc" / f"ch{ch}" / "out").glob("*.json")):
        for name, r in json.loads(p.read_text(encoding="utf-8")).items():
            out[f"{p.stem}.{name}"] = r
    return out


def fmt_num(x, digits=None):
    if isinstance(x, list):
        return "–".join(fmt_num(v, digits) for v in x)  # en dash for ranges
    if isinstance(x, str):
        return x
    x = float(x)
    if digits:
        if x == 0:
            return "0"
        mag = math.floor(math.log10(abs(x)))
        x = round(x, digits - 1 - mag)
    s = f"{x:.6g}"
    if "e" in s:
        m, e = s.split("e")
        return f"{m}×10<sup>{int(e)}</sup>"
    return s


def fmt_unit(u):
    return "" if u in ("1", "", None) else f" {u}"


def build(ch):
    recs, srcs = load_ledger(ch)
    calc = load_calc(ch)
    md = (BOOK / "chapters" / f"ch{ch}.md").read_text(encoding="utf-8")
    order, errors = [], []

    def cite(sid):
        if sid not in srcs:
            errors.append(f"unknown source {sid}")
            return "[?]"
        if sid not in order:
            order.append(sid)
        n = order.index(sid) + 1
        return f'<a class="cite" href="#ref-{n}">[{n}]</a>'

    def repl(m):
        kind, key, vonly = m.groups()
        if kind == "L":
            r = recs.get(key)
            if not r:
                errors.append(f"unknown ledger id {key}")
                return "??"
            val = fmt_num(r["value"])
            u = "" if vonly else fmt_unit(r.get("unit"))
            return f'<span class="lv" title="{key}">{val}{u}</span> {cite(r["source_id"])}'
        if kind == "Q":
            r = recs.get(key)
            if not r:
                errors.append(f"unknown ledger id {key}")
                return "??"
            return cite(r["source_id"])
        if kind == "S":
            return cite(key)
        r = calc.get(key)
        if not r:
            errors.append(f"unknown calc result {key}")
            return "??"
        val = fmt_num(r["value"], r.get("digits"))
        u = "" if vonly else fmt_unit(r.get("unit"))
        return f'<span class="cv" title="calc: {key}">{val}{u}</span>'

    body = MACRO.sub(repl, md)
    if errors:
        for e in sorted(set(errors)):
            print("build:", e)
        sys.exit(1)

    refs = ["\n\n## References {#references}\n"]
    for i, sid in enumerate(order, 1):
        s = srcs[sid]
        doi = f" doi:{s['doi']}." if s.get("doi") else ""
        url = f" <{s['url']}>" if s.get("url") else ""
        refs.append(f'<p id="ref-{i}" class="ref">[{i}] {s.get("authors", "")}, '
                    f'"{s.get("title", "")}," <em>{s.get("venue", "")}</em>, {s.get("year", "")}.{doi}{url} '
                    f'<span class="tier">tier {s.get("tier")}</span></p>')
    body += "\n".join(refs)

    DIST.mkdir(exist_ok=True)
    tmp = DIST / f"ch{ch}.resolved.md"
    tmp.write_text(body, encoding="utf-8")
    out = DIST / f"ch{ch}.html"
    cmd = ["pandoc", str(tmp), "-f", "markdown+tex_math_dollars+raw_html", "-t", "html5",
           "-s", f"--katex={KATEX}", "--toc", "--toc-depth=2", "--number-sections",
           "--css", "style.css", "--resource-path", str(BOOK), "-o", str(out),
           "--metadata", f"title=Chapter {int(ch)}"]
    style = ROOT / "tools" / "style.css"
    if style.exists():
        cmd[cmd.index("--css") + 1] = "style.css"
        (DIST / "style.css").write_text(style.read_text(encoding="utf-8"), encoding="utf-8")
    subprocess.run(cmd, check=True)
    print(f"build: {out} ({len(order)} sources cited)")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else "01")
