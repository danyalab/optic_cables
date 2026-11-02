"""Shared helpers for worked-example scripts.

Inputs come only from the ledger (`L(id)`), so every number in a worked
example traces to a source. Results are written with `emit()` to
book/calc/<chapter>/out/<script>.json and referenced from prose as
{{C:<script>.<name>}}.

Physical constants are ledger records too (CODATA, kind: constant).
"""
import inspect
import json
from functools import lru_cache
from pathlib import Path

import yaml

BOOK = Path(__file__).resolve().parent.parent


@lru_cache(maxsize=None)
def _ledger():
    recs = {}
    for path in sorted((BOOK / "ledger").glob("ch*.yaml")):
        if path.name.endswith("_equations.yaml"):
            continue
        for r in (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("records") or []:
            recs[r["id"]] = r
    return recs


def L(rid, pick=None):
    """Numeric value of ledger record `rid`.

    For range values [lo, hi], pass pick="lo", "hi", or "mid".
    """
    v = _ledger()[rid]["value"]
    if isinstance(v, list):
        lo, hi = float(v[0]), float(v[1])
        if pick is None:
            raise ValueError(f"{rid} is a range; pass pick='lo'|'hi'|'mid'")
        return {"lo": lo, "hi": hi, "mid": 0.5 * (lo + hi)}[pick]
    return float(v)


def unit(rid):
    return _ledger()[rid]["unit"]


class Results:
    """Collects named results for one script and writes them as JSON."""

    def __init__(self):
        caller = Path(inspect.stack()[1].filename)
        self.script = caller.stem
        self.out = caller.parent / "out" / f"{self.script}.json"
        self.data = {}
        self.inputs = set()

    def emit(self, name, value, unit, digits=3, inputs=()):
        """Record a result. `digits` = significant figures for display."""
        self.data[name] = {"value": float(value), "unit": unit, "digits": digits,
                           "inputs": sorted(inputs)}
        self.inputs.update(inputs)

    def save(self):
        self.out.parent.mkdir(exist_ok=True)
        self.out.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"{self.script}: {len(self.data)} results")
