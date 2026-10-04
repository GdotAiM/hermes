#!/usr/bin/env python3
"""Scan HERMES-X LEDGER + board locks for actionable clears; write MINT tickets.

Does NOT place orders. Emits dispatch tickets under dispatch/out/ for MINT/human.

Monorepo layout (GdotAiM/hermes): research spine lives at ../research relative
to trading/. With no flags the scanner resolves the research root in this order:
  1. --hermes-x PATH (alias --research)
  2. $HERMES_RESEARCH_PATH, then legacy $HERMES_X_PATH
  3. <monorepo>/research (auto-detected next to trading/)

Usage (from trading/):
  PYTHONPATH=src python3 -m mint.dispatch.scan_clears
  PYTHONPATH=src python3 -m mint.dispatch.scan_clears --apply-filters
  PYTHONPATH=src python3 -m mint.dispatch.scan_clears --hermes-x /path/to/research
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

SURVIVES_RE = re.compile(r"\bSURVIVES\b", re.I)
FAILS_RE = re.compile(r"\bFAILS\b", re.I)
INCONCLUSIVE_RE = re.compile(r"\bINCONCLUSIVE\b", re.I)
VERIFY_RE = re.compile(r"\bVERIFY\b", re.I)
BOARD_LOCK = re.compile(r".*_BOARD_LOCK\.md$", re.I)

# trading/ root (…/trading/src/mint/dispatch/scan_clears.py -> parents[3])
TRADING_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_RESEARCH = TRADING_ROOT.parent / "research"


def resolve_research_root(cli_value: Path | None) -> Path:
    """Pick the research spine root (dir containing summaries/ and beliefs/)."""
    if cli_value is not None:
        return cli_value.expanduser().resolve()
    for env in ("HERMES_RESEARCH_PATH", "HERMES_X_PATH"):
        val = os.environ.get(env, "").strip()
        if val:
            return Path(val).expanduser().resolve()
    return DEFAULT_RESEARCH.resolve()


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


def _decision_text(text: str) -> str:
    """Return only the '## Decision…' section (up to the next '## ' heading).

    Falls back to the first 1200 chars when no Decision heading exists. Bounding
    the section matters: board locks often list other hypotheses' FAILS under
    later headings (e.g. '## KEY FINDINGS'), which previously leaked into the
    800-char window and mislabeled INCONCLUSIVE locks as FAILS.
    """
    m = re.search(r"^##\s*Decision[^\n]*\n", text, re.M | re.I)
    if not m:
        return text[:1200]
    rest = text[m.end():]
    nxt = re.search(r"^##\s", rest, re.M)
    return rest[: nxt.start()] if nxt else rest[:800]


# Explicit verdict line in a Decision section, e.g. "**H004b = FAILS.**",
# "**H013 = OPEN** — NEEDS MORE DATA", "**H014 = FAILS (historical) / … OPEN**".
EXPLICIT_STATUS_RE = re.compile(
    r"\*\*[^*=\n]*=\s*(INCONCLUSIVE|FAILS|VERIFY COMPLETE|VERIFY|SURVIVES|OPEN|HOLD)\b", re.I
)
# Negated mentions must never count as a clearance ("Not SURVIVES", "no SURVIVES").
NEGATED_SURVIVES_RE = re.compile(r"\b(not|no|never|is\s+not|isn't)\s+SURVIVES\b", re.I)


def _decision_status(text: str) -> str:
    dec = _decision_text(text)
    m = EXPLICIT_STATUS_RE.search(dec)
    if m:
        label = m.group(1).upper()
        return "VERIFY" if label.startswith("VERIFY") else label
    dec = NEGATED_SURVIVES_RE.sub(" ", dec)
    # Order: INCONCLUSIVE before FAILS/SURVIVES so "INCONCLUSIVE" parks.
    for label, rx in (
        ("INCONCLUSIVE", INCONCLUSIVE_RE),
        ("FAILS", FAILS_RE),
        ("VERIFY", VERIFY_RE),
        ("SURVIVES", SURVIVES_RE),
    ):
        if rx.search(dec):
            return label
    return "UNKNOWN"


def scan_board_locks(summaries: Path) -> list[Ticket]:
    tickets: list[Ticket] = []
    if not summaries.is_dir():
        return tickets
    for path in sorted(summaries.glob("*BOARD_LOCK*.md")):
        if path.name.startswith("_"):
            continue
        text = _read(path)
        status = _decision_status(text)

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
        elif status in ("OPEN", "HOLD"):
            tickets.append(
                Ticket(
                    "ignore",
                    str(path),
                    hint,
                    status,
                    f"{status} — no verdict yet (forward test / needs data); no size; park",
                    False,
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
    reject_markers = (
        "rejected", "artifact", "inconclusive", "fails", "parked", "not survive", "did not survive",
        "no survives", "forbidden", "= open", "needs more data", "forward-only",
    )
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


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Scan HERMES-X for MINT dispatch tickets")
    ap.add_argument(
        "--hermes-x",
        "--research",
        dest="hermes_x",
        type=Path,
        default=None,
        help="Research spine root (default: $HERMES_RESEARCH_PATH, $HERMES_X_PATH, or ../research in the monorepo)",
    )
    ap.add_argument("--out", type=Path, default=None, help="Output dir (default: dispatch/out)")
    ap.add_argument("--apply-filters", action="store_true", help="Write demote snippets under fixtures/generated_filters")
    args = ap.parse_args(argv)
    hx = resolve_research_root(args.hermes_x)
    summaries = hx / "summaries"
    ledger = hx / "beliefs" / "LEDGER.md"
    if not summaries.is_dir() or not ledger.is_file():
        print(
            f"ERROR: research spine not found at {hx} "
            f"(need summaries/ and beliefs/LEDGER.md). "
            "Pass --hermes-x PATH or set HERMES_RESEARCH_PATH.",
            file=sys.stderr,
        )
        return 2
    out = args.out or (TRADING_ROOT / "dispatch" / "out")
    out.mkdir(parents=True, exist_ok=True)

    tickets = scan_board_locks(summaries) + scan_ledger(ledger)
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
        filt = TRADING_ROOT / "fixtures" / "generated_filters"
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
