
"""python -m ftn"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ftn.workflow.orchestrator import run_workflow
from ftn.os.briefing import brief_from_fixture


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="FTN / Month-9 OS — paper-first.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    def add_common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--symbol", default="EURUSD")
        sp.add_argument("--fixture", type=Path, default=None)
        sp.add_argument("--bias", choices=["bullish", "bearish", "auto"], default="auto")
        sp.add_argument("--price", type=float, default=None)
        sp.add_argument("--out", type=Path, default=None)

    run = sub.add_parser("run", help="Run FTN PREP→JOURNAL workflow")
    add_common(run)
    prep = sub.add_parser("prep", help="Daily prep only")
    add_common(prep)
    br = sub.add_parser("brief", help="Month-9 DTR briefing + candidate log")
    br.add_argument("--fixture", type=Path, required=True)
    br.add_argument("--out", type=Path, default=None)
    sc = sub.add_parser("score", help="EXPLORATORY: score month-layer hypotheses on M9 kernel tickets over 1m bars")
    sc.add_argument("--asof", default=None, help="date stamp for output files (default today)")
    sc.add_argument("--bars-us100", default=None)
    sc.add_argument("--bars-us500", default=None)
    sc.add_argument("--research-dir", type=Path, default=None, help="default: <monorepo>/research")
    sc.add_argument("--no-write", action="store_true")
    sc.add_argument("--no-interp", action="store_true", help="skip the interpretation-trigger variant")
    sc.add_argument("--tag", default="", help="suffix for output files (e.g. _rev_raid_side)")
    sc.add_argument("--before", default=None, help="previous FTN_M9_SCORE_*.json for a before/after table")
    sc.add_argument("--with-legacy", action="store_true", help="also run the pre-D18 kernel-side-as-is streams")
    sc.add_argument("--asks-us100", default=None, help="ASK 1m CSV (same layout); needed by --cost-model correct_side")
    sc.add_argument("--asks-us500", default=None)
    sc.add_argument("--cost-model", choices=["correct_side", "flat"], default="correct_side",
                    help="correct_side (default): bid/ask fills + DATA slippage floors; flat: legacy 0.8/0.5 pt per side")
    sc.add_argument("--book", choices=["flat", "running", "both"], default="flat",
                    help="flat: gate every ticket against a flat book; running: 2%%/5%% caps bind (RunningBook)")
    sc.add_argument("--drawdown-reset", choices=["none", "next_calendar_month"], default=None,
                    help="running book 5%% DD reset rule (default: config risk_caps.drawdown_reset) — HUMAN DECISION")
    sc.add_argument("--no-calendar", action="store_true", help="do not attach the FOMC/CPI/NFP calendar")
    def add_bars(sp):
        sp.add_argument("--symbol", choices=["US100", "US500"], default="US100")
        sp.add_argument("--data-dir", type=Path, default=None,
                        help="dir with US{100,500}_1m_{bid,ask}.csv.gz (default: the F1 guard tape, $FTN_GUARD_DATA_DIR)")
    tr = sub.add_parser("trace", help="Pipeline trace (ftn.trace.v1) for one day's Month 9 sessions (bar-derived; context only)")
    tr.add_argument("--date", required=True)
    add_bars(tr)
    rs = sub.add_parser("results", help="Paper results journal: trace + outcome per session (H016b forward R sealed)")
    rs.add_argument("--from", dest="date_from", required=True)
    rs.add_argument("--to", dest="date_to", required=True)
    rs.add_argument("--clearance", type=Path, default=None,
                    help="human-signed H016b clearance stamp (CASSANDRA: CLEARED + DATA: CLEARED); without it, "
                         "sessions after 2026-09-25 stay sealed (no R computed)")
    rs.add_argument("--no-write", action="store_true")
    add_bars(rs)
    gd = sub.add_parser("guard", help="F1: re-run the H016b registration-input streams on the burned window, byte-compare, check H016b eligibility (254/258)")
    gd.add_argument("--trace", action="store_true", help="also run with the pipeline trace attached")
    hy = sub.add_parser("hypotheses", help="Print the typed FTN hypothesis family (JSON)")
    lp = sub.add_parser("live-probe", help="Probe live DATA adapters (quotes only; orders refused)")
    lp.add_argument("--symbol", default="EURUSD")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "live-probe":
        from ftn.adapters.live import fetch_quote, fetch_calendar, refuse_live_orders, live_data_allowed
        from ftn.config_load import load_config
        cfg = {}
        try:
            cfg = load_config()
        except Exception:
            pass
        payload = {
            "data_allowed": live_data_allowed(cfg),
            "quote": fetch_quote(args.symbol, cfg),
            "calendar": fetch_calendar(cfg),
            "orders": refuse_live_orders(),
        }
        print(json.dumps(payload, indent=2))
        return 0
    if args.command in ("trace", "results"):
        return _bar_commands(args)
    if args.command == "guard":
        import tempfile
        from ftn.pipeline import invariance as inv
        bad = inv.check_data()
        if bad:
            print(f"ftn guard: burned tape unavailable: {bad}", file=sys.stderr)
            return 2
        hists = inv.load_histories()
        out = {}
        with tempfile.TemporaryDirectory() as td:
            out["base"] = inv.compare(inv.regenerate(Path(td) / "base", hists))
            if args.trace:
                out["trace"] = inv.compare(inv.regenerate(Path(td) / "trace", hists, trace=True))
        elig = inv.h016b_eligibility(hists)
        print(json.dumps({**out, "h016b_eligibility": elig}, indent=2))
        ok = all(v["identical"] for r in out.values() for v in r.values())
        return 0 if ok and elig["matches_prereg"] and elig["n_eligible"] == 254 else 1
    if args.command == "hypotheses":
        from ftn.research.hypotheses import HYPOTHESES
        print(json.dumps([h.to_dict() for h in HYPOTHESES], indent=2))
        return 0
    if args.command == "score":
        from ftn.research.score import score
        res = score(asof=args.asof, bars_us100=args.bars_us100, bars_us500=args.bars_us500,
                    research_dir=args.research_dir, write=not args.no_write, with_interp=not args.no_interp,
                    tag=args.tag, before=args.before, with_legacy=args.with_legacy,
                    asks_us100=args.asks_us100, asks_us500=args.asks_us500, cost_model=args.cost_model,
                    book=args.book, drawdown_reset=args.drawdown_reset, calendar=not args.no_calendar)
        print(json.dumps({k: {"tickets": v["tickets"], "modules": v["modules"], "summary": v["summary"],
                              "foil_pct": v["foil_pct"]} for k, v in res.items() if not k.startswith("_")}, indent=2, default=str))
        return 0
    if args.command == "brief":
        from ftn.os.contracts import FixtureError
        try:
            state, cands, md, ftn = brief_from_fixture(args.fixture)
        except FixtureError as exc:
            print(f"ftn brief: {exc}", file=sys.stderr)
            return 2
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ftn brief: cannot read {args.fixture}: {exc}", file=sys.stderr)
            return 2
        from ftn.paths import journal_dir
        from ftn.pipeline.trace import render_trace_summary, trace_for_state
        md += render_trace_summary(trace_for_state(state, cands, ftn, "ftn brief"))
        out = args.out or journal_dir() / f"{state.context.date}_{state.context.symbol}_BRIEFING.md"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md)
        print(md)
        print(f"\n# wrote {out}", file=sys.stderr)
        return 0
    stage = "all" if args.command == "run" else "prep"
    from ftn.workflow.orchestrator import RunFixtureError
    try:
        result = _run(args, stage)
    except RunFixtureError as exc:
        print(f"ftn {args.command}: {exc}", file=sys.stderr)
        return 2
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ftn {args.command}: cannot read {args.fixture}: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, default=str))
    return 0 if result.get("ok") else 1


def _bar_commands(args: argparse.Namespace) -> int:
    from datetime import date
    from ftn.journal.results import BURNED_END, BURNED_START, journal_rows
    from ftn.pipeline import invariance as inv
    from ftn.research.kernel_log import session_ticket_log
    from ftn.research.score import load_history, make_sim, row_outcome

    d0 = date.fromisoformat(args.date if args.command == "trace" else args.date_from)
    d1 = date.fromisoformat(args.date if args.command == "trace" else args.date_to)
    if args.data_dir:
        import os
        os.environ["FTN_GUARD_DATA_DIR"] = str(args.data_dir)
    dd = inv.data_dir()
    hists = {}
    for sym in ("US100", "US500"):
        bid, ask = dd / f"{sym}_1m_bid.csv.gz", dd / f"{sym}_1m_ask.csv.gz"
        if not bid.is_file() or not ask.is_file():
            print(f"ftn {args.command}: missing BID/ASK tape for {sym} in {dd}", file=sys.stderr)
            return 2
        hists[sym] = load_history(sym, str(bid), str(ask))
    h = hists[args.symbol]
    other = hists["US500"] if args.symbol == "US100" else None
    days = [x for x in h.days if d0 <= x <= d1]
    if not days:
        print(f"ftn {args.command}: no trading days {d0}..{d1} in the tape "
              f"(burned window {BURNED_START}..{BURNED_END})", file=sys.stderr)
        return 2
    from ftn.pipeline.kernel_trace import trace_rows
    cfg = inv.base_cfg()
    rows = trace_rows(session_ticket_log(h, cfg, days=days), h, cfg, other)
    if args.command == "trace":
        print(json.dumps([r.get("trace") or {k: r.get(k) for k in ("date", "symbol", "session", "ticket", "reason")}
                          for r in rows], indent=2, default=str))
        return 0
    recs = journal_rows(rows, row_outcome(make_sim(args.symbol, h, "correct_side")), args.clearance,
                        write=not args.no_write)
    print(json.dumps([{k: r[k] for k in ("date", "symbol", "session", "ticket", "module", "result")} for r in recs],
                     indent=2, default=str))
    return 0


def _run(args: argparse.Namespace, stage: str) -> dict:
    return run_workflow(
        symbol=args.symbol,
        fixture=args.fixture,
        bias=args.bias,
        price=args.price,
        stage=stage,
        out_dir=args.out,
    )


if __name__ == "__main__":
    raise SystemExit(main())
