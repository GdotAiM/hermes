"""Legacy FTN research draft (was: "MINT paper draft"). Tickets ≠ orders. No broker call.

Brought in line with HERMES_INTEGRATION_I0 (frozen, supersedes Slice I):
- DayContext / handoff.v1 is the ONLY cross-part object. This draft is not a
  contract and MINT rejects it (kind != "day_context_handoff").
- No BUY/SELL anywhere: the old ``side: "buy"|"sell"`` (mapped from IOF state)
  is replaced by ``direction_hypothesis`` = the institutional IOF state copied
  verbatim ("bullish" | "bearish" | "unclear") — a research label, not a trade
  side. Annotation ≠ candidate ≠ ticket ≠ order.
- Not written by default. ``ftn brief`` writes it only when
  ``FTN_WRITE_MINT_DRAFT=1``, and then to ``dispatch/drafts/`` (or
  ``$FTN_DRAFT_DIR``) — never to ``dispatch/out/`` where handoffs live.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

from ftn.paths import draft_dir

DRAFT_KIND = "ftn_research_draft"


def drafts_enabled() -> bool:
    return os.environ.get("FTN_WRITE_MINT_DRAFT", "").strip() == "1"


def draft_from_handoff(handoff: dict) -> dict | None:
    selected = next((c for c in handoff.get("candidates") or [] if c.get("state") == "selected"), None)
    if not selected:
        return None
    ms = handoff.get("market_state") or {}
    iof = (ms.get("institutional") or {}).get("state") or "unclear"
    ticket = handoff.get("session_ticket") or {}
    return {
        "kind": DRAFT_KIND,
        "mode": "paper",
        "actionable_for_mint": False,
        "requires": ["board SURVIVES", "allowlist", "RISK", "human_ack"],
        "from": "ftn-agent",
        "to": "human_review",
        "symbol": handoff.get("symbol"),
        "date": handoff.get("date"),
        "session": handoff.get("session"),
        "direction_hypothesis": iof,
        "module": selected["module"],
        "reason": selected.get("reason"),
        "origin": selected.get("origin"),
        "fingerprint": handoff.get("fingerprint"),
        "session_ticket_id": ticket.get("id"),
        "contrary": handoff.get("contrary"),
        "ftn_objectives": (handoff.get("ftn_annotation") or {}).get("four") or [],
        "notes": "Research draft only — not an order, not a contract. direction_hypothesis is the IOF label, not a trade side.",
    }


def write_draft(handoff: dict, *, force: bool = False) -> Path | None:
    """Write the draft only when enabled (FTN_WRITE_MINT_DRAFT=1) or forced."""
    if not (force or drafts_enabled()):
        return None
    draft = draft_from_handoff(handoff)
    if not draft:
        return None
    out = draft_dir()
    blob = json.dumps(draft, indent=2) + "\n"
    path = out / f"ftn_draft_{handoff.get('date')}_{handoff.get('symbol')}.json"
    path.write_text(blob)
    (out / "ftn_draft_latest.json").write_text(blob)
    return path
