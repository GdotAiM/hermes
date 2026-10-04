
"""Candidate logger — frozen MarketState only. Does not load *.expected.json."""

from __future__ import annotations

from ftn.models.bb import evaluate_bb
from ftn.models.conso import evaluate_conso
from ftn.models.pip20 import evaluate_pip20
from ftn.models.rev import evaluate_rev
from ftn.os.contracts import Candidate, MarketState


def evaluate_candidates(state: MarketState, cfg: dict | None = None) -> tuple[Candidate, ...]:
    rev = evaluate_rev(state)["candidate"]
    conso_r = evaluate_conso(state)
    bb_r = evaluate_bb(state)
    pip_r = evaluate_pip20(state)
    conso, bb, pip = conso_r["candidate"], bb_r["candidate"], pip_r["candidate"]

    if rev.state == "selected" and conso.eligible:
        conso = Candidate("CONSO", "suppressed", True, "REV_preemption", "hermes_governance")

    # PIP20 is the stricter offset subset; if both eligible, suppress BB for the ticket
    if pip.eligible and bb.eligible and rev.state != "selected" and not rev.eligible:
        bb = Candidate("BB", "suppressed", True, "PIP20_stricter_offset", "hermes_governance")

    if rev.eligible:
        if bb.state != "suppressed":
            bb = Candidate("BB", "invalidated", False, "named_extreme_plus_htf_array", "hermes_governance")
        if pip.eligible:
            pip = Candidate("PIP20", "invalidated", False, "named_extreme_plus_htf_array", "hermes_governance")

    # Interpretation triggers (REPORT D15): off by default; REV preempts; priority
    # CONSO > PIP20 > BB (MONTH9_BLUEPRINT §7 default_preemption_policy). One selection.
    if cfg is None:
        from ftn.config_load import load_config
        cfg = load_config()
    trig = cfg.get("interpretation_triggers") or {}
    if rev.state != "selected" and any(trig.values()):
        from ftn.models.triggers import bb_trigger, conso_trigger, pip20_trigger
        if trig.get("conso") and conso.eligible and conso.state != "suppressed" \
                and conso_trigger(state, conso_r)["fired"]:
            conso = Candidate("CONSO", "selected", True, f"{conso.reason}+interp_trigger", "hermes_interpretation")
        elif trig.get("pip20") and pip.eligible and pip.state not in {"suppressed", "invalidated"} \
                and pip20_trigger(state, pip_r)["fired"]:
            pip = Candidate("PIP20", "selected", True, f"{pip.reason}+interp_trigger", "hermes_interpretation")
        elif trig.get("bb") and bb.eligible and bb.state not in {"suppressed", "invalidated"} \
                and bb_trigger(state, bb_r)["fired"]:
            bb = Candidate("BB", "selected", True, f"{bb.reason}+interp_trigger", "hermes_interpretation")

    ftn = Candidate("FTN", "annotate", False, "objectives_only", "hermes_governance")
    return (rev, conso, pip, bb, ftn)
