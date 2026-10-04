"""Attach ``ftn.trace.v1`` to bar-derived Month 9 session rows WITHOUT touching the kernel or its log.

``research/kernel_log.session_ticket_log`` (H016/H016b-pinned, unchanged) produces the session rows. For every ticket
row this module re-evaluates the SAME causal kernel step at the row's entry time (``build_raw`` →
``kernel_step``, bars up to the entry close only), attaches the same session ticket, and checks that the
MarketState fingerprint equals the row's fingerprint, i.e. the trace describes exactly the state the kernel
decided on. Gates, blocked_by and the stop are copied from the row (the authoritative record). Bar-derived month
layers (``pipeline/layers_bar``) are added as annotation. Nothing is written back into the kernel inputs.
"""

from __future__ import annotations

import tempfile
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

from ftn.pipeline.layers_bar import bar_layers
from ftn.pipeline.trace import build_trace


class TraceMismatch(RuntimeError):
    """The re-evaluated kernel state does not match the logged ticket (would mean the trace is not faithful)."""


def trace_rows(rows: list[dict], hist, cfg: dict, other=None) -> list[dict]:
    """Return copies of ``rows`` with ``trace`` attached to ticket rows (non-ticket rows unchanged)."""
    from ftn.os.candidates import evaluate_candidates  # noqa: F401  (import order: os before models)
    from ftn.models.ftn import annotate_ftn
    from ftn.os.contracts import SessionTicket, freeze_market_state
    from ftn.os.handoff import build_handoff
    from ftn.os.mint_draft import draft_from_handoff, gate_input
    from ftn.research.daycontext import build_raw
    from ftn.research.kernel_log import FLAT_BOOK, kernel_step

    out = []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        for row in rows:
            row = dict(row)
            if row.get("ticket"):
                d, t = date.fromisoformat(row["date"]), datetime.fromisoformat(row["entry_time"])
                raw = build_raw(hist, d, t, row["session"])
                ctx, state, cands, sel = kernel_step(raw, cfg, tmp)
                if sel is None or sel.module != row["module"]:
                    raise TraceMismatch(f"{row['date']} {row['session']}: re-evaluated selection {sel} != {row['module']}")
                tk = SessionTicket(id=f"{d}-{hist.s.symbol}-{row['session']}-{sel.module}", kind="paper_entry",
                                   module=sel.module, session=row["session"])
                state2 = freeze_market_state(replace(ctx, session_ticket=tk))
                if state2.fingerprint != row.get("fingerprint"):
                    raise TraceMismatch(f"{row['date']} {row['session']}: fingerprint {state2.fingerprint} != "
                                        f"{row.get('fingerprint')}")
                gin = gate_input(state2, build_handoff(state2, cands, annotate_ftn(state2)))
                draft = draft_from_handoff(gin, cfg=cfg, book=FLAT_BOOK) or {}
                row["trace"] = build_trace(state2.context, cands, draft, fingerprint=state2.fingerprint,
                                           source="ftn.research.kernel_log (bar-derived) + ftn.pipeline.kernel_trace",
                                           bar_layers=bar_layers(row, hist, other), ticket_row=row)
            out.append(row)
    return out
