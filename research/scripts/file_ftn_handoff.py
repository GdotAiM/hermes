#!/usr/bin/env python3
"""File an FTN handoff.v1 (DayContext) as research evidence.

Validates the handoff against the contract (ftn.os.handoff_contract: structure +
recursive bans), copies it byte-for-byte into research/evidence/ftn/handoffs/
as <date>_<symbol>_<session>_<sha8>.json and appends a provenance row to
research/evidence/ftn/INDEX.md. Idempotent: the same bytes are filed once.

Filing is evidence intake only. It is not a claim, a verdict or a clearance,
and it never touches beliefs/LEDGER.md or summaries/.

Usage (from the monorepo root or research/):
  python3 research/scripts/file_ftn_handoff.py --origin fixture \
      ftn/dispatch/samples/handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json
  python3 research/scripts/file_ftn_handoff.py --origin live_observation   # default: ftn/dispatch/out/handoff_latest.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1]
MONOREPO = RESEARCH.parent
EVIDENCE = RESEARCH / "evidence" / "ftn"
HANDOFFS = EVIDENCE / "handoffs"
INDEX = EVIDENCE / "INDEX.md"
DEFAULT_SRC = MONOREPO / "ftn" / "dispatch" / "out" / "handoff_latest.json"
ORIGINS = ("fixture", "historical_tape", "live_observation")

INDEX_HEADER = (
    "# FTN DayContext evidence index\n\n"
    "Filed by `research/scripts/file_ftn_handoff.py`. One row per distinct handoff (sha256).\n"
    "`origin` is the provenance label given at filing time: `fixture` = built from an FTN\n"
    "test fixture (hand-labelled evidence, **not** tape); `historical_tape` / `live_observation`\n"
    "= built from real market data. Rows are evidence intake, not claims or verdicts.\n\n"
    "| filed_at (UTC) | file | origin | symbol | date | session | fingerprint | sha256[:12] | source |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
)


def _contract():
    sys.path.insert(0, str(MONOREPO / "ftn" / "src"))
    from ftn.os.handoff_contract import validate_handoff  # noqa: E402
    return validate_handoff


def file_handoff(src: Path, origin: str, now: datetime | None = None) -> tuple[Path, bool]:
    raw = src.read_bytes()
    h = json.loads(raw)
    errs = _contract()(h)
    if errs:
        raise SystemExit(f"REFUSED {src}: not a valid handoff.v1:\n  - " + "\n  - ".join(errs))
    sha = hashlib.sha256(raw).hexdigest()
    name = f"{h['date']}_{h['symbol']}_{h.get('session') or 'nosession'}_{sha[:8]}.json"
    HANDOFFS.mkdir(parents=True, exist_ok=True)
    dest = HANDOFFS / name
    if dest.exists():
        return dest, False
    dest.write_bytes(raw)
    if not INDEX.exists():
        INDEX.write_text(INDEX_HEADER, encoding="utf-8")
    try:
        rel_src = src.resolve().relative_to(MONOREPO)
    except ValueError:
        rel_src = src.name
    stamp = (now or datetime.now(timezone.utc)).strftime("%Y-%m-%dT%H:%M:%SZ")
    row = (
        f"| {stamp} | `handoffs/{name}` | {origin} | {h['symbol']} | {h['date']} | "
        f"{h.get('session') or '—'} | {h.get('fingerprint')} | {sha[:12]} | `{rel_src}` |\n"
    )
    with INDEX.open("a", encoding="utf-8") as f:
        f.write(row)
    return dest, True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="File an FTN handoff.v1 as research evidence")
    ap.add_argument("handoff", nargs="*", type=Path, help=f"handoff JSON(s) (default: {DEFAULT_SRC.relative_to(MONOREPO)})")
    ap.add_argument("--origin", required=True, choices=ORIGINS, help="provenance label (required; be honest)")
    args = ap.parse_args(argv)
    for src in args.handoff or [DEFAULT_SRC]:
        dest, new = file_handoff(src, args.origin)
        print(("filed " if new else "already filed ") + str(dest.relative_to(MONOREPO)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
