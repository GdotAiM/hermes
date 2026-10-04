"""Read-only, log-only view of FTN's research-draft gate chain (FTN → MINT, paper only).

FTN writes ``ftn/dispatch/drafts/ftn_draft_latest.json`` only when the operator opts in
(``FTN_WRITE_MINT_DRAFT=1``). Under HERMES_INTEGRATION_I0 that draft is research context:
``kind: ftn_research_draft``, no side, ``actionable_for_mint`` always false, and its last
gate (``contract``) always fails. The DayContext itself is read by ``mint.dispatch.ftn_context``.

This module only *records* the draft's gate chain next to the MINT scan so a human can see
why FTN stopped. It never places, stages, sizes or routes an order; it never edits an
allowlist; and it never produces an ``entry_candidate``. ``mint_decision`` is always
``log_only``. A draft that claims otherwise (actionable, carries a side, contract gate
passing, gates out of order) is flagged ``consistent: false`` and still only logged.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

TRADING_ROOT = Path(__file__).resolve().parents[3]
GATES = ("kernel_ticket", "direction", "risk", "allowlist", "mode", "contract")
CONTRACT_REASON = "hermes_integration_i0_ftn_never_actionable"
DRAFT_NAME = "ftn_draft_latest.json"
MINT_DECISION = "log_only"  # the only value this module can return


def resolve_ftn_drafts(cli_value: Path | None = None) -> Path:
    if cli_value:
        return Path(cli_value)
    env = os.environ.get("FTN_DRAFT_DIR", "").strip()
    if env:
        return Path(env)
    return TRADING_ROOT.parent / "ftn" / "dispatch" / "drafts"


def _gate_list(draft: dict) -> list[dict]:
    return [{"gate": g.get("gate"), "pass": bool(g.get("pass")), "reason": g.get("reason")}
            for g in draft.get("gates") or [] if isinstance(g, dict)]


def _problems(draft: dict, gates: list[dict]) -> list[str]:
    p = []
    failed = [g for g in gates if not g["pass"]]
    if draft.get("kind") != "ftn_research_draft":
        p.append("kind_not_ftn_research_draft")
    if tuple(g["gate"] for g in gates) != GATES:
        p.append("gate_order")
    if draft.get("actionable_for_mint") is not False:
        p.append("claims_actionable")
    if "side" in draft:
        p.append("carries_side")
    if not gates or gates[-1]["pass"] or gates[-1]["reason"] != CONTRACT_REASON:
        p.append("contract_gate_not_failing")
    if failed and draft.get("blocked_by") != f"{failed[0]['gate']}:{failed[0]['reason']}":
        p.append("blocked_by_not_first_failure")
    if draft.get("mode") not in (None, "paper"):
        p.append("non_paper_mode")
    return p


def read_ftn_gate(ftn_drafts: Path | None = None) -> dict:
    d = resolve_ftn_drafts(ftn_drafts)
    draft_p = d / DRAFT_NAME
    base = {"source": str(draft_p), "orders": "none (read-only consumer)", "mode": "paper",
            "mint_decision": MINT_DECISION}
    if not draft_p.is_file():
        return {**base, "present": False, "reason": "no_ftn_research_draft"}
    try:
        draft = json.loads(draft_p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {**base, "present": False, "reason": f"unreadable_ftn_research_draft: {exc}"}
    gates = _gate_list(draft)
    problems = _problems(draft, gates)
    return {**base, "present": True, "date": draft.get("date"), "symbol": draft.get("symbol"),
            "module": draft.get("module"), "direction_hypothesis": draft.get("direction_hypothesis"),
            "blocked_by": draft.get("blocked_by"),
            "gates_before_contract_pass": draft.get("gates_before_contract_pass"),
            "gates": [f"{g['gate']}:{'pass' if g['pass'] else 'FAIL'}:{g['reason']}" for g in gates],
            "consistent": not problems, "problems": problems,
            "reason": "ftn_gate_chain_inconsistent" if problems else f"ftn_blocked_by:{draft.get('blocked_by')}"}


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description="Log FTN research-draft gate chain (read-only; no orders)")
    ap.add_argument("--ftn-drafts", type=Path, default=None, help="FTN drafts dir (default ../ftn/dispatch/drafts)")
    args = ap.parse_args(argv)
    print(json.dumps(read_ftn_gate(args.ftn_drafts), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
