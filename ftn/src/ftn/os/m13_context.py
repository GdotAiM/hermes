"""Model 13 bridge context (labeled ingest).

Reads the explicit model13_bridge switch + optional research card.
Does not derive charter_recognition, does not touch recognized_pams,
does not create candidates, session tickets or swing tickets.
"""

from __future__ import annotations

from dataclasses import replace

from ftn.os.m13_contracts import MODEL13_REFERENCE, explicit_bridge, parse_model13_card


def bridge_value(raw: dict) -> str:
    ev = raw.get("evidence") or {}
    ch = raw.get("charter") or raw.get("ict_charter") or {}
    v = ev.get("model13_bridge")
    if v is None:
        v = ch.get("model13_bridge")
    return explicit_bridge(v)


def has_model13_evidence(raw: dict) -> bool:
    """True when the pack explicitly labels Model 13 (switch or card)."""
    ev = raw.get("evidence") or {}
    ch = raw.get("charter") or raw.get("ict_charter") or {}
    return bool(
        "model13_bridge" in ev or "model13_bridge" in ch
        or ev.get("model13_context") or ch.get("model13_context")
    )


def attach_model13(charter_state, raw: dict):
    """Return CharterState with explicit model13_bridge + card. Never adds a PAM."""
    if charter_state is None:
        return None
    return replace(
        charter_state,
        model13_bridge=bridge_value(raw),
        model13=parse_model13_card(raw),
    )


def model13_annotation(raw: dict) -> dict:
    """Read-only annotation for the legacy orchestrator payload (never a ticket)."""
    card = parse_model13_card(raw)
    return {
        "model13_bridge": bridge_value(raw),
        "card": None if card is None else {
            "direction": card.direction,
            "required_missing": list(card.required_missing),
            "confirming_present": list(card.confirming_present),
            "reason": card.reason,
        },
        "reference": MODEL13_REFERENCE,
        "note": "Model 13 is a Charter bridge/reference, not a PAM, candidate or ticket.",
    }
