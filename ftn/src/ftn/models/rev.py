
"""Slice 4 — narrow REV. Consumes frozen MarketState only."""

from __future__ import annotations

from ftn.os.contracts import Candidate, MarketState

NAMED = {"pdh", "pdl", "week_so_far_high", "week_so_far_low", "ith", "itl"}
LOW_RAIDS = {"pdl", "week_so_far_low", "itl"}
HIGH_RAIDS = {"pdh", "week_so_far_high", "ith"}


def raided_sides(raid: dict | None) -> set[str]:
    """Which extremes the raid took: subset of {"low", "high"} (primary level + ``also``)."""
    raid = raid or {}
    if not raid.get("taken"):
        return set()
    levels = [raid.get("level"), *(raid.get("also") or [])]
    return {"low" for x in levels if x in LOW_RAIDS} | {"high" for x in levels if x in HIGH_RAIDS}


def rev_direction(raid: dict | None) -> str | None:
    """REV direction comes from the raid (REPORT D18 fix): low raided → bullish reversal,
    high raided → bearish reversal. Neither or both raided → None (undetermined, no ticket)."""
    sides = raided_sides(raid)
    if sides == {"low"}:
        return "bullish"
    if sides == {"high"}:
        return "bearish"
    return None


def evaluate_rev(state: MarketState) -> dict:
    ctx = state.context
    ev = ctx.evidence or {}
    raid = ev.get("raid") or {}
    named = set((ctx.ranges or {}).get("named_extremes") or {})
    raid_taken = bool(raid.get("taken"))
    level = raid.get("level")
    raid_named = level in named or level in NAMED
    htf = ev.get("htf_pd_at_raid") or ctx.origin_pd_array
    session_exception = ev.get("session") in {"ny_am", "london_close"} and bool(htf)
    iof_ok = ctx.pair_institutional.state != "unclear"
    mss = bool(ev.get("mss"))
    direction = rev_direction(raid)

    eligibility = {
        "named_extreme_raid": raid_taken and raid_named,
        "htf_pd_at_or_around_raid": bool(htf),
        "contextual_exception": bool(session_exception),
        "institutional_context_clear": iof_ok,
    }
    eligible = eligibility["named_extreme_raid"] and (
        eligibility["htf_pd_at_or_around_raid"] or eligibility["contextual_exception"]
    ) and eligibility["institutional_context_clear"]

    execution = {"mss_or_displacement": mss, "direction": direction,
                 "raided_sides": sorted(raided_sides(raid)),
                 "confirmed": eligible and mss and direction is not None}

    if execution["confirmed"]:
        cand = Candidate("REV", "selected", True, "named_extreme_raid+htf_pd+mss", "hermes_interpretation")
    elif eligible and mss:
        # both (or neither) extremes raided: the reversal side is undetermined → no ticket
        cand = Candidate("REV", "ineligible", False, "rev_direction_undetermined_raid_both_or_neither",
                         "hermes_interpretation")
    elif eligible:
        cand = Candidate("REV", "unevaluated", True, "eligible_waiting_mss", "ict_source")
    else:
        cand = Candidate("REV", "ineligible", False, "no_named_extreme_plus_htf_context", "ict_source")

    return {
        "candidate": cand,
        "eligibility": eligibility,
        "execution": execution,
        "evidence": {
            "raid": raid,
            "htf_pd": htf,
            "session": ev.get("session"),
            "mss": mss,
            "direction": direction,
            "fingerprint": state.fingerprint,
        },
    }
