
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
    if args.command == "hypotheses":
        from ftn.research.hypotheses import HYPOTHESES
        print(json.dumps([h.to_dict() for h in HYPOTHESES], indent=2))
        return 0
    if args.command == "score":
        from ftn.research.score import score
        res = score(asof=args.asof, bars_us100=args.bars_us100, bars_us500=args.bars_us500,
                    research_dir=args.research_dir, write=not args.no_write, with_interp=not args.no_interp,
                    tag=args.tag, before=args.before, with_legacy=args.with_legacy)
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
