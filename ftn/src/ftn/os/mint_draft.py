"""FTN research draft + gate-chain status. Tickets ≠ orders. No broker call.

Main's HERMES_INTEGRATION_I0 (frozen) stays authoritative:
- handoff.v1 is the ONLY cross-part object. This draft is not a contract and MINT
  rejects it (kind != "day_context_handoff").
- No BUY/SELL anywhere in the draft: the direction travels as
  ``direction_hypothesis`` ("bullish" | "bearish" | "unclear"), a research label.
- Not written by default. ``ftn brief`` writes it only when ``FTN_WRITE_MINT_DRAFT=1``,
  and then to ``dispatch/drafts/`` (or ``$FTN_DRAFT_DIR``), never to ``dispatch/out/``.
- ``actionable_for_mint`` is always False (gate 6).

Ported from the FTN review (PR #1): one gate chain that brief, the desk snapshot and
the scorer all read through ``draft_status``. Gates, in order:

1. ``kernel_ticket`` — the Month 9 kernel selected a model AND holds its session ticket.
2. ``direction``     — determined from evidence, never defaulted (REV must oppose the
                       raided extreme, REPORT D18; CONSO from the raided box edge).
3. ``risk``          — config.yaml caps 0.5% / 2% / 5% with a protective stop reference.
4. ``allowlist``     — config.yaml ``mint_allowlist`` (empty today; Path A board SURVIVES
                       or Path B *signed* human paper-pilot stamp, unexpired).
5. ``mode``          — paper only; live stays dual-locked and refused.
6. ``contract``      — HERMES_INTEGRATION_I0: FTN is never MINT-actionable. Always fails
                       until a human amends I0 (REPORT D20).

``blocked_by`` names the first failing gate.
"""

from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path
from typing import Any

from ftn.config_load import dispatch_out, load_config, repo_root
from ftn.paths import draft_dir

DRAFT_KIND = "ftn_research_draft"
GATES = ("kernel_ticket", "direction", "risk", "allowlist", "mode", "contract")
ENTRY_MODULES = {"REV", "CONSO", "BB", "PIP20"}
REV_STOP_BUFFER_PIPS = 1  # FTN-D22: fixed in the prereg; no other values are run
PIP20_STOP_PIPS = 20  # docs/MONTH9_BLUEPRINT.md §6 "PIP20: +20 objective, 20-pip stop"
_LABEL = {"buy": "bullish", "sell": "bearish"}


def drafts_enabled() -> bool:
    return os.environ.get("FTN_WRITE_MINT_DRAFT", "").strip() == "1"


def execution_context(state) -> dict:
    """Evidence the gate chain needs. Internal only, never written into handoff.v1."""
    from ftn.models.conso import raided_edge

    c = state.context
    ev = c.evidence or {}
    sym = c.symbol or ""
    return {
        "last": c.last,
        "raid": {k: (ev.get("raid") or {}).get(k) for k in ("level", "price", "taken", "also")},
        "box": {k: (ev.get("box") or {}).get(k) for k in ("high", "low")} if ev.get("box") else None,
        "conso_raided_edge": raided_edge(ev.get("box"), ev.get("raid")),
        "stop_reference": ev.get("stop_reference"),
        "raid_extreme": ev.get("raid_extreme"),
        "pip": float(ev.get("pip") or (0.01 if "JPY" in sym else 0.1 if "XAU" in sym else 0.0001)),
    }


def gate_input(state, handoff: dict) -> dict:
    """handoff.v1 + internal execution context (in memory only)."""
    ec = execution_context(state)
    return {**handoff, "last": ec["last"], "execution_context": ec}


def _gate(name: str, ok: bool, reason: str, **extra) -> dict:
    return {"gate": name, "pass": bool(ok), "reason": reason, **extra}


def _side(module: str, handoff: dict) -> tuple[str | None, str]:
    """Internal long/short orientation for the risk arithmetic (never exported as a side)."""
    ms = handoff.get("market_state") or {}
    iof = (ms.get("institutional") or {}).get("state")
    if module == "CONSO":
        edge = (handoff.get("execution_context") or {}).get("conso_raided_edge")
        side = {"low": "buy", "high": "sell"}.get(edge or "")
        return side, f"conso_raided_edge={edge}"
    if module == "REV":
        # REV direction comes from the raid, not the IOF (REPORT D18 fix)
        from ftn.models.rev import rev_direction
        raid = (handoff.get("execution_context") or {}).get("raid") or {}
        d = rev_direction(raid)
        return {"bullish": "buy", "bearish": "sell"}.get(d or ""), f"raid={raid.get('level')}"
    if module in {"BB", "PIP20"}:
        side = "buy" if iof == "bullish" else "sell" if iof == "bearish" else None
        return side, f"daytrade_iof={iof}"
    return None, "not_an_entry_model"


LOW_RAIDS = {"pdl", "week_so_far_low", "itl"}
HIGH_RAIDS = {"pdh", "week_so_far_high", "ith"}


def _stop(module: str, side: str | None, handoff: dict) -> tuple[float | None, str]:
    ctx = handoff.get("execution_context") or {}
    if ctx.get("stop_reference") is not None:
        return float(ctx["stop_reference"]), "labeled_stop_reference"
    raid = ctx.get("raid") or {}
    last = handoff.get("last")
    if module == "PIP20" and last is not None and side:
        d = PIP20_STOP_PIPS * float(ctx.get("pip") or 0.0001)
        return (float(last) - d if side == "buy" else float(last) + d), "pip20_20_pip_stop"
    if module == "CONSO":
        box = ctx.get("box") or {}
        edge = ctx.get("conso_raided_edge")
        if edge in ("low", "high") and box.get(edge) is not None:
            return float(box[edge]), f"raided_box_{edge}"
        return None, "no_raided_box_edge"
    if module == "REV" and side and raid.get("taken") and raid.get("price") is not None:
        # FTN-D22 (prereg research/protocols/preregs/FTN_D22_REV_STOP_BEYOND_RAID_PREREG_2026-10-04.json):
        # stop beyond the raid's own extreme by a 1-pip buffer; the raided level only without bars
        buf = REV_STOP_BUFFER_PIPS * float(ctx.get("pip") or 0.0001)
        ext = ctx.get("raid_extreme") or {}
        want = "low" if side == "buy" else "high"
        if ext.get("price") is not None and ext.get("side") == want:
            px, src = float(ext["price"]), "beyond_raid_extreme"
        else:
            px, src = float(raid["price"]), "beyond_raided_level_no_bars"
        return (px - buf if side == "buy" else px + buf), f"{src}_{raid.get('level')}"
    if module == "BB" and raid.get("taken") and raid.get("price") is not None:
        return float(raid["price"]), f"raided_{raid.get('level')}"
    return None, "no_stop_reference"


def load_book() -> dict:
    """Paper book state (MINT-owned P&L mirrored as a file). Absent → flat book."""
    p = dispatch_out() / "paper_book.json"
    book = {"daily_loss_pct": 0.0, "drawdown_pct": 0.0, "source": "default_flat"}
    if p.is_file():
        raw = json.loads(p.read_text())
        book.update({k: float(raw[k]) for k in ("daily_loss_pct", "drawdown_pct") if k in raw})
        book["source"] = str(p)
    return book


def risk_gate(module: str, side: str | None, handoff: dict, cfg: dict, book: dict) -> dict:
    caps = {k: cfg.get(k) for k in ("max_trade_risk_pct", "max_daily_loss_pct", "max_portfolio_dd_pct")}
    if any(v is None for v in caps.values()):
        return _gate("risk", False, "hold_missing_risk_caps", caps=caps)
    risk_pct = float(caps["max_trade_risk_pct"])  # propose AT the cap, never above
    equity = float(cfg.get("equity_usd", 100000))
    entry = handoff.get("last")
    stop, stop_src = _stop(module, side, handoff)
    base = {"caps": caps, "risk_pct": risk_pct, "equity_usd": equity, "entry_reference": entry,
            "stop_reference": stop, "stop_source": stop_src, "book": book}
    if side is None:
        return _gate("risk", False, "hold_side_undetermined", **base)
    if entry is None or stop is None:
        return _gate("risk", False, "hold_missing_stop_or_entry", **base)
    dist = (float(entry) - stop) if side == "buy" else (stop - float(entry))
    if dist <= 0:
        return _gate("risk", False, "stop_not_protective", **base)
    if book["daily_loss_pct"] + risk_pct > float(caps["max_daily_loss_pct"]):
        return _gate("risk", False, "daily_loss_cap", **base)
    if book["drawdown_pct"] + risk_pct > float(caps["max_portfolio_dd_pct"]):
        return _gate("risk", False, "max_drawdown_cap", **base)
    risk_usd = equity * risk_pct / 100.0
    return _gate("risk", True, "within_caps", **base, risk_usd=risk_usd,
                 stop_distance=dist, size_units=risk_usd / dist)


def stamp_is_signed(text: str) -> bool:
    """A pilot stamp counts only if a human signed it.

    Refused: a ``STATUS: UNSIGNED`` marker, a missing ``Signature:`` line, or a signature
    that is blank, underscores, or a ``<placeholder>``.
    """
    import re

    if re.search(r"^\s*STATUS:\s*UNSIGNED\b", text, re.M | re.I):
        return False
    sigs = re.findall(r"^\s*Signature:\s*(.*)$", text, re.M)
    if not sigs:
        return False
    val = sigs[-1].strip()
    return bool(val) and not re.fullmatch(r"[_\s.-]*|<[^>]*>", val)


def allowlist_gate(module: str, cfg: dict, today: date | None = None) -> dict:
    today = today or date.today()
    entry = next((e for e in cfg.get("mint_allowlist") or [] if e.get("id") == module), None)
    if entry is None:
        return _gate("allowlist", False, "not_on_mint_allowlist", entry=None)
    ref = entry.get("board_ref") if entry.get("kind") == "survives" else entry.get("stamp")
    ref_path = Path(ref) if ref and Path(ref).is_absolute() else repo_root() / str(ref or "")
    if not ref or not ref_path.is_file():
        return _gate("allowlist", False, f"{entry.get('kind')}_reference_missing", entry=entry)
    if entry.get("kind") == "paper_pilot" and not stamp_is_signed(ref_path.read_text(encoding="utf-8")):
        return _gate("allowlist", False, "paper_pilot_stamp_unsigned", entry=entry)
    if entry.get("kind") == "paper_pilot" and date.fromisoformat(entry["expires"]) < today:
        return _gate("allowlist", False, "paper_pilot_expired", entry=entry)
    return _gate("allowlist", True, f"allowlisted_{entry.get('kind')}", entry=entry)


def mode_gate(cfg: dict) -> dict:
    if cfg.get("mode") != "paper":
        return _gate("mode", False, "non_paper_mode_refused", mode=cfg.get("mode"))
    return _gate("mode", True, "paper", mode="paper", live_orders="refused")


def direction_gate(module: str, orient: str | None, basis: str, handoff: dict) -> dict:
    """Direction must be determined AND, for REV, oppose the raided extreme (REPORT D18).

    REV is "Trading Market Reversals": a sell-side (low) raid reverses up (bullish) and a
    buy-side (high) raid reverses down (bearish). ``detect_mss`` already looks for the MSS
    in that reversal direction, so a direction that agrees with the raid is incoherent.
    """
    if orient is None:
        return _gate("direction", False, "undetermined", basis=basis)
    if module == "REV":
        raid = (handoff.get("execution_context") or {}).get("raid") or {}
        level = raid.get("level")
        also = set(raid.get("also") or [])
        if (level in LOW_RAIDS and also & HIGH_RAIDS) or (level in HIGH_RAIDS and also & LOW_RAIDS):
            return _gate("direction", False, "rev_raid_both_sides", basis=basis,
                         direction_proposed=_LABEL[orient])
        want = "buy" if level in LOW_RAIDS else "sell" if level in HIGH_RAIDS else None
        if want is None:
            return _gate("direction", False, "rev_raid_level_unknown", basis=basis,
                         direction_proposed=_LABEL[orient])
        if want != orient:
            return _gate("direction", False, "rev_direction_conflicts_with_raid", basis=basis,
                         direction_proposed=_LABEL[orient], raid_level=level, reversal_direction=_LABEL[want])
    return _gate("direction", True, "determined", basis=basis)


def contract_gate() -> dict:
    return _gate("contract", False, "hermes_integration_i0_ftn_never_actionable",
                 doc="docs/HERMES_INTEGRATION_I0.md")


def draft_from_handoff(handoff: dict, cfg: dict | None = None, book: dict | None = None) -> dict | None:
    """``handoff`` should come from ``gate_input`` (handoff.v1 + execution context)."""
    selected = next((c for c in handoff.get("candidates") or [] if c.get("state") == "selected"), None)
    if not selected:
        return None
    cfg = cfg if cfg is not None else load_config()
    book = book if book is not None else load_book()
    module = selected["module"]
    ticket = handoff.get("session_ticket") or {}
    kt_ok = module in ENTRY_MODULES and bool(ticket) and ticket.get("module") == module
    kt_reason = ("kernel_session_ticket" if kt_ok else
                 "no_session_ticket" if not ticket else
                 "not_an_entry_model" if module not in ENTRY_MODULES else
                 "session_ticket_module_mismatch")
    orient, basis = _side(module, handoff)
    gates = [
        _gate("kernel_ticket", kt_ok, kt_reason, session_ticket_id=ticket.get("id")),
        direction_gate(module, orient, basis, handoff),
        risk_gate(module, orient, handoff, cfg, book),
        allowlist_gate(module, cfg),
        mode_gate(cfg),
        contract_gate(),
    ]
    failed = [g for g in gates if not g["pass"]]
    risk = gates[2]
    ms = handoff.get("market_state") or {}
    iof = (ms.get("institutional") or {}).get("state") or "unclear"
    has_ctx = "execution_context" in handoff
    if module in ENTRY_MODULES and has_ctx:
        hyp, src = _LABEL.get(orient or "", "unclear"), basis.split("=")[0]
    else:
        # plain handoff.v1 (no gate evidence): main's I0 meaning — the IOF label, context only
        hyp, src = iof, "iof_label_only_no_execution_context"
    return {
        "kind": DRAFT_KIND,
        "mode": "paper",
        "actionable_for_mint": False,
        "blocked_by": f"{failed[0]['gate']}:{failed[0]['reason']}",
        "blocked": [f"{g['gate']}:{g['reason']}" for g in failed],
        "gates": gates,
        "gates_before_contract_pass": all(g["pass"] for g in gates[:-1]),
        "requires": ["board SURVIVES", "allowlist", "RISK", "human_ack"],
        "from": "ftn-agent",
        "to": "human_review",
        "symbol": handoff.get("symbol"),
        "date": handoff.get("date"),
        "session": handoff.get("session"),
        "direction_hypothesis": hyp,
        "direction_source": src,
        "iof_state": iof,
        "module": module,
        "entry_reference": risk.get("entry_reference"),
        "stop_reference": risk.get("stop_reference"),
        "risk_pct": risk.get("risk_pct"),
        "risk_usd": risk.get("risk_usd"),
        "reason": selected.get("reason"),
        "origin": selected.get("origin"),
        "fingerprint": handoff.get("fingerprint"),
        "session_ticket_id": ticket.get("id"),
        "contrary": handoff.get("contrary"),
        "ftn_objectives": (handoff.get("ftn_annotation") or {}).get("four") or [],
        "notes": "Research draft only — not an order, not a contract. direction_hypothesis is a label, not a trade side.",
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
