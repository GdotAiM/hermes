"""H014 forward harness: MMXM v5 A_overnight_5mFVG_ce_c12_none, frozen forward-only test. HYPOTHETICAL paper research only:
no orders, no broker calls. Implements research/protocols/preregs/H014_FORWARD_PREREG_2026-10-04.json (GdotAiM/hermes):
  * frozen rule = configs/v5_A_overnight_5mFVG_ce_c12_none.yaml + mmxm/{engine,data,config,baseline}.py, sha256-verified
    (mismatch aborts); engine run UNCHANGED via run_backtest(m1, cfg, root, symbol); US100 -> NQ root, US500 -> ES root
  * PRIMARY (binding) R = frozen settings: 1-tick fill-through, RT cost 0.8 / 0.5 pts once per trade, no stop slippage,
    touch-both = stop
  * CO-REPORTS (never binding, per prereg required_co_reports / DATA fix 2): spread-side fill model = DATA fill-realism
    proxy (limit entries and targets need spread + 1 tick trade-through, stops slip 1 spread, RT 2 x 0.25 slippage;
    US100 6/4 ticks, US500 3/2 ticks), DATA measured-cost model (1.617 / 1.01 RT), 2x cost, random-entry baseline
    (mmxm/baseline.py outcome_table on the same trade/day), exit reason
  * feed = TradingView CAPITALCOM:US100 / CAPITALCOM:US500 only (no fallback; failed fetch = logged gap)
  * day filters: prereg holiday list; >= 86/90 1m bars 09:30-10:59 and >= 791/930 in the 18:00 -> 09:30 overnight range
  * 1H-context warm-up (DATA open item): CAPITALCOM bars from every saved fetch (archive + earlier sessions) first; any
    older bars needed for the 60-day context window come from the pinned Dukascopy BID parquet (ends 2026-09-25). Rows log
    how many warm-up bars are Dukascopy; the session's own bars (18:00 prior day -> 16:59) must be 100% CAPITALCOM to count
  * raw 1m bars consumed (incl. the src column) -> raw/forward/<inst>_<date>.csv (never overwritten), sha256 in the row
  * APPEND-ONLY log h014_forward_log.csv: US100 and US500 rows separately, pooled cumulative R and the binding -5R kill
Usage: h014_forward.py [YYYY-MM-DD|today] [--backfill] [--dry] [--raw US100=a.csv US500=b.csv]
Run after 11:00 NY (17:05 SAST until 30 Oct 2026; 18:05 SAST from 2 Nov 2026). All rule times America/New_York."""
import copy, csv, datetime as dt, glob, hashlib, json, os, pathlib, subprocess, sys, uuid
import numpy as np, pandas as pd

HERE = pathlib.Path(__file__).resolve().parent; MM = HERE.parent
sys.path.insert(0, str(MM))
TZ = "America/New_York"; SAST = "Africa/Johannesburg"
HERMES = pathlib.Path(os.environ.get("HERMES_REPO", "/workspace/hermes"))
TVFEED_DIR = pathlib.Path(os.environ.get("TVFEED_DIR", "/workspace/ict-blueprint/forward-test"))
CAPCOM_ARCHIVES = [TVFEED_DIR / "raw/forward/archive"]
PREREG_PATH = "research/protocols/preregs/H014_FORWARD_PREREG_2026-10-04.json"
CONFIG = "configs/v5_A_overnight_5mFVG_ce_c12_none.yaml"
RULE_SHA256 = {
    "configs/v5_A_overnight_5mFVG_ce_c12_none.yaml": "3414c77c4693a2ad0557a3f77513118ad292821e6d18f6713b901c7451b67968",
    "mmxm/engine.py": "86e7180980517e20b03a9bf4668dea28329fa203151fe56fa872e02a51f6c67f",
    "mmxm/data.py": "fa2ebee1e25c87507f9faf26fed99f7c7a9edf7a234dcfda198ad163bd255fcd",
    "mmxm/config.py": "4614c85b38c52f60018bd1b174368b4be221c47d645960a0cb89e6de16988f65",
    "mmxm/baseline.py": "8298952b8dcd2903e1783bb70a97ed257c255d2b613609c5c0373f72778516ed",
}
WARMUP_SHA256 = {"data/US100_1m.parquet": "faf8477da05c3484f5ec582ae857ce0cdca4683d13c307763de84c48868bdffb",
                 "data/US500_1m.parquet": "87b753229d2c9accec913b540bc06635ce135dc9e719f9e2204e2f4f71856f1a"}
HARNESS_FILES = {"h014_forward.py": HERE / "h014_forward.py", "tv_feed.py": TVFEED_DIR / "tv_feed.py"}
SYMS = ("US100", "US500"); ROOT = {"US100": "NQ", "US500": "ES"}
FEED = {"US100": "CAPITALCOM:US100", "US500": "CAPITALCOM:US500"}
STREAM = {"US100": "FWD-TV-CAPITALCOM-US100", "US500": "FWD-TV-CAPITALCOM-US500"}
HOLIDAYS_FULL = {"2026-11-26", "2026-12-25", "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31", "2027-06-18",
                 "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24"}
HOLIDAYS_EARLY = {"2026-11-27", "2026-12-24", "2027-11-26"}
HOLIDAYS_HIST = {"2025-11-27", "2025-12-24", "2026-07-03"}
CALENDAR_LAST_COVERED = "2027-12-31"
MIN_RTH, N_RTH, MIN_ON, N_ON = 86, 90, 791, 930
FIRST_POSSIBLE_SESSION = "2026-10-05"
KILL_R = -5.0
HIST_DAYS = 60
SPREAD_PROXY = {"US100": dict(fill_through_ticks=6, stop_slippage_ticks=4, cost=0.5), "US500": dict(fill_through_ticks=3, stop_slippage_ticks=2, cost=0.5)}
MEASURED_COST_RT = {"US100": 1.617, "US500": 1.01}
LOG = HERE / "h014_forward_log.csv"; RAW = HERE / "raw" / "forward"
COLUMNS = ["run_id", "run_kind", "backfilled", "logged_at_sast", "date", "instrument", "stream", "feed", "fetch_time_sast",
           "fetch_first_bar_ny", "fetch_last_bar_ny", "raw_file", "raw_sha256", "raw_rows", "warmup_dukascopy_bars", "session_bars_all_capitalcom",
           "bars_0930_1059", "bars_overnight", "missing_0930_1059", "calendar_status", "min_bar_ok", "engine_sha256_ok",
           "harness_sha256_digest", "harness_registered_on_main", "prereg_main_commit", "registration_landed_ny", "session_start_ny",
           "status", "trade_no", "direction", "order_time_ny", "entry_time_ny", "exit_time_ny", "entry", "stop", "risk_pts", "tp1", "tp1_source",
           "draw", "draw_kind", "exit_reason", "R_frozen", "R_spread_proxy", "spread_proxy_status", "R_measured_cost", "R_2x_cost",
           "baseline_mean_R", "baseline_n", "baseline_file", "orders_today", "counted", "not_counted_reasons", "duplicate_of_run",
           "cum_R_pooled_counted", "cum_R_US100_counted", "cum_R_US500_counted", "kill_triggered", "note"]

class FeedError(RuntimeError): pass

def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def now_sast(): return pd.Timestamp.now(tz=SAST)
def at(d, hm): return pd.Timestamp(f"{d} {hm}").tz_localize(TZ)
def prev_bday(d): return (pd.Timestamp(d) - pd.tseries.offsets.BDay(1)).strftime("%Y-%m-%d")

def verify_rule_objects():
    bad = {k: sha256_file(MM / k) for k in RULE_SHA256 if sha256_file(MM / k) != RULE_SHA256[k]}
    if bad: raise SystemExit(f"H014 ABORT: frozen rule object hash mismatch {bad} -> counting void, new ID needed (H014b)")
    return True

def load_engine():
    verify_rule_objects()
    from mmxm.config import Config
    from mmxm import data as D
    from mmxm.engine import run_backtest
    from mmxm.baseline import outcome_table
    cfg = Config.from_yaml(str(MM / CONFIG))
    return cfg, D, run_backtest, outcome_table

def calendar_status(d):
    if pd.Timestamp(d).weekday() >= 5: return "weekend"
    if d in HOLIDAYS_FULL: return "holiday_full_closure"
    if d in HOLIDAYS_EARLY: return "holiday_early_close"
    if d in HOLIDAYS_HIST: return "holiday_historical_exclusion"
    if d > CALENDAR_LAST_COVERED: return "calendar_not_covered"
    return "ok"

def session_start(d):
    """Overnight range opens 18:00 NY on the prior calendar day (engine key wraps midnight: [18:00, 24:00) -> next day)."""
    return at((pd.Timestamp(d) - pd.Timedelta(days=1)).strftime("%Y-%m-%d"), "18:00")

def bar_counts(m1, d):
    rth = m1[(m1.index >= at(d, "09:30")) & (m1.index < at(d, "11:00"))]
    on = m1[(m1.index >= session_start(d)) & (m1.index < at(d, "09:30"))]
    full = pd.date_range(at(d, "09:30"), periods=N_RTH, freq="1min")
    return len(rth), len(on), [t.strftime("%H:%M") for t in full.difference(rth.index)]

# ------------------------------------------------------------------ data
def _norm(df):
    df = df.copy(); df.columns = [str(c).lower() for c in df.columns]
    idx = pd.DatetimeIndex(df.index); df.index = (idx.tz_localize(TZ) if idx.tz is None else idx.tz_convert(TZ))
    return df[["open", "high", "low", "close"]].astype(float)

def read_csv_bars(p):
    df = pd.read_csv(p, index_col=0); df.index = pd.to_datetime(df.index, utc=True).tz_convert(TZ)
    if "src" in df.columns: df = df[df["src"] == "CAPITALCOM"]
    return _norm(df)

def fetch(nm, n=8000):
    sys.path.insert(0, str(TVFEED_DIR)); from tv_feed import fetch_tv
    t = now_sast()
    try: df = fetch_tv(FEED[nm], n=n)
    except Exception as e: raise FeedError(f"{FEED[nm]}: {str(e)[:200]} (no fallback feed by prereg; session gap logged)")
    now = pd.Timestamp.now(tz=TZ); df = df[df.index + pd.Timedelta(minutes=1) <= now]
    if not len(df): raise FeedError(f"{FEED[nm]}: no bars")
    return _norm(df), dict(feed=f"TradingView {FEED[nm]}", fetch_time_sast=t.strftime("%Y-%m-%d %H:%M:%S"),
                           fetch_first_bar_ny=str(df.index[0]), fetch_last_bar_ny=str(df.index[-1]))

def capitalcom_history(nm, extra=None):
    """Union of every saved CAPITALCOM 1m fetch for nm (archives + earlier session raw files); later files win; extra wins last."""
    files = []
    for a in CAPCOM_ARCHIVES: files += sorted(glob.glob(str(a / f"CAPITALCOM_{nm}_1m_*.csv")))
    files += sorted(glob.glob(str(RAW / f"{nm}_*.csv")))
    parts = [read_csv_bars(f) for f in sorted(files, key=os.path.getmtime)]
    if extra is not None: parts.append(extra)
    if not parts: return pd.DataFrame(columns=["open", "high", "low", "close"])
    df = pd.concat(parts); return df[~df.index.duplicated(keep="last")].sort_index()

def build_input(nm, d, cap, D):
    """Engine input for session d: [d-60 days, d 16:59] NY. CAPITALCOM wherever available; Dukascopy BID only before the first
    CAPITALCOM bar. Returns (m1 with volume NaN, src Series)."""
    lo, hi = at(d, "00:00") - pd.Timedelta(days=HIST_DAYS), at(d, "16:59")
    if not len(cap): cap = pd.DataFrame(columns=["open", "high", "low", "close"], index=pd.DatetimeIndex([], tz=TZ), dtype=float)
    cap = cap[(cap.index >= lo) & (cap.index <= hi)]
    first = cap.index[0] if len(cap) else hi + pd.Timedelta(minutes=1)
    duk = D.load_cfd(nm); duk = duk[(duk.index >= lo) & (duk.index < first)][["open", "high", "low", "close"]]
    m1 = pd.concat([duk, cap]).sort_index(); src = pd.Series(["DUKASCOPY_BID_WARMUP"] * len(duk) + ["CAPITALCOM"] * len(cap), index=m1.index)
    m1["volume"] = np.nan
    return m1, src

def save_raw(m1, src, name, dry=False):
    out = m1[["open", "high", "low", "close"]].copy(); out["src"] = src.values
    body = out.to_csv(index_label="time_ny").encode(); h = hashlib.sha256(body).hexdigest(); p = RAW / f"{name}.csv"
    if dry: return f"(dry-run, not written) {p.relative_to(HERE)}", h
    RAW.mkdir(parents=True, exist_ok=True)
    if p.exists() and sha256_file(p) != h: p = RAW / f"{name}__{now_sast():%Y%m%dT%H%M%S}.csv"
    if not p.exists(): p.write_bytes(body)
    assert sha256_file(p) == h
    return str(p.relative_to(HERE)), h

# ------------------------------------------------------------------ registration on main
def harness_hashes(): return {k: sha256_file(p) for k, p in HARNESS_FILES.items()}
def harness_digest(hh=None): return hashlib.sha256(json.dumps(hh or harness_hashes(), sort_keys=True).encode()).hexdigest()

def registration_status(fetch_remote=True):
    out = dict(ok=False, main_commit=None, landed_ny=None, mismatches=None, error=None)
    try:
        if fetch_remote: subprocess.run(["git", "-C", str(HERMES), "fetch", "-q", "origin", "main"], timeout=30, capture_output=True)
        out["main_commit"] = subprocess.run(["git", "-C", str(HERMES), "rev-parse", "origin/main"], capture_output=True, text=True, timeout=10).stdout.strip()
        js = json.loads(subprocess.run(["git", "-C", str(HERMES), "show", f"origin/main:{PREREG_PATH}"], capture_output=True, text=True, timeout=10, check=True).stdout)
        reg = js.get("harness_sha256"); mine = harness_hashes()
        if not isinstance(reg, dict) or "files" not in reg: out["mismatches"] = "harness_sha256 not registered on main (PENDING)"; return out
        mm = {f: (reg["files"].get(f), h) for f, h in mine.items() if reg["files"].get(f) != h}
        if mm: out["mismatches"] = json.dumps(mm); return out
        log = subprocess.run(["git", "-C", str(HERMES), "log", "--first-parent", "-m", "-S", mine["h014_forward.py"], "--format=%H|%cI", "origin/main", "--", PREREG_PATH],
                             capture_output=True, text=True, timeout=20).stdout.strip().splitlines()
        if log: out["landed_ny"] = str(pd.Timestamp(log[-1].split("|")[1]).tz_convert(TZ))
        out["ok"] = out["landed_ny"] is not None
    except Exception as e: out["error"] = str(e)[:200]
    return out

# ------------------------------------------------------------------ engine on one session
def day_trades(run_backtest, m1, cfg, nm, d):
    tr, od, _ = run_backtest(m1, cfg, ROOT[nm], nm)
    dd = pd.Timestamp(d).date()
    tr = tr[pd.to_datetime(tr["entry_time_ny"]).map(lambda x: x.date()) == dd] if len(tr) else tr
    od = od[pd.to_datetime(od["order_time_ny"]).map(lambda x: x.date()) == dd] if len(od) else od
    return tr.reset_index(drop=True), od.reset_index(drop=True)

def evaluate(m1, d, nm, eng, baseline_dir=None, dry=True):
    cfg, D, run_backtest, outcome_table = eng
    tr, od = day_trades(run_backtest, m1, cfg, nm, d)
    pc = copy.deepcopy(cfg); sp = SPREAD_PROXY[nm]
    pc.fill_through_ticks, pc.stop_slippage_ticks, pc.cost_points_round_trip = sp["fill_through_ticks"], sp["stop_slippage_ticks"], {ROOT[nm]: sp["cost"]}
    trp, _ = day_trades(run_backtest, m1, pc, nm, d)
    cost = float(cfg.cost_points_round_trip[ROOT[nm]])
    rows = []
    tabs = outcome_table(m1, tr, cfg, ROOT[nm]) if len(tr) else []
    for i, t in tr.iterrows():
        risk = float(t["risk_pts"])
        px = trp[(trp["direction"] == t["direction"]) & (pd.to_datetime(trp["order_time_ny"]) == pd.to_datetime(t["order_time_ny"]))]
        r = dict(status="trade", trade_no=i + 1, direction=t["direction"], order_time_ny=str(t["order_time_ny"]), entry_time_ny=str(t["entry_time_ny"]),
                 exit_time_ny=str(t["exit_time_ny"]), entry=t["entry"], stop=t["stop"], risk_pts=risk, tp1=t["tp1"], tp1_source=t["tp1_source"],
                 draw=t["draw"], draw_kind=t["draw_kind"], exit_reason=t["exit_reason"], R_frozen=float(t["r_multiple"]),
                 R_spread_proxy=float(px["r_multiple"].iloc[0]) if len(px) else None,
                 spread_proxy_status="filled" if len(px) else "not filled under spread proxy",
                 R_measured_cost=float(t["r_multiple"]) - (MEASURED_COST_RT[nm] - cost) / risk, R_2x_cost=float(t["r_multiple"]) - cost / risk,
                 baseline_mean_R=float(np.mean(tabs[i])), baseline_n=int(len(tabs[i])))
        if baseline_dir is not None:
            body = json.dumps(dict(date=d, instrument=nm, trade_no=i + 1, outcomes_R=[round(float(x), 6) for x in tabs[i]])).encode()
            r["baseline_file"] = f"baseline/{nm}_{d}_t{i + 1}.json sha256={hashlib.sha256(body).hexdigest()}"
            if not dry:
                (baseline_dir).mkdir(parents=True, exist_ok=True); p = baseline_dir / f"{nm}_{d}_t{i + 1}.json"
                if not p.exists(): p.write_bytes(body)
        rows.append(r)
    extra = len(trp[~trp["order_time_ny"].isin(tr["order_time_ny"])]) if len(trp) and len(tr) else len(trp)
    if not rows: rows = [dict(status="no trade", trade_no=0, R_spread_proxy=None,
                              spread_proxy_status=f"{extra} spread-proxy-only trade(s)" if extra else None)]
    orders = "; ".join(f"{o.direction} {o.status} @{o.entry:.2f} {pd.Timestamp(o.order_time_ny):%H:%M}" for o in od.itertuples()) if len(od) else ""
    for r in rows: r["orders_today"] = orders
    return rows

# ------------------------------------------------------------------ append-only log
def read_log(): return pd.read_csv(LOG, dtype=str) if LOG.exists() else pd.DataFrame(columns=COLUMNS)

def append_rows(rows):
    new = not LOG.exists()
    if not new:
        with open(LOG) as f: hdr = next(csv.reader(f))
        if hdr != COLUMNS: raise SystemExit("H014 ABORT: log header differs from harness schema (append-only log must not be rewritten)")
    with open(LOG, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, extrasaction="raise")
        if new: w.writeheader()
        for r in rows: w.writerow({k: r.get(k) for k in COLUMNS})

def counted_so_far(prior):
    if not len(prior): return prior
    c = prior[prior["counted"].astype(str) == "True"]
    return c

def run_session(d, run_kind, fetched, metas, reg, note="", dry=False):
    eng = load_engine(); cfg, D, _, _ = eng
    run_id = f"{now_sast():%Y%m%dT%H%M%S}-{uuid.uuid4().hex[:6]}"; logged = now_sast().strftime("%Y-%m-%d %H:%M:%S")
    prior = read_log(); cprior = counted_so_far(prior)
    cum = {s: float(pd.to_numeric(cprior[cprior.instrument == s]["R_frozen"], errors="coerce").fillna(0).sum()) if len(cprior) else 0.0 for s in SYMS}
    killed_before = bool(len(prior) and (prior["kill_triggered"].astype(str) == "True").any())
    out = []
    for nm in SYMS:
        base = dict(run_id=run_id, run_kind=run_kind, backfilled=run_kind == "BACKFILL", logged_at_sast=logged, date=d, instrument=nm, stream=STREAM[nm],
                    engine_sha256_ok=True, harness_sha256_digest=harness_digest(), harness_registered_on_main=reg.get("ok"),
                    prereg_main_commit=reg.get("main_commit"), registration_landed_ny=reg.get("landed_ny"), session_start_ny=str(session_start(d)),
                    calendar_status=calendar_status(d), note=note, **{k: v for k, v in metas.get(nm, {}).items() if k in COLUMNS})
        if nm not in fetched:
            out.append({**base, "status": "feed gap (no data)", "counted": False, "not_counted_reasons": "feed_error: " + metas.get(nm, {}).get("error", "?")}); continue
        cap = capitalcom_history(nm, fetched[nm]); m1, src = build_input(nm, d, cap, D)
        base["raw_file"], base["raw_sha256"] = save_raw(m1, src, f"{nm}_{d}", dry=dry); base["raw_rows"] = len(m1)
        sess = src[(src.index >= session_start(d)) & (src.index <= at(d, "16:59"))]
        base["warmup_dukascopy_bars"] = int((src == "DUKASCOPY_BID_WARMUP").sum()); base["session_bars_all_capitalcom"] = bool(len(sess) and (sess == "CAPITALCOM").all())
        nr, no, miss = bar_counts(m1, d); base.update(bars_0930_1059=nr, bars_overnight=no, missing_0930_1059=" ".join(miss), min_bar_ok=nr >= MIN_RTH and no >= MIN_ON)
        reasons = []
        if base["calendar_status"] != "ok": reasons.append(base["calendar_status"])
        if nr < MIN_RTH: reasons.append(f"min_bars 09:30-10:59 {nr}<{MIN_RTH}")
        if no < MIN_ON: reasons.append(f"min_bars overnight {no}<{MIN_ON}")
        if not base["session_bars_all_capitalcom"]: reasons.append("session bars not 100% CAPITALCOM")
        if base["calendar_status"] in ("weekend", "holiday_full_closure") or nr == 0:
            out.append({**base, "status": "excluded (no session)", "counted": False, "not_counted_reasons": "; ".join(reasons)}); continue
        rows = evaluate(m1, d, nm, eng, baseline_dir=HERE / "baseline", dry=dry)
        if d < FIRST_POSSIBLE_SESSION: reasons.append("before first eligible session (pre-registration / burned)")
        if run_kind not in ("FINAL", "BACKFILL"): reasons.append(f"run_kind {run_kind}")
        if not reg.get("ok"): reasons.append("harness hash not registered on origin/main: " + str(reg.get("mismatches") or reg.get("error")))
        elif pd.Timestamp(reg["landed_ny"]) >= session_start(d): reasons.append("harness registered on main after session start (18:00 NY prior day)")
        if killed_before: reasons.append("H014 already killed (cumulative <= -5R)")
        dup = prior[(prior.date == d) & (prior.instrument == nm) & prior.run_kind.isin(["FINAL", "BACKFILL"])] if len(prior) else prior
        if len(dup): reasons.append("duplicate run (first FINAL/BACKFILL row for this session stands)")
        for r in rows:
            row = {**base, **r, "duplicate_of_run": dup.run_id.iloc[0] if len(dup) else None}
            rr = list(reasons) + (["DRY-RUN (not logged)"] if dry else [])
            row["counted"] = not rr; row["not_counted_reasons"] = "; ".join(rr)
            if row["counted"] and r["status"] == "trade": cum[nm] += r["R_frozen"]
            out.append(row)
    pooled = cum["US100"] + cum["US500"]; kill = pooled <= KILL_R and not killed_before
    for r in out:
        r.update(cum_R_pooled_counted=round(pooled, 6), cum_R_US100_counted=round(cum["US100"], 6), cum_R_US500_counted=round(cum["US500"], 6), kill_triggered=kill)
    if not dry: append_rows(out)
    if kill: print(f"*** H014 KILL: pooled counted cumulative R = {pooled:.3f} <= {KILL_R} -> FAILS (final), stop counting ***")
    return out

def main(argv):
    args = [a for a in argv if not a.startswith("--") and "=" not in a]
    today = pd.Timestamp.now(tz=TZ).strftime("%Y-%m-%d"); d = today if not args or args[0] == "today" else args[0]
    dry = "--dry" in argv; raw = dict(a.split("=", 1) for a in argv if "=" in a)
    run_kind = "BACKFILL" if "--backfill" in argv else ("FINAL" if d == today else "LATE_FINAL")
    if raw: run_kind, dry = "REPLAY", True
    if run_kind == "LATE_FINAL": raise SystemExit("h014: past session -> use --backfill (rows note=BACKFILLED)")
    if run_kind == "FINAL" and not dry and pd.Timestamp.now(tz=TZ) < at(d, "11:01"): raise SystemExit("h014: run after 11:00 NY (flat time); use --dry for a preview")
    fetched, metas = {}, {}
    for nm in SYMS:
        try:
            if nm in raw:
                fetched[nm] = read_csv_bars(raw[nm]); metas[nm] = dict(feed=f"TradingView {FEED[nm]} (replay of saved raw {raw[nm]})")
            else: fetched[nm], metas[nm] = fetch(nm)
            fetched[nm] = fetched[nm][fetched[nm].index <= at(d, "16:59")]
        except FeedError as e: metas[nm] = dict(feed=f"TradingView {FEED[nm]}", error=str(e), fetch_time_sast=now_sast().strftime("%Y-%m-%d %H:%M:%S"))
    reg = registration_status(fetch_remote=not dry)
    note = f"BACKFILLED {now_sast():%Y-%m-%d %H:%M} SAST" if run_kind == "BACKFILL" else ""
    rows = run_session(d, run_kind, fetched, metas, reg, note=note, dry=dry)
    show = ["date", "instrument", "run_kind", "status", "direction", "entry_time_ny", "entry", "stop", "R_frozen", "R_spread_proxy", "R_measured_cost",
            "baseline_mean_R", "exit_reason", "bars_0930_1059", "bars_overnight", "warmup_dukascopy_bars", "raw_sha256", "counted",
            "not_counted_reasons", "cum_R_pooled_counted", "kill_triggered"]
    print(pd.DataFrame(rows).reindex(columns=show).T.to_string())
    return rows

if __name__ == "__main__": main(sys.argv[1:])
