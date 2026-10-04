"""Model 13 bridge contracts ("Month 13"). Parse only. No detectors.

Model 13 = ICT Charter lecture on the 2022 YouTube model
(https://www.youtube.com/watch?v=kNlySn81dmo, Charter playlist 34/34).

Frozen boundary (docs/CHARTER_ESSENCE.md, docs/MONTH13_RESEARCH_CARD.md):
- Model 13 is a bridge/reference, NOT a peer PAM. It is never in pam_id.
- The single present|none switch is the EXISTING CharterState.model13_bridge
  (pam_contracts.py). This module does not add a second switch; it adds the
  optional labeled research card that sits beside it.
- model13_bridge is "present" only on an explicit literal "present".
  Card notes never mint it (same rule as M10–M12 identified_* fields).
- No session_ticket, no paper_swing, no M9 candidate, no ranking, no detector.
- Peer-vs-bridge status is a later decision (signed Slice 0), not code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

Pres = Literal["present", "none"]
Dir = Literal["bullish", "bearish", "none"]
PRES = set(Pres.__args__)
DIRS = set(Dir.__args__)

# Reference metadata (citation only — not rules).
MODEL13_REFERENCE = {
    "kind": "charter_bridge_reference",
    "primary_lecture": "https://www.youtube.com/watch?v=kNlySn81dmo",
    "primary_lecture_id": "kNlySn81dmo",
    "charter_playlist": "https://www.youtube.com/playlist?list=PLVgHx4Z63paasvEhegIwtiaGalrQphFg3",
    "base_series_playlist_2022": "https://www.youtube.com/playlist?list=PLVgHx4Z63paYiFGQ56PjTF1PGePL3r69s",
    "source_status": "user_supplied_lecture_notes_unsigned",
    "peer_status": "bridge_until_signed_slice0",
}

# Field classification is hermes_interpretation of user-supplied notes on
# kNlySn81dmo; to be confirmed by a signed Model 13 Slice 0.
REQUIRED = (
    "direction",
    "opposing_pd_objective_note",
    "time_window_note",
    "liquidity_raid_note",
    "short_term_mss_note",
    "fvg_entry_note",
    "risk_frame_note",
)
CONFIRMING = (
    "fvg_eq_side_note",
    "ltf_refinement_note",
    "target_ladder_note",
    "index_timing_note",
)


def _one(v, allowed):
    return v if v in allowed else "none"


@dataclass(frozen=True)
class Model13Card:
    """Labeled lecture-note evidence for a Model 13 reading. Not a detector result."""

    direction: Dir = "none"
    opposing_pd_objective_note: Pres = "none"
    time_window_note: Pres = "none"
    liquidity_raid_note: Pres = "none"
    short_term_mss_note: Pres = "none"
    fvg_entry_note: Pres = "none"
    risk_frame_note: Pres = "none"
    fvg_eq_side_note: Pres = "none"
    ltf_refinement_note: Pres = "none"
    target_ladder_note: Pres = "none"
    index_timing_note: Pres = "none"
    # descriptive completeness only — never recognition, never a ticket
    required_missing: tuple = ()
    confirming_present: tuple = ()
    reference: str = MODEL13_REFERENCE["primary_lecture_id"]
    reason: str = "unevaluated"


def explicit_bridge(value) -> Pres:
    """Only the literal string "present" counts. True/"yes"/"pam13" → "none"."""
    return "present" if value == "present" else "none"


def _card_block(raw: dict):
    ev = raw.get("evidence") or {}
    ch = raw.get("charter") or raw.get("ict_charter") or {}
    block = ev.get("model13_context") or ch.get("model13_context") or raw.get("model13_context")
    return block if isinstance(block, dict) else None


def parse_model13_card(raw: dict) -> Model13Card | None:
    block = _card_block(raw)
    if not block:
        return None
    vals = {k: _one(block.get(k), PRES) for k in REQUIRED + CONFIRMING if k != "direction"}
    direction = _one(block.get("direction"), DIRS)
    missing = tuple(
        k for k in REQUIRED
        if (direction == "none" if k == "direction" else vals[k] != "present")
    )
    conf = tuple(k for k in CONFIRMING if vals[k] == "present")
    return Model13Card(
        direction=direction,  # type: ignore[arg-type]
        required_missing=missing,
        confirming_present=conf,
        reason="required_notes_complete" if not missing else "required_notes_incomplete",
        **vals,  # type: ignore[arg-type]
    )
