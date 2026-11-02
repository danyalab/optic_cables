#!/usr/bin/env python3
"""Stamp a chapter's ledger with its blind-verifier results.

For every record and equation in book/ledger/chNN*.yaml:
  verified: match | partial | mismatch | unreachable | not_checked
and, for non-matches, append the verifier's action to `notes` (once).
Substantive corrections (value, tier, source) are made separately by hand
and then marked by changing `verified` to partial_fixed / mismatch_fixed.

Usage: tools/apply_verify.py NN
"""
import sys
from pathlib import Path

import yaml

BOOK = Path(__file__).resolve().parent.parent / "book"
LABEL = {"MATCH": "match", "PARTIAL": "partial", "MISMATCH": "mismatch", "UNREACHABLE": "unreachable"}


def main(ch):
    status = {}
    for rep in sorted((BOOK / "verify").glob(f"ch{ch}*_report.yaml")):
        for r in yaml.safe_load(rep.read_text(encoding="utf-8"))["results"]:
            status[r["id"]] = r
    counts = {}
    for path in sorted((BOOK / "ledger").glob(f"ch{ch}*.yaml")):
        key = "equations" if path.name.endswith("_equations.yaml") else "records"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for rec in data.get(key) or []:
            res = status.get(rec["id"])
            label = LABEL.get(res["status"], "not_checked") if res else "not_checked"
            if str(rec.get("verified", "")).endswith("_fixed"):
                label = rec["verified"]
            rec["verified"] = label
            counts[label] = counts.get(label, 0) + 1
            if res and res["status"] != "MATCH" and res.get("action"):
                note = f"Verifier ({res['status']}): {res['action']}"
                if note not in str(rec.get("notes", "")):
                    rec["notes"] = (str(rec.get("notes") or "") + " " + note).strip()
        path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False, width=120), encoding="utf-8")
    print(f"ch{ch}: {counts}")


if __name__ == "__main__":
    main(sys.argv[1])
