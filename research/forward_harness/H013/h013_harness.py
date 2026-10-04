"""H013 forward harness core (Model U v1 base, frozen forward-only test). HYPOTHETICAL paper research: no orders, no broker.
Implements research/protocols/preregs/H013_FORWARD_PREREG_2026-10-04.json (GdotAiM/hermes) exactly:
  * rule objects = the four sha256-pinned files (u_engine.py, run_u_lib.py, longrun.py, costs.json); a mismatch aborts the run
  * invocation best_trade(ctx, "11:00", False, False, True); E1.FILL_THRU = 1 tick; E1.SLIP = cost/tick (US100 0.8 -> 3.2 ticks)
  * feed = TradingView CAPITALCOM:US100 (decision) / CAPITALCOM:US500 (disclosure). NO fallback feed; missing minutes are
    logged as gaps, never substituted
  * holiday filter (prereg list) + min-bar filter (>= 285 of 300 1m bars in 07:00-11:59 NY)
  * raw 1m bars consumed are persisted to raw/forward/<inst>_<YYYY-MM-DD>.csv (never overwritten) and their sha256 is logged
  * append-only log h013_forward_log.csv with provenance (feed, fetch time, raw file + sha256, harness/engine hashes,
    registration-on-main status) and the counting decision with reasons
Feed: TradingView CAPITALCOM (NOT Dukascopy). All rule times America/New_York wall clock."""
import csv, datetime as dt, hashlib, json, os, pathlib, subprocess, sys, uuid
import numpy as np, pandas as pd

CODE = pathlib.Path(__file__).resolve().parent; FT = CODE; ROOT = CODE.parent; LR = ROOT / "research/model-u-longrun"
TZ = "America/New_York"; SAST = "Africa/Johannesburg"
HERMES = pathlib.Path(os.environ.get("HERMES_REPO", "/workspace/hermes"))
PREREG_PATH = "research/protocols/preregs/H013_FORWARD_PREREG_2026-10-04.json"
RULE_SHA256 = {  # copied from the prereg; verified at import of the engine
    "research/model-u-longrun/scripts/v1/u_engine.py": "5e98e99e47133905c6662afcdea9d9df4ef74e7afefa49f17e7798925613fe4e",
    "research/model-u-longrun/scripts/v1/run_u_lib.py": "8d00223c1f326bd386c1f924f05dc92fd38a3674639b57cd96df12194cdddad2",
    "research/model-u-longrun/scripts/longrun.py": "bf88f0ad0b1d097a483f6cd02f4adba9e5072ffbb533d921d1956d65ef743fc4",
    "research/model-u-longrun/data/costs.json": "a1df6f5b59122ae91bd9673911dbab1f3560737c14515234b3dd78bddd07062d",
}
HARNESS_FILES = ["h013_harness.py", "tv_final.py", "backfill_tv.py", "h013_live_watch.py", "tv_feed.py"]   # counting gate set
FEED = {"US100": "CAPITALCOM:US100", "US500": "CAPITALCOM:US500"}
STREAM = {"US100": "FWD-TV-CAPITALCOM-US100", "US500": "FWD-TV-CAPITALCOM-US500"}
DECISION_INST = "US100"
FILL_THRU_TICKS = 1
INVOCATION = ("11:00", False, False, True)
MIN_BARS, WIN_FROM, WIN_TO, WIN_N = 285, "07:00", "11:59", 300
HOLIDAYS_FULL = {"2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18",
                 "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24"}
HOLIDAYS_EARLY = {"2026-11-27", "2026-12-24", "2027-11-26"}
HOLIDAYS_HIST = {"2025-12-24"}
CALENDAR_LAST_COVERED = "2027-12-31"      # DATA must extend the list before any session after this date
FIRST_POSSIBLE_SESSION = "2026-10-05"
LOG = FT / "h013_forward_log.csv"; ALERTS = FT / "h013_alerts.jsonl"; RAW = FT / "raw" / "forward"
COLUMNS = ["run_id", "run_kind", "logged_at_sast", "date", "instrument", "stream", "series_role", "feed", "fetch_time_sast",
           "fetch_first_bar_ny", "fetch_last_bar_ny", "raw_file", "raw_sha256", "raw_rows", "bars_0700_1159", "missing_0700_1159",
           "gap_day", "calendar_status", "min_bar_ok", "engine_sha256_ok", "harness_sha256_digest", "harness_registered_on_main",
           "prereg_main_commit", "registration_landed_ny", "session_start_ny", "fill_thru_ticks", "cost_per_side_pts", "slip_ticks",
           "status", "direction", "setup", "trigger", "c2_time_ny", "entry_time_ny", "entry", "stop", "T1", "T2", "risk_pts",
           "R_T1", "out_T1", "R_T2", "out_T2", "R_5050", "out_5050", "exit_time_5050_ny", "range_low", "range_high",
           "fill_alert_sast", "fill_alert_raw_sha256", "live_alerted", "counted", "not_counted_reasons", "duplicate_of_run", "note"]

class FeedError(RuntimeError): pass

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

def now_sast(): return pd.Timestamp.now(tz=SAST)
def at(d, hm): return pd.Timestamp(f"{d} {hm}").tz_localize(TZ)

# ---------------------------------------------------------------- frozen engine
def verify_rule_objects():
    bad = {k: sha256_file(ROOT / k) for k in RULE_SHA256 if sha256_file(ROOT / k) != RULE_SHA256[k]}
    if bad: raise SystemExit(f"H013 ABORT: frozen rule object hash mismatch {bad} -> counting void, new ID needed (H013b)")
    return True

def load_engine():
    verify_rule_objects()
    for p in (str(LR / "scripts/v1"),):
        if p not in sys.path: sys.path.insert(0, p)
    import u_engine as E1, run_u_lib as V1
    E1.FILL_THRU = FILL_THRU_TICKS
    return E1, V1

COST = json.load(open(LR / "data/costs.json"))
def set_cost(E1, nm, fill_thru=FILL_THRU_TICKS): E1.SLIP = COST[nm] / E1.TICK; E1.FILL_THRU = fill_thru

# ---------------------------------------------------------------- calendar / bar filters
def calendar_status(d):
    ts = pd.Timestamp(d)
    if ts.weekday() >= 5: return "weekend"
    if d in HOLIDAYS_FULL: return "holiday_full_closure"
    if d in HOLIDAYS_EARLY: return "holiday_early_close"
    if d in HOLIDAYS_HIST: return "holiday_historical_exclusion"
    if d > CALENDAR_LAST_COVERED: return "calendar_not_covered"
    return "ok"

def window_bars(df, d):
    w = df[(df.index >= at(d, WIN_FROM)) & (df.index < at(d, "12:00"))]
    full = pd.date_range(at(d, WIN_FROM), periods=WIN_N, freq="1min")
    missing = [t.strftime("%H:%M") for t in full.difference(w.index)]
    return len(w), missing

# ---------------------------------------------------------------- feed (CAPITALCOM only, no fallback)
def fetch(nm, n, d=None, end_hm="16:59"):
    """TradingView CAPITALCOM only. Drops the still-forming bar; optionally truncates to d end_hm NY. Raises FeedError."""
    from tv_feed import fetch_tv
    t_fetch = now_sast()
    try: df = fetch_tv(FEED[nm], n=n)
    except Exception as e: raise FeedError(f"{FEED[nm]}: {str(e)[:200]} (no fallback feed by prereg; session gap logged)")
    now = pd.Timestamp.now(tz=TZ)
    df = df[df.index + pd.Timedelta(minutes=1) <= now]
    if d is not None: df = df[df.index <= at(d, end_hm)]
    if not len(df): raise FeedError(f"{FEED[nm]}: no bars")
    return df[["Open", "High", "Low", "Close"]].astype(float), dict(feed=f"TradingView {FEED[nm]}", fetch_time_sast=t_fetch.strftime("%Y-%m-%d %H:%M:%S"),
                                                                   fetch_first_bar_ny=str(df.index[0]), fetch_last_bar_ny=str(df.index[-1]))

def save_raw(df, name, sub=None, dry=False):
    """Write raw bars; never overwrite. Returns (relative path, sha256). Identical content re-uses the existing file."""
    d = RAW / sub if sub else RAW
    body = df.to_csv(index_label="time_ny").encode()
    h = hashlib.sha256(body).hexdigest(); p = d / f"{name}.csv"
    if dry: return f"(dry-run, not written) {p.relative_to(FT)}", h
    d.mkdir(parents=True, exist_ok=True)
    if p.exists() and sha256_file(p) != h:
        p = d / f"{name}__{now_sast():%Y%m%dT%H%M%S}.csv"
    if not p.exists(): p.write_bytes(body)
    assert sha256_file(p) == h
    return str(p.relative_to(FT)), h

def load_raw(path):
    p = pathlib.Path(path); p = p if p.is_absolute() else FT / p
    df = pd.read_csv(p, index_col=0); df.index = pd.to_datetime(df.index, utc=True).tz_convert(TZ)
    df.columns = [c.capitalize() for c in df.columns]
    return df[["Open", "High", "Low", "Close"]].astype(float)

# ---------------------------------------------------------------- harness hash + registration on main
def harness_hashes(): return {f: sha256_file(CODE / f) for f in HARNESS_FILES}
def harness_digest(hh=None):
    hh = hh or harness_hashes(); return hashlib.sha256(json.dumps(hh, sort_keys=True).encode()).hexdigest()

def registration_status(fetch_remote=True):
    """Is this exact harness hash-registered in the prereg on origin/main, and when did it land (first-parent commit time)?"""
    out = dict(ok=False, main_commit=None, landed_ny=None, mismatches=None, error=None)
    try:
        if fetch_remote: subprocess.run(["git", "-C", str(HERMES), "fetch", "-q", "origin", "main"], timeout=30, capture_output=True)
        out["main_commit"] = subprocess.run(["git", "-C", str(HERMES), "rev-parse", "origin/main"], capture_output=True, text=True, timeout=10).stdout.strip()
        js = json.loads(subprocess.run(["git", "-C", str(HERMES), "show", f"origin/main:{PREREG_PATH}"], capture_output=True, text=True, timeout=10, check=True).stdout)
        reg = js.get("harness_sha256"); mine = harness_hashes()
        if not isinstance(reg, dict) or "files" not in reg: out["mismatches"] = "harness_sha256 not registered on main (PENDING)"; return out
        mm = {f: (reg["files"].get(f), h) for f, h in mine.items() if reg["files"].get(f) != h}
        if mm: out["mismatches"] = json.dumps(mm); return out
        probe = mine["h013_harness.py"]
        log = subprocess.run(["git", "-C", str(HERMES), "log", "--first-parent", "-m", "-S", probe, "--format=%H|%cI", "origin/main", "--", PREREG_PATH],
                             capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
        if log: out["landed_ny"] = str(pd.Timestamp(log[-1].split("|")[1]).tz_convert(TZ))
        out["ok"] = out["landed_ny"] is not None
    except Exception as e: out["error"] = str(e)[:200]
    return out

# ---------------------------------------------------------------- live alerts (append-only JSONL)
def append_alert(ev):
    with open(ALERTS, "a") as f: f.write(json.dumps(ev, default=str) + "\n")

def read_alerts():
    if not ALERTS.exists(): return []
    return [json.loads(l) for l in open(ALERTS) if l.strip()]

def trade_key(d, nm, side, entry, fill_hm): return f"{d}|{nm}|{side}|{float(entry):.2f}|{fill_hm}"

def first_fill_alert(d, nm, side, entry, fill_hm):
    k = trade_key(d, nm, side, entry, fill_hm)
    ev = [a for a in read_alerts() if a.get("event") == "FILL" and a.get("key") == k]
    return min(ev, key=lambda a: a["alert_sast"]) if ev else None

# ---------------------------------------------------------------- one session evaluation (pure: no I/O besides engine)
def evaluate(E1, V1, df, d, nm, fill_thru=FILL_THRU_TICKS):
    """fill_thru is fixed at the frozen 1 tick in every harness path; tests pass 0 only to reproduce legacy/as-reported runs."""
    set_cost(E1, nm, fill_thru)
    c = V1.ctx_for(df, d, nm); g = c["g"]
    t = V1.best_trade(c, *INVOCATION) if len(g) and c["i900"] < len(g) else None
    base = dict(range_low=c["L"], range_high=c["H"], fill_thru_ticks=E1.FILL_THRU, cost_per_side_pts=COST[nm], slip_ticks=E1.SLIP)
    if t is None: return {**base, "status": "no trade"}, None
    r = t["res"]; cand = t["cand"]
    xi = r["exit_part_i"]; exit_t = g.index[xi] + pd.Timedelta(minutes=1)
    return {**base, "status": "trade", "direction": t["side"], "setup": cand["kind"], "trigger": cand["why"],
            "c2_time_ny": g.index[cand["c2"]].strftime("%H:%M") if cand.get("c2") is not None else None,
            "entry_time_ny": g.index[r["fill_i"]].strftime("%H:%M"), "entry": t["entry"], "stop": t["stop"], "T1": t["t1"], "T2": t["t2"],
            "risk_pts": abs(t["entry"] - t["stop"]), "R_T1": r["R_t1"], "out_T1": r["out_t1"], "R_T2": r["R_t2"], "out_T2": r["out_t2"],
            "R_5050": r["R_part"], "out_5050": r["out_part"], "exit_time_5050_ny": str(exit_t)}, t

# ---------------------------------------------------------------- append-only log
def read_log():
    return pd.read_csv(LOG, dtype=str) if LOG.exists() else pd.DataFrame(columns=COLUMNS)

def append_rows(rows):
    new = not LOG.exists()
    if not new:
        with open(LOG) as f: hdr = next(csv.reader(f))
        if hdr != COLUMNS: raise SystemExit(f"H013 ABORT: {LOG.name} header differs from harness schema (append-only log must not be rewritten)")
    with open(LOG, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="raise")
        if new: w.writeheader()
        for r in rows: w.writerow({k: r.get(k) for k in COLUMNS})

def finalize_session(d, run_kind, frames, metas, reg, note="", dry=False):
    """frames: {inst: df of raw CAPITALCOM bars consumed}. Writes raw files + appends one row per instrument. Returns rows."""
    E1, V1 = load_engine()
    run_id = f"{now_sast():%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:6]}"; logged = now_sast().strftime("%Y-%m-%d %H:%M:%S")
    hh = harness_hashes(); dig = harness_digest(hh); prior = read_log(); rows = []
    for nm in ("US100", "US500"):
        base = dict(run_id=run_id, run_kind=run_kind, logged_at_sast=logged, date=d, instrument=nm, stream=STREAM[nm],
                    series_role="decision" if nm == DECISION_INST else "disclosure (never pooled, never gating)",
                    engine_sha256_ok=True, harness_sha256_digest=dig, harness_registered_on_main=reg.get("ok"),
                    prereg_main_commit=reg.get("main_commit"), registration_landed_ny=reg.get("landed_ny"),
                    session_start_ny=str(at(d, "07:00")), calendar_status=calendar_status(d), note=note)
        reasons = []
        if nm not in frames:
            rows.append({**base, **metas.get(nm, {}), "status": "feed gap (no data)", "counted": False,
                         "not_counted_reasons": "feed_error: " + metas.get(nm, {}).get("error", "?")}); continue
        df = frames[nm]; base.update(metas[nm])
        base["raw_file"], base["raw_sha256"] = save_raw(df, f"{nm}_{d}", dry=dry); base["raw_rows"] = len(df)
        nb, miss = window_bars(df, d); base.update(bars_0700_1159=nb, missing_0700_1159=" ".join(miss), gap_day=bool(miss),
                                                   min_bar_ok=nb >= MIN_BARS)
        if base["calendar_status"] != "ok": reasons.append(base["calendar_status"])
        if nb < MIN_BARS: reasons.append(f"min_bars {nb}<{MIN_BARS}")
        if base["calendar_status"] in ("weekend", "holiday_full_closure") or nb < 150:
            rows.append({**base, "status": "excluded (no session)", "counted": False, "not_counted_reasons": "; ".join(reasons)}); continue
        res, t = evaluate(E1, V1, df, d, nm); row = {**base, **res}
        if t is not None:
            a = first_fill_alert(d, nm, res["direction"], res["entry"], res["entry_time_ny"])
            if a:
                row["fill_alert_sast"] = a["alert_sast"]; row["fill_alert_raw_sha256"] = a.get("raw_sha256")
                row["live_alerted"] = pd.Timestamp(a["alert_sast"]).tz_localize(SAST) < pd.Timestamp(res["exit_time_5050_ny"])
            else: row["live_alerted"] = False
            if not row["live_alerted"]: reasons.append("not live-alerted before exit")
        if nm != DECISION_INST: reasons.append("disclosure series (US500 never counts)")
        if run_kind != "FINAL": reasons.append(f"run_kind {run_kind} (only same-day FINAL rows count; backfills never count)")
        if d < FIRST_POSSIBLE_SESSION: reasons.append("before first eligible session (pre-registration row)")
        if not reg.get("ok"): reasons.append("harness hash not registered on origin/main: " + str(reg.get("mismatches") or reg.get("error")))
        elif pd.Timestamp(reg["landed_ny"]) >= at(d, "07:00"): reasons.append("harness registered on main after session start")
        dup = prior[(prior.date == d) & (prior.instrument == nm) & (prior.run_kind == "FINAL")] if len(prior) else prior
        if run_kind == "FINAL" and len(dup): row["duplicate_of_run"] = dup.run_id.iloc[0]; reasons.append("duplicate final run (first FINAL row stands)")
        if dry: reasons.append("DRY-RUN (not logged)")
        row["counted"] = not reasons; row["not_counted_reasons"] = "; ".join(reasons); rows.append(row)
    if not dry: append_rows(rows)
    return rows
