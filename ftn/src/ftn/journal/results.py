"""F7: paper results journal (research only; no order, no broker, not MINT).

For each Month 9 session ticket from the bar-derived kernel it records the trace (``ftn.trace.v1``) and, where
allowed, the paper outcome (correct-side BID/ASK fills, ``research.outcomes.simulate_both`` with DATA's
slippage floors; the same functions the scorer uses, called read-only).

H016 seal: no R is computed for any session after the burned window (2026-09-25) unless a human-signed
clearance stamp records that BOTH CASSANDRA and DATA cleared H016. Sealed rows carry
``result.status = "sealed_pending_cassandra_data_clearance"`` and ``R = None``; the outcome function is never
called for them, so no forward R is read. The burned window 2025-08-25 -> 2026-09-25 is open (already burned).

Output: ``$FTN_JOURNAL_DIR/paper_results.jsonl`` (append), one JSON object per session row.
"""

from __future__ import annotations

import json
import re
from datetime import date
from pathlib import Path

from ftn.paths import journal_dir

BURNED_START = date(2025, 8, 25)
BURNED_END = date(2026, 9, 25)
SEALED = "sealed_pending_cassandra_data_clearance"
JOURNAL_NAME = "paper_results.jsonl"


def clearance_ok(path: str | Path | None) -> tuple[bool, str]:
    """A clearance stamp counts only if a human signed it and it names H016 with CASSANDRA and DATA cleared."""
    from ftn.os.mint_draft import stamp_is_signed
    if not path:
        return False, "no_clearance_stamp"
    p = Path(path)
    if not p.is_file():
        return False, "clearance_stamp_missing"
    text = p.read_text(encoding="utf-8")
    if not re.search(r"\bH016\b", text):
        return False, "clearance_stamp_not_for_H016"
    for who in ("CASSANDRA", "DATA"):
        if not re.search(rf"^\s*{who}:\s*CLEARED\b", text, re.M):
            return False, f"clearance_missing_{who.lower()}"
    if not stamp_is_signed(text):
        return False, "clearance_stamp_unsigned"
    return True, "cleared"


def result_for(row: dict, outcome, clearance: tuple[bool, str]) -> dict:
    """Result block for one session row. ``outcome(row) -> dict`` is called only when allowed."""
    from ftn.research.kernel_log import tradeable
    d = date.fromisoformat(row["date"])
    if not row.get("ticket"):
        return {"status": "no_ticket", "R": None, "reason": row.get("reason")}
    if d > BURNED_END and not clearance[0]:
        return {"status": SEALED, "R": None, "seal_reason": clearance[1],
                "note": "H016 forward window: no R until CASSANDRA and DATA clear H016 (human-signed stamp)"}
    if d < BURNED_START:
        return {"status": "outside_burned_window", "R": None}
    if not tradeable(row):
        return {"status": "blocked", "R": None, "blocked_by": row.get("blocked_by")}
    out = outcome(row)
    return {"status": "burned_window" if d <= BURNED_END else "forward_cleared",
            **{k: out.get(k) for k in ("R", "R_gross", "exit", "exit_time", "fill_in", "fill_out", "risk_pts", "cost_model")}}


def journal_rows(rows: list[dict], outcome, clearance_path: str | Path | None = None,
                 out: Path | None = None, write: bool = True) -> list[dict]:
    cl = clearance_ok(clearance_path)
    recs = []
    for row in rows:
        res = result_for(row, outcome, cl)
        tr = dict(row.get("trace") or {})
        if tr:
            tr["result"] = res
        recs.append({"date": row["date"], "symbol": row["symbol"], "session": row["session"],
                     "ticket": row.get("ticket"), "module": row.get("module"), "result": res, "trace": tr or None,
                     "paper_only": True, "actionable_for_mint": False})
    if write:
        p = (out or journal_dir()) / JOURNAL_NAME
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as fh:
            for r in recs:
                fh.write(json.dumps(r, default=str) + "\n")
    return recs
