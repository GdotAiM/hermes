"""H015b forward harness: FTN Month 9 REV (raid-side direction + FTN-D22 stop beyond the raid), US100 + US500 CFD, frozen
forward-only test. HYPOTHETICAL paper research: no orders, no broker calls, nothing reaches MINT.

Implements research/protocols/preregs/H015b_FORWARD_PREREG_2026-10-04.json (tag prereg-H015b) and its data-handling appendix
research/protocols/preregs/H015b_DATA_APPENDIX_2026-10-04.md (DATA_REVIEW_H015_PREREG_2026-10-04 C1-C13):
  * feed = Dukascopy datafeed BID 1m day files only (duka.py), context included; ASK stored for co-reports only; no fallback,
    no HistData / reused parquet / marketdata loader, no filled or synthesised bars
  * the pinned ftn files are verified IN PLACE, by content, against `git show prereg-H015b:<path>` and the prereg sha256 pins;
    any mismatch refuses to run (harness_hash_mismatch). ftn is imported from <repo>/ftn/src only
  * per session: History(series, trading_days(series)) over CONTEXT_DAYS calendar days of stored day files ->
    kernel_log.session_ticket_log(hist, cfg[interpretation_triggers all false], days=[d]) -> kernel_log.tradeable ->
    outcomes.simulate(..., COST_PER_SIDE[inst]) exactly as the exploratory scorer
  * session-cluster bootstrap (binding v[500]), futility once at trade 200, kill at -45R, foil with N per replicate
  * R is SEALED (sealed/outcomes.csv, never printed) until DATA_CERTIFIED.json and CASSANDRA_CLEARED.json carrying this
    harness's sha256 exist in the data dir; no verdict wording below N=100
Data/logs: $HERMES_FWD_DATA/H015b (default /home/box/hermes-x/forward/H015b), outside git.

CLI (from the repo root; scheduled run = `final` at or after 01:00 UTC (03:00 SAST) every day, scoring the previous NY day):
  python research/forward/H015/h015.py final        score every pending session date d with now >= d+1 01:00 UTC
  python research/forward/H015/h015.py report       status counts; R/stats only after both clearance files exist
  python research/forward/H015/h015.py verify       recompute every FINAL row from stored files; must match exactly
  python research/forward/H015/h015.py selfcheck    pins, tag, harness manifest/digest, registration
  python research/forward/H015/h015.py repro-burned full per-session reproduction of the FTN-D22 burned trades (C11)
  python research/forward/H015/h015.py c5 [N]       re-pull N (default 5) burned-window days, compare with marketdata's native
                                                    Dukascopy parquet bit-for-bit (C5; network)"""
from __future__ import annotations

import csv, datetime as dt, hashlib, io, json, os, pathlib, random, subprocess, sys, tempfile, uuid
from copy import deepcopy
from statistics import mean, median

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
sys.path.insert(0, str(HERE))
import duka  # noqa: E402

LEAD = "H015b"
PREREG_REL = "research/protocols/preregs/H015b_FORWARD_PREREG_2026-10-04.json"
APPENDIX_REL = "research/protocols/preregs/H015b_DATA_APPENDIX_2026-10-04.md"
REG_NOTE_REL = "research/protocols/preregs/H015b_HARNESS_REGISTRATION_2026-10-04.json"
TAG = "prereg-H015b"
TAG_COMMIT = "49be2d6c47878ea48da15fadd969a0af3ef94e5a"
REG_REFS = ("origin/main", "origin/feat/ftn-research-bridge", "origin/forward/h015-harness")
HARNESS_FILES = [HERE / "__init__.py", HERE / "duka.py", HERE / "h015.py", REPO / APPENDIX_REL]
DATA_ROOT = pathlib.Path(os.environ.get("HERMES_FWD_DATA", "/home/box/hermes-x/forward")) / LEAD
INSTS = ("US100", "US500")
SESSIONS = ("london", "ny_am")
FIRST_DATE = dt.date(2026, 10, 5)
CONTEXT_DAYS = 45              # calendar days of stored BID day files before d (>= 22 prior sessions + margin)
CONTEXT_SESSIONS = 22
KZ_MIN, KZ_N = 171, 180
RTH_MIN = 300
LAST_BAR = dt.time(16, 14)     # session complete only when bars run to the 16:14 NY halt
RETRY_TRADING_DAYS = 5
SUSPEND_AFTER = 10             # consecutive feed_gap trading days -> feed_suspended
KILL_R = -45.0
N_DECISION = 824
FUTILITY_AT = 200
FUTILITY_BAR = 0.10
NO_VERDICT_BELOW = 100
SEED = 20261004
N_BOOT = 10_000
LB_INDEX = int(0.05 * N_BOOT)          # 500: binding one-sided 95% lower bound (5th percentile)
UB975_INDEX = int(0.975 * N_BOOT) - 1  # 9749: futility upper one-sided 97.5% bound
N_FOIL = 2000
COST_PER_SIDE = {"US100": 0.8, "US500": 0.5}       # binding (prereg costs)
DATA_COST_RT = {"US100": 1.617, "US500": 1.01}     # co-report only
SPREAD_FLAG = {"US100": 1.1, "US500": 0.5}         # appendix A9: monthly killzone median spread flag
STOP_SLIP = (0.0, 0.25, 1.0)
HOLIDAYS_2028 = {"full_closures": ["2028-01-17", "2028-02-21", "2028-04-14", "2028-05-29", "2028-06-19", "2028-07-04",
                                   "2028-09-04", "2028-11-23", "2028-12-25"],
                 "early_closes": ["2028-07-03", "2028-11-24"]}           # appendix A10 (DATA F8)
FEED_DISCLOSURE = ("Feed: Dukascopy CFD BID 1m (datafeed day files), NOT TradingView CAPITALCOM as in H013/H014. "
                   "Binding fills are BID on every leg + fixed cost; ASK is a co-report only.")
LOG_COLS = ["run_id", "computed_at_utc", "computed_at_sast", "date", "instrument", "session", "status", "counted",
            "not_counted_reasons", "ticket", "module", "side", "entry_time", "entry", "stop", "stop_source", "risk_pts",
            "gates", "reason", "kz_bars", "rth_bars", "last_bar_ny", "context_sessions", "session_raw_sha256",
            "context_manifest_sha256", "manifest_file", "filler_dropped_session", "pins_ok", "harness_sha256",
            "registration_commit", "registration_time_utc", "harness_matches_registered", "dst_mismatch_week", "error"]
OUT_COLS = ["date", "instrument", "session", "R", "R_gross", "exit", "risk_pts", "cost_R", "exit_time_rule_ok",
            "session_raw_sha256", "context_manifest_sha256"]
TERMINAL = {"trade", "no_trade", "feed_gap", "holiday", "short_session", "context_gap", "feed_suspended",
            "calendar_not_covered", "not_trading_day"}


# ------------------------------------------------------------------ small utils
def sha256_file(p) -> str:
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def now_utc() -> dt.datetime:
    return dt.datetime.now(duka.UTC)


def _git(*a) -> str:
    return subprocess.run(["git", "-C", str(REPO), *a], check=True, capture_output=True, text=True).stdout


def _git_bytes(*a) -> bytes:
    return subprocess.run(["git", "-C", str(REPO), *a], check=True, capture_output=True).stdout


def prereg() -> dict:
    return json.loads((REPO / PREREG_REL).read_text())


def pins() -> dict:
    c = prereg()["code"]
    return {**c["kernel_and_dtr_sha256"], **c["scoring_sha256"]}


# ------------------------------------------------------------------ pins / manifest / registration
def verify_pins() -> dict:
    """{} if OK. Checks: the tag resolves to TAG_COMMIT; the prereg and every pinned file are byte-identical to the tag and
    hash to the prereg pins, in place in this checkout."""
    bad = {}
    try:
        tc = _git("rev-parse", f"{TAG}^{{commit}}").strip()
    except Exception as e:
        return {"tag": f"missing: {str(e)[:80]}"}
    if tc != TAG_COMMIT:
        bad["tag"] = tc
    for rel in [PREREG_REL, *pins()]:
        p = REPO / rel
        got = p.read_bytes() if p.exists() else None
        try:
            want = _git_bytes("show", f"{TAG}:{rel}")
        except Exception:
            want = b"<not in tag>"
        if got != want:
            bad[rel] = "differs_from_tag" if got is not None else "MISSING"
        elif rel != PREREG_REL and hashlib.sha256(got).hexdigest() != pins()[rel]:
            bad[rel] = "sha256_differs_from_prereg_pin"
    return bad


def harness_manifest() -> dict:
    return {"repo_root": "GdotAiM/hermes",
            "files": {str(pathlib.Path(f).resolve().relative_to(REPO)): sha256_file(f) for f in HARNESS_FILES}}


def harness_digest(m=None) -> str:
    return hashlib.sha256(json.dumps(m or harness_manifest(), sort_keys=True).encode()).hexdigest()


def registration_status(fetch: bool = False) -> dict:
    """The earliest commit on any REG_REFS that carries the registration note with a harness_sha256.files manifest.
    Counting needs the current manifest to equal that FIRST registered manifest."""
    out = dict(registered=False, registration_commit=None, registration_time_utc=None, harness_matches_registered=False,
               error=None)
    try:
        if fetch:
            subprocess.run(["git", "-C", str(REPO), "fetch", "-q", "origin"], check=False, capture_output=True, timeout=90)
        best = None
        for ref in REG_REFS:
            try:
                lines = _git("log", "--format=%H %cI", ref, "--", REG_NOTE_REL).splitlines()
            except Exception:
                continue
            for line in reversed(lines):
                sha, when = line.split()
                try:
                    hs = json.loads(_git("show", f"{sha}:{REG_NOTE_REL}")).get("harness_sha256")
                except Exception:
                    continue
                if isinstance(hs, dict) and hs.get("repo_root") == "GdotAiM/hermes" and hs.get("files"):
                    t = dt.datetime.fromisoformat(when).astimezone(duka.UTC)
                    if best is None or t < best[1]:
                        best = (sha, t, hs)
                    break
        if best:
            out.update(registered=True, registration_commit=best[0], registration_time_utc=best[1].isoformat(),
                       harness_matches_registered=(best[2]["files"] == harness_manifest()["files"]))
    except Exception as e:
        out["error"] = str(e)[:200]
    return out


_FTN = None


def ftn():
    """Import ftn from <repo>/ftn/src after the pin check (never any other copy)."""
    global _FTN
    if _FTN is None:
        bad = verify_pins()
        if bad:
            raise RuntimeError(f"harness_hash_mismatch: {bad}")
        src = REPO / "ftn" / "src"
        sys.path.insert(0, str(src))
        import ftn as _f
        if pathlib.Path(_f.__file__).resolve().parent != (src / "ftn").resolve():
            raise RuntimeError(f"imported ftn from {_f.__file__}, not {src}")
        from ftn.config_load import load_config
        from ftn.research import bars, daycontext, kernel_log, outcomes, stats, score
        cfg = deepcopy(load_config())
        cfg["interpretation_triggers"] = {"conso": False, "bb": False, "pip20": False}
        _FTN = dict(cfg=cfg, bars=bars, dc=daycontext, kl=kernel_log, out=outcomes, stats=stats, score=score)
    return _FTN


# ------------------------------------------------------------------ calendar
def holidays() -> dict:
    h = deepcopy(prereg()["counting_rules"]["holidays_excluded"])
    h["full_closures"] = sorted(set(h["full_closures"]) | set(HOLIDAYS_2028["full_closures"]))
    h["early_closes"] = sorted(set(h["early_closes"]) | set(HOLIDAYS_2028["early_closes"]))
    return h


def calendar_status(d: dt.date) -> str:
    h = holidays(); s = d.isoformat()
    if d.weekday() >= 5:
        return "weekend"
    if s in h["full_closures"] or s in h["early_closes"] or s in h.get("historical_additions", []):
        return "holiday"
    if s > max(h["full_closures"] + h["early_closes"])[:4] + "-12-31":
        return "calendar_not_covered"
    return "ok"


def expected_trading_days(a: dt.date, b: dt.date) -> list[dt.date]:
    """Weekdays in [a, b] that are not on the holiday / early-close list."""
    out, d = [], a
    while d <= b:
        if calendar_status(d) in ("ok", "calendar_not_covered"):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def dst_mismatch_week(d: dt.date) -> bool:
    """US and EU clocks out of step (London killzone 06:00-09:00 London instead of 07:00-10:00)."""
    lon = dt.datetime(d.year, d.month, d.day, 12, tzinfo=duka.UTC).astimezone(__import__("zoneinfo").ZoneInfo("Europe/London"))
    ny = dt.datetime(d.year, d.month, d.day, 12, tzinfo=duka.UTC).astimezone(duka.NY)
    return (lon.utcoffset() - ny.utcoffset()) != dt.timedelta(hours=5)


# ------------------------------------------------------------------ series assembly
def utc_days_for(d: dt.date) -> list[dt.date]:
    return [d - dt.timedelta(days=k) for k in range(CONTEXT_DAYS, -1, -1)]


def series_from_csv_texts(texts: list[str], inst: str, end_ny: dt.datetime, start_ny: dt.datetime | None = None):
    """ftn Series from normalised day CSVs, keeping start_ny <= NY wall clock < end_ny (session end 17:00 NY of d)."""
    B = ftn()["bars"]
    lines = ["Datetime,Open,High,Low,Close"]
    e = end_ny.strftime("%Y-%m-%d %H:%M:%S"); s0 = start_ny.strftime("%Y-%m-%d %H:%M:%S") if start_ny else ""
    for t in texts:
        for ln in t.splitlines()[1:]:
            if ln and s0 <= ln[:19] < e:
                lines.append(ln.rsplit(",", 1)[0])
    with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as f:
        f.write("\n".join(lines) + "\n")
    try:
        return B.load_series(f.name, inst)
    finally:
        os.unlink(f.name)


def ny(d: dt.date, hh: int, mm: int = 0) -> dt.datetime:
    return dt.datetime(d.year, d.month, d.day, hh, mm)


# ------------------------------------------------------------------ per-session scoring (pure: from a Series)
def score_sessions(series, d: dt.date) -> list[dict]:
    """The exploratory scorer's path for one day: History(series, trading_days) -> session_ticket_log(days=[d]) ->
    tradeable -> simulate. Returns one dict per killzone (ticket fields + outcome or None). No filters applied here."""
    F = ftn()
    hist = F["dc"].History(series, F["bars"].trading_days(series))
    if d not in hist.pos:
        return [dict(date=d.isoformat(), session=s, ticket=False, reason="not_in_trading_days", outcome=None) for s in SESSIONS]
    rows = F["kl"].session_ticket_log(hist, F["cfg"], days=[d])
    out = []
    for r in rows:
        r = dict(r); r["outcome"] = None
        if F["kl"].tradeable(r):
            o = F["out"].simulate(series, dt.datetime.fromisoformat(r["entry_time"]), float(r["entry"]), float(r["stop"]),
                                  r["side"], COST_PER_SIDE[series.symbol])
            if o["R"] is not None:
                r["outcome"] = o
        out.append(r)
    return out


def exit_bars_ok(series, entry_time: dt.datetime) -> bool:
    """Appendix A4 'bars to 16:00 exist': >= 1 bar in [15:45, 16:00) and no gap > 5 min between entry and 16:00."""
    d = entry_time.date(); end = ny(d, 16)
    idx = list(series.window(entry_time, end))
    if not idx or not any(series.t[i] >= ny(d, 15, 45) for i in idx):
        return False
    ts = [entry_time] + [series.t[i] for i in idx]
    return all((b - a) <= dt.timedelta(minutes=5) for a, b in zip(ts, ts[1:]))


# ------------------------------------------------------------------ forward session rows
class Ledger:
    def __init__(self, root: pathlib.Path = None):
        self.root = pathlib.Path(root or DATA_ROOT)
        self.log = self.root / "log.csv"
        self.sealed = self.root / "sealed" / "outcomes.csv"

    def _append(self, p, row, cols):
        p.parent.mkdir(parents=True, exist_ok=True)
        new = not p.exists()
        with open(p, "a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            if new:
                w.writeheader()
            w.writerow({k: row.get(k) for k in cols})

    def add(self, row: dict, outcome: dict | None):
        self._append(self.log, row, LOG_COLS)
        if outcome is not None:
            self._append(self.sealed, {**row, **outcome}, OUT_COLS)

    def rows(self) -> list[dict]:
        return list(csv.DictReader(open(self.log))) if self.log.exists() else []

    def outcomes(self) -> list[dict]:
        return list(csv.DictReader(open(self.sealed))) if self.sealed.exists() else []

    def latest(self) -> dict:
        """(date, instrument, session) -> latest row (latest run is authoritative; FINAL rows are never recomputed)."""
        out = {}
        for r in self.rows():
            out[(r["date"], r["instrument"], r["session"])] = r
        return out


def gather(store: duka.Store, inst: str, d: dt.date) -> dict:
    """Ensure all BID day files for d's context + session and the ASK files for d-1, d. Returns metas or a status."""
    metas, problems = [], []
    for day in utc_days_for(d):
        try:
            metas.append(store.ensure(inst, "BID", day))
        except duka.FeedError as e:
            problems.append(("feed_error", day, str(e)[:160]))
        except duka.SchemaError as e:
            return dict(status="feed_suspended", error=f"{day}: {e}")
    for day in (d - dt.timedelta(days=1), d):
        try:
            store.ensure(inst, "ASK", day)
        except (duka.FeedError, duka.SchemaError) as e:      # ASK is co-report only; never blocks a row
            problems.append(("ask_error", day, str(e)[:160]))
    nf = [m["day"] for m in metas if not m.get("final")]
    return dict(status="ok", metas=metas, problems=problems, not_final=nf)


def manifest_for(metas: list[dict]) -> tuple[str, str, list]:
    lst = [[m["day"], m["side"], m["bi5_sha256"], m["csv_sha256"]] for m in metas]
    sess = lst[-2:]                                   # UTC days d-1 and d: the session's own BID files
    ctx = hashlib.sha256(json.dumps(lst).encode()).hexdigest()
    sraw = hashlib.sha256(json.dumps(sess).encode()).hexdigest()
    return sraw, ctx, lst


def trading_days_after(d: dt.date, today: dt.date) -> int:
    return len([x for x in expected_trading_days(d + dt.timedelta(days=1), today)])


def session_rows_for(store: duka.Store, inst: str, d: dt.date, reg: dict, pins_ok: bool, run_id: str,
                     at: dt.datetime) -> list[tuple[dict, dict | None]]:
    """Rows (one per killzone) for instrument inst on NY date d, or [] if d is not final yet and may be retried."""
    base = dict(run_id=run_id, computed_at_utc=at.isoformat(timespec="seconds"),
                computed_at_sast=at.astimezone(__import__("zoneinfo").ZoneInfo("Africa/Johannesburg")).strftime("%Y-%m-%d %H:%M:%S"),
                date=d.isoformat(), instrument=inst, pins_ok=pins_ok, harness_sha256=harness_digest(),
                registration_commit=reg.get("registration_commit"), registration_time_utc=reg.get("registration_time_utc"),
                harness_matches_registered=reg.get("harness_matches_registered"), dst_mismatch_week=dst_mismatch_week(d))
    mk = lambda status, extra=None: [({**base, "session": s, "status": status, "counted": False,
                                       "not_counted_reasons": status, **(extra or {})}, None) for s in SESSIONS]
    cal = calendar_status(d)
    if cal == "weekend":
        return []
    if cal != "ok":
        return mk(cal)
    g = gather(store, inst, d)
    if g["status"] == "feed_suspended":
        return mk("feed_suspended", dict(error=g["error"]))
    age = trading_days_after(d, at.date() - dt.timedelta(days=1))   # trading days since d already past
    sraw, cman, lst = manifest_for(g["metas"])
    # session completeness (appendix A1): files FINAL and bars to the 16:14 NY halt
    texts = [store.csv_text(inst, "BID", dt.date.fromisoformat(m["day"])) for m in g["metas"]]
    series = series_from_csv_texts(texts, inst, ny(d, 17))
    sess_idx = series.window(ny(d - dt.timedelta(days=1), 18), ny(d, 17))
    last = series.t[sess_idx[-1]] if len(sess_idx) else None
    complete = (not g["not_final"]) and not [p for p in g["problems"] if p[0] == "feed_error"] and last is not None \
        and last.time() >= LAST_BAR
    if not complete:
        if age > RETRY_TRADING_DAYS:
            return mk("feed_gap", dict(error=f"incomplete after {RETRY_TRADING_DAYS} trading days; last bar {last}; "
                                             f"not_final={g['not_final'][:3]} problems={g['problems'][:2]}",
                                       session_raw_sha256=sraw, context_manifest_sha256=cman))
        return mk("provisional", dict(error=f"last bar {last}; not_final={g['not_final'][:3]}; problems={g['problems'][:2]}"))
    mf = DATA_ROOT_rel(store, inst, d, lst)
    F = ftn()
    tdays = F["bars"].trading_days(series)
    rth = len(series.window(ny(d, 9, 30), ny(d, 16)))
    dropped = sum(json.loads((store.paths(inst, "BID", dt.date.fromisoformat(x))[2]).read_text())["filler_dropped"]
                  for x in (lst[-2][0], lst[-1][0]))
    base.update(session_raw_sha256=sraw, context_manifest_sha256=cman, manifest_file=mf, rth_bars=rth,
                last_bar_ny=str(last), filler_dropped_session=dropped)
    # context completeness (appendix A4): the CONTEXT_SESSIONS expected trading days before d all present
    exp = [x for x in expected_trading_days(d - dt.timedelta(days=CONTEXT_DAYS), d - dt.timedelta(days=1))][-CONTEXT_SESSIONS:]
    miss = [x.isoformat() for x in exp if x not in set(tdays)]
    base["context_sessions"] = len([x for x in tdays if x < d])
    if miss or len(exp) < CONTEXT_SESSIONS:
        return mk("context_gap", dict(error=f"missing context sessions {miss}"))
    if d not in tdays:
        return mk("not_trading_day", dict(error=f"{rth} RTH bars < {RTH_MIN}"))
    res = []
    for r in score_sessions(series, d):
        s = r["session"]; a, b = {"london": (2, 5), "ny_am": (7, 10)}[s]
        kz = len(series.window(ny(d, a), ny(d, b)))
        row = {**base, "session": s, "kz_bars": kz, "ticket": r.get("ticket"), "module": r.get("module"),
               "side": r.get("side"), "entry_time": r.get("entry_time"), "entry": r.get("entry"), "stop": r.get("stop"),
               "stop_source": ("raid_extreme" if r.get("raid_bar_index") is not None else "level_buffer_fallback")
               if r.get("ticket") else None, "gates": "|".join(r.get("gates") or []), "reason": r.get("reason")}
        reasons = []
        status = "trade" if r["outcome"] is not None else "no_trade"
        if kz < KZ_MIN:
            status = "short_session"; reasons.append(f"kz_bars {kz}/{KZ_N}")
        o = r["outcome"]
        if o is not None and status == "trade":
            ok = exit_bars_ok(series, dt.datetime.fromisoformat(r["entry_time"]))
            if not ok:
                status = "short_session"; reasons.append("exit_bars_missing_or_gap>5min")
            row["risk_pts"] = o["risk_pts"]
            o = dict(date=d.isoformat(), instrument=inst, session=s, R=repr(o["R"]), R_gross=repr(o["R_gross"]),
                     exit=o["exit"], risk_pts=repr(o["risk_pts"]), cost_R=repr(o["cost_R"]), exit_time_rule_ok=ok,
                     session_raw_sha256=sraw, context_manifest_sha256=cman)
        if status == "trade":
            if d < FIRST_DATE: reasons.append("before_first_eligible_session")
            if not pins_ok: reasons.append("harness_hash_mismatch")
            if not reg.get("registered"): reasons.append("harness_not_registered")
            elif not reg.get("harness_matches_registered"): reasons.append("harness_hash_mismatch")
            elif dt.datetime.fromisoformat(reg["registration_time_utc"]) >= at: reasons.append("computed_before_registration")
            tag_t = dt.datetime.fromisoformat(_git("show", "-s", "--format=%cI", TAG_COMMIT).strip())
            if dt.datetime(d.year, d.month, d.day, a, tzinfo=duka.NY) <= tag_t: reasons.append("session_started_before_prereg")
        row.update(status=status, counted=(status == "trade" and not reasons), not_counted_reasons=";".join(reasons) or None)
        res.append((row, o if status in ("trade", "short_session") and r["outcome"] is not None else None))
    return res


def DATA_ROOT_rel(store: duka.Store, inst, d, lst) -> str:
    p = store.root / "manifests" / inst / f"{d.isoformat()}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    b = (json.dumps(lst, indent=0) + "\n").encode()
    if p.exists() and p.read_bytes() != b:
        p = p.with_name(f"{d.isoformat()}__{hashlib.sha256(b).hexdigest()[:12]}.json")
    if not p.exists():
        p.write_bytes(b)
    return str(p.relative_to(store.root))


# ------------------------------------------------------------------ commands
def pending_dates(led: Ledger, at: dt.datetime) -> list[dt.date]:
    """Dates d >= FIRST_DATE with at >= d+1 01:00 UTC and no terminal row for every (instrument, session)."""
    lat = led.latest(); out = []
    d = FIRST_DATE
    while dt.datetime(d.year, d.month, d.day, tzinfo=duka.UTC) + duka.FINAL_AFTER <= at:
        if d.weekday() < 5 and not all(lat.get((d.isoformat(), i, s), {}).get("status") in TERMINAL for i in INSTS for s in SESSIONS):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def cmd_final(root=None, at: dt.datetime | None = None, get=None, fetch_remote: bool = True) -> list[dict]:
    at = at or now_utc()
    bad = verify_pins()
    if bad:
        raise SystemExit(f"harness_hash_mismatch, refusing to run: {bad}")
    led = Ledger(root); store = duka.Store(led.root, now=lambda: at, get=get)
    reg = registration_status(fetch=fetch_remote)
    run_id = uuid.uuid4().hex[:12]; out = []
    for d in pending_dates(led, at):
        lat = led.latest()
        for inst in INSTS:
            if all(lat.get((d.isoformat(), inst, s), {}).get("status") in TERMINAL for s in SESSIONS):
                continue
            for row, o in session_rows_for(store, inst, d, reg, True, run_id, at):
                led.add(row, o); out.append(row)
    return out


def cmd_verify(root=None) -> dict:
    """Recompute every terminal trade/no_trade row from its stored manifest; compare ticket + sealed outcome exactly."""
    led = Ledger(root); store = duka.Store(led.root, get=lambda u: (_ for _ in ()).throw(RuntimeError("verify never downloads")))
    outs = {(o["date"], o["instrument"], o["session"]): o for o in led.outcomes()}
    mism, n = [], 0
    for (ds, inst, s), r in led.latest().items():
        if r["status"] not in ("trade", "no_trade", "short_session") or not r.get("manifest_file"):
            continue
        d = dt.date.fromisoformat(ds)
        lst = json.loads((led.root / r["manifest_file"]).read_text())
        for day, side, b5, cs in lst:
            if not store.verify(inst, side, dt.date.fromisoformat(day)) or store.meta(inst, side, dt.date.fromisoformat(day))["csv_sha256"] != cs:
                mism.append((ds, inst, s, f"stored file changed {day}"))
        texts = [store.csv_text(inst, "BID", dt.date.fromisoformat(x[0])) for x in lst]
        rr = {x["session"]: x for x in score_sessions(series_from_csv_texts(texts, inst, ny(d, 17)), d)}[s]
        n += 1
        for k in ("entry_time", "entry", "stop", "side"):
            if str(rr.get(k) if rr.get(k) is not None else "") != (r.get(k) or ""):
                mism.append((ds, inst, s, k))
        o = outs.get((ds, inst, s))
        if (o is None) != (rr["outcome"] is None) or (o and repr(rr["outcome"]["R"]) != o["R"]):
            mism.append((ds, inst, s, "outcome"))
    return dict(rows_checked=n, mismatches=mism, ok=not mism)


# ------------------------------------------------------------------ statistics
def canonical(trades: list[dict]) -> list[dict]:
    return sorted(trades, key=lambda t: (t["date"], SESSIONS.index(t["session"]), INSTS.index(t["instrument"])))


def cluster_boot(trades: list[dict], n: int = N_BOOT, seed: int = SEED) -> list[float]:
    """Session-cluster percentile bootstrap of the pooled mean R. Cluster = (date, killzone); canonical order."""
    keys, S, C = [], {}, {}
    for t in canonical(trades):
        k = (t["date"], t["session"])
        if k not in S:
            keys.append(k); S[k] = 0.0; C[k] = 0
        S[k] += float(t["R"]); C[k] += 1
    s = [S[k] for k in keys]; c = [C[k] for k in keys]; k = len(keys)
    rng = random.Random(seed); vals = []
    for _ in range(n):
        a = b = 0
        for _ in range(k):
            j = rng.randrange(k); a += s[j]; b += c[j]
        vals.append(a / b)
    vals.sort()
    return vals


def binding_bound(trades) -> dict:
    v = cluster_boot(trades)
    return dict(lb_one_sided_95=v[LB_INDEX], p_one_sided=(sum(1 for x in v if x <= 0) + 1) / (len(v) + 1),
                ub_one_sided_975=v[UB975_INDEX], n_clusters=len({(t["date"], t["session"]) for t in trades}))


def futility(trades: list[dict]) -> dict | None:
    """Fires ONCE on exactly the first FUTILITY_AT counted trades (canonical order); None before that."""
    c = canonical(trades)
    if len(c) < FUTILITY_AT:
        return None
    v = cluster_boot(c[:FUTILITY_AT])
    return dict(n=FUTILITY_AT, ub_one_sided_975=v[UB975_INDEX], fails=v[UB975_INDEX] < FUTILITY_BAR)


def kill_walk(trades: list[dict]) -> dict:
    cum, hit = 0.0, None
    for i, t in enumerate(canonical(trades), 1):
        cum += float(t["R"])
        if cum <= KILL_R and hit is None:
            hit = i
    return dict(kill=hit is not None, kill_at_trade=hit, min_cum=None)


def foil_with_n(series, trades: list[dict], cost: float, n: int = N_FOIL, seed: int = SEED) -> list[tuple]:
    """ftn.research.score.foil (same rng sequence) but returning (mean, n_not_none, sum) per replicate."""
    F = ftn(); KZ = F["kl"].KILLZONES
    rng = random.Random(seed); out = []
    for _ in range(n):
        rs = []
        for tr in trades:
            d = dt.date.fromisoformat(tr["date"]); a, b = KZ[tr["session"]]
            mins = rng.randrange(int((dt.datetime.combine(d, b) - dt.datetime.combine(d, a)).total_seconds() // 60))
            et = dt.datetime.combine(d, a) + dt.timedelta(minutes=mins + 1)
            px = series.close_at(et); side = rng.choice(("buy", "sell")); risk = float(tr["risk_pts"])
            stop = px - risk if side == "buy" else px + risk
            r = F["out"].simulate(series, et, px, stop, side, cost)["R"]
            if r is not None:
                rs.append(r)
        out.append((mean(rs) if rs else 0.0, len(rs), sum(rs)))
    return out


def ask_resim(bid, ask, t: dict, slip: float) -> float | None:
    """Correct-side co-report: long buys at ASK, exits on BID; short sells at BID, exits on ASK; stop slip in points."""
    side = "buy" if t["side"] == "buy" else "sell"
    et = dt.datetime.fromisoformat(t["entry_time"]); stop = float(t["stop"]); risk = float(t["risk_pts"])
    entry = ask.close_at(et) if side == "buy" else bid.close_at(et)
    if entry is None:
        return None
    tgt = float(t["entry"]) + 2 * risk if side == "buy" else float(t["entry"]) - 2 * risk
    ex = bid if side == "buy" else ask
    end = ny(et.date(), 16); last = None
    for i in ex.window(et, end):
        hi, lo = ex.h[i], ex.l[i]
        if (lo <= stop) if side == "buy" else (hi >= stop):
            px = stop - slip if side == "buy" else stop + slip
            return ((px - entry) if side == "buy" else (entry - px)) / risk
        if (hi >= tgt) if side == "buy" else (lo <= tgt):
            return ((tgt - entry) if side == "buy" else (entry - tgt)) / risk
        last = ex.c[i]
    if last is None:
        return None
    return ((last - entry) if side == "buy" else (entry - last)) / risk


# ------------------------------------------------------------------ report
def cleared(root: pathlib.Path) -> dict:
    out = {}
    for f in ("DATA_CERTIFIED.json", "CASSANDRA_CLEARED.json"):
        p = root / f
        try:
            out[f] = json.loads(p.read_text()).get("harness_sha256") == harness_digest()
        except Exception:
            out[f] = False
    return out


def full_series(store: duka.Store, inst: str, side: str, days: list[dt.date]):
    want = sorted({x for d in days for x in utc_days_for(d)})
    texts = [store.csv_text(inst, side, x) for x in want if store.meta(inst, side, x)]
    return series_from_csv_texts(texts, inst, ny(max(days), 17))


def cmd_report(root=None, foil_n: int = N_FOIL) -> dict:
    led = Ledger(root); lat = led.latest()
    st = {}
    for r in lat.values():
        st[r["status"]] = st.get(r["status"], 0) + 1
    susp = suspension(lat, led.root)
    counted = [r for r in lat.values() if r["status"] == "trade" and r["counted"] == "True"
               and not (susp["since"] and r["date"] >= susp["since"] and not (susp["resume_from"] and r["date"] >= susp["resume_from"]))]
    rep = dict(lead=LEAD, feed_disclosure=FEED_DISCLOSURE, status_counts=st, n_counted=len(counted),
               binding_N=N_DECISION, kill_R=KILL_R, futility_at=FUTILITY_AT,
               dropped_sessions=sorted((r["date"], r["instrument"], r["session"], r["status"]) for r in lat.values()
                                       if r["status"] not in ("trade", "no_trade")),
               registration=registration_status(), clearance=cleared(led.root), feed_suspension=susp)
    if not all(rep["clearance"].values()):
        rep["R"] = "SEALED: DATA_CERTIFIED.json and CASSANDRA_CLEARED.json with this harness_sha256 are required before any R is shown"
        return rep
    outs = {(o["date"], o["instrument"], o["session"]): o for o in led.outcomes()}
    tr = [dict(r, **{k: outs[(r["date"], r["instrument"], r["session"])][k] for k in ("R", "exit", "risk_pts")}) for r in counted]
    for t in tr:
        t["R"] = float(t["R"]); t["risk_pts"] = float(t["risk_pts"])
    tr = canonical(tr)
    k = kill_walk(tr)
    if k["kill"]:
        tr_eval = tr[:k["kill_at_trade"]]
    else:
        tr_eval = tr[:N_DECISION]
    rep["kill"] = k
    fu = futility(tr_eval)
    rep["futility"] = fu
    per = {i: [t for t in tr_eval if t["instrument"] == i] for i in INSTS}
    rep["per_instrument"] = {i: dict(n=len(x), mean_R=mean([t["R"] for t in x]) if x else None) for i, x in per.items()}
    rs = [t["R"] for t in tr_eval]
    n = len(rs)
    if n:
        bb = binding_bound(tr_eval)
        S = ftn()["stats"]
        rep["pooled"] = dict(n=n, mean_R=mean(rs), binding_cluster_bound=bb,
                             trade_level_co_report_lb95=S.boot_ci(rs, alpha=0.10)[0] if n > 1 else None)
        top = sorted(rs, reverse=True); kk = max(1, n // 100)
        p25 = {i: sorted(t["risk_pts"] for t in per[i])[len(per[i]) // 4] for i in INSTS if per[i]}
        big = [t["R"] for t in tr_eval if t["risk_pts"] >= p25.get(t["instrument"], 0)]
        rep["robustness"] = dict(ex_top1pct=mean(top[kk:]) if n > kk else None, ex_small_stop=mean(big) if big else None)
        rep["cost_ladder"] = dict(
            x1=mean(rs), x2=mean(t["R"] - 2 * COST_PER_SIDE[t["instrument"]] / t["risk_pts"] for t in tr_eval),
            data_measured=mean(t["R"] - (DATA_COST_RT[t["instrument"]] - 2 * COST_PER_SIDE[t["instrument"]]) / t["risk_pts"] for t in tr_eval))
        rep["splits"] = {k2: {v: (lambda xs: dict(n=len(xs), mean_R=mean(xs) if xs else None))([t["R"] for t in tr_eval if f(t) == v])
                              for v in vals} for k2, f, vals in
                         (("side", lambda t: t["side"], ("buy", "sell")), ("session", lambda t: t["session"], SESSIONS),
                          ("london_dst_mismatch", lambda t: (t["session"], t["dst_mismatch_week"]),
                           (("london", "True"), ("london", "False"))))}
        rep["splits"]["london_dst_mismatch"] = {str(a): b for a, b in rep["splits"]["london_dst_mismatch"].items()}
        # foil (pooled per replicate; N per replicate logged)
        store = duka.Store(led.root, get=lambda u: (_ for _ in ()).throw(RuntimeError("report never downloads")))
        days = sorted({dt.date.fromisoformat(t["date"]) for t in tr_eval})
        reps = None
        for i in INSTS:
            if not per[i]:
                continue
            ser = full_series(store, i, "BID", days)
            fr = foil_with_n(ser, per[i], COST_PER_SIDE[i], n=foil_n)
            reps = fr if reps is None else [(0, a[1] + b[1], a[2] + b[2]) for a, b in zip(reps, fr)]
        pm = [x[2] / x[1] if x[1] else 0.0 for x in reps]
        ns = sorted(x[1] for x in reps)
        rep["foil"] = dict(pct=100.0 * sum(1 for m in pm if m < mean(rs)) / len(pm), median=sorted(pm)[len(pm) // 2],
                           n_per_replicate=dict(min=ns[0], median=ns[len(ns) // 2], max=ns[-1], trades=n))
        # spread + ASK co-reports
        rep["spread_monthly"] = spread_report(store, tr_eval)
        rep["ask_resim"] = ask_report(store, tr_eval)
        if n >= NO_VERDICT_BELOW:
            rep["ask_spot_check_short_stopouts"] = [x for x in rep["ask_resim"].pop("_rows") if x["side"] == "sell" and x["exit"] == "stop"]
        else:
            rep["ask_resim"].pop("_rows")
    rep["verdict"] = verdict(rep, n, k, fu)
    rep["family_rule"] = ("PASS is 'PASSES (unadjusted)'; SURVIVES only if p_one_sided clears Holm across the active family "
                          "(research/protocols/FORWARD_FAMILY_RULE_2026-10-04.md, main ebfa83b: 0.0167 / 0.025 / 0.05). "
                          "Kill and futility are never relaxed. Non-binding Holm co-report across H013/H014/H015b: ORION")
    return rep


def suspension(lat: dict, root: pathlib.Path) -> dict:
    """Appendix A4/A11: a schema failure (feed_suspended row) or > SUSPEND_AFTER consecutive expected trading days whose rows
    are all feed_gap suspends counting from the first such date, until DATA writes FEED_RESUMED.json {"resume_from": date}."""
    by = {}
    for (ds, _, _), r in lat.items():
        by.setdefault(ds, set()).add(r["status"])
    since, streak = None, []
    for ds in sorted(by):
        st = by[ds]
        if "feed_suspended" in st:
            since = since or ds; break
        if st == {"feed_gap"}:
            streak.append(ds)
            if len(streak) > SUSPEND_AFTER:
                since = streak[0]; break
        elif st & {"trade", "no_trade", "short_session", "not_trading_day", "context_gap"}:
            streak = []
    res = None
    p = root / "FEED_RESUMED.json"
    if since and p.exists():
        try:
            res = json.loads(p.read_text()).get("resume_from")
        except Exception:
            res = None
    return dict(since=since, resume_from=res, suspended=bool(since and not res))


def verdict(rep, n, k, fu) -> str:
    if k["kill"]:
        return f"FAILS (kill: pooled cumulative R <= {KILL_R}R at trade {k['kill_at_trade']})"
    if fu and fu["fails"]:
        return f"FAILS (futility at N={FUTILITY_AT}: upper 97.5% cluster bound {fu['ub_one_sided_975']:+.3f} < +{FUTILITY_BAR})"
    if n < NO_VERDICT_BELOW:
        return f"OPEN (N={n} < {NO_VERDICT_BELOW}: no verdict or edge wording)"
    if n < N_DECISION:
        return f"OPEN (N={n} of {N_DECISION})"
    p, pi = rep["pooled"], rep["per_instrument"]
    crit = [p["mean_R"] >= 0.10, p["binding_cluster_bound"]["lb_one_sided_95"] > 0, rep["foil"]["pct"] >= 95.0,
            all((pi[i]["mean_R"] or -1) > 0 for i in INSTS), (rep["robustness"]["ex_top1pct"] or -1) > 0,
            (rep["robustness"]["ex_small_stop"] or -1) > 0]
    return "PASSES (unadjusted)" if all(crit) else f"FAILS (pass criteria at N={N_DECISION}: {crit})"


def spread_report(store, trades) -> dict:
    by = {}
    for t in trades:
        d = dt.date.fromisoformat(t["date"]); inst = t["instrument"]
        a, b = {"london": (2, 5), "ny_am": (7, 10)}[t["session"]]
        days = [d - dt.timedelta(days=1), d]
        if not all(store.meta(inst, s, x) for s in ("BID", "ASK") for x in days):
            continue
        bid = series_from_csv_texts([store.csv_text(inst, "BID", x) for x in days], inst, ny(d, 17))
        ask = series_from_csv_texts([store.csv_text(inst, "ASK", x) for x in days], inst, ny(d, 17))
        bm = {bid.t[i]: bid.c[i] for i in bid.window(ny(d, a), ny(d, b))}
        for i in ask.window(ny(d, a), ny(d, b)):
            if ask.t[i] in bm:
                by.setdefault((inst, t["date"][:7]), []).append(ask.c[i] - bm[ask.t[i]])
    return {f"{i} {m}": dict(median=median(v), n=len(v), crossed=sum(1 for x in v if x < 0), flag=median(v) > SPREAD_FLAG[i])
            for (i, m), v in sorted(by.items())}


def ask_report(store, trades) -> dict:
    rows = []
    for t in trades:
        d = dt.date.fromisoformat(t["date"]); inst = t["instrument"]; days = [d - dt.timedelta(days=1), d]
        if not all(store.meta(inst, s, x) for s in ("BID", "ASK") for x in days):
            continue
        bid = series_from_csv_texts([store.csv_text(inst, "BID", x) for x in days], inst, ny(d, 17))
        ask = series_from_csv_texts([store.csv_text(inst, "ASK", x) for x in days], inst, ny(d, 17))
        rows.append(dict(date=t["date"], instrument=inst, session=t["session"], side=t["side"], exit=t["exit"], R=t["R"],
                         **{f"R_ask_slip{s}": ask_resim(bid, ask, t, s) for s in STOP_SLIP}))
    out = {f"mean_R_ask_slip{s}": (lambda v: mean(v) if v else None)([r[f"R_ask_slip{s}"] for r in rows if r[f"R_ask_slip{s}"] is not None])
           for s in STOP_SLIP}
    out["n"] = len(rows); out["_rows"] = rows
    return out


# ------------------------------------------------------------------ certification helpers
def repro_burned(tape_dir: str = "/workspace/ict-blueprint/research/model-u-longrun/data", every: int = 1,
                 insts=INSTS) -> dict:
    """C11: per-session path on the burned tape (DATA only: the code is not used) vs the committed FTN-D22 trades CSVs."""
    B = ftn()["bars"]; res = {}
    for inst in insts:
        full = B.load_series(f"{tape_dir}/{inst}_1m.csv.gz", inst)
        want = {(r["date"], r["session"]): r for r in csv.DictReader(open(
            REPO / f"research/evidence/quant/FTN_M9_TRADES_{inst}_base_2026-10-04_d22_stop_beyond_raid.csv"))}
        days = B.trading_days(full)
        got, mism = {}, []
        for d in days[CONTEXT_SESSIONS::every]:
            lo = full.idx(ny(d - dt.timedelta(days=CONTEXT_DAYS), 0)); hi = full.idx(ny(d, 17))
            s = type(full)(inst, full.t[lo:hi], full.o[lo:hi], full.h[lo:hi], full.l[lo:hi], full.c[lo:hi], "tape")
            for r in score_sessions(s, d):
                if r["outcome"] is not None:
                    got[(d.isoformat(), r["session"])] = r
        cand = {k: v for k, v in want.items() if dt.date.fromisoformat(k[0]) in set(days[CONTEXT_SESSIONS::every])}
        for k in sorted(set(cand) | set(got)):
            a, b = cand.get(k), got.get(k)
            if a is None or b is None:
                mism.append((k, "missing_in_" + ("csv" if a is None else "harness"))); continue
            for f in ("entry_time", "entry", "stop"):
                if str(b[f]) != a[f]:
                    mism.append((k, f, a[f], b[f]))
            if repr(b["outcome"]["R"]) != a["R"] or b["outcome"]["exit"] != a["exit"]:
                mism.append((k, "R/exit", a["R"], b["outcome"]["R"]))
        rs = [float(v["outcome"]["R"]) for v in got.values()]
        res[inst] = dict(n_harness=len(got), n_csv=len(cand), mean_R=mean(rs) if rs else None, mismatches=mism[:20],
                         n_mismatch=len(mism))
    return res


def cmd_c5(n_days: int = 5, root: str | None = None) -> dict:
    """C5: re-pull n burned-window days through duka.py; compare with marketdata's NATIVE Dukascopy files (data/dukascopy only,
    never the HistData fallback) row-for-row, and the bi5 bytes with marketdata's raw bi5."""
    import pandas as pd
    days = [dt.date(2026, 3, 9), dt.date(2026, 3, 30), dt.date(2026, 6, 15), dt.date(2026, 9, 10), dt.date(2025, 11, 3),
            dt.date(2026, 1, 2)][:max(n_days, 5)]
    tmp = pathlib.Path(root or tempfile.mkdtemp(prefix="h015b_c5_"))
    store = duka.Store(tmp); out = []
    for inst in INSTS:
        sym = duka.SYMBOL[inst]
        for d in days:
            for side in ("BID", "ASK"):
                m = store.ensure(inst, side, d, reason="c5_certification")
                rawp = pathlib.Path(f"/workspace/marketdata/raw/dukascopy/{sym}/{d.year}/{d:%Y%m%d}_{side}.bi5")
                pq = pathlib.Path(f"/workspace/marketdata/data/dukascopy/{inst}/1m_{side.lower()}/{d.year}.parquet")
                rec = dict(inst=inst, day=d.isoformat(), side=side, rows=m["rows_kept"], filler_dropped=m["filler_dropped"])
                rec["bi5_equal_marketdata_raw"] = (duka.sha256(rawp.read_bytes()) == m["bi5_sha256"]) if rawp.exists() else None
                if pq.exists():
                    P = pd.read_parquet(pq)
                    P = P[(P.ts_utc >= pd.Timestamp(d, tz="UTC")) & (P.ts_utc < pd.Timestamp(d, tz="UTC") + pd.Timedelta(days=1))]
                    df = pd.read_csv(io.StringIO(store.csv_text(inst, side, d)))
                    rec["rows_marketdata"] = len(P)
                    rec["csv_equal_marketdata"] = bool(len(P) == len(df) and len(P) and (df.Datetime.values == P.ts_ny.astype(str).values).all()
                                                       and all((df[c.capitalize()].values == P[c].values).all() for c in ("open", "high", "low", "close")))
                    rec["bars_17h_ny"] = int((pd.to_datetime(df.Datetime.str[:19]).dt.hour == 17).sum())
                out.append(rec)
    return dict(dir=str(tmp), days=[d.isoformat() for d in days], results=out,
                ok=all(r.get("csv_equal_marketdata") is not False and r.get("bars_17h_ny", 0) == 0 for r in out))


def selfcheck() -> dict:
    m = harness_manifest()
    return dict(pins_ok=not verify_pins(), pin_problems=verify_pins(), tag=TAG, tag_commit=TAG_COMMIT, harness_manifest=m,
                harness_sha256=harness_digest(m), registration=registration_status(), data_dir=str(DATA_ROOT),
                clearance=cleared(DATA_ROOT))


if __name__ == "__main__":
    a = sys.argv[1:]
    cmd = a[0] if a else "selfcheck"
    if cmd == "final":
        rows = cmd_final()
        for r in rows:   # never prints R / exit
            print({k: r.get(k) for k in ("date", "instrument", "session", "status", "ticket", "side", "entry_time", "counted",
                                        "not_counted_reasons")})
        print(json.dumps({k: v for k, v in cmd_report().items() if k in ("status_counts", "n_counted", "clearance", "R")}, indent=1))
    elif cmd == "report":
        print(json.dumps(cmd_report(), indent=1, default=str))
    elif cmd == "verify":
        print(json.dumps(cmd_verify(), indent=1, default=str))
    elif cmd == "repro-burned":
        print(json.dumps(repro_burned(every=int(a[1]) if len(a) > 1 else 1), indent=1, default=str))
    elif cmd == "c5":
        print(json.dumps(cmd_c5(int(a[1]) if len(a) > 1 else 5), indent=1, default=str))
    else:
        print(json.dumps(selfcheck(), indent=1, default=str))
