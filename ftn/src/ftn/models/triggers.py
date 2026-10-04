"""Interpretation entry triggers for CONSO / BB / PIP20 (REPORT D15).

The Month 9 docs (``docs/MONTH9_BLUEPRINT.md`` §6) give *eligibility* for CONSO, BB and
PIP20 but no sourced execution trigger. REV's trigger (LTF MSS) is itself labelled
``hermes_interpretation``. Each trigger here is the matching labelled interpretation and
runs only when ``config.yaml → interpretation_triggers.<model>`` is true (default false).

Every trigger reads frozen MarketState evidence only. None of them issues a ticket by
itself: the arbiter in ``os/candidates.py`` decides, REV still preempts, and MINT drafts
still go through the full gate chain.
"""

from __future__ import annotations

from ftn.os.contracts import MarketState

ORIGIN = "hermes_interpretation"


def conso_trigger(state: MarketState, conso: dict) -> dict:
    """fade_edge play + a 15m close back inside the box after the raid bar."""
    ev = state.context.evidence or {}
    box = ev.get("box") or {}
    if conso.get("play") != "fade_edge" or not box:
        return {"fired": False, "reason": "no_fade_edge_play", "origin": ORIGIN}
    closes = ev.get("post_raid_closes")
    if closes is None:
        return {"fired": False, "reason": "raid_bar_unknown", "origin": ORIGIN}
    lo, hi = float(box["low"]), float(box["high"])
    edge = conso.get("raided_edge")
    for c in closes:
        c = float(c)
        if edge == "low" and lo < c < hi:
            return {"fired": True, "reason": "close_back_inside_after_low_raid", "origin": ORIGIN}
        if edge == "high" and lo < c < hi:
            return {"fired": True, "reason": "close_back_inside_after_high_raid", "origin": ORIGIN}
    return {"fired": False, "reason": "no_close_back_inside", "origin": ORIGIN}


def bb_trigger(state: MarketState, bb: dict) -> dict:
    """engine=offset (soup in the IOF direction) + LTF MSS after the raid."""
    ev = state.context.evidence or {}
    if bb.get("engine") != "offset" or not bb.get("side"):
        return {"fired": False, "reason": "no_offset_engine", "origin": ORIGIN}
    if not ev.get("mss"):
        return {"fired": False, "reason": "no_mss_after_raid", "origin": ORIGIN}
    return {"fired": True, "reason": "offset_plus_mss", "origin": ORIGIN}


def pip20_trigger(state: MarketState, pip: dict) -> dict:
    """PIP20 eligible (window + raid + IOF + ADR) + displacement after the raid. Side = IOF."""
    ev = state.context.evidence or {}
    if not pip["candidate"].eligible:
        return {"fired": False, "reason": "pip20_not_eligible", "origin": ORIGIN}
    if not ev.get("displacement"):
        return {"fired": False, "reason": "no_displacement_after_raid", "origin": ORIGIN}
    return {"fired": True, "reason": "eligible_plus_displacement", "origin": ORIGIN}
