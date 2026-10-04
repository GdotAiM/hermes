"""H014 forward harness: MMXM v5 A_overnight_5mFVG_ce_c12_none, US100 + US500 CFD, frozen forward-only test.
HYPOTHETICAL paper research: no orders, no broker calls.

Implements research/protocols/preregs/H014_FORWARD_PREREG_2026-10-04.json:
  * rule objects = the sha256-pinned yaml + mmxm modules, copied verbatim into research/forward/H014/frozen/ (PROVENANCE.md);
    the frozen config runs UNCHANGED through mmxm.engine.run_backtest
  * feed = TradingView CAPITALCOM:US100 / CAPITALCOM:US500 only (no fallback)
  * day-eligibility layer (harness, not engine): prereg NYSE holiday list; >= 86/90 1m bars 09:30-10:59 and
    >= 791/930 1m bars in the 18:00 (prior calendar day) -> 09:30 overnight range, per symbol
  * raw bars saved per run; the CAPITALCOM archive (all saved raw files) is the engine's history (1H context)
  * US100 and US500 logged separately; running pooled total R over counted trades drives the -5R kill
  * same-day random-entry baseline (mmxm.baseline.outcome_table on the session's trades)
  * backfill of post-registration sessions is allowed (raw bars saved) and flagged BACKFILLED
Data/logs go to $HERMES_FWD_DATA/H014 (default /home/box/hermes-x/forward/H014), outside git.

CLI (from the repo root):
  python research/forward/H014/h014.py final    [YYYY-MM-DD]     post-session (after 12:00 NY)
  python research/forward/H014/h014.py backfill YYYY-MM-DD       a past post-registration session (raw bars saved)
  python research/forward/H014/h014.py report                    per-symbol + pooled, kill status
  python research/forward/H014/h014.py seed                      save currently served CAPITALCOM bars as 1H context
  python research/forward/H014/h014.py selfcheck"""
from __future__ import annotations

import json, pathlib, sys, uuid
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import fwdlib as F  # noqa: E402

LEAD = "H014"
PREREG_REL = "research/protocols/preregs/H014_FORWARD_PREREG_2026-10-04.json"
FROZEN = HERE / "frozen"
YAML = FROZEN / "configs/v5_A_overnight_5mFVG_ce_c12_none.yaml"
HARNESS_FILES = [HERE.parent / "common/__init__.py", HERE.parent / "common/fwdlib.py", HERE.parent / "common/tv_feed.py",
                 HERE / "__init__.py", HERE / "h014.py"]
DEPENDENCY_PINS = ["mmxm/__init__.py", "mmxm/indicators.py"]      # imported by the engine, not in the prereg rule list
INSTS = ("US100", "US500")
ROOT = {"US100": "NQ", "US500": "ES"}
STREAM = {"US100": "FWD-TV-CAPITALCOM-US100", "US500": "FWD-TV-CAPITALCOM-US500"}
WIN_MIN, WIN_N = 86, 90
ON_MIN, ON_N = 791, 930
KILL_R = -5.0
COST_RT = {"US100": 0.8, "US500": 0.5}           # frozen (binding)
DATA_COST_RT = {"US100": 1.617, "US500": 1.01}   # DATA measured spread + 2x0.25 slip (co-report only; Dukascopy spread)
COLUMNS = ["run_id", "run_kind", "logged_at_sast", "date", "instrument", "stream", "feed", "fetch_time_sast", "fetch_first_bar_ny",
           "fetch_last_bar_ny", "raw_file", "raw_sha256", "archive_first_bar_ny", "archive_rows", "h1_context_bars",
           "context_short", "bars_0930_1059", "bars_overnight", "calendar_status", "min_bar_ok", "session_complete",
           "rule_pins_ok", "harness_digest", "registration_commit", "registration_time_ny", "harness_matches_registered",
           "n_orders", "status", "trade_no", "direction", "order_time_ny", "entry_time_ny", "entry", "stop", "risk_pts", "tp1",
           "tp1_source", "draw", "draw_kind", "exit_time_ny", "exit_reason", "r_multiple", "r_cost2x", "r_data_measured_cost", "baseline_n", "baseline_mean_R",
           "baseline_outcomes", "backfilled", "session_valid", "counted", "not_counted_reasons", "error"]


def data_dir() -> pathlib.Path:
    return F.DATA_ROOT / LEAD


def prereg() -> dict:
    return F.load_prereg(PREREG_REL)


def harness_manifest() -> dict:
    return F.manifest(HARNESS_FILES)


def harness_digest(m=None) -> str:
    return F.sha256_bytes(json.dumps(m or harness_manifest(), sort_keys=True).encode())


def all_pins() -> dict:
    pr = prereg()
    return {**pr["rule_object_sha256"], **pr.get("rule_object_dependencies_sha256", {})}


_ENGINE = None


def load_engine():
    """Verify pins, then import the frozen mmxm package from research/forward/H014/frozen (never /workspace/mmxm)."""
    global _ENGINE
    if _ENGINE is None:
        bad = F.verify_pins(FROZEN, all_pins())
        if bad:
            raise RuntimeError(f"H014 rule-object sha256 mismatch, refusing to run: {bad}")
        for k in [m for m in sys.modules if m == "mmxm" or m.startswith("mmxm.")]:
            del sys.modules[k]
        sys.path.insert(0, str(FROZEN))
        import mmxm
        if pathlib.Path(mmxm.__file__).resolve().parent != (FROZEN / "mmxm").resolve():
            raise RuntimeError(f"imported mmxm from {mmxm.__file__}, not the frozen copy")
        from mmxm.config import Config
        from mmxm import data as D
        from mmxm.engine import run_backtest
        from mmxm.baseline import outcome_table
        _ENGINE = (Config.from_yaml(str(YAML)), D, run_backtest, outcome_table)
    return _ENGINE


def to_m1(df: pd.DataFrame) -> pd.DataFrame:
    cfg, D, _, _ = load_engine()
    return D._normalise(df)


def run_engine(m1: pd.DataFrame, inst: str):
    cfg, D, run_backtest, _ = load_engine()
    return run_backtest(m1, cfg, ROOT[inst], inst)


# ------------------------------------------------------------------ eligibility
def day_quality(m1: pd.DataFrame, d: str) -> dict:
    ix = m1.index
    win = int(((ix >= F.at(d, "09:30")) & (ix < F.at(d, "11:00"))).sum())
    prev = (pd.Timestamp(d) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    on = int(((ix >= F.at(prev, "18:00")) & (ix < F.at(d, "09:30"))).sum())
    return dict(bars_0930_1059=win, bars_overnight=on, min_bar_ok=(win >= WIN_MIN and on >= ON_MIN))


def session_first_bar(m1: pd.DataFrame, d: str):
    prev = (pd.Timestamp(d) - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    x = m1.index[m1.index >= F.at(prev, "18:00")]
    return x[0] if len(x) else F.at(prev, "18:00")


def eligibility(m1, d, reg, pins_ok) -> tuple[dict, list]:
    pr = prereg(); q = day_quality(m1, d); reasons = []
    cal = F.calendar_status(d, pr)
    complete = len(m1) > 0 and m1.index[-1] >= F.at(d, "11:00")
    if cal != "ok": reasons.append(f"calendar:{cal}")
    if not q["min_bar_ok"]: reasons.append(f"min_bars:win {q['bars_0930_1059']}/{WIN_N},overnight {q['bars_overnight']}/{ON_N}")
    if not complete: reasons.append("session_incomplete(last bar < 11:00 NY)")
    if not pins_ok: reasons.append("rule_hash_mismatch")
    if not reg.get("registered"): reasons.append("harness_not_registered_on_main")
    elif not reg.get("harness_matches_registered"): reasons.append("harness_hash_mismatch")
    elif pd.Timestamp(reg["registration_time_ny"]) >= session_first_bar(m1, d): reasons.append("registered_after_session_data_began")
    return {**q, "calendar_status": cal, "session_complete": complete}, reasons


# ------------------------------------------------------------------ archive
def archive(inst: str, extra: pd.DataFrame | None = None) -> pd.DataFrame:
    """Every raw CAPITALCOM file saved for this symbol (oldest first; later fetches win on overlap) + the current fetch."""
    parts = []
    for p in sorted((data_dir() / "raw" / inst).glob("*.csv")):
        parts.append(F.read_raw(str(p.relative_to(F.DATA_ROOT))))
    if extra is not None:
        parts.append(extra[["Open", "High", "Low", "Close"]])
    if not parts:
        return pd.DataFrame(columns=["Open", "High", "Low", "Close"])
    df = pd.concat(parts)
    return df[~df.index.duplicated(keep="last")].sort_index()


def session_rows(hist: pd.DataFrame, d: str, inst: str, run_kind: str, reg: dict, run_id: str, meta: dict,
                 raw_file=None, raw_sha=None, pins_ok=True) -> list[dict]:
    """Run the frozen engine on history up to < d 12:00 NY (the engine is flat at 11:00) and return this session's rows (one per trade, or one no-trade row)."""
    cfg, D, run_backtest, outcome_table = load_engine()
    m1 = to_m1(hist[hist.index < F.at(d, "12:00")])
    h1_ctx = int(m1[m1.index < F.at(d, "09:30")]["close"].resample("1h").count().gt(0).sum()) if len(m1) else 0
    q, reasons = eligibility(m1, d, reg, pins_ok)
    base = dict(run_id=run_id, run_kind=run_kind, logged_at_sast=F.now_sast().strftime("%Y-%m-%d %H:%M:%S"), date=d,
                instrument=inst, stream=STREAM[inst], raw_file=raw_file, raw_sha256=raw_sha,
                archive_first_bar_ny=str(m1.index[0]) if len(m1) else None, archive_rows=len(m1), h1_context_bars=h1_ctx,
                context_short=h1_ctx < cfg.h1_lookback_bars, rule_pins_ok=pins_ok, harness_digest=harness_digest(),
                registration_commit=reg.get("registration_commit"), registration_time_ny=reg.get("registration_time_ny"),
                harness_matches_registered=reg.get("harness_matches_registered"), backfilled=(run_kind == "BACKFILL"),
                session_valid=not reasons, **q, **meta)
    if not len(m1) or m1.index[-1] < F.at(d, "09:30"):
        return [{**base, "status": "no data", "counted": False, "not_counted_reasons": ";".join(reasons + ["no_data"])}]
    trades, orders, _ = run_engine(m1, inst)
    day = lambda s: pd.to_datetime(s.astype(str), utc=True).dt.tz_convert(F.TZ).dt.strftime("%Y-%m-%d") if len(s) else s
    tr = trades[day(trades["entry_time_ny"]) == d] if len(trades) else trades
    n_orders = int((day(orders["order_time_ny"]) == d).sum()) if len(orders) else 0
    if not len(tr):
        return [{**base, "n_orders": n_orders, "status": "no trade", "counted": False,
                 "not_counted_reasons": ";".join(reasons + ["no_trade"])}]
    tabs = outcome_table(m1, tr, cfg, ROOT[inst])
    rows = []
    for k, ((_, t), tab) in enumerate(zip(tr.iterrows(), tabs), 1):
        rows.append({**base, "n_orders": n_orders, "status": "trade", "trade_no": k,
                     **{c: t[c] for c in ("direction", "order_time_ny", "entry_time_ny", "entry", "stop", "risk_pts", "tp1",
                                          "tp1_source", "draw", "draw_kind", "exit_time_ny", "exit_reason", "r_multiple")},
                     # co-reports (DATA fix 2): flat round-trip deduction, so R_k = R - (k-1)*cost/risk exactly
                     "r_cost2x": float(t["r_multiple"]) - COST_RT[inst] / float(t["risk_pts"]),
                     "r_data_measured_cost": float(t["r_multiple"]) - (DATA_COST_RT[inst] - COST_RT[inst]) / float(t["risk_pts"]),
                     "baseline_n": len(tab), "baseline_mean_R": float(np.mean(tab)),
                     "baseline_outcomes": json.dumps([round(float(x), 4) for x in tab]),
                     "counted": not reasons, "not_counted_reasons": ";".join(reasons)})
    return rows


# ------------------------------------------------------------------ commands
def cmd_final(d: str, run_kind: str = "FINAL", fetch=None, fetch_remote: bool = True) -> list[dict]:
    load_engine()
    reg = F.registration_status(PREREG_REL, harness_manifest(), fetch=fetch_remote)
    run_id = uuid.uuid4().hex[:12]; out = []
    for inst in INSTS:
        try:
            df, meta = F.fetch_capitalcom(inst, n=8000, _fetch=fetch)
        except F.FeedError as e:
            row = dict(run_id=run_id, run_kind=run_kind, date=d, instrument=inst, status="feed_gap", error=str(e), counted=False,
                       not_counted_reasons="feed_gap", logged_at_sast=F.now_sast().strftime("%Y-%m-%d %H:%M:%S"))
            F.append_csv(data_dir() / "log.csv", row, COLUMNS); out.append(row); continue
        hist = archive(inst, df)                                         # archive BEFORE saving this fetch, then save it
        raw_file, raw_sha = F.save_raw(df, LEAD, inst, f"{d}__{run_kind.lower()}__{F.now_sast():%Y%m%dT%H%M%S}")
        for row in session_rows(hist, d, inst, run_kind, reg, run_id, meta, raw_file, raw_sha):
            F.append_csv(data_dir() / "log.csv", row, COLUMNS); out.append(row)
    return out


def cmd_seed(fetch=None) -> dict:
    """Save the CAPITALCOM bars TradingView currently serves (about 5 sessions) as 1H-context history. Never a session row."""
    out = {}
    for inst in INSTS:
        df, meta = F.fetch_capitalcom(inst, n=8000, _fetch=fetch)
        out[inst] = dict(zip(("raw_file", "raw_sha256"), F.save_raw(df, LEAD, inst, f"context_seed__{F.now_sast():%Y%m%dT%H%M%S}")), **meta)
        F.append_jsonl(data_dir() / "seed.jsonl", dict(instrument=inst, **out[inst]))
    return out


def kill_walk(trades: pd.DataFrame) -> pd.DataFrame:
    """Pooled running total over counted trades in entry-time order; FAILS (kill) at the first cum <= -5R."""
    t = trades.sort_values("entry_time_ny").copy()
    t["cum_pooled_R"] = t["r_multiple"].astype(float).cumsum()
    hit = t.index[t["cum_pooled_R"] <= KILL_R]
    t["after_kill"] = False
    if len(hit):
        t.loc[t.index[t.index.get_loc(hit[0]) + 1:], "after_kill"] = True
    return t


def cmd_report(log: pd.DataFrame | None = None) -> dict:
    p = data_dir() / "log.csv"
    if log is None:
        if not p.exists():
            return dict(n_counted=0, kill=False)
        log = pd.read_csv(p)
    log = log.copy(); log["counted"] = log["counted"].astype(str) == "True"
    latest_run = log.groupby(["date", "instrument"])["run_id"].transform("last")
    cur = log[log.run_id == latest_run]                                # latest run per session/symbol is authoritative
    tr = cur[(cur.status == "trade") & cur.counted]
    w = kill_walk(tr) if len(tr) else tr.assign(cum_pooled_R=[], after_kill=[])
    out = {}
    for inst in INSTS:
        x = w[w.instrument == inst]
        out[inst] = dict(n=len(x), total_R=float(x.r_multiple.sum()) if len(x) else 0.0,
                         mean_R=float(x.r_multiple.mean()) if len(x) else None)
    out["pooled_secondary"] = dict(n=len(w), total_R=float(w.r_multiple.sum()) if len(w) else 0.0,
                                   min_cum_R=float(w.cum_pooled_R.min()) if len(w) else 0.0)
    out["kill_triggered"] = bool(len(w) and (w.cum_pooled_R <= KILL_R).any())
    out["status"] = "FAILS (kill: cumulative <= -5R)" if out["kill_triggered"] else "OPEN"
    out["backfilled_counted"] = int(w.backfilled.astype(str).eq("True").sum()) if len(w) else 0
    out["binding_N"] = prereg()["binding_N"]
    return out


def selfcheck() -> dict:
    bad = F.verify_pins(FROZEN, all_pins()); m = harness_manifest()
    return dict(rule_pins_ok=not bad, rule_pin_mismatch=bad, harness_manifest=m, harness_digest=harness_digest(m),
                prereg_harness=prereg().get("harness_sha256"), registration=F.registration_status(PREREG_REL, m))


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "selfcheck"
    day = next((x for x in a[1:] if x[:2] == "20" and len(x) == 10), None) or pd.Timestamp.now(tz=F.TZ).strftime("%Y-%m-%d")
    if cmd in ("final", "backfill"):
        for r in cmd_final(day, "FINAL" if cmd == "final" else "BACKFILL"):
            print({k: r.get(k) for k in ("date", "instrument", "status", "direction", "entry_time_ny", "r_multiple", "baseline_mean_R",
                                        "bars_0930_1059", "bars_overnight", "h1_context_bars", "counted", "not_counted_reasons")})
        print(json.dumps(cmd_report(), indent=2, default=str))
    elif cmd == "report":
        print(json.dumps(cmd_report(), indent=2, default=str))
    elif cmd == "seed":
        print(json.dumps(cmd_seed(), indent=2, default=str))
    else:
        print(json.dumps(selfcheck(), indent=2, default=str))
