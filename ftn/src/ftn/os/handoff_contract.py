"""handoff.v1 contract — structural validation + recursive signal/order bans.

The single cross-part contract of the HERMES monorepo is
``ftn/dispatch/out/handoff_latest.json`` (schemaVersion "1",
kind "day_context_handoff"). Committed reference samples live in
``ftn/dispatch/samples/``; the JSON Schema is
``ftn/dispatch/schema/handoff.v1.schema.json``.

Stdlib only (FTN core has no dependencies). The JSON Schema covers
structure; the ban walk below is authoritative for HERMES_INTEGRATION_I0
"Handoff bans": BUY/SELL recommendation, confidence / best_pam / pam_rank,
broker instructions, and order fields must be ABSENT (not merely null),
at any depth.

Usage:
    python -m ftn.os.handoff_contract PATH [PATH ...]   # exit 1 on any violation
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1"
KIND = "day_context_handoff"
SCHEMA_PATH = Path(__file__).resolve().parents[3] / "dispatch" / "schema" / "handoff.v1.schema.json"

# Keys banned at ANY depth (case-insensitive exact match).
BANNED_KEYS = frozenset(
    {
        # trade-direction recommendation / signal
        "buy", "sell", "side", "action", "signal", "signals", "recommendation",
        "trade_direction", "direction_recommendation", "trade_signal",
        # confidence / model ranking
        "confidence", "confidence_score", "best_pam", "pam_rank", "rank", "ranking",
        # order / broker fields
        "order", "orders", "order_id", "order_type", "client_order_id", "qty",
        "quantity", "limit_price", "stop_price", "stop_loss", "take_profit",
        "time_in_force", "tif", "position_size", "lots", "notional", "account_id",
        "place_order", "submit_order", "route", "routing", "auto_clear",
        "automatic_clearance",
    }
)
# Substrings banned inside any key (case-insensitive).
BANNED_KEY_SUBSTRINGS = ("broker", "confidence", "best_pam", "pam_rank")
# String values banned anywhere (an explicit buy/sell call as a value).
BANNED_VALUE_RE = re.compile(r"^\s*(strong[\s_-]*)?(buy|sell)\s*$", re.IGNORECASE)

REQUIRED_TOP = {
    "schemaVersion": str,
    "kind": str,
    "producer": str,
    "consumer": str,
    "mode": str,
    "fingerprint": str,
    "symbol": str,
    "date": str,
    "market_state": dict,
    "candidates": list,
    "ftn_annotation": dict,
    "notes": list,
}
# Nullable top-level keys that must still be present.
NULLABLE_TOP = ("session", "session_ticket", "contrary")
ALLOWED_TOP = frozenset(REQUIRED_TOP) | frozenset(NULLABLE_TOP) | {"_provenance"}
REQUIRED_MARKET_STATE = (
    "sentiment", "institutional", "profile", "charter", "pam1_evidence", "pam1_completeness",
)
CANDIDATE_KEYS = ("module", "state", "eligible", "reason", "origin")


def find_ban_violations(obj: Any, path: str = "$") -> list[str]:
    """Recursively list every banned key / value (path-qualified)."""
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kp = f"{path}.{k}"
            kl = str(k).lower()
            if kl in BANNED_KEYS:
                out.append(f"banned key {kp}")
            elif any(s in kl for s in BANNED_KEY_SUBSTRINGS):
                out.append(f"banned key {kp}")
            out.extend(find_ban_violations(v, kp))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(find_ban_violations(v, f"{path}[{i}]"))
    elif isinstance(obj, str) and BANNED_VALUE_RE.match(obj):
        out.append(f"banned buy/sell value at {path}: {obj!r}")
    return out


def structural_errors(h: Any) -> list[str]:
    """Stdlib mirror of the JSON Schema's structural rules."""
    if not isinstance(h, dict):
        return ["handoff must be a JSON object"]
    errs: list[str] = []
    for k, t in REQUIRED_TOP.items():
        if k not in h:
            errs.append(f"missing required key {k}")
        elif not isinstance(h[k], t):
            errs.append(f"{k} must be {t.__name__}")
    for k in NULLABLE_TOP:
        if k not in h:
            errs.append(f"missing key {k} (may be null)")
    for k in h:
        if k not in ALLOWED_TOP:
            errs.append(f"unexpected top-level key {k}")
    if h.get("schemaVersion") != SCHEMA_VERSION:
        errs.append(f"schemaVersion must be {SCHEMA_VERSION!r}")
    if h.get("kind") != KIND:
        errs.append(f"kind must be {KIND!r}")
    if h.get("mode") != "paper":
        errs.append("mode must be 'paper'")
    ms = h.get("market_state")
    if isinstance(ms, dict):
        for k in REQUIRED_MARKET_STATE:
            if k not in ms:
                errs.append(f"market_state.{k} missing (may be null)")
    for i, c in enumerate(h.get("candidates") or []):
        if not isinstance(c, dict):
            errs.append(f"candidates[{i}] must be an object")
            continue
        for k in CANDIDATE_KEYS:
            if k not in c:
                errs.append(f"candidates[{i}].{k} missing")
    fa = h.get("ftn_annotation")
    if isinstance(fa, dict):
        four = fa.get("four")
        if not isinstance(four, list):
            errs.append("ftn_annotation.four must be a list")
        else:
            for i, lv in enumerate(four):
                if not isinstance(lv, dict) or not isinstance(lv.get("price"), (int, float)) or "name" not in lv:
                    errs.append(f"ftn_annotation.four[{i}] needs name + numeric price")
    return errs


def validate_handoff(h: Any) -> list[str]:
    """All contract errors (structure + bans). Empty list = valid handoff.v1."""
    return structural_errors(h) + find_ban_violations(h)


def validate_file(path: str | Path) -> list[str]:
    try:
        h = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        return [f"unreadable: {e}"]
    return validate_handoff(h)


def main(argv: list[str] | None = None) -> int:
    paths = argv if argv is not None else sys.argv[1:]
    if not paths:
        print("usage: python -m ftn.os.handoff_contract PATH [PATH ...]", file=sys.stderr)
        return 2
    bad = 0
    for p in paths:
        errs = validate_file(p)
        if errs:
            bad += 1
            print(f"INVALID {p}")
            for e in errs:
                print(f"  - {e}")
        else:
            print(f"OK handoff.v1 {p}")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
