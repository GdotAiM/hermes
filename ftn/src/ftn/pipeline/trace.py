"""F3: per-ticket pipeline trace (``ftn.trace.v1``). READ-ONLY over the kernel's result.

The trace is assembled AFTER ``evaluate_candidates`` + the research-draft gate chain have run, from the frozen
DayContext they used, and is never written back. It is not handoff.v1 (no handoff change, F6 is out of scope),
it is not read by MINT, and it never changes a candidate, ticket, stop, gate or fingerprint
(``tests/test_ticket_invariance.py`` re-runs the H016b registration-input streams with the trace on).

Stages and roles (what each month actually does in code today):
  bias     IOF state/confidence (feeds REV eligibility: ``institutional_context_clear``) and the REV direction from
           the raid (decides); HTF layers (M5/M6/M12, bar-derived) are annotate-only
  context  M8 CBDR / London gate, calendar, DXY, sentiment / W%R, M1-M4, M10-M12, Charter / Model 13: annotate only
  setup    raid, MSS, box, origin PD array (feed REV), candidate set (REV decides; CONSO/BB/PIP20 eligibility only)
  ticket   the session's selected module + session_ticket id + entry / stop references
  gates    kernel_ticket -> direction -> risk -> allowlist -> mode -> contract (blocked_by = first failure)
  result   ``pending`` here; filled only by ``ftn.journal.results`` (burned window, or forward after clearance)
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

SCHEMA = "ftn.trace.v1"
MONTH_LAYERS = ("month1", "month2", "month3", "month4", "month5", "month6", "month7", "month8",
                "month10", "month11", "month12", "charter")
_FLAG = {"month1": "setup_elements", "month2": "low_risk_frame", "month3": "next_setup", "month4": "array_opportunity",
         "month5": "position_opportunity", "month6": "swing_opportunity", "month7": "osok_opportunity",
         "month10": "multi_asset_context", "month11": "mega_trade", "month12": "top_down",
         "charter": "charter_recognition"}


def _d(x):
    return asdict(x) if is_dataclass(x) else x


def _no_bars() -> dict:
    return {"available": False, "why_unavailable": "no_bar_history (fixture path: bar-derived layers need ftn.research)",
            "role": "annotate", "feeds_rev": False}


def _labelled_layer(ctx, name: str) -> dict:
    st = getattr(ctx, name, None)
    if st is None:
        return {"available": False, "why_unavailable": "no_labelled_evidence_in_daycontext", "role": "annotate",
                "feeds_rev": False}
    out = {"available": True, "role": "annotate", "feeds_rev": False, "origin": "daycontext_label"}
    if name == "month8":
        out["value"] = {"cbdr_class": st.cbdr.classification, "cbdr_height_pips": st.cbdr.height_pips,
                        "london_gate_allowed": st.london_session_gate.allowed,
                        "london_gate_reason": st.london_session_gate.reason or "allowed",
                        "london_profile": st.ict_london_profile,
                        "daytrade_opportunity": st.daytrade_opportunity,
                        "projection_draw": st.daily_extreme_projection.draw}
        out["note"] = "computed and logged; not enforced on REV tickets (enforcing it would change tickets: F8, new prereg)"
    else:
        fl = getattr(st, _FLAG.get(name, ""), None)
        out["value"] = {"flag": getattr(fl, "flag", None), "reason": getattr(fl, "reason", None)}
        if name == "charter":
            m13 = getattr(st, "model13", None)
            out["value"].update({"identified_pam": st.identified_pam, "model13_bridge": st.model13_bridge,
                                 "model13_card": None if m13 is None else {"direction": m13.direction,
                                                                           "reason": m13.reason}})
    return out


def build_trace(ctx, cands, draft: dict | None, *, fingerprint: str | None = None, source: str = "",
                bar_layers: dict | None = None, ticket_row: dict | None = None, result: dict | None = None) -> dict:
    """``ctx``: the frozen DayContext the kernel evaluated; ``cands``: its candidate tuple; ``draft``:
    ``mint_draft.draft_from_handoff`` output (or None when nothing was selected)."""
    from ftn.models.rev import raided_sides, rev_direction

    ev = ctx.evidence or {}
    raid = ev.get("raid") or {}
    ic = ctx.pair_institutional
    s = ctx.sentiment
    sel = next((c for c in cands if c.state == "selected"), None)
    bl = bar_layers or {}
    tr = ticket_row or {}
    gate_chain = tr.get("gates") if tr.get("gates") is not None else \
        [f"{g['gate']}:{'pass' if g['pass'] else 'FAIL'}:{g['reason']}" for g in (draft or {}).get("gates", [])]
    blocked = tr.get("blocked_by") if tr else ((draft or {}).get("blocked_by") if draft else
                                               "kernel_ticket:no_selected_candidate")
    return {
        "schema": SCHEMA,
        "source": source,
        "date": ctx.date, "symbol": ctx.symbol, "session": ev.get("session"),
        "fingerprint": fingerprint,
        "bias": {
            "iof": {"value": {"state": ic.state, "confidence": ic.confidence,
                              "daytrade_iof": _d(ic.daytrade_iof), "sponsorship": _d(ic.sponsorship)},
                    "role": "filter", "feeds_rev": True,
                    "note": "REV eligibility requires state != unclear; REV direction does NOT follow the IOF"},
            "rev_direction": {"value": rev_direction(raid), "raided_sides": sorted(raided_sides(raid)),
                              "role": "decide", "feeds_rev": True, "origin": "hermes_interpretation (REPORT D18)"},
            "M5_ipda": bl.get("M5_ipda") or _no_bars(),
            "M6_swing": bl.get("M6_swing") or _no_bars(),
            "M12_topdown": bl.get("M12_topdown") or _no_bars(),
        },
        "context": {
            "M1": _labelled_layer(ctx, "month1"), "M2": _labelled_layer(ctx, "month2"),
            "M3": _labelled_layer(ctx, "month3"), "M4": _labelled_layer(ctx, "month4"),
            "M5_label": _labelled_layer(ctx, "month5"), "M6_label": _labelled_layer(ctx, "month6"),
            "M7_label": _labelled_layer(ctx, "month7"),
            "M7_week": bl.get("M7_week") or _no_bars(),
            "M8": _labelled_layer(ctx, "month8"),
            "M10": _labelled_layer(ctx, "month10"), "M11": _labelled_layer(ctx, "month11"),
            "M12_label": _labelled_layer(ctx, "month12"),
            "M13_charter": _labelled_layer(ctx, "charter"),
            "calendar": {"value": [{k: e.get(k) for k in ("time_ny", "when", "kind", "event", "impact", "killzone")
                                    if e.get(k) is not None} for e in (ctx.calendar or ())],
                         "focus_source": ev.get("focus_source"), "role": "annotate", "feeds_rev": False,
                         "note": "feeds M8 london gate 'news' only"},
            "dxy": {"value": (ctx.dxy or {}).get("relationship"), "role": "annotate", "feeds_rev": False,
                    "available": (ctx.dxy or {}).get("relationship") not in (None, "unavailable")},
            "sentiment": {"value": {"direction": s.direction, "wr_kernel": {"value": s.indicator.value,
                                                                            "state": s.indicator.state},
                                    "judas_side": s.judas_side},
                          "role": "annotate", "feeds_rev": False,
                          "note": "feeds BB eligibility only; BB cannot be selected while interpretation_triggers are off"},
            "W%R_prior_evening": bl.get("W%R_prior_evening") or _no_bars(),
            "features": bl.get("features") or _no_bars(),
        },
        "setup": {
            "raid": {k: raid.get(k) for k in ("taken", "level", "price", "also")},
            "mss": ev.get("mss"), "displacement": ev.get("displacement"),
            "raid_bar_index": (ev.get("mss_meta") or {}).get("raid_bar_index"),
            "box": ev.get("box"), "origin_pd_array": ctx.origin_pd_array, "profile": ctx.profile,
            "candidates": [{"module": c.module, "state": c.state, "eligible": c.eligible, "reason": c.reason,
                            "origin": c.origin, "role": "decide" if c.module == "REV" else
                            ("annotate" if c.module == "FTN" else "eligibility_only")} for c in cands],
        },
        "ticket": {
            "selected_module": sel.module if sel else None,
            "session_ticket_id": (draft or {}).get("session_ticket_id")
            or (ctx.session_ticket.id if ctx.session_ticket else None),
            "direction": (draft or {}).get("direction_hypothesis") if draft else None,
            "entry_time": tr.get("entry_time"),
            "entry_reference": tr.get("entry") if tr else (draft or {}).get("entry_reference"),
            "stop_reference": tr.get("stop") if tr else (draft or {}).get("stop_reference"),
        },
        "gates": {
            "chain": gate_chain,
            "blocked_by": blocked,
            "actionable_for_mint": False,
        },
        "result": result or {"status": "pending", "R": None,
                             "note": "filled only by ftn.journal.results (burned window, or forward after "
                                     "CASSANDRA + DATA clearance)"},
    }


def render_trace_summary(tr: dict) -> str:
    """Markdown summary of a trace (appended to `ftn brief` output by the CLI; the kernel is not involved)."""
    lines = ["", "## Pipeline trace (bias → context → setup → ticket → gates → result)", ""]
    for stage in ("bias", "context"):
        for name, lay in tr[stage].items():
            lines.append(f"- {stage}.{name}: role={lay.get('role')} feeds_rev={lay.get('feeds_rev')} "
                         f"available={lay.get('available', True)}")
    lines += [f"- ticket: {tr['ticket']['selected_module']} ({tr['ticket']['session_ticket_id']})",
              f"- gates: blocked_by={tr['gates']['blocked_by']}",
              f"- result: {tr['result']['status']}", "",
              "Context layers are annotation only (feeds_rev=False); only REV decides. Bar-derived M5/M6/M7/M12 and "
              "W%R-prior-evening layers need bar history (`ftn trace` / `ftn results`).", ""]
    return "\n".join(lines)


def trace_for_state(state, cands, ftn, source: str) -> dict:
    """Trace for a frozen MarketState from the fixture path (`ftn brief` / `ftn run`)."""
    from ftn.os.handoff import build_handoff
    from ftn.os.mint_draft import draft_from_handoff, gate_input
    return build_trace(state.context, cands, draft_from_handoff(gate_input(state, build_handoff(state, cands, ftn))),
                       fingerprint=state.fingerprint, source=source)
