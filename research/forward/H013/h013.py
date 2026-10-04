"""H013 forward harness: Model U v1 base, US100 CFD, frozen forward-only test. HYPOTHETICAL paper research: no orders, no broker.

Implements research/protocols/preregs/H013_FORWARD_PREREG_2026-10-04.json:
  * rule objects = the four sha256-pinned files, copied verbatim into research/forward/H013/frozen/ (PROVENANCE.md); a pin
    mismatch aborts the run
  * invocation best_trade(ctx, "11:00", False, False, True); E1.FILL_THRU = 1 tick; E1.SLIP = cost/tick (US100 0.8 pt/side)
  * feed = TradingView CAPITALCOM:US100 (decision) / CAPITALCOM:US500 (disclosure, never counted). NO fallback feed
  * NYSE holiday/early-close list from the prereg; >= 285 of 300 1m bars in 07:00-11:59 NY
  * raw 1m bars consumed are saved (live snapshots, final and backfill runs) with their sha256 in the row
  * a trade counts only if a live FILL alert (watch) preceded its exit; BACKFILL rows never count
Data/logs go to $HERMES_FWD_DATA/H013 (default /home/box/hermes-x/forward/H013), outside git.

CLI (run from the repo root):
  python research/forward/H013/h013.py watch  [YYYY-MM-DD] [--until HH:MM]   live poller, start before 09:00 NY
  python research/forward/H013/h013.py final  [YYYY-MM-DD]                    post-session (after 12:00 NY)
  python research/forward/H013/h013.py backfill YYYY-MM-DD                    re-log a past session (never counted)
  python research/forward/H013/h013.py report                                 counted N / mean / cum R
  python research/forward/H013/h013.py selfcheck                              pins + registration status, no fetch"""
from __future__ import annotations

import fcntl, json, pathlib, sys, time, uuid
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from common import fwdlib as F  # noqa: E402

LEAD = "H013"
PREREG_REL = "research/protocols/preregs/H013_FORWARD_PREREG_2026-10-04.json"
FROZEN = HERE / "frozen"
V1_DIR = FROZEN / "research/model-u-longrun/scripts/v1"
HARNESS_FILES = [HERE.parent / "common/__init__.py", HERE.parent / "common/fwdlib.py", HERE.parent / "common/tv_feed.py",
                 HERE / "__init__.py", HERE / "h013.py"]
DECISION_INST, INSTS = "US100", ("US100", "US500")
STREAM = {"US100": "FWD-TV-CAPITALCOM-US100", "US500": "FWD-TV-CAPITALCOM-US500"}
INVOCATION = ("11:00", False, False, True)
FILL_THRU_TICKS = 1
MIN_BARS, WIN_N = 285, 300
COLUMNS = ["run_id", "run_kind", "logged_at_sast", "date", "instrument", "series_role", "stream", "feed", "fetch_time_sast",
           "fetch_first_bar_ny", "fetch_last_bar_ny", "raw_file", "raw_sha256", "raw_rows", "bars_0700_1159", "missing_0700_1159",
           "calendar_status", "min_bar_ok", "session_complete", "rule_pins_ok", "harness_digest", "registration_commit",
           "registration_time_ny", "harness_matches_registered", "fill_thru_ticks", "cost_per_side_pts", "status", "direction",
           "type", "trigger", "entry_time_ny", "entry", "stop", "t1", "t2", "risk_pts", "R_T1", "out_T1", "R_T2", "out_T2",
           "R_5050", "out_5050", "exit_time_5050", "R_5050_cost1p5x", "R_5050_cost2x", "R_5050_cost3x", "range_low", "range_high", "trade_key", "alert_time_sast", "alert_time_ny",
           "live_alerted", "session_valid", "counted", "not_counted_reasons", "error"]


def data_dir() -> pathlib.Path:
    return F.DATA_ROOT / LEAD


def prereg() -> dict:
    return F.load_prereg(PREREG_REL)


def harness_manifest() -> dict:
    return F.manifest(HARNESS_FILES)


def harness_digest(m=None) -> str:
    m = m or harness_manifest()
    return F.sha256_bytes(json.dumps(m, sort_keys=True).encode())


# ------------------------------------------------------------------ frozen engine
_ENGINE = None


def load_engine():
    """Verify the sha256 pins, then import the frozen v1 engine from research/forward/H013/frozen. Sets FILL_THRU=1."""
    global _ENGINE
    if _ENGINE is None:
        bad = F.verify_pins(FROZEN, prereg()["rule_object_sha256"])
        if bad:
            raise RuntimeError(f"H013 rule-object sha256 mismatch, refusing to run: {bad}")
        sys.path.insert(0, str(V1_DIR))
        import u_engine as E1, run_u_lib as V1
        if pathlib.Path(E1.__file__).resolve().parent != V1_DIR.resolve():
            raise RuntimeError(f"imported u_engine from {E1.__file__}, not the frozen copy")
        _ENGINE = (E1, V1)
    E1, V1 = _ENGINE
    E1.FILL_THRU = FILL_THRU_TICKS
    return E1, V1


def costs() -> dict:
    return json.loads((FROZEN / "research/model-u-longrun/data/costs.json").read_text())


def evaluate(df: pd.DataFrame, d: str, inst: str, fill_thru: int = FILL_THRU_TICKS, cost: float | None = None) -> dict:
    """Frozen v1 base on one day, exactly as longrun.run() does it. Returns a longrun-shaped row (status trade / no trade)."""
    E1, V1 = load_engine()
    E1.FILL_THRU = fill_thru
    cost = costs()[inst] if cost is None else cost
    E1.SLIP = cost / E1.TICK
    pre = df[(df.index >= F.at(d, "07:00")) & (df.index < F.at(d, "09:00"))]
    if not len(pre):
        return dict(date=d, inst=inst, status="no data", cost_per_side_pts=cost, fill_thru_ticks=fill_thru)
    c = V1.ctx_for(df, d, inst); g = c["g"]
    t = V1.best_trade(c, *INVOCATION)
    base = dict(date=d, inst=inst, range_low=c["L"], range_high=c["H"], cost_per_side_pts=cost, fill_thru_ticks=fill_thru)
    if t is None:
        return {**base, "status": "no trade"}
    r = t["res"]; ft = g.index[r["fill_i"]]; risk = abs(t["entry"] - t["stop"])
    return {**base, "status": "trade", "direction": t["side"], "type": t["cand"]["kind"], "trigger": t["cand"]["why"],
            "entry_time_ny": ft.strftime("%H:%M"), "entry": t["entry"], "stop": t["stop"], "t1": t["t1"], "t2": t["t2"],
            "risk_pts": risk, "R_T1": r["R_t1"], "out_T1": r["out_t1"], "R_T2": r["R_t2"], "out_T2": r["out_t2"],
            "R_5050": r["R_part"], "out_5050": r["out_part"], "exit_time_5050": g.index[r["exit_part_i"]].strftime("%H:%M"),
            # cost ladder co-report (DATA fix 2): triggers do not depend on cost, so R_k = R - 2(k-1)*cost/risk exactly
            "R_5050_cost1p5x": r["R_part"] - 1.0 * cost / risk, "R_5050_cost2x": r["R_part"] - 2.0 * cost / risk,
            "R_5050_cost3x": r["R_part"] - 4.0 * cost / risk}


def bars_in_window(df: pd.DataFrame, d: str) -> int:
    return int(((df.index >= F.at(d, "07:00")) & (df.index < F.at(d, "12:00"))).sum())


def consumed(df: pd.DataFrame, d: str) -> pd.DataFrame:
    """The bars the engine can read for day d: from 18:00 NY two business days back (prior-session bias window) to < 12:00."""
    p2 = (pd.Timestamp(d) - pd.tseries.offsets.BDay(2)).date()
    return df[(df.index >= F.at(p2, "18:00")) & (df.index < F.at(d, "12:00"))]


def trade_key(row: dict) -> str | None:
    if row.get("status") != "trade":
        return None
    return f"{row['date']}|{row['inst']}|{row['direction']}|{row['entry']:.2f}|{row['entry_time_ny']}"


# ------------------------------------------------------------------ counting
def counting(row: dict, run_kind: str, reg: dict, alerts: list[dict], pins_ok: bool) -> dict:
    d, inst = row["date"], row["inst"]
    pr = prereg(); reasons = []
    cal = F.calendar_status(d, pr)
    bars = row.get("bars_0700_1159", 0) or 0
    complete = bool(row.get("session_complete"))
    if cal != "ok": reasons.append(f"calendar:{cal}")
    if bars < MIN_BARS: reasons.append(f"min_bars:{bars}<{MIN_BARS}")
    if not complete: reasons.append("session_incomplete(last bar < 11:59 NY)")
    if not pins_ok: reasons.append("rule_hash_mismatch")
    if not reg.get("registered"): reasons.append("harness_not_registered_on_main")
    elif not reg.get("harness_matches_registered"): reasons.append("harness_hash_mismatch")
    elif pd.Timestamp(reg["registration_time_ny"]) >= F.at(d, "07:00"): reasons.append("registered_after_session_start")
    session_valid = not reasons
    if inst != DECISION_INST: reasons.append("disclosure_series(US500 never counted)")
    if run_kind != "FINAL": reasons.append(f"{run_kind.lower()}_never_counted")
    out = dict(calendar_status=cal, min_bar_ok=bars >= MIN_BARS, session_valid=session_valid)
    k = trade_key(row)
    if k is None:
        reasons.append("no_trade")
        return {**out, "trade_key": None, "live_alerted": None, "counted": False, "not_counted_reasons": ";".join(reasons)}
    hit = [a for a in alerts if a.get("event") == "FILL" and a.get("key") == k]
    exit_close = F.at(d, row["exit_time_5050"]) + pd.Timedelta(minutes=1)
    live = bool(hit) and pd.Timestamp(hit[0]["alert_time_ny"]) < exit_close
    if not live: reasons.append("no_live_alert_before_exit" if not hit else "alert_after_exit")
    return {**out, "trade_key": k, "live_alerted": live, "alert_time_sast": hit[0]["alert_time_sast"] if hit else None,
            "alert_time_ny": hit[0]["alert_time_ny"] if hit else None, "counted": not reasons,
            "not_counted_reasons": ";".join(reasons)}


def session_row(df: pd.DataFrame, meta: dict, d: str, inst: str, run_kind: str, reg: dict, alerts: list[dict], run_id: str,
                pins_ok: bool = True, save: bool = True) -> dict:
    cons = consumed(df, d)
    raw_file, raw_sha = F.save_raw(cons, LEAD, inst, f"{d}__{run_kind.lower()}__{F.now_sast():%Y%m%dT%H%M%S}") if save else (None, F.sha256_bytes(F.bars_to_csv_bytes(cons)))
    bars = bars_in_window(cons, d)
    complete = len(cons) > 0 and cons.index[-1] >= F.at(d, "11:59")
    row = evaluate(cons, d, inst)
    row.update(bars_0700_1159=bars, missing_0700_1159=WIN_N - bars, session_complete=complete)
    row.update(counting(row, run_kind, reg, alerts, pins_ok))
    row.update(run_id=run_id, run_kind=run_kind, logged_at_sast=F.now_sast().strftime("%Y-%m-%d %H:%M:%S"), instrument=inst,
               series_role="decision" if inst == DECISION_INST else "disclosure", stream=STREAM[inst], raw_file=raw_file,
               raw_sha256=raw_sha, raw_rows=len(cons), rule_pins_ok=pins_ok, harness_digest=harness_digest(),
               registration_commit=reg.get("registration_commit"), registration_time_ny=reg.get("registration_time_ny"),
               harness_matches_registered=reg.get("harness_matches_registered"), **meta)
    return row


# ------------------------------------------------------------------ commands
def cmd_final(d: str, run_kind: str = "FINAL", fetch=None, fetch_remote: bool = True) -> list[dict]:
    load_engine()
    reg = F.registration_status(PREREG_REL, harness_manifest(), fetch=fetch_remote)
    alerts = F.read_jsonl(data_dir() / "alerts.jsonl")
    run_id = uuid.uuid4().hex[:12]; rows = []
    for inst in INSTS:
        try:
            df, meta = F.fetch_capitalcom(inst, n=8000, _fetch=fetch)
            row = session_row(df, meta, d, inst, run_kind, reg, alerts, run_id)
        except F.FeedError as e:
            row = dict(run_id=run_id, run_kind=run_kind, date=d, instrument=inst, status="feed_gap", error=str(e), counted=False,
                       not_counted_reasons="feed_gap", feed=f"TradingView {F.FEEDS[inst]}",
                       logged_at_sast=F.now_sast().strftime("%Y-%m-%d %H:%M:%S"))
        F.append_csv(data_dir() / "log.csv", row, COLUMNS); rows.append(row)
    return rows


def cmd_watch(d: str, until: str = "11:31", fetch=None, sleep=time.sleep, now_fn=None, max_polls: int | None = None):
    """Poll CAPITALCOM once a minute (at :05 s); on each NEW first fill append a FILL alert + raw snapshot."""
    load_engine()
    now_fn = now_fn or (lambda: pd.Timestamp.now(tz=F.TZ))
    cal = F.calendar_status(d, prereg())
    if cal != "ok":
        print(f"{d}: calendar {cal}, no watch"); return 0
    data_dir().mkdir(parents=True, exist_ok=True)
    lock = open(data_dir() / "watch.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)    # single watcher per box; a watchdog re-run is a no-op
    except BlockingIOError:
        print("watcher already running"); return 0
    seen = {a["key"] for a in F.read_jsonl(data_dir() / "alerts.jsonl") if a.get("event") == "FILL"}
    polls = 0
    while now_fn() < F.at(d, until) and (max_polls is None or polls < max_polls):
        polls += 1
        for inst in INSTS:
            ts = F.now_sast()
            try:
                df, meta = F.fetch_capitalcom(inst, n=1500, now=now_fn(), _fetch=fetch)
            except F.FeedError as e:
                F.append_jsonl(data_dir() / "alerts.jsonl", dict(event="FEED_GAP", date=d, instrument=inst,
                                                                alert_time_sast=str(ts), error=str(e))); continue
            cons = consumed(df, d)
            if not len(cons) or cons.index[-1] < F.at(d, "09:00"):
                continue
            row = evaluate(cons, d, inst); k = trade_key(row)
            if k is None or k in seen:
                continue
            raw_file, raw_sha = F.save_raw(cons, LEAD, inst, f"{d}__live__{ts:%Y%m%dT%H%M%S}")
            F.append_jsonl(data_dir() / "alerts.jsonl", dict(
                event="FILL", key=k, date=d, instrument=inst, stream=STREAM[inst], alert_time_sast=str(ts),
                alert_time_ny=str(now_fn()), last_bar_ny=str(cons.index[-1]), fill_time_ny=row["entry_time_ny"],
                direction=row["direction"], entry=row["entry"], stop=row["stop"], t1=row["t1"], t2=row["t2"],
                raw_file=raw_file, raw_sha256=raw_sha, harness_digest=harness_digest(), **meta))
            seen.add(k)
        nxt = now_fn().floor("min") + pd.Timedelta(minutes=1, seconds=5)
        sleep(max(1.0, (nxt - now_fn()).total_seconds()))
    return polls


def cmd_report() -> dict:
    p = data_dir() / "log.csv"
    if not p.exists():
        return dict(n_counted=0)
    lg = pd.read_csv(p)
    fin = lg[lg.run_kind == "FINAL"].drop_duplicates(["date", "instrument"], keep="last")
    out = {}
    for inst in INSTS:
        x = fin[(fin.instrument == inst) & (fin.status == "trade")]
        c = x[x.counted.astype(str) == "True"] if inst == DECISION_INST else x[x.session_valid.astype(str) == "True"]
        out[inst] = dict(role="decision" if inst == DECISION_INST else "disclosure", n=len(c),
                         mean_R=float(c.R_5050.mean()) if len(c) else None, cum_R=float(c.R_5050.sum()) if len(c) else 0.0)
    bf = lg[lg.run_kind == "BACKFILL"]
    out["backfill_rows_never_counted"] = int(len(bf))
    out["binding_N"] = prereg()["binding_N"]
    return out


def selfcheck() -> dict:
    bad = F.verify_pins(FROZEN, prereg()["rule_object_sha256"])
    m = harness_manifest()
    return dict(rule_pins_ok=not bad, rule_pin_mismatch=bad, harness_manifest=m, harness_digest=harness_digest(m),
                prereg_harness=prereg().get("harness_sha256"), registration=F.registration_status(PREREG_REL, m))


def _today_ny() -> str:
    return pd.Timestamp.now(tz=F.TZ).strftime("%Y-%m-%d")


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "selfcheck"
    day = next((x for x in a[1:] if x[:2] == "20" and len(x) == 10), None) or _today_ny()
    if cmd == "watch":
        until = a[a.index("--until") + 1] if "--until" in a else "11:31"
        print("polls", cmd_watch(day, until))
    elif cmd == "final":
        for r in cmd_final(day): print({k: r.get(k) for k in ("date", "instrument", "status", "direction", "entry_time_ny", "R_5050", "bars_0700_1159", "counted", "not_counted_reasons")})
    elif cmd == "backfill":
        for r in cmd_final(day, "BACKFILL"): print({k: r.get(k) for k in ("date", "instrument", "status", "R_5050", "counted", "not_counted_reasons")})
    elif cmd == "report":
        print(json.dumps(cmd_report(), indent=2, default=str))
    else:
        print(json.dumps(selfcheck(), indent=2, default=str))
