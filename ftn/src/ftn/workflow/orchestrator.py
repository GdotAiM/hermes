from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ftn.config_load import load_config, repo_root
from ftn.engine.levels import atr_pips, build_families, count_four, detect_bias, overlap_pd
from ftn.engine.ohlc import load_bars
from ftn.journal.write import write_journal
from ftn.paths import out_dir as default_out_dir


STAGES = ["PREP", "FILTER", "WATCH", "GATE", "MANAGE", "JOURNAL"]


class RunFixtureError(ValueError):
    """The file is not an `ftn run`/`ftn prep` fixture."""


RUN_KEYS = ("previous_day", "cbdr", "asian", "flout")


def _unique(path: Path) -> Path:
    """Same-second runs must not overwrite each other (scanned_at has 1 s resolution)."""
    n, cand = 1, path
    while cand.exists():
        cand = path.with_name(f"{path.stem}_{n}{path.suffix}")
        n += 1
    return cand


def _check_run_pack(pack: dict, fixture: Path | None) -> None:
    missing = [k for k in RUN_KEYS if not isinstance(pack.get(k), dict)]
    if missing:
        name = Path(fixture).name if fixture else "<default fixture>"
        raise RunFixtureError(f"{name}: neither a Month 9 DTR fixture (date + evidence/ranges) nor a legacy "
                              f"four-count pack: missing {', '.join(missing)}.")


def is_dtr_fixture(pack: dict) -> bool:
    """A Month 9 DTR fixture (what `ftn brief` reads) rather than a legacy four-count run pack."""
    return "date" in pack and any(k in pack for k in ("evidence", "ranges", "bars_m15", "pair_institutional"))


def run_month9(fixture: Path, stage: str = "all", out_dir: Path | None = None) -> dict[str, Any]:
    """F2: `ftn run` on a DTR fixture goes through the Month 9 kernel — the sole ticket authority.

    Same path as `ftn brief` (DayContext → frozen MarketState → candidates → session_ticket → handoff.v1 →
    research-draft gate chain), plus the per-ticket pipeline trace and a decision journal. Paper only; the ticket
    is never actionable for MINT and never an ``entry_candidate``; no broker call. ``stage="prep"`` stops before the
    journal. The FTN four-count stays an annotation (objectives), never the ticket.
    """
    from ftn.os.briefing import brief_from_fixture
    from ftn.os.contracts import FixtureError
    from ftn.os.handoff import build_handoff
    from ftn.os.mint_draft import draft_from_handoff, gate_input
    from ftn.pipeline.trace import trace_for_state

    try:
        state, cands, _md, ftn = brief_from_fixture(fixture)
    except FixtureError as exc:
        raise RunFixtureError(str(exc)) from exc
    ctx = state.context
    draft = draft_from_handoff(gate_input(state, build_handoff(state, cands, ftn)))
    sel = next((c for c in cands if c.state == "selected"), None)
    trace = trace_for_state(state, cands, ftn, f"ftn run (fixture {Path(fixture).name})")
    st = ctx.session_ticket
    ticket = {
        "kind": "m9_kernel_ticket" if sel else "no_trade",
        "authority": "month9_kernel",
        "selected_module": sel.module if sel else None,
        "session_ticket": {"id": st.id, "module": st.module, "session": st.session} if st else None,
        "actionable_for_mint": False,
        "requires": ["board SURVIVES", "allowlist", "RISK", "human_ack"],
        "symbol": ctx.symbol,
        "date": ctx.date,
        "direction_hypothesis": (draft or {}).get("direction_hypothesis"),
        "blocked_by": (draft or {}).get("blocked_by") or "kernel_ticket:no_selected_candidate",
        "gates": trace["gates"]["chain"],
        "candidates": trace["setup"]["candidates"],
        "four_levels": ftn.get("four") or [],
        "family": ftn.get("family"),
        "bias": ftn.get("bias"),
        "no_trade_reasons": [] if sel else ["no_selected_candidate"],
        "setup": {},
        "legacy_gate_ok": None,
        "fingerprint": state.fingerprint,
        "mode": "paper",
    }
    payload = {
        "ok": True,
        "scanned_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "stage": stage,
        "engine": "month9_kernel",
        "stages": STAGES if stage == "all" else ["PREP"],
        "ticket": ticket,
        "trace": trace,
        "annotations": {},
        "note": "No orders placed. Month 9 research ticket, not a contract and not for MINT; only handoff.v1 crosses parts.",
    }
    return _write(payload, out_dir, stage)


def _write(payload: dict, out_dir: Path | None, stage: str) -> dict:
    out = out_dir or default_out_dir()
    out.mkdir(parents=True, exist_ok=True)
    path = _unique(out / f"ftn_{payload['scanned_at']}.json")
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n", encoding="utf-8")
    (out / "latest.json").write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    payload["dispatch_path"] = str(path)
    if stage == "all":
        payload["journal_path"] = str(write_journal(payload))
    return payload


def _model13_annotations(cfg: dict, pack: dict) -> dict:
    if not cfg.get("model13_bridge_enabled"):
        return {}
    from ftn.os.m13_context import model13_annotation
    return {"model13": model13_annotation(pack)}


def run_workflow(
    *,
    symbol: str,
    fixture: Path | None,
    bias: str,
    price: float | None,
    stage: str = "all",
    out_dir: Path | None = None,
) -> dict[str, Any]:
    pack = load_bars(fixture, symbol)
    if fixture is not None and is_dtr_fixture(pack):
        return run_month9(Path(fixture), stage, out_dir)
    cfg = load_config()
    _check_run_pack(pack, fixture)
    families = build_families(pack)
    last = price if price is not None else pack.get("last", pack["previous_day"]["close"])
    direction = detect_bias(pack, bias)
    pip = float(pack.get("pip", 0.0001))
    vol = atr_pips(pack, pip)
    compressed = vol < float(cfg.get("min_atr_pips", 20))

    counts = {
        fam: count_four(families, bias=direction, price=last, family=fam)
        for fam in ("pivots", "cbdr", "asian", "flout")
    }
    # pick the family with a full 4-count nearest to last price
    chosen_name, chosen = max(
        counts.items(),
        key=lambda kv: (len(kv[1]), -abs(kv[1][0]["price"] - last) if kv[1] else 0),
    )
    tol = float(cfg.get("overlap_tolerance_pips", 8)) * pip
    hits = overlap_pd(chosen, pack.get("pd_arrays", []), tol)

    setup = pack.get("setup", {})
    gate_ok = bool(
        setup.get("liquidity_raid")
        and setup.get("displacement")
        and setup.get("mss")
        and setup.get("pd_retrace")
        and setup.get("killzone") in ("london", "ny_am")
    )

    no_trade_reasons: list[str] = []
    if compressed and cfg.get("compress_blocks_trade", True):
        no_trade_reasons.append("compressed_atr")
    if cfg.get("require_pd_overlap", True) and not hits:
        no_trade_reasons.append("no_pd_array_overlap")
    if not gate_ok:
        no_trade_reasons.append("setup_gate_incomplete")
    if cfg.get("mode") != "paper":
        no_trade_reasons.append("non_paper_mode_refused")
    if direction == "undetermined":
        # No explicit --bias and no htf_bias: no four-count (never a default bullish).
        no_trade_reasons.append("bias_undetermined")

    setup_complete = len(no_trade_reasons) == 0
    # I0: FTN never clears anything for MINT. `entry_candidate` is MINT's own kind
    # for board-SURVIVES tickets, so FTN must not emit it, and actionable_for_mint is
    # always False. The only cross-part object is handoff.v1 (`ftn brief`).
    ticket = {
        "kind": "ftn_setup_ticket" if setup_complete else "no_trade",
        # Legacy four-count pack: objectives + fixture-provided setup flags only. Not a Month 9 ticket and
        # never a session_ticket (the Month 9 kernel is the sole ticket authority; give `ftn run` a DTR fixture).
        "engine": "legacy_four_count_objectives",
        "setup_complete": setup_complete,
        "actionable_for_mint": False,
        "requires": ["board SURVIVES", "allowlist", "RISK", "human_ack"],
        "symbol": pack.get("symbol", symbol),
        "bias": direction,
        "price": last,
        "family": chosen_name,
        "four_levels": chosen,
        "all_families": counts,
        "pd_confluence": hits,
        "volatility_atr_pips": vol,
        "compressed": compressed,
        "setup": setup,
        "gate_ok": gate_ok,
        "no_trade_reasons": no_trade_reasons,
        "management": {
            "scale_out_after_levels": cfg.get("scale_out_after_levels", 4),
            "runner_pct": cfg.get("runner_pct", 0.25),
            "note": "Pivots/ranges are targets. Entry remains PD-array after MSS.",
        },
        "mode": cfg.get("mode"),
        "live_enabled": cfg.get("live_enabled"),
    }

    payload = {
        "ok": True,
        "scanned_at": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "stage": stage,
        "engine": "legacy_four_count",
        "stages": STAGES if stage == "all" else ["PREP"],
        "ticket": ticket,
        # Model 13 (Charter bridge) annotation: off by default, never changes the ticket.
        "annotations": _model13_annotations(cfg, pack),
        "note": "No orders placed. Research ticket, not a contract and not for MINT; only handoff.v1 crosses parts.",
    }

    return _write(payload, out_dir, stage)
