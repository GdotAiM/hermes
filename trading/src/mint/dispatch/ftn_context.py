#!/usr/bin/env python3
"""Read-only FTN DayContext reader for MINT (handoff.v1).

Reads the single cross-part contract ``ftn/dispatch/out/handoff_latest.json``
(schemaVersion "1", kind "day_context_handoff") and writes a **context record**
to ``trading/dispatch/out/ftn_context_latest.json``.

What it does
  - validates the handoff (version/kind/mode + recursive ban walk — a handoff
    carrying BUY/SELL calls, confidence, best_pam/pam_rank, broker or order
    fields is rejected, exit 1, nothing written)
  - summarises the DayContext as *context* (symbol, date, session, profile,
    candidates, PAM1 completeness, FTN objectives, session-ticket id)
  - attaches the research board gate: which board locks say SURVIVES (via
    scan_clears) — with zero SURVIVES the gate is ``blocked``

What it never does
  - place, draft or size orders; import or call the broker adapter
  - turn FTN candidates, the FTN session_ticket, FTN objectives or PAM1 into
    order intents. Even when the board clears a strategy the record only says
    "human review required" — entries still need allowlist + RISK + human
    paper ack through the normal W4 path. PAM1 is ignored for execution unless
    a cleared strategy_id exists (HERMES_INTEGRATION_I0), and even then this
    reader only links it.

Path resolution for the handoff: --handoff PATH, $FTN_HANDOFF_PATH, then
<monorepo>/ftn/dispatch/out/handoff_latest.json.

Usage (from trading/):
  PYTHONPATH=src python3 -m mint.dispatch.ftn_context
  PYTHONPATH=src python3 -m mint.dispatch.ftn_context --handoff ../ftn/dispatch/samples/<file>.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from mint.dispatch import scan_clears as sc

TRADING_ROOT = sc.TRADING_ROOT
MONOREPO_ROOT = TRADING_ROOT.parent
DEFAULT_HANDOFF = MONOREPO_ROOT / "ftn" / "dispatch" / "out" / "handoff_latest.json"
CONFIG_PATH = TRADING_ROOT / "config.yaml"

# Hard paper limits (README / config.yaml). The reader refuses to run if config drifts.
PAPER_LIMITS = {
    "starting_usd": 100000.0,
    "max_trade_risk_pct": 0.5,
    "max_daily_loss_pct": 2.0,
    "max_portfolio_dd_pct": 5.0,
}

# Mirror of ftn/src/ftn/os/handoff_contract.py (kept local so MINT does not import FTN).
BANNED_KEYS = frozenset(
    {
        "buy", "sell", "side", "action", "signal", "signals", "recommendation",
        "trade_direction", "direction_recommendation", "trade_signal",
        "confidence", "confidence_score", "best_pam", "pam_rank", "rank", "ranking",
        "order", "orders", "order_id", "order_type", "client_order_id", "qty",
        "quantity", "limit_price", "stop_price", "stop_loss", "take_profit",
        "time_in_force", "tif", "position_size", "lots", "notional", "account_id",
        "place_order", "submit_order", "route", "routing", "auto_clear",
        "automatic_clearance",
    }
)
BANNED_KEY_SUBSTRINGS = ("broker", "confidence", "best_pam", "pam_rank")
BANNED_VALUE_RE = re.compile(r"^\s*(strong[\s_-]*)?(buy|sell)\s*$", re.IGNORECASE)


class HandoffRejected(ValueError):
    pass


def ban_violations(obj: Any, path: str = "$") -> list[str]:
    out: list[str] = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            kl = str(k).lower()
            if kl in BANNED_KEYS or any(s in kl for s in BANNED_KEY_SUBSTRINGS):
                out.append(f"banned key {path}.{k}")
            out.extend(ban_violations(v, f"{path}.{k}"))
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            out.extend(ban_violations(v, f"{path}[{i}]"))
    elif isinstance(obj, str) and BANNED_VALUE_RE.match(obj):
        out.append(f"banned buy/sell value at {path}")
    return out


def resolve_handoff_path(cli_value: Path | None) -> Path:
    if cli_value is not None:
        return cli_value.expanduser().resolve()
    env = os.environ.get("FTN_HANDOFF_PATH", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    return DEFAULT_HANDOFF


def load_handoff(path: Path) -> dict:
    try:
        h = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        raise HandoffRejected(f"unreadable handoff {path}: {e}") from e
    errs: list[str] = []
    if not isinstance(h, dict):
        raise HandoffRejected("handoff must be a JSON object")
    if h.get("schemaVersion") != "1":
        errs.append("schemaVersion must be '1'")
    if h.get("kind") != "day_context_handoff":
        errs.append("kind must be 'day_context_handoff' (mint_draft_* files are not the contract)")
    if h.get("mode") != "paper":
        errs.append("mode must be 'paper'")
    errs.extend(ban_violations(h))
    if errs:
        raise HandoffRejected("; ".join(errs))
    return h


def _cfg_number(text: str, key: str) -> float | None:
    m = re.search(rf"^\s*{re.escape(key)}\s*:\s*([0-9.]+)", text, re.M)
    return float(m.group(1)) if m else None


def paper_limits_from_config(path: Path = CONFIG_PATH) -> dict:
    text = path.read_text(encoding="utf-8")
    got = {k: _cfg_number(text, k) for k in PAPER_LIMITS}
    live = re.search(r"^live_enabled\s*:\s*(\S+)", text, re.M)
    mode = re.search(r"^mode\s*:\s*(\S+)", text, re.M)
    got["live_enabled"] = (live.group(1).lower() == "true") if live else False
    got["mode"] = mode.group(1) if mode else "paper"
    return got


def assert_paper_limits(limits: dict) -> None:
    for k, v in PAPER_LIMITS.items():
        if limits.get(k) != v:
            raise SystemExit(f"REFUSED: config {k}={limits.get(k)!r} differs from hard paper limit {v} (human-only change)")
    if limits.get("live_enabled") or limits.get("mode") != "paper":
        raise SystemExit("REFUSED: MINT config is not paper-only (live_enabled must be false, mode paper)")


def board_gate(research_root: Path) -> dict:
    """SURVIVES board locks = the only thing that can ever clear a strategy."""
    summaries = research_root / "summaries"
    tickets = sc.scan_board_locks(summaries) if summaries.is_dir() else []
    cleared = [t.hypothesis_hint for t in tickets if t.kind == "entry_candidate"]
    return {
        "research_root": str(research_root),
        "board_locks_scanned": len(tickets),
        "survives": cleared,
        "status": "cleared_strategies_exist" if cleared else "blocked_no_survives",
    }


def build_context_record(h: dict, source: Path, gate: dict, limits: dict) -> dict:
    ms = h.get("market_state") or {}
    comp = ms.get("pam1_completeness") or {}
    ticket = h.get("session_ticket") or {}
    cleared = gate["survives"]
    return {
        "kind": "ftn_day_context",  # context only — never an order / order intent
        "read_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "handoff_path": str(source),
        "handoff_kind": h.get("kind"),
        "schemaVersion": h.get("schemaVersion"),
        "fingerprint": h.get("fingerprint"),
        "symbol": h.get("symbol"),
        "date": h.get("date"),
        "session": h.get("session"),
        "context": {
            "profile": ms.get("profile"),
            "candidates": [
                {"module": c.get("module"), "state": c.get("state"), "eligible": c.get("eligible")}
                for c in h.get("candidates") or []
            ],
            "ftn_objectives": (h.get("ftn_annotation") or {}).get("four") or [],
            "ftn_session_ticket_id": ticket.get("id"),
            "pam1_required_complete": comp.get("required_complete"),
            "charter_present": ms.get("charter") is not None,
        },
        "board_gate": gate,
        "execution": {
            "actionable_for_mint": False,
            "order_intents_emitted": 0,
            "pam1_used_for_execution": False,
            "ftn_candidates_used_for_execution": False,
            "why": (
                "Board has zero SURVIVES: DayContext is logged as context only."
                if not cleared
                else "Board SURVIVES exists for " + ", ".join(cleared)
                + ": DayContext may be attached for human review; entries still need allowlist + RISK"
                " + human paper ack via W4. This reader never places or drafts orders."
            ),
        },
        "paper_limits": {k: limits.get(k) for k in (*PAPER_LIMITS, "live_enabled", "mode")},
        "note": "Read-only FTN DayContext context record. Tickets != orders. No broker call.",
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Read FTN DayContext handoff.v1 as MINT context (no orders)")
    ap.add_argument("--handoff", type=Path, default=None, help="handoff.v1 JSON (default: $FTN_HANDOFF_PATH or ../ftn/dispatch/out/handoff_latest.json)")
    ap.add_argument("--hermes-x", "--research", dest="hermes_x", type=Path, default=None, help="research spine root (as scan_clears)")
    ap.add_argument("--out", type=Path, default=None, help="Output dir (default: dispatch/out)")
    args = ap.parse_args(argv)

    limits = paper_limits_from_config()
    assert_paper_limits(limits)

    src = resolve_handoff_path(args.handoff)
    try:
        h = load_handoff(src)
    except HandoffRejected as e:
        print(f"REJECTED {src}: {e}", file=sys.stderr)
        return 1

    gate = board_gate(sc.resolve_research_root(args.hermes_x))
    rec = build_context_record(h, src, gate, limits)
    out = args.out or (TRADING_ROOT / "dispatch" / "out")
    out.mkdir(parents=True, exist_ok=True)
    path = out / "ftn_context_latest.json"
    path.write_text(json.dumps(rec, indent=2, default=str) + "\n", encoding="utf-8")
    print(
        f"Wrote {path} (ftn_day_context {rec['symbol']} {rec['date']} {rec['session']}; "
        f"board gate {gate['status']}; order_intents_emitted=0)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
