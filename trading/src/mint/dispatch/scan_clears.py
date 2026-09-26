#!/usr/bin/env python3
"""Scan HERMES-X LEDGER + board locks for actionable clears; write MINT tickets.

Does NOT place orders. Emits dispatch tickets under dispatch/out/ for MINT/human.

Usage:
  PYTHONPATH=src python -m mint.dispatch.scan_clears --hermes-x /path/to/hermes-x
  PYTHONPATH=src python -m mint.dispatch.scan_clears --hermes-x /path/to/hermes-x --apply-filters
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

SURVIVES_RE = re.compile(r"\bSURVIVES\b", re.I)
FAILS_RE = re.compile(r"\bFAILS\b", re.I)
INCONCLUSIVE_RE = re.compile(r"\bINCONCLUSIVE\b", re.I)
VERIFY_RE = re.compile(r"\bVERIFY\b", re.I)
BOARD_LOCK = re.compile(r".*_BOARD_LOCK\.md$", re.I)


@dataclass
class Ticket:
    kind: str  # entry_candidate | demote_filter | prior_log | ignore
    source: str
    hypothesis_hint: str
    board_status: str
    summary: str
    actionable_for_mint: bool


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except OSError:
        return ""


def scan_board_locks(summaries: Path) -> list[Ticket]:
    tickets: list[Ticket] = []
    if not summaries.is_dir():
        return tickets
    for path in sorted(summaries.glob("*BOARD_LOCK*.md")):
        if path.name.startswith("_"):
            continue
        text = _read(path)
        status = "UNKNOWN"
        if SURVIVES_RE.search(text) and not FAILS_RE.search(text.split("Decision")[-1] if "Decision" in text else text[:500]):
            # Prefer explicit Decision section if present
            dec = text
            if "## Decision" in text:
                dec = text.split("## Decision", 1)[1][:800]
            if re.search(r"\bFAILS\b", dec):
                status = "FAILS"
            elif re.search(r"\bINCONCLUSIVE\b", dec):
                status = "INCONCLUSIVE"
            elif re.search(r"\bSURVIVES\b", dec):
                status = "SURVIVES"
            elif re.search(r"\bVERIFY\b", dec):
                status = "VERIFY"
            else:
                status = "SURVIVES" if SURVIVES_RE.search(dec) else "UNKNOWN"
        else:
            dec = text.split("## Decision", 1)[1][:800] if "## Decision" in text else text[:1200]
            if re.search(r"\bFAILS\b", dec):
                status = "FAILS"
            elif re.search(r"\bINCONCLUSIVE\b", dec):
                status = "INCONCLUSIVE"
            elif re.search(r"\bVERIFY\b", dec):
                status = "VERIFY"
            elif re.search(r"\bSURVIVES\b", dec):
                status = "SURVIVES"

        hint = path.stem
        if status == "SURVIVES":
            tickets.append(
                Ticket(
                    "entry_candidate",
                    str(path),
                    hint,
                    status,
                    "Board SURVIVES — requires allowlist + RISK + human paper ack before orders",
                    True,
                )
            )
        elif status == "FAILS":
            tickets.append(
                Ticket(
                    "demote_filter",
                    str(path),
                    hint,
                    status,
                    "Board FAILS — encode as no-trade / demotion filter only",
                    True,
                )
            )
        elif status == "VERIFY":
            tickets.append(
                Ticket(
                    "prior_log",
                    str(path),
                    hint,
                    status,
                    "VERIFY — research logging / prior only; not an entry",
                    True,
                )
            )
        elif status == "INCONCLUSIVE":
            tickets.append(
                Ticket(
                    "ignore",
                    str(path),
                    hint,
                    status,
                    "INCONCLUSIVE — no size; park",
                    False,
                )
            )
    return tickets


def scan_ledger(ledger: Path) -> list[Ticket]:
    """LEDGER is noisy — only emit when the row clearly affirms a board SURVIVES.

    Skip rows that mention SURVIVES only to reject it (artifact / rejected / FAILS).
    Prefer board-lock files for entry_candidate; LEDGER is secondary.
    """
    tickets: list[Ticket] = []
    text = _read(ledger)
    reject_markers = ("rejected", "artifact", "inconclusive", "fails", "parked", "not survive", "did not survive")
    for i, line in enumerate(text.splitlines()):
        if not line.startswith("|"):
            continue
        low = line.lower()
        if SURVIVES_RE.search(line) and "packaging" not in low:
            if any(m in low for m in reject_markers):
                continue
            if "board" in low and "survives" in low and "fail" not in low:
                tickets.append(
                    Ticket(
                        "entry_candidate",
                        f"{ledger}:line{i+1}",
                        "LEDGER",
                        "SURVIVES",
                        line.strip()[:240],
                        True,
                    )
                )
        elif FAILS_RE.search(line) and "board" in low and "survives rejected" not in low:
            if "board fail" in low or "board lock" in low and "fail" in low or "fails" in low:
                tickets.append(
                    Ticket(
                        "demote_filter",
                        f"{ledger}:line{i+1}",
                        "LEDGER",
                        "FAILS",
                        line.strip()[:240],
                        True,
                    )
                )
    return tickets


def main() -> int:
    ap = argparse.ArgumentParser(description="Scan HERMES-X for MINT dispatch tickets")
    ap.add_argument("--hermes-x", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None, help="Output dir (default: dispatch/out)")
    ap.add_argument("--apply-filters", action="store_true", help="Write demote snippets under fixtures/generated_filters")
    args = ap.parse_args()
    hx = args.hermes_x.resolve()
    out = args.out or (Path(__file__).resolve().parents[3] / "dispatch" / "out")
    out.mkdir(parents=True, exist_ok=True)

    tickets = scan_board_locks(hx / "summaries") + scan_ledger(hx / "beliefs" / "LEDGER.md")
    # Dedupe by source
    seen: set[str] = set()
    uniq: list[Ticket] = []
    for t in tickets:
        if t.source in seen:
            continue
        seen.add(t.source)
        uniq.append(t)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    payload = {
        "scanned_at": stamp,
        "hermes_x": str(hx),
        "ticket_count": len(uniq),
        "entry_candidates": sum(1 for t in uniq if t.kind == "entry_candidate"),
        "tickets": [asdict(t) for t in uniq],
        "note": "No orders placed. entry_candidate still needs allowlist+RISK+human.",
    }
    path = out / f"dispatch_{stamp}.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    latest = out / "latest.json"
    latest.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {path} ({len(uniq)} tickets, {payload['entry_candidates']} entry_candidates)")

    if args.apply_filters:
        filt = Path(__file__).resolve().parents[3] / "fixtures" / "generated_filters"
        filt.mkdir(parents=True, exist_ok=True)
        demotes = [t for t in uniq if t.kind == "demote_filter"]
        (filt / "demotions.md").write_text(
            "# Auto demotions from board FAILS\n\n"
            + "\n".join(f"- `{t.hypothesis_hint}` ← {t.source}" for t in demotes)
            + "\n",
            encoding="utf-8",
        )
        print(f"Wrote {filt / 'demotions.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
