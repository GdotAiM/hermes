"""Run the unchanged Month 9 kernel over historical sessions → per-session ticket log.

For each trading day and each killzone (london 02:00–05:00, ny_am 07:00–10:00 NY), the
kernel is evaluated at every 15m close with only the bars up to that close. The first
selection in a session becomes that session's ticket (one ticket per session,
``hermes_governance``). The ticket is attached in memory exactly as ``ftn brief`` does it,
then the research-draft gate chain runs. No file is persisted, no order is created, and the
allowlist is left as configured (empty → every draft is ``blocked_by: allowlist``).
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import replace
from datetime import date, datetime, time, timedelta
from pathlib import Path

from ftn.os.candidates import evaluate_candidates  # noqa: I001  (import ftn.os first: models↔os cycle)
from ftn.models.ftn import annotate_ftn
from ftn.os.contracts import SessionTicket, freeze_market_state
from ftn.os.dtr import build_context
from ftn.os.handoff import build_handoff
from ftn.os.mint_draft import _side, draft_from_handoff, gate_input
from ftn.research.daycontext import History, build_raw

KILLZONES = {"london": (time(2, 0), time(5, 0)), "ny_am": (time(7, 0), time(10, 0))}
REV_UNDETERMINED = "rev_direction_undetermined_raid_both_or_neither"
FLAT_BOOK = {"daily_loss_pct": 0.0, "drawdown_pct": 0.0, "source": "scorer_flat_book"}


def kernel_step(raw: dict, cfg: dict, tmpdir: Path):
    p = tmpdir / "ctx.json"
    p.write_text(json.dumps(raw))
    ctx = build_context(p)
    state = freeze_market_state(ctx)
    cands = evaluate_candidates(state, cfg)
    sel = next((c for c in cands if c.state == "selected"), None)
    return ctx, state, cands, sel


def session_ticket_log(hist: History, cfg: dict, days: list[date] | None = None) -> list[dict]:
    rows: list[dict] = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for d in days or hist.days:
            for sname, (a, b) in KILLZONES.items():
                t = datetime.combine(d, a) + timedelta(minutes=15)
                end = datetime.combine(d, b)
                row = {"date": d.isoformat(), "symbol": hist.s.symbol, "session": sname,
                       "ticket": False, "module": None, "reason": "no_selected_candidate"}
                while t <= end:
                    raw = build_raw(hist, d, t, sname)
                    if raw is None:
                        row["reason"] = "insufficient_history_or_bars"
                        break
                    ctx, state, cands, sel = kernel_step(raw, cfg, tmp)
                    if any(c.module == "REV" and c.reason == REV_UNDETERMINED for c in cands):
                        row["rev_direction_undetermined_seen"] = True
                    if sel is not None:
                        tk = SessionTicket(id=f"{d}-{hist.s.symbol}-{sname}-{sel.module}",
                                           kind="paper_entry", module=sel.module, session=sname)
                        state2 = freeze_market_state(replace(ctx, session_ticket=tk))
                        gin = gate_input(state2, build_handoff(state2, cands, annotate_ftn(state2)))
                        draft = draft_from_handoff(gin, cfg=cfg, book=FLAT_BOOK) or {}
                        orient, _basis = _side(sel.module, gin)  # internal orientation (research only)
                        ev = ctx.evidence or {}
                        row.update({
                            "ticket": True, "module": sel.module, "reason": sel.reason,
                            "entry_time": t.isoformat(), "entry": raw["last"],
                            "side": orient, "direction": {"buy": "bullish", "sell": "bearish"}.get(orient or "", "unclear"),
                            "stop": draft.get("stop_reference"),
                            "blocked_by": draft.get("blocked_by"),
                            "gates": [f"{g['gate']}:{'pass' if g['pass'] else 'FAIL'}:{g['reason']}" for g in draft.get("gates", [])],
                            "raid_level": (ev.get("raid") or {}).get("level"),
                            "raid_price": (ev.get("raid") or {}).get("price"),
                            "raid_bar_index": (ev.get("mss_meta") or {}).get("raid_bar_index"),
                            "iof_state": ctx.pair_institutional.state,
                            "iof_confidence": ctx.pair_institutional.confidence,
                            "origin_pd_array": ctx.origin_pd_array,
                            "fingerprint": state2.fingerprint,
                        })
                        break
                    t += timedelta(minutes=15)
                rows.append(row)
    return rows


LEGACY_SIDE_FAIL = "direction:FAIL:rev_direction_conflicts_with_raid"
NON_RESEARCH_GATES = ("allowlist:", "contract:")  # empty allowlist; I0 contract always fails


def tradeable(row: dict, legacy_side: bool = False) -> bool:
    """Ticket whose draft passes every gate except the (empty) allowlist and the I0 contract.

    ``legacy_side=True`` also admits drafts blocked only by the REV side-vs-raid check
    (REPORT D18). That is a disclosure stream showing the kernel side as it was before.
    """
    if not row.get("ticket"):
        return False
    fails = [g for g in row.get("gates", []) if ":FAIL:" in g]
    ok = all(g.startswith(NON_RESEARCH_GATES) or (legacy_side and g == LEGACY_SIDE_FAIL) for g in fails)
    return bool(ok and row.get("side") and row.get("stop") is not None)
