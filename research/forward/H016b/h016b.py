"""H016b forward harness: FTN Month 9 REV, FIXED (ftn/demo-fixes 9bed235), US100 + US500 CFD, frozen forward-only test.
HYPOTHETICAL paper research: no orders, no broker calls, nothing reaches MINT.

Implements research/protocols/preregs/H016b_FORWARD_PREREG_2026-10-04.json (tag prereg-H016b -> 74b13d3; supersedes H016
pre-data after CASSANDRA's HOLD) and its data-handling appendix research/protocols/preregs/H016b_DATA_APPENDIX_2026-10-04.md.
Adapted from the DATA-certified H015b v2 harness (tag harness-H015b-v2 -> 5ea3e89, research/forward/H015/h015.py; never
edited), keeping DATA's v1 blockers B1-B5 fixes:
  B1 day-file finality by content (duka.Store, code-identical) B2 session completeness on the full datetime (d 16:14 NY)
  B3 missing/frozen context days skipped + disclosed per row     B4 full NYSE context calendar (pre-window + 2028 + 2029)
  B5 exit-bar rule = >= 1 BID AND >= 1 ASK bar in [15:45, 16:00) NY on EVERY session; > 5-min gap either side = gap_flag
H016b binding items (prereg):
  * feed = Dukascopy datafeed BID AND ASK, both binding (feed_gap_bid / feed_gap_ask; never a fallback or synthetic ASK)
  * pins verified in place against `git show prereg-H016b:<path>` (harness_hash_mismatch); no unpinned ftn module may be
    imported (unpinned_import); FTN_EVENTS_CSV refused
  * per session: History(bid, trading_days(bid), ask=ask, calendar=True) -> session_ticket_log(days=[d], flat book) ->
    tradeable -> entry-minute rule (BID and ASK bars at exactly t-1m, else feed_gap_entry) -> simulate_both binding
    (R None -> no_r_ticket); calendar on/off ticket identity per session (else calendar_identity_fail, refused)
  * N = 747, kill at -40R (crossing logged once to sealed/KILL_LOG.json and STICKY: a logged kill forces FAILS forever;
    CASSANDRA F1 / harness-H016b-v2), futility once at trade 200 on the frozen
    sealed/FUTILITY_SET.json (v[9749] < +0.10), session-cluster bootstrap seed 20261004, 10,000 resamples, LB v[500]
  * counting only for rows computed after the first H016b harness registration commit on origin; R SEALED until
    DATA_CERTIFIED.json and CASSANDRA_CLEARED.json carrying this harness digest exist; no verdict wording below N=100
  * co-reports: flat cost, 2x slippage, running paper book, fill-fragility (verdict label 'fill-fragile'), gap_flag,
    short_session-dropped, entry-minute / no_r counts, DATA condition 4, monthly spread monitor, family rule (H013/H014/H016b)
Data/logs: $HERMES_FWD_DATA/H016b (default /home/box/hermes-x/forward/H016b), outside git.

CLI (from the root of a clean checkout at tag harness-H016b-v2; scheduled run = `final` at or after 01:00 UTC, Tue-Sat):
  python research/forward/H016b/h016b.py final        score every pending session date d with now >= d+1 01:00 UTC
  python research/forward/H016b/h016b.py report       status counts; R/stats only after both clearance files exist
  python research/forward/H016b/h016b.py verify       recompute every FINAL row from stored files; must match exactly
  python research/forward/H016b/h016b.py selfcheck    pins, tag, harness manifest/digest, registration
  python research/forward/H016b/h016b.py repro-burned [every]  per-session reproduction of the burned H016 trades
  python research/forward/H016b/h016b.py repull <outdir> [local|network]  CASSANDRA F8 burned-day re-pull evidence"""
from __future__ import annotations

import csv, datetime as dt, fcntl, hashlib, io, json, os, pathlib, random, subprocess, sys, tempfile, uuid
from copy import deepcopy
from statistics import mean, median

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parents[2]
import importlib.util  # noqa: E402
# load THIS directory's duka.py under a unique name (H015/duka.py may already be imported as `duka` in the same process)
_spec = importlib.util.spec_from_file_location("h016b_duka", HERE / "duka.py")
duka = importlib.util.module_from_spec(_spec); sys.modules["h016b_duka"] = duka; _spec.loader.exec_module(duka)
_spec2 = importlib.util.spec_from_file_location("h016b_one_sided", HERE / "one_sided.py")
one_sided = importlib.util.module_from_spec(_spec2); sys.modules["h016b_one_sided"] = one_sided; _spec2.loader.exec_module(one_sided)

LEAD = "H016b"
PREREG_REL = "research/protocols/preregs/H016b_FORWARD_PREREG_2026-10-04.json"
APPENDIX_REL = "research/protocols/preregs/H016b_DATA_APPENDIX_2026-10-04.md"
REG_NOTE_REL = "research/protocols/preregs/H016b_HARNESS_REGISTRATION_V2_2026-10-05.json"
HARNESS_VERSION = "v2"
TAG = "prereg-H016b"
TAG_COMMIT = "74b13d312990e22c24d2ccfcd1f2072aca67cfdc"
REG_REFS = ("origin/main", "origin/ftn/demo-fixes")
HARNESS_FILES = [HERE / "__init__.py", HERE / "duka.py", HERE / "h016b.py", HERE / "one_sided.py",
                 REPO / "research/forward/tests/test_h016b.py", REPO / APPENDIX_REL]
DATA_ROOT = pathlib.Path(os.environ.get("HERMES_FWD_DATA", "/home/box/hermes-x/forward")) / LEAD
# CASSANDRA C2 / DATA B1: the H015b data directory and every file the H016b harness did not download itself are QUARANTINED.
# The harness never reads H015b's directory (no path to it is built anywhere), refuses to run with a data root inside it,
# and refuses any raw file without its own provenance record (OwnStore). Disclosed in the registration note.
QUARANTINED_DIRS = ("/home/box/hermes-x/forward/H015b", "/workspace/marketdata")
PRE_REGISTRATION_TOUCHED = tuple((dt.date(2026, 9, 26) + dt.timedelta(days=k)).isoformat() for k in range(8))  # 09-26..10-03
TAG_PUSH_UTC = dt.datetime(2026, 10, 4, 9, 48, 19, tzinfo=dt.timezone.utc)   # prereg-H016b tagger time 11:48:19 SAST
INSTS = ("US100", "US500")
SIDES = ("BID", "ASK")
SESSIONS = ("london", "ny_am")
KZ = {"london": (2, 5), "ny_am": (7, 10)}
FIRST_DATE = dt.date(2026, 10, 5)
BURNED_END = dt.date(2026, 9, 25)
CONTEXT_DAYS = 45
CONTEXT_SESSIONS = 22
KZ_MIN, KZ_N = 171, 180
RTH_MIN = 300
LAST_BAR = dt.time(16, 14)
RETRY_TRADING_DAYS = 5
SUSPEND_AFTER = 10
KILL_R = -40.0
N_DECISION = 747
FUTILITY_AT = 200
FUTILITY_BAR = 0.10
NO_VERDICT_BELOW = 100
SEED = 20261004
N_BOOT = 10_000
LB_INDEX = int(0.05 * N_BOOT)          # 500
UB975_INDEX = int(0.975 * N_BOOT) - 1  # 9749
N_FOIL = 2000
COST_PER_SIDE = {"US100": 0.8, "US500": 0.5}       # flat-cost CO-REPORT only (CASSANDRA)
SLIP_MULT_BINDING, SLIP_MULT_CO = 1.0, 2.0
SPREAD_FLAG = {"US100": 1.1, "US500": 0.5}
HOLM_3 = (0.05 / 3, 0.025, 0.05)              # active family H013, H014, H016b (prereg family_rule)
FAMILY = ("H013", "H014", "H016b")
FRAG_DELTA = 0.25                               # min_risk re-gate / threshold-ticket band (prereg fill_fragility_co_report)
HOLIDAYS_PRE_WINDOW = {"full_closures": ["2025-09-01", "2025-11-27", "2025-12-25", "2026-01-01", "2026-01-19", "2026-02-16",
                                         "2026-04-03", "2026-05-25", "2026-06-19", "2026-07-03", "2026-09-07"],
                       "early_closes": ["2025-11-28", "2025-12-24"]}   # NYSE, context calendar (DATA cert B4)
HOLIDAYS_2028 = {"full_closures": ["2028-01-17", "2028-02-21", "2028-04-14", "2028-05-29", "2028-06-19", "2028-07-04",
                                   "2028-09-04", "2028-11-23", "2028-12-25"],
                 "early_closes": ["2028-07-03", "2028-11-24"]}           # DATA F8 (H015b appendix A10)
HOLIDAYS_2029 = {"full_closures": ["2029-01-01", "2029-01-15", "2029-02-19", "2029-03-30", "2029-05-28", "2029-06-19",
                                   "2029-07-04", "2029-09-03", "2029-11-22", "2029-12-25"],
                 "early_closes": ["2029-07-03", "2029-11-23", "2029-12-24"]}   # pandas_market_calendars NYSE; DATA to verify
HOLIDAYS_2030 = {"full_closures": ["2030-01-01", "2030-01-21", "2030-02-18", "2030-04-19", "2030-05-27", "2030-06-19",
                                   "2030-07-04", "2030-09-02", "2030-11-28", "2030-12-25"],
                 "early_closes": ["2030-07-03", "2030-11-29", "2030-12-24"]}   # PROJECTED (DATA NYSE_HOLIDAYS_2028_2030)
HOLIDAY_SOURCE = ("NYSE published holiday / early-close calendar (nyse.com markets/hours-calendars); a discrepancy is "
                  "resolved in favour of the NYSE publication (prereg counting_rules.holiday_source). 2028 OFFICIAL; 2029-2030 "
                  "PROJECTED from NYSE Rule 7.2 (DATA NYSE_HOLIDAYS_2028_2030.{csv,md}: pandas_market_calendars 5.4.0, "
                  "exchange_calendars 4.13.2 and a rule-set implementation agree); DATA re-verifies each year against the "
                  "NYSE publication before its first session. A date past the last covered year is held PROVISIONAL "
                  "(calendar_not_covered, never terminal) until the calendar is extended")
FEED_DISCLOSURE = ("Feed: Dukascopy CFD BID+ASK 1m (datafeed day files), NOT TradingView CAPITALCOM as in H013/H014, and unlike "
                   "H015b's BID-only binding stream (H015b WITHDRAWN-PRE-DATA). Binding fills are correct-side (buys on ASK, sells on BID) plus DATA's "
                   "slippage floors; flat cost is a co-report only.")
LOG_COLS = ["run_id", "computed_at_utc", "computed_at_sast", "date", "instrument", "session", "status", "counted",
            "not_counted_reasons", "ticket", "module", "side", "entry_time", "entry", "stop", "stop_source", "stop_buffer",
            "spread_measured", "block_reason", "risk_pts", "gates", "reason", "kz_bars", "kz_bars_ask", "rth_bars",
            "last_bar_ny", "last_bar_ask_ny", "context_sessions", "session_raw_sha256", "context_manifest_sha256",
            "manifest_file", "filler_dropped_session", "filler_dropped_session_ask", "pins_ok", "harness_sha256",
            "registration_commit", "registration_time_utc", "harness_matches_registered", "dst_mismatch_week",
            "exit_bar_1545_ok", "exit_bar_1545_ok_ask", "gap_flag", "ask_gap_minutes", "context_missing_days",
            "context_frozen_incomplete", "entry_bar_bid", "entry_bar_ask", "calendar_identity_ok", "unpinned_modules",
            "regate_candidate", "dist_pts", "context_pre_registration_touched", "harness_version", "error"]
OUT_COLS = ["date", "instrument", "session", "R", "exit", "risk_pts", "fill_in", "fill_out", "exit_time", "R_slip2x",
            "exit_slip2x", "R_flatcost", "exit_flatcost", "exit_time_rule_ok", "gap_flag", "ask_gap_minutes",
            "session_raw_sha256", "context_manifest_sha256", "one_sided_exit_minutes", "bid_only_minutes",
            "ask_only_minutes", "R_conservative", "exit_conservative", "exit_time_conservative", "proxy_events"]
TERMINAL = {"trade", "no_trade", "feed_gap_bid", "feed_gap_ask", "feed_gap_entry", "no_r_ticket", "holiday",
            "short_session", "context_gap", "feed_suspended", "not_trading_day", "calendar_identity_fail"}
# calendar_not_covered is deliberately NOT terminal (DATA K3): the row waits until the calendar covers the year
FEED_GAP_DAY = {"feed_gap_bid", "feed_gap_ask"}   # whole-session feed gaps (feed suspension counter)
SCORED = ("trade", "no_trade", "short_session", "feed_gap_entry", "no_r_ticket", "calendar_identity_fail")


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
    return {**c["kernel_and_dtr_sha256"], **c["risk_sha256"], **c["scoring_sha256"], **c["registration_inputs_sha256"]}


# ------------------------------------------------------------------ pins / manifest / registration
def verify_pins() -> dict:
    """{} if OK. The tag resolves to TAG_COMMIT; the prereg and every pinned file are byte-identical to the tag and hash to
    the prereg pins, in place in this checkout. FTN_EVENTS_CSV (calendar override) is forbidden (prereg rule.calendar)."""
    bad = {}
    if os.environ.get("FTN_EVENTS_CSV"):
        bad["FTN_EVENTS_CSV"] = "override_forbidden"
    try:
        tc = _git("rev-parse", f"{TAG}^{{commit}}").strip()
    except Exception as e:
        return {**bad, "tag": f"missing: {str(e)[:80]}"}
    if tc != TAG_COMMIT:
        bad["tag"] = tc
    P = pins()
    for rel in [PREREG_REL, *P]:
        p = REPO / rel
        got = p.read_bytes() if p.exists() else None
        try:
            want = _git_bytes("show", f"{TAG}:{rel}")
        except Exception:
            want = b"<not in tag>"
        if got != want:
            bad[rel] = "differs_from_tag" if got is not None else "MISSING"
        elif rel != PREREG_REL and hashlib.sha256(got).hexdigest() != P[rel]:
            bad[rel] = "sha256_differs_from_prereg_pin"
    return bad


def harness_manifest() -> dict:
    return {"repo_root": "GdotAiM/hermes",
            "files": {str(pathlib.Path(f).resolve().relative_to(REPO)): sha256_file(f) for f in HARNESS_FILES}}


def harness_digest(m=None) -> str:
    return hashlib.sha256(json.dumps(m or harness_manifest(), sort_keys=True).encode()).hexdigest()


def registration_status(fetch: bool = False) -> dict:
    """The earliest commit on any REG_REFS that carries the registration note (status REGISTERED, harness_sha256.files).
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
                    note = json.loads(_git("show", f"{sha}:{REG_NOTE_REL}"))
                    hs = note.get("harness_sha256")
                except Exception:
                    continue
                if not str(note.get("status", "")).startswith("REGISTERED"):
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
        from ftn.os import instruments
        from ftn.research import bars, book, daycontext, kernel_log, outcomes, stats, score
        cfg = deepcopy(load_config())
        cfg["interpretation_triggers"] = {"conso": False, "bb": False, "pip20": False}
        _FTN = dict(cfg=cfg, bars=bars, dc=daycontext, kl=kernel_log, out=outcomes, stats=stats, score=score, book=book,
                    ins=instruments)
    return _FTN


def unpinned_ftn_modules() -> list[str]:
    """CASSANDRA F12a: every imported ftn module must be a pinned file of THIS checkout (prereg code.*_sha256); anything
    else (e.g. ftn.__main__, adapters, journal, workflow, or a copy outside <repo>/ftn/src) is reported and refuses rows."""
    src = (REPO / "ftn" / "src").resolve(); P = set(pins()); bad = []
    for name, m in list(sys.modules.items()):
        if not (name == "ftn" or name.startswith("ftn.")):
            continue
        f = getattr(m, "__file__", None)
        if f is None:
            bad.append(f"{name}:<no file>"); continue
        fp = pathlib.Path(f).resolve()
        try:
            rel = str(fp.relative_to(REPO.resolve()))
        except ValueError:
            bad.append(f"{name}:{fp}"); continue
        if not str(fp).startswith(str(src)) or rel not in P:
            bad.append(f"{name}:{rel}")
    return sorted(bad)


def slip(inst: str) -> dict:
    """DATA slippage floors per side (pinned ftn.os.instruments; identical to ftn.research.score.slip_floors)."""
    return ftn()["score"].slip_floors(inst)


# ------------------------------------------------------------------ calendar
def holidays() -> dict:
    h = deepcopy(prereg()["counting_rules"]["holidays_excluded"])
    for k in ("full_closures", "early_closes"):
        h[k] = sorted(set(h[k]) | set(HOLIDAYS_PRE_WINDOW[k]) | set(HOLIDAYS_2028[k]) | set(HOLIDAYS_2029[k]) | set(HOLIDAYS_2030[k]))
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
    out, d = [], a
    while d <= b:
        if calendar_status(d) in ("ok", "calendar_not_covered"):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def dst_mismatch_week(d: dt.date) -> bool:
    from zoneinfo import ZoneInfo
    lon = dt.datetime(d.year, d.month, d.day, 12, tzinfo=duka.UTC).astimezone(ZoneInfo("Europe/London"))
    nyt = dt.datetime(d.year, d.month, d.day, 12, tzinfo=duka.UTC).astimezone(duka.NY)
    return (lon.utcoffset() - nyt.utcoffset()) != dt.timedelta(hours=5)


# ------------------------------------------------------------------ series assembly
def utc_days_for(d: dt.date) -> list[dt.date]:
    return [d - dt.timedelta(days=k) for k in range(CONTEXT_DAYS, -1, -1)]


def session_utc_days(d: dt.date) -> list[dt.date]:
    return [d - dt.timedelta(days=1), d]


def series_from_csv_texts(texts: list[str], inst: str, end_ny: dt.datetime, start_ny: dt.datetime | None = None):
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


def timing_reasons(d: dt.date, session: str, reg: dict) -> list[str]:
    """CASSANDRA C1 (reading B): a session counts only if its killzone STARTS after the later of the prereg-H016b tag push
    and the first harness registration commit on origin; earlier sessions are context only, never backfilled. Days
    2026-09-26..10-03 are pre_registration_touched (never counted; they are before FIRST_DATE anyway)."""
    out = []
    a = KZ[session][0]
    start = dt.datetime(d.year, d.month, d.day, a, tzinfo=duka.NY)
    if d.isoformat() in PRE_REGISTRATION_TOUCHED:
        out.append("pre_registration_touched")
    if start <= TAG_PUSH_UTC:
        out.append("session_started_before_prereg")
    rt = reg.get("registration_time_utc")
    if not rt or start <= dt.datetime.fromisoformat(rt):
        out.append("session_started_before_harness_registration")
    return out


def ny(d: dt.date, hh: int, mm: int = 0) -> dt.datetime:
    return dt.datetime(d.year, d.month, d.day, hh, mm)


def ask_start_ny(d: dt.date) -> dt.datetime:
    """NY wall clock of 00:00 UTC on d-1: the first minute covered by the session's ASK day files."""
    x = dt.datetime(d.year, d.month, d.day, tzinfo=duka.UTC) - dt.timedelta(days=1)
    return x.astimezone(duka.NY).replace(tzinfo=None)


# ------------------------------------------------------------------ per-session scoring (pure: from BID + ASK series)
def _risk_block(r: dict) -> str | None:
    for g in r.get("gates") or []:
        if g.startswith("risk:FAIL:"):
            return g.split(":", 2)[2]
    return None


def outcome_both(bid, ask, inst: str, r: dict, slip_mult: float = SLIP_MULT_BINDING) -> dict:
    return ftn()["out"].simulate_both(bid, ask, dt.datetime.fromisoformat(r["entry_time"]), float(r["entry"]),
                                      float(r["stop"]), r["side"], slip(inst), slip_mult=slip_mult)


def entry_bars(bid, ask, entry_time: dt.datetime) -> tuple[bool, bool]:
    """BINDING (prereg rule.entry_minute, CASSANDRA F1): the entry / spread_measured / simulate_both entry fill use the last
    bar strictly before t; the ticket counts only if that bar is EXACTLY t-1m on BID and on ASK."""
    want = entry_time - dt.timedelta(minutes=1)
    out = []
    for s in (bid, ask):
        i = s.idx(entry_time) - 1
        out.append(i >= 0 and s.t[i] == want)
    return out[0], out[1]


TICKET_KEYS = ("ticket", "side", "entry_time", "entry", "stop")


def score_sessions(bid, ask, d: dt.date, entry_rule: bool = True, calendar_check: bool = True) -> list[dict]:
    """The pinned scorer path for one day: History(bid, trading_days, ask=ask, calendar=True) -> session_ticket_log(days=[d],
    flat book) -> tradeable -> entry-minute rule -> simulate_both (binding) + simulate_both 2x slip + flat simulate.
    entry_rule=False only for the bit-for-bit reproduction of the burned (pre-rule) H016 CSVs; the forward path always
    applies it, and no outcome is computed for a ticket that fails it. calendar_check: the same day with
    History(calendar=False) must give the identical ticket (prereg counting_rules.calendar_identity)."""
    F = ftn(); inst = bid.symbol
    days = F["bars"].trading_days(bid)
    hist = F["dc"].History(bid, days, ask=ask, calendar=True)
    if d not in hist.pos:
        return [dict(date=d.isoformat(), session=s, ticket=False, reason="not_in_trading_days", outcome=None) for s in SESSIONS]
    rows = F["kl"].session_ticket_log(hist, F["cfg"], days=[d])
    off = {}
    if calendar_check:
        h0 = F["dc"].History(bid, days, ask=ask, calendar=False)
        off = {r["session"]: r for r in F["kl"].session_ticket_log(h0, F["cfg"], days=[d])}
    out = []
    for r in rows:
        r = dict(r); r["outcome"] = None; r["block_reason"] = _risk_block(r) if r.get("ticket") else None
        r["calendar_identity_ok"] = (None if not calendar_check else
                                     all(str(r.get(k)) == str(off.get(r["session"], {}).get(k)) for k in TICKET_KEYS))
        r["entry_bar_bid"] = r["entry_bar_ask"] = None
        if r.get("ticket") and r.get("entry_time"):
            r["entry_bar_bid"], r["entry_bar_ask"] = entry_bars(bid, ask, dt.datetime.fromisoformat(r["entry_time"]))
        r["regate_candidate"] = bool(r.get("ticket") and r.get("side") and r.get("stop") is not None
                                     and r["block_reason"] == "stop_below_min_risk"
                                     and all(g.startswith(F["kl"].NON_RESEARCH_GATES) or g.startswith("risk:FAIL:stop_below_min_risk")
                                             for g in r.get("gates", []) if ":FAIL:" in g))
        r["tradeable"] = F["kl"].tradeable(r)
        r["no_r_exit"] = None
        if r["tradeable"] and entry_rule and not (r["entry_bar_bid"] and r["entry_bar_ask"]):
            out.append(r); continue
        if r["tradeable"]:
            o = outcome_both(bid, ask, inst, r)
            if o["R"] is None:
                r["no_r_exit"] = o["exit"]
            if o["R"] is not None:
                o2 = outcome_both(bid, ask, inst, r, SLIP_MULT_CO)
                of = F["out"].simulate(bid, dt.datetime.fromisoformat(r["entry_time"]), float(r["entry"]), float(r["stop"]),
                                       r["side"], COST_PER_SIDE[inst])
                o = dict(o, R_slip2x=o2["R"], exit_slip2x=o2["exit"], R_flatcost=of["R"], exit_flatcost=of["exit"])
                r["outcome"] = o
        out.append(r)
    return out


def one_sided_fields(bid, ask, inst: str, r: dict, o: dict) -> dict:
    """Per-trade one-sided exit-minute flag + conservative re-resolution (DATA reference functions, verbatim in one_sided.py).
    Sealed with the outcome (it encodes exit timing)."""
    et = dt.datetime.fromisoformat(r["entry_time"])
    n, bo, ao = one_sided.one_sided_count(bid, ask, et, o["exit_time"])
    ev = []
    c = one_sided.conservative(bid, ask, et, float(r["entry"]), float(r["stop"]), r["side"], slip(inst), events=ev)
    return dict(proxy_events=json.dumps(ev) if ev else "", one_sided_exit_minutes=n, bid_only_minutes=bo, ask_only_minutes=ao,
                R_conservative=repr(c["R"]) if c["R"] is not None else "", exit_conservative=c["exit"],
                exit_time_conservative=c.get("exit_time"))


def exit_bars_ok(series, d: dt.date) -> bool:
    """BINDING (DATA cert B5): >= 1 bar in [15:45, 16:00) NY on date d; evaluated for EVERY session (and on BID and ASK)."""
    return len(series.window(ny(d, 15, 45), ny(d, 16))) > 0


def gap_flag(series, entry_time: dt.datetime, ask=None) -> bool:
    """NON-BINDING co-report flag: a gap > 5 min between the entry and 16:00 NY on BID or (if given) on ASK."""
    end = ny(entry_time.date(), 16)
    for s in (series, ask) if ask is not None else (series,):
        ts = [entry_time] + [s.t[i] for i in s.window(entry_time, end)]
        if any((b - a) > dt.timedelta(minutes=5) for a, b in zip(ts, ts[1:])):
            return True
    return False


def ask_gap_minutes(bid, ask, entry_time: dt.datetime) -> int:
    """BID minutes in [entry, 16:00) without an ASK print (simulate_both skips them; logged, never filled)."""
    end = ny(entry_time.date(), 16); have = set(ask.t[i] for i in ask.window(entry_time, end))
    return sum(1 for i in bid.window(entry_time, end) if bid.t[i] not in have)


# ------------------------------------------------------------------ own-download provenance (CASSANDRA C2, DATA B1)
class ForeignFile(RuntimeError):
    """A raw file in the H016b store that this harness did not download itself (or whose bytes changed)."""


def guard_root(root: pathlib.Path) -> None:
    r = str(pathlib.Path(root).resolve())
    for q in QUARANTINED_DIRS:
        if r == q or r.startswith(q.rstrip("/") + "/"):
            raise SystemExit(f"refusing to run: data root {r} is inside quarantined {q}")


class OwnStore(duka.Store):
    """duka.Store (code-identical to the certified H015b v2 client) plus a provenance record per pull, written by THIS
    harness at download time: prov/<inst>/<SIDE>/<day>.json = {harness, harness_sha256, pulled_at_utc, bi5_sha256,
    csv_sha256, url}. Every file used must carry a matching record; anything else raises ForeignFile (never used)."""

    def prov_path(self, inst, side, day) -> pathlib.Path:
        return self.root / "prov" / inst / side / f"{day.isoformat()}.json"

    def ensure(self, inst, side, day, reason="missing"):
        before = self.meta(inst, side, day)
        if before is not None:
            self.check_own(inst, side, day)
        m = super().ensure(inst, side, day, reason)
        if m.get("bi5_sha256") and (before is None or before.get("pulled_at_utc") != m.get("pulled_at_utc")):
            pp = self.prov_path(inst, side, day); pp.parent.mkdir(parents=True, exist_ok=True)
            pp.write_text(json.dumps(dict(harness=LEAD, harness_sha256=harness_digest(), pulled_at_utc=m["pulled_at_utc"],
                                          bi5_sha256=m["bi5_sha256"], csv_sha256=m["csv_sha256"], url=m["url"]),
                                     indent=1, sort_keys=True) + "\n")
        if m.get("bi5_sha256"):
            self.check_own(inst, side, day)
        return m

    def check_own(self, inst, side, day) -> None:
        m = self.meta(inst, side, day); pp = self.prov_path(inst, side, day)
        if not pp.exists():
            raise ForeignFile(f"{inst} {side} {day}: no H016b provenance record (not downloaded by this harness)")
        pr = json.loads(pp.read_text())
        if pr.get("harness") != LEAD or pr.get("pulled_at_utc") != m.get("pulled_at_utc") or pr.get("bi5_sha256") != m.get("bi5_sha256") \
                or pr.get("csv_sha256") != m.get("csv_sha256") or not self.verify(inst, side, day):
            raise ForeignFile(f"{inst} {side} {day}: provenance / bytes mismatch")


def foreign_files(root: pathlib.Path) -> list[str]:
    """Every raw .json meta under <root>/raw lacking a matching OwnStore provenance record."""
    st = OwnStore(pathlib.Path(root)); bad = []
    for mp in sorted((pathlib.Path(root) / "raw").glob("*/*/*.json")):
        inst, side, day = mp.parts[-3], mp.parts[-2], dt.date.fromisoformat(mp.stem)
        try:
            st.check_own(inst, side, day)
        except (ForeignFile, Exception) as e:
            bad.append(f"{inst}/{side}/{day}: {str(e)[:80]}")
    return bad


# ------------------------------------------------------------------ ledger
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
        out = {}
        for r in self.rows():
            out[(r["date"], r["instrument"], r["session"])] = r
        return out


def gather(store: "OwnStore", inst: str, d: dt.date) -> dict:
    """Ensure BID day files for d's context + session and ASK day files for UTC days d-1, d (BOTH binding for H016)."""
    metas, problems = [], []
    want = [("BID", x) for x in utc_days_for(d)] + [("ASK", x) for x in session_utc_days(d)]
    for side, day in want:
        try:
            metas.append(store.ensure(inst, side, day))
        except duka.FeedError as e:
            problems.append(("feed_error", side, day.isoformat(), str(e)[:160]))
        except duka.SchemaError as e:
            return dict(status="feed_suspended", error=f"{side} {day}: {e}")
    nf = [f"{m['side']}:{m['day']}" for m in metas if not m.get("final")]
    return dict(status="ok", metas=metas, problems=problems, not_final=nf)


def manifest_for(metas: list[dict], d: dt.date) -> tuple[str, str, list]:
    lst = [[m["day"], m["side"], m["bi5_sha256"], m["csv_sha256"]] for m in metas]
    sd = {x.isoformat() for x in session_utc_days(d)}
    sess = [x for x in lst if x[0] in sd]          # BID d-1, d then ASK d-1, d
    ctx = hashlib.sha256(json.dumps(lst).encode()).hexdigest()
    sraw = hashlib.sha256(json.dumps(sess).encode()).hexdigest()
    return sraw, ctx, lst


def trading_days_after(d: dt.date, today: dt.date) -> int:
    return len(expected_trading_days(d + dt.timedelta(days=1), today))


def write_manifest(store: duka.Store, inst, d, lst) -> str:
    p = store.root / "manifests" / inst / f"{d.isoformat()}.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    b = (json.dumps(lst, indent=0) + "\n").encode()
    if p.exists() and p.read_bytes() != b:
        p = p.with_name(f"{d.isoformat()}__{hashlib.sha256(b).hexdigest()[:12]}.json")
    if not p.exists():
        p.write_bytes(b)
    return str(p.relative_to(store.root))


def series_pair(store: duka.Store, inst: str, d: dt.date, lst: list):
    bid = series_from_csv_texts([store.csv_text(inst, "BID", dt.date.fromisoformat(x[0])) for x in lst if x[1] == "BID"],
                                inst, ny(d, 17))
    ask = series_from_csv_texts([store.csv_text(inst, "ASK", dt.date.fromisoformat(x[0])) for x in lst if x[1] == "ASK"],
                                inst, ny(d, 17))
    return bid, ask


def session_rows_for(store: duka.Store, inst: str, d: dt.date, reg: dict, pins_ok: bool, run_id: str,
                     at: dt.datetime) -> list[tuple[dict, dict | None]]:
    """Rows (one per killzone) for instrument inst on NY date d, or [] for a weekend."""
    from zoneinfo import ZoneInfo
    base = dict(run_id=run_id, computed_at_utc=at.isoformat(timespec="seconds"),
                computed_at_sast=at.astimezone(ZoneInfo("Africa/Johannesburg")).strftime("%Y-%m-%d %H:%M:%S"),
                date=d.isoformat(), instrument=inst, pins_ok=pins_ok, harness_sha256=harness_digest(),
                registration_commit=reg.get("registration_commit"), registration_time_utc=reg.get("registration_time_utc"),
                harness_matches_registered=reg.get("harness_matches_registered"), dst_mismatch_week=dst_mismatch_week(d),
                harness_version=HARNESS_VERSION)
    mk = lambda status, extra=None: [({**base, "session": s, "status": status, "counted": False,
                                       "not_counted_reasons": status, **(extra or {})}, None) for s in SESSIONS]
    cal = calendar_status(d)
    if cal == "weekend":
        return []
    if cal == "calendar_not_covered":
        return mk("provisional", dict(error="calendar_not_covered: waiting for the NYSE calendar extension (DATA K3)"))
    if cal != "ok":
        return mk(cal)
    g = gather(store, inst, d)
    if g["status"] == "feed_suspended":
        return mk("feed_suspended", dict(error=g["error"]))
    age = trading_days_after(d, at.date() - dt.timedelta(days=1))
    sraw, cman, lst = manifest_for(g["metas"], d)
    bid, ask = series_pair(store, inst, d, lst)
    lasts = {}
    for side, s in (("BID", bid), ("ASK", ask)):
        idx = s.window(ny(d - dt.timedelta(days=1), 18), ny(d, 17))
        lasts[side] = s.t[idx[-1]] if len(idx) else None
    feed_err = [p for p in g["problems"] if p[0] == "feed_error"]
    files_ok = not g["not_final"] and not feed_err
    complete = files_ok and all(v is not None and v >= dt.datetime.combine(d, LAST_BAR) for v in lasts.values())   # B2
    if not complete:
        info = f"last bar BID {lasts['BID']} ASK {lasts['ASK']}"
        bid_bad = (any(x.startswith("BID:") for x in g["not_final"]) or any(p[1] == "BID" for p in feed_err)
                   or lasts["BID"] is None or lasts["BID"] < dt.datetime.combine(d, LAST_BAR))
        gap_st = "feed_gap_bid" if bid_bad else "feed_gap_ask"
        if files_ok:
            return mk(gap_st, dict(error=f"{info} < {d} {LAST_BAR}; files final", session_raw_sha256=sraw,
                                       context_manifest_sha256=cman))
        if age > RETRY_TRADING_DAYS:
            return mk(gap_st, dict(error=f"incomplete after {RETRY_TRADING_DAYS} trading days; {info}; "
                                             f"not_final={g['not_final'][:3]} problems={g['problems'][:2]}",
                                       session_raw_sha256=sraw, context_manifest_sha256=cman))
        return mk("provisional", dict(error=f"{info}; not_final={g['not_final'][:3]}; problems={g['problems'][:2]}"))
    mf = write_manifest(store, inst, d, lst)
    F = ftn()
    tdays = F["bars"].trading_days(bid)
    rth = len(bid.window(ny(d, 9, 30), ny(d, 16)))
    sd = [x.isoformat() for x in session_utc_days(d)]
    drop = {side: sum(json.loads(store.paths(inst, side, dt.date.fromisoformat(x))[2].read_text())["filler_dropped"] for x in sd)
            for side in SIDES}
    base.update(session_raw_sha256=sraw, context_manifest_sha256=cman, manifest_file=mf, rth_bars=rth,
                last_bar_ny=str(lasts["BID"]), last_bar_ask_ny=str(lasts["ASK"]), filler_dropped_session=drop["BID"],
                filler_dropped_session_ask=drop["ASK"])
    # context (DATA cert B3/B4): missing expected trading days skipped as History skips them, disclosed per row
    exp = expected_trading_days(d - dt.timedelta(days=CONTEXT_DAYS), d - dt.timedelta(days=1))[-CONTEXT_SESSIONS:]
    miss = [x.isoformat() for x in exp if x not in set(tdays)]
    frozen = [f"{m['side']}:{m['day']}" for m in g["metas"] if m.get("frozen_incomplete")]
    prior = [x for x in tdays if x < d]
    base.update(context_sessions=len(prior), context_missing_days=";".join(miss) or None,
                context_frozen_incomplete=";".join(frozen) or None,
                context_pre_registration_touched=";".join(x for x in PRE_REGISTRATION_TOUCHED
                                                          if dt.date.fromisoformat(x) in set(utc_days_for(d))) or None)
    if len(prior) < CONTEXT_SESSIONS:
        return mk("context_gap", dict(error=f"only {len(prior)} prior sessions < {CONTEXT_SESSIONS}; missing {miss}"))
    if d not in tdays:
        return mk("not_trading_day", dict(error=f"{rth} RTH bars < {RTH_MIN}"))
    exit_ok, exit_ok_ask = exit_bars_ok(bid, d), exit_bars_ok(ask, d)
    base.update(exit_bar_1545_ok=exit_ok, exit_bar_1545_ok_ask=exit_ok_ask)
    res = []
    scored = score_sessions(bid, ask, d)
    unp = unpinned_ftn_modules()
    for r in scored:
        s = r["session"]; a, b = KZ[s]
        kz, kza = len(bid.window(ny(d, a), ny(d, b))), len(ask.window(ny(d, a), ny(d, b)))
        sm = r.get("spread_measured")
        row = {**base, "session": s, "kz_bars": kz, "kz_bars_ask": kza, "ticket": r.get("ticket"), "module": r.get("module"),
               "side": r.get("side"), "entry_time": r.get("entry_time"), "entry": r.get("entry"), "stop": r.get("stop"),
               "stop_source": ("raid_extreme" if r.get("raid_bar_index") is not None else "level_buffer_fallback")
               if r.get("ticket") else None,
               "stop_buffer": (F["ins"].rev_stop_buffer(inst, r["side"], 1.0, sm)[1] if r.get("ticket") and r.get("side") else None),
               "spread_measured": sm, "block_reason": r.get("block_reason"),
               "gates": "|".join(r.get("gates") or []), "reason": r.get("reason"),
               "entry_bar_bid": r.get("entry_bar_bid"), "entry_bar_ask": r.get("entry_bar_ask"),
               "calendar_identity_ok": r.get("calendar_identity_ok"), "unpinned_modules": ";".join(unp) or None,
               "regate_candidate": r.get("regate_candidate"),
               "dist_pts": (abs(float(r["entry"]) - float(r["stop"])) if r.get("ticket") and r.get("stop") is not None
                            and r.get("entry") is not None else None)}
        reasons = []
        if r["outcome"] is not None:
            status = "trade"
        elif r.get("tradeable") and not (r.get("entry_bar_bid") and r.get("entry_bar_ask")):
            status = "feed_gap_entry"; reasons.append(f"entry_bar_bid={r.get('entry_bar_bid')} entry_bar_ask={r.get('entry_bar_ask')}")
        elif r.get("tradeable"):
            status = "no_r_ticket"; reasons.append(f"no_r:{r.get('no_r_exit')}")
        else:
            status = "no_trade"
        if r.get("calendar_identity_ok") is False:
            status = "calendar_identity_fail"; reasons.append("calendar_on_off_ticket_differs")
        if kz < KZ_MIN:
            status = "short_session"; reasons.append(f"kz_bars {kz}/{KZ_N}")
        if kza < KZ_MIN:
            status = "short_session"; reasons.append(f"kz_bars_ask {kza}/{KZ_N}")
        if not exit_ok:
            status = "short_session"; reasons.append("no_bar_1545_1600")
        if not exit_ok_ask:
            status = "short_session"; reasons.append("no_ask_bar_1545_1600")
        o = r["outcome"]
        if o is not None:
            et = dt.datetime.fromisoformat(r["entry_time"])
            gf, agm = gap_flag(bid, et, ask), ask_gap_minutes(bid, ask, et)
            row.update(risk_pts=o["risk_pts"], gap_flag=gf, ask_gap_minutes=agm)
            o = dict(date=d.isoformat(), instrument=inst, session=s, R=repr(o["R"]), exit=o["exit"],
                     risk_pts=repr(o["risk_pts"]), fill_in=repr(o["fill_in"]), fill_out=repr(o["fill_out"]),
                     exit_time=o["exit_time"], R_slip2x=repr(o["R_slip2x"]) if o["R_slip2x"] is not None else "",
                     exit_slip2x=o["exit_slip2x"], R_flatcost=repr(o["R_flatcost"]) if o["R_flatcost"] is not None else "",
                     exit_flatcost=o["exit_flatcost"], exit_time_rule_ok=exit_ok and exit_ok_ask, gap_flag=gf,
                     ask_gap_minutes=agm, session_raw_sha256=sraw, context_manifest_sha256=cman,
                     **one_sided_fields(bid, fragility_series(store, inst, d)[1], inst, r, o))
        if status == "trade" or (status == "no_trade" and r.get("regate_candidate")):
            if unp: reasons.append("unpinned_import")
            if d < FIRST_DATE: reasons.append("before_first_eligible_session")
            if not pins_ok: reasons.append("harness_hash_mismatch")
            if not reg.get("registered"): reasons.append("harness_not_registered")
            elif not reg.get("harness_matches_registered"): reasons.append("harness_hash_mismatch")
            elif dt.datetime.fromisoformat(reg["registration_time_utc"]) >= at: reasons.append("computed_before_registration")
            reasons += timing_reasons(d, s, reg)
        if status == "no_trade":
            # a min_risk-blocked ticket keeps its counting eligibility for the fill-fragility min_risk re-gate (co-report only)
            row["regate_candidate"] = bool(r.get("regate_candidate") and not reasons and r.get("entry_bar_bid") and r.get("entry_bar_ask"))
            reasons = []
        row.update(status=status, counted=(status == "trade" and not reasons), not_counted_reasons=";".join(reasons) or None)
        res.append((row, o if status in ("trade", "short_session") and r["outcome"] is not None else None))
    return res


# ------------------------------------------------------------------ commands
def pending_dates(led: Ledger, at: dt.datetime) -> list[dt.date]:
    lat = led.latest(); out = []
    d = FIRST_DATE
    while dt.datetime(d.year, d.month, d.day, tzinfo=duka.UTC) + duka.FINAL_AFTER <= at:
        if d.weekday() < 5 and not all(lat.get((d.isoformat(), i, s), {}).get("status") in TERMINAL for i in INSTS for s in SESSIONS):
            out.append(d)
        d += dt.timedelta(days=1)
    return out


def write_state(led: Ledger, at: dt.datetime, run_id: str) -> None:
    """STATE.json (public, no R) and sealed/STATE.json (cumulative R, kill, futility; never printed)."""
    lat = led.latest(); st = {}
    for r in lat.values():
        st[r["status"]] = st.get(r["status"], 0) + 1
    tr = counted_trades(led)
    pub = dict(lead=LEAD, harness_version=HARNESS_VERSION, harness_sha256=harness_digest(), last_run_id=run_id,
               last_run_utc=at.isoformat(timespec="seconds"), status_counts=st, n_counted=len(tr), binding_N=N_DECISION,
               pending_dates=[x.isoformat() for x in pending_dates(led, at)])
    (led.root / "STATE.json").write_text(json.dumps(pub, indent=1) + "\n")
    k = kill_sticky(tr, led.root, at)                         # F1: sticky; writes the log on first crossing
    sealed = dict(pub, cum_R=sum(float(t["R"]) for t in k["eval_trades"]), kill={x: k[x] for x in ("kill", "kill_at_trade", "min_cum", "sticky")})
    fu = futility_frozen(k["eval_trades"], led.root)
    sealed["futility"] = fu
    (led.root / "sealed").mkdir(parents=True, exist_ok=True)
    (led.root / "sealed" / "STATE.json").write_text(json.dumps(sealed, indent=1, default=str) + "\n")


def cmd_final(root=None, at: dt.datetime | None = None, get=None, fetch_remote: bool = True) -> list[dict]:
    at = at or now_utc()
    bad = verify_pins()
    if bad:
        raise SystemExit(f"harness_hash_mismatch, refusing to run: {bad}")
    led = Ledger(root); guard_root(led.root); led.root.mkdir(parents=True, exist_ok=True)
    ff = foreign_files(led.root)
    if ff:
        raise SystemExit(f"refusing to run: {len(ff)} raw files not downloaded by this harness (quarantine): {ff[:3]}")
    lock = open(led.root / ".final.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit("another h016b final run holds the lock; refusing to run concurrently")
    try:
        store = OwnStore(led.root, now=lambda: at, get=get, short_ok=lambda day: calendar_status(day) == "holiday")
        reg = registration_status(fetch=fetch_remote)
        run_id = uuid.uuid4().hex[:12]; out = []
        for d in pending_dates(led, at):
            lat = led.latest()
            for inst in INSTS:
                if all(lat.get((d.isoformat(), inst, s), {}).get("status") in TERMINAL for s in SESSIONS):
                    continue
                for row, o in session_rows_for(store, inst, d, reg, True, run_id, at):
                    led.add(row, o); out.append(row)
        write_state(led, at, run_id)
        return out
    finally:
        fcntl.flock(lock, fcntl.LOCK_UN); lock.close()


def cmd_verify(root=None) -> dict:
    """Recompute every terminal trade/no_trade/short_session row from its stored manifest; compare ticket + sealed outcome."""
    led = Ledger(root); store = OwnStore(led.root, get=lambda u: (_ for _ in ()).throw(RuntimeError("verify never downloads")))
    outs = {(o["date"], o["instrument"], o["session"]): o for o in led.outcomes()}
    mism, n = [], 0
    for (ds, inst, s), r in led.latest().items():
        if r["status"] not in SCORED or not r.get("manifest_file"):
            continue
        d = dt.date.fromisoformat(ds)
        lst = json.loads((led.root / r["manifest_file"]).read_text())
        for day, side, b5, cs in lst:
            try:
                store.check_own(inst, side, dt.date.fromisoformat(day))
            except ForeignFile as e:
                mism.append((ds, inst, s, str(e)[:80]))
            m = store.meta(inst, side, dt.date.fromisoformat(day))
            if not store.verify(inst, side, dt.date.fromisoformat(day)) or m["csv_sha256"] != cs or m["bi5_sha256"] != b5:
                mism.append((ds, inst, s, f"stored file changed {side} {day}"))
        bid, ask = series_pair(store, inst, d, lst)
        rr = {x["session"]: x for x in score_sessions(bid, ask, d)}[s]
        n += 1
        for k in ("entry_time", "entry", "stop", "side", "entry_bar_bid", "entry_bar_ask", "calendar_identity_ok"):
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
    c = canonical(trades)
    if len(c) < FUTILITY_AT:
        return None
    v = cluster_boot(c[:FUTILITY_AT])
    return dict(n=FUTILITY_AT, ub_one_sided_975=v[UB975_INDEX], fails=v[UB975_INDEX] < FUTILITY_BAR)


def kill_walk(trades: list[dict]) -> dict:
    cum, hit, lo = 0.0, None, 0.0
    for i, t in enumerate(canonical(trades), 1):
        cum += float(t["R"]); lo = min(lo, cum)
        if cum <= KILL_R and hit is None:
            hit = i
    return dict(kill=hit is not None, kill_at_trade=hit, min_cum=lo)


def kill_log_once(trades: list[dict], k: dict, root: pathlib.Path, at: dt.datetime) -> dict | None:
    """CASSANDRA F5: the first crossing of the kill line is written ONCE to sealed/KILL_LOG.json (row keys up to and
    including the crossing trade, cumulative R, compute time), never overwritten; later reports read it back."""
    p = pathlib.Path(root) / "sealed" / "KILL_LOG.json"
    if p.exists():
        return json.loads(p.read_text())
    if not k["kill"]:
        return None
    c = canonical(trades)[:k["kill_at_trade"]]
    p.parent.mkdir(parents=True, exist_ok=True)
    rec = dict(logged_at_utc=at.isoformat(timespec="seconds"), kill_R=KILL_R, kill_at_trade=k["kill_at_trade"],
               cum_R_at_crossing=sum(float(t["R"]) for t in c), keys=[key(t) for t in c], harness_sha256=harness_digest())
    p.write_text(json.dumps(rec, indent=1) + "\n")
    return rec


def kill_sticky(trades: list[dict], root: pathlib.Path, at: dt.datetime | None = None) -> dict:
    """CASSANDRA F1 (harness-H016b-v2): if sealed/KILL_LOG.json exists, the kill is STICKY - verdict is FAILS and evaluation
    uses the logged keys (a late backfill of an earlier positive session cannot undo it). Otherwise compute kill_walk and,
    on a first crossing, write the log once. Returns kill, kill_at_trade, min_cum, sticky, keys, eval_trades."""
    p = pathlib.Path(root) / "sealed" / "KILL_LOG.json"
    by = {key(t): t for t in canonical(trades)}
    if p.exists():
        log = json.loads(p.read_text())
        keys = list(log["keys"])
        ev = [by[k] for k in keys if k in by]
        return dict(kill=True, kill_at_trade=log["kill_at_trade"], min_cum=log.get("cum_R_at_crossing"),
                    sticky=True, keys=keys, keys_missing=[k for k in keys if k not in by],
                    eval_trades=ev, log=log)
    k = kill_walk(trades)
    log = kill_log_once(trades, k, root, at or now_utc()) if k["kill"] else None
    if k["kill"]:
        c = canonical(trades)[:k["kill_at_trade"]]
        return dict(k, sticky=False, keys=[key(t) for t in c], keys_missing=[], eval_trades=c, log=log)
    return dict(k, sticky=False, keys=None, keys_missing=[], eval_trades=canonical(trades)[:N_DECISION], log=None)


def key(t: dict) -> str:
    return f"{t['date']}|{t['instrument']}|{t['session']}"


def futility_frozen(trades: list[dict], root: pathlib.Path) -> dict | None:
    """CASSANDRA condition 4 (H015b v2): the first time counted N reaches 200 the 200 row keys are written ONCE to
    sealed/FUTILITY_SET.json (never overwritten; in sealed/ because it carries an R-derived bound) and futility is evaluated
    on exactly that set; a later backfill that changes the canonical first 200 is reported as a reshuffle, never used."""
    c = canonical(trades)
    if len(c) < FUTILITY_AT:
        return None
    p = pathlib.Path(root) / "sealed" / "FUTILITY_SET.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    cur = [key(t) for t in c[:FUTILITY_AT]]
    if not p.exists():
        f = futility(c)
        p.write_text(json.dumps(dict(frozen_at_utc=now_utc().isoformat(timespec="seconds"), keys=cur,
                                     ub_one_sided_975=f["ub_one_sided_975"], fails=f["fails"]), indent=1) + "\n")
    fz = json.loads(p.read_text())
    by = {key(t): t for t in c}
    missing = [k for k in fz["keys"] if k not in by]
    if missing:
        return dict(n=FUTILITY_AT, frozen_keys_missing=missing, fails=fz["fails"], ub_one_sided_975=fz["ub_one_sided_975"],
                    reshuffle=sorted(set(cur) ^ set(fz["keys"])), note="evaluated result frozen at first N=200")
    v = cluster_boot([by[k] for k in fz["keys"]])
    return dict(n=FUTILITY_AT, ub_one_sided_975=v[UB975_INDEX], fails=v[UB975_INDEX] < FUTILITY_BAR, frozen_set=str(p),
                reshuffle=sorted(set(cur) ^ set(fz["keys"])))


def book_replay(trades: list[dict], pooled: bool = True) -> dict:
    """Running paper book CO-REPORT (never binding): RunningBook(max_trade_risk_pct, reset = config drawdown_reset) replayed
    over the binding tickets in entry-time order; the risk gate's book checks (daily loss / drawdown + risk_pct > cap) are
    applied exactly as ftn.os.mint_draft.risk_gate does with a running book. pooled=False -> one book per instrument."""
    F = ftn(); caps = F["cfg"]   # load_config flattens risk_caps (pinned ftn/config.yaml)
    rp, dl_cap, dd_cap = float(caps["max_trade_risk_pct"]), float(caps["max_daily_loss_pct"]), float(caps["max_portfolio_dd_pct"])
    reset = caps["drawdown_reset"]
    groups = {"pooled": list(trades)} if pooled else {i: [t for t in trades if t["instrument"] == i] for i in INSTS}
    out = {}
    for g, ts in groups.items():
        bk = F["book"].RunningBook(risk_pct=rp, reset=reset)
        taken, blocked = [], {"daily_loss_cap": 0, "max_drawdown_cap": 0}
        for t in sorted(ts, key=lambda t: (t["entry_time"], INSTS.index(t["instrument"]))):
            et = dt.datetime.fromisoformat(t["entry_time"]); stt = bk.state(et)
            if stt["daily_loss_pct"] + rp > dl_cap:
                blocked["daily_loss_cap"] += 1; bk.blocked(et, "daily_loss_cap"); continue
            if stt["drawdown_pct"] + rp > dd_cap:
                blocked["max_drawdown_cap"] += 1; bk.blocked(et, "max_drawdown_cap"); continue
            taken.append(t); bk.record(dt.datetime.fromisoformat(t["exit_time"]), float(t["R"]))
        eq = peak = 100.0; mdd = 0.0
        for t in sorted(taken, key=lambda t: t["exit_time"]):
            eq *= 1 + float(t["R"]) * rp / 100.0; peak = max(peak, eq); mdd = max(mdd, 100 * (peak - eq) / peak)
        rs = [float(t["R"]) for t in taken]
        out[g] = dict(n_taken=len(taken), n_blocked=blocked, tickets_lost=len(ts) - len(taken),
                      mean_R=mean(rs) if rs else None, total_R=sum(rs), final_equity_pct=eq, max_dd_pct_no_reset=mdd,
                      reset=reset, events=bk.events, taken_keys=[key(t) for t in taken])
    return out


def foil_with_n(bid, ask, trades: list[dict], inst: str, n: int = N_FOIL, seed: int = SEED) -> list[tuple]:
    """ftn.research.score.foil with the correct-side sim (same rng sequence) returning (mean, n_not_none, sum, stale) where
    stale = draws whose entry minute lacks the exact t-1m BID or ASK bar (DATA K6(iii): the pinned foil may take stale
    entries; logged per replicate, the binding foil method is unchanged)."""
    F = ftn(); KZ_ = F["kl"].KILLZONES; sl = slip(inst)
    rng = random.Random(seed); out = []
    for _ in range(n):
        rs = []; stale = 0
        for tr in trades:
            d = dt.date.fromisoformat(tr["date"]); a, b = KZ_[tr["session"]]
            mins = rng.randrange(int((dt.datetime.combine(d, b) - dt.datetime.combine(d, a)).total_seconds() // 60))
            et = dt.datetime.combine(d, a) + dt.timedelta(minutes=mins + 1)
            px = bid.close_at(et); side = rng.choice(("buy", "sell")); risk = float(tr["risk_pts"])
            stale += int(not all(entry_bars(bid, ask, et)))
            stop = px - risk if side == "buy" else px + risk
            r = F["out"].simulate_both(bid, ask, et, px, stop, side, sl)["R"]
            if r is not None:
                rs.append(r)
        out.append((mean(rs) if rs else 0.0, len(rs), sum(rs), stale))
    return out


# ------------------------------------------------------------------ report
def cleared(root: pathlib.Path) -> dict:
    out = {}
    for f in ("DATA_CERTIFIED.json", "CASSANDRA_CLEARED.json"):
        p = pathlib.Path(root) / f
        try:
            out[f] = json.loads(p.read_text()).get("harness_sha256") == harness_digest()
        except Exception:
            out[f] = False
    return out


def full_series(store: duka.Store, inst: str, side: str, days: list[dt.date]):
    want = sorted({x for d in days for x in (utc_days_for(d) if side == "BID" else session_utc_days(d))})
    texts = [store.csv_text(inst, side, x) for x in want if store.meta(inst, side, x)]
    return series_from_csv_texts(texts, inst, ny(max(days), 17))


def suspension(lat: dict, root: pathlib.Path) -> dict:
    by = {}
    for (ds, _, _), r in lat.items():
        by.setdefault(ds, set()).add(r["status"])
    since, streak = None, []
    for ds in sorted(by):
        st = by[ds]
        if "feed_suspended" in st:
            since = since or ds; break
        if st and st <= FEED_GAP_DAY:
            streak.append(ds)
            if len(streak) > SUSPEND_AFTER:
                since = streak[0]; break
        elif st & {*SCORED, "not_trading_day", "context_gap"}:
            streak = []
    res = None
    p = pathlib.Path(root) / "FEED_RESUMED.json"
    if since and p.exists():
        try:
            res = json.loads(p.read_text()).get("resume_from")
        except Exception:
            res = None
    return dict(since=since, resume_from=res, suspended=bool(since and not res))


def counted_rows(led: Ledger) -> list[dict]:
    lat = led.latest(); susp = suspension(lat, led.root)
    return [r for r in lat.values() if r["status"] == "trade" and r["counted"] == "True"
            and not (susp["since"] and r["date"] >= susp["since"] and not (susp["resume_from"] and r["date"] >= susp["resume_from"]))]


def counted_trades(led: Ledger) -> list[dict]:
    outs = {(o["date"], o["instrument"], o["session"]): o for o in led.outcomes()}
    tr = []
    for r in counted_rows(led):
        o = outs[(r["date"], r["instrument"], r["session"])]
        t = dict(r, **{k: o.get(k) for k in ("R", "exit", "risk_pts", "exit_time", "R_slip2x", "R_flatcost", "one_sided_exit_minutes",
                                               "bid_only_minutes", "ask_only_minutes", "R_conservative", "exit_conservative")})
        t["R"] = float(t["R"]); t["risk_pts"] = float(t["risk_pts"])
        tr.append(t)
    return canonical(tr)


def h015b_overlap(tr: list[dict]) -> dict:
    """The prereg's H015b overlap co-report is NOT computed: CASSANDRA C2 quarantines the H015b data directory (this harness
    never reads it) and H015b is WITHDRAWN-PRE-DATA with zero rows. Burned-window overlap is disclosed in the prereg."""
    return dict(available=False, n_h016b=len(tr), note="H015b directory quarantined (CASSANDRA C2); H015b withdrawn, 0 rows")


def spread_report(store, rows) -> dict:
    """DATA monthly monitor: killzone ASK-BID close spread per instrument-month over every scored session (no R), with
    the 1.1 / 0.5 median flag and the crossed-bar count (any of O/H/L/C with BID > ASK)."""
    by, crossed = {}, {}
    for t in rows:
        d = dt.date.fromisoformat(t["date"]); inst = t["instrument"]; a, b = KZ[t["session"]]
        days = session_utc_days(d)
        if not all(store.meta(inst, s, x) for s in SIDES for x in days):
            continue
        bid = series_from_csv_texts([store.csv_text(inst, "BID", x) for x in days], inst, ny(d, 17))
        ask = series_from_csv_texts([store.csv_text(inst, "ASK", x) for x in days], inst, ny(d, 17))
        bm = {bid.t[i]: i for i in bid.window(ny(d, a), ny(d, b))}
        mk_ = (inst, t["date"][:7])
        for i in ask.window(ny(d, a), ny(d, b)):
            j = bm.get(ask.t[i])
            if j is not None:
                by.setdefault(mk_, []).append(ask.c[i] - bid.c[j])
                crossed[mk_] = crossed.get(mk_, 0) + int(bid.o[j] > ask.o[i] or bid.h[j] > ask.h[i] or bid.l[j] > ask.l[i]
                                                         or bid.c[j] > ask.c[i])
    return {f"{i} {m}": dict(median=median(v), n=len(v), crossed_bars=crossed.get((i, m), 0), flag=median(v) > SPREAD_FLAG[i])
            for (i, m), v in sorted(by.items())}


def verdict(rep, n, k, fu) -> str:
    if k["kill"]:
        sticky = " [sticky: sealed/KILL_LOG.json]" if k.get("sticky") else ""
        return f"FAILS (kill: pooled cumulative R <= {KILL_R}R at trade {k['kill_at_trade']}{sticky})"
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
    if not all(crit):
        return f"FAILS (pass criteria at N={N_DECISION}: {crit})"
    return "PASSES (unadjusted, fill-fragile)" if (rep.get("fill_fragility") or {}).get("verdict_flips") else "PASSES (unadjusted)"


def criteria(tr: list[dict], foil_means: list[float] | None, root: pathlib.Path | None = None,
             sticky: bool = False) -> dict:
    """The six binding pass criteria + kill + futility outcome for a trade list (canonical; fragility co-report).
    sticky=True (binding base, CASSANDRA F1/F5): use sealed/KILL_LOG.json and sealed/FUTILITY_SET.json when present.
    sticky=False (perturbed legs): recompute kill_walk / futility on the perturbed trades themselves."""
    c = canonical(tr)
    if sticky and root is not None:
        ks = kill_sticky(c, root)
        ev = ks["eval_trades"]; k_kill = ks["kill"]
        fu = futility_frozen(ev, root)
    else:
        k = kill_walk(c)
        ev = c[:k["kill_at_trade"]] if k["kill"] else c[:N_DECISION]
        k_kill = k["kill"]; fu = futility(ev)
    rs = [float(t["R"]) for t in ev]; n = len(rs)
    if not n:
        return dict(n=0, kill=k_kill, futility_fails=None, crit=None, mean_R=None)
    per = {i: [float(t["R"]) for t in ev if t["instrument"] == i] for i in INSTS}
    top = sorted(rs, reverse=True); kk = max(1, n // 100)
    p25 = {i: sorted(float(t["risk_pts"]) for t in ev if t["instrument"] == i)[len(per[i]) // 4] for i in INSTS if per[i]}
    big = [float(t["R"]) for t in ev if float(t["risk_pts"]) >= p25.get(t["instrument"], 0)]
    m = mean(rs)
    crit = [m >= 0.10, binding_bound(ev)["lb_one_sided_95"] > 0,
            (100.0 * sum(1 for x in foil_means if x < m) / len(foil_means) >= 95.0) if foil_means else None,
            all(per[i] and mean(per[i]) > 0 for i in INSTS), (mean(top[kk:]) if n > kk else -1) > 0, (mean(big) if big else -1) > 0]
    return dict(n=n, mean_R=m, per_instrument={i: mean(v) if v else None for i, v in per.items()}, kill=k_kill,
                futility_fails=(fu or {}).get("fails"), crit=crit)


def _shift(series, d: float):
    return type(series)(series.symbol, series.t, [x + d for x in series.o], [x + d for x in series.h],
                        [x + d for x in series.l], [x + d for x in series.c], getattr(series, "source", "shifted"))


def fragility_series(store, inst: str, d: dt.date):
    """BID context (utc_days_for(d)) + every ASK day file this harness has stored for UTC days d-31..d (the session's own
    ASK days always; earlier ones exist for previously scored sessions). Used by the one-sided-exit leg so DATA's p95
    floor can use 20 prior sessions when available (else its documented 'p95_session' fallback) and by fill_fragility."""
    bd = [x for x in utc_days_for(d) if store.meta(inst, "BID", x)]
    ad = [d - dt.timedelta(days=k) for k in range(31, -1, -1)]
    ad = [x for x in ad if store.meta(inst, "ASK", x)]
    for side, days in (("BID", bd), ("ASK", ad)):
        for x in days:
            store.check_own(inst, side, x)
    return (series_from_csv_texts([store.csv_text(inst, "BID", x) for x in bd], inst, ny(d, 17)),
            series_from_csv_texts([store.csv_text(inst, "ASK", x) for x in ad], inst, ny(d, 17)))


def session_series(store: duka.Store, inst: str, d: dt.date):
    """BID and ASK for the session's UTC days d-1, d only (enough for the entry bar and the exit loop)."""
    days = session_utc_days(d)
    return (series_from_csv_texts([store.csv_text(inst, "BID", x) for x in days], inst, ny(d, 17)),
            series_from_csv_texts([store.csv_text(inst, "ASK", x) for x in days], inst, ny(d, 17)))


TICK = 0.001
# CASSANDRA C3: the full registered set. "+" = the level moves AWAY from the entry (wider stop / farther target), "-" =
# TOWARDS it. trigger_*: only the trigger level(s) move; the planned risk (R denominator), the registered 2R target (for a
# stop-only shift) and the entry fill are HELD; a triggered exit fills at the shifted level exactly as simulate_both fills
# (stop: min/max(level, open) -/+ stop slip; target: level -/+ limit slip). recompute_*: CASSANDRA's probe variant, the
# stop itself moves and the PINNED simulate_both recomputes risk and the 2R target. ask_*: all ASK O/H/L/C shifted.
# min_risk_*: re-gating. conservative_one_sided_exit: DATA's reference conservative() (binding fragility leg).
PERTURBATIONS = tuple(
    [(f"trigger_{w}_{sg}{lab}", dict(kind="trigger", which=w, delta=(1 if sg == "+" else -1) * d))
     for w in ("stop", "target", "both") for sg in ("+", "-") for d, lab in ((0.1, "0.1"), (TICK, "1tick"))]
    + [(f"recompute_stop_{sg}{lab}", dict(kind="recompute", delta=(1 if sg == "+" else -1) * d))
       for sg in ("+", "-") for d, lab in ((0.1, "0.1"), (TICK, "1tick"))]
    + [("ask_+0.1", dict(kind="ask", delta=0.1)), ("ask_-0.1", dict(kind="ask", delta=-0.1)),
       ("min_risk_+0.25", dict(kind="min_risk", delta=FRAG_DELTA)), ("min_risk_-0.25", dict(kind="min_risk", delta=-FRAG_DELTA)),
       ("conservative_one_sided_exit", dict(kind="conservative"))])


def sim_trigger(bid, ask, et: dt.datetime, entry: float, stop: float, side: str, slip_: dict, d_stop: float = 0.0,
                d_tgt: float = 0.0, target_r: float = 2.0) -> dict:
    """simulate_both (pinned logic, line for line) with trigger-only shifts: stop level moved d_stop AWAY from the entry,
    target level moved d_tgt AWAY from the entry; planned risk and the entry fill held. d_stop = d_tgt = 0 is exactly the
    pinned simulate_both (asserted on all 258 burned trades by the tests)."""
    sl = dict(slip_)
    risk = (entry - stop) if side == "buy" else (stop - entry)
    if risk <= 0:
        return {"R": None, "exit": "invalid_stop"}
    tgt = entry + target_r * risk if side == "buy" else entry - target_r * risk
    st_ = stop - d_stop if side == "buy" else stop + d_stop
    tg_ = tgt + d_tgt if side == "buy" else tgt - d_tgt
    ib, ia = bid.idx(et) - 1, ask.idx(et) - 1
    if ib < 0 or ia < 0:
        return {"R": None, "exit": "no_entry_bar"}
    fill_in = ask.c[ia] + sl["market"] if side == "buy" else bid.c[ib] - sl["market"]
    end = dt.datetime.combine(et.date(), dt.time(16, 0))
    how, xp, xt, last = "time", None, None, None
    for i in bid.window(et, end):
        j = ask.idx(bid.t[i])
        if j >= len(ask.t) or ask.t[j] != bid.t[i]:
            continue
        if side == "buy":
            if bid.l[i] <= st_:
                xp, how = min(st_, bid.o[i]) - sl["stop"], "stop"
            elif bid.h[i] > tg_:
                xp, how = tg_ - sl["limit"], "target"
        else:
            if ask.h[j] >= st_:
                xp, how = max(st_, ask.o[j]) + sl["stop"], "stop"
            elif ask.l[j] < tg_:
                xp, how = tg_ + sl["limit"], "target"
        if xp is not None:
            xt = bid.t[i]
            break
        last = (i, j)
    if xp is None:
        if last is None:
            return {"R": None, "exit": "no_bars"}
        i, j = last
        xp = (bid.c[i] - sl["market"]) if side == "buy" else (ask.c[j] + sl["market"])
        xt = bid.t[i]
    pnl = (xp - fill_in) if side == "buy" else (fill_in - xp)
    return {"R": pnl / risk, "exit": how, "risk_pts": risk, "fill_in": fill_in, "fill_out": xp, "exit_time": xt.isoformat()}


def perturbed_outcome(bid, ask, t: dict, kw: dict, F=None) -> dict:
    """One trade under one non-gating perturbation (trigger / recompute / ask / conservative)."""
    F = F or ftn(); et = dt.datetime.fromisoformat(t["entry_time"]); e, st_ = float(t["entry"]), float(t["stop"])
    sd, sl = t["side"], slip(t["instrument"]); k = kw["kind"]
    if k == "trigger":
        w, d = kw["which"], kw["delta"]
        return sim_trigger(bid, ask, et, e, st_, sd, sl, d_stop=d if w in ("stop", "both") else 0.0,
                           d_tgt=d if w in ("target", "both") else 0.0)
    if k == "recompute":
        st2 = st_ + (kw["delta"] if sd == "sell" else -kw["delta"])
        return F["out"].simulate_both(bid, ask, et, e, st2, sd, sl)
    if k == "ask":
        return F["out"].simulate_both(bid, _shift(ask, kw["delta"]), et, e, st_, sd, sl)
    if k == "conservative":
        return one_sided.conservative(bid, ask, et, e, st_, sd, sl)
    raise ValueError(k)


def fill_fragility(store, tr: list[dict], cands: list[dict], foil_means: list[float] | None,
                   root: pathlib.Path | None = None) -> dict:
    """Prereg fill_fragility_co_report (CASSANDRA F7 + C3) and the binding one-sided-exit leg (CASSANDRA/ORION 2026-10-04).
    Binding base uses sticky kill + frozen futility (CASSANDRA F1/F5). Each perturbed leg recomputes kill/futility on its
    own trades. For each PERTURBATIONS entry: n, pooled / per-instrument mean, exit flips, dropped_R_none (F5), the six
    pass criteria, kill and futility. verdict_flips = any perturbation changes any criterion, kill or futility ->
    'PASSES (unadjusted, fill-fragile)', SURVIVES blocked."""
    F = ftn(); base = criteria(tr, foil_means, root=root, sticky=True); cache = {}

    def ser(t):
        k2 = (t["instrument"], t["date"])
        if k2 not in cache:
            cache[k2] = fragility_series(store, t["instrument"], dt.date.fromisoformat(t["date"]))
        return cache[k2]

    mr = {i: F["ins"].spec(i).min_risk for i in INSTS}
    thr = [key(t) for t in [*tr, *cands] if t.get("dist_pts") not in (None, "")
           and abs(float(t["dist_pts"]) - mr[t["instrument"]]) <= FRAG_DELTA]
    out = dict(binding=base, min_risk=mr, threshold_tickets_within_0_25=len(thr), threshold_keys=thr, perturbations={})
    flips_any = False
    for name, kw in PERTURBATIONS:
        new, ex_flips, dropped = [], 0, 0
        if kw["kind"] == "min_risk":
            dm = kw["delta"]
            new = [t for t in tr if float(t.get("dist_pts") or t["risk_pts"]) >= mr[t["instrument"]] + dm]
            for t in cands:
                if float(t["dist_pts"]) >= mr[t["instrument"]] + dm:
                    o = F["out"].simulate_both(*ser(t), dt.datetime.fromisoformat(t["entry_time"]), float(t["entry"]),
                                               float(t["stop"]), t["side"], slip(t["instrument"]))
                    if o["R"] is None:
                        dropped += 1
                    else:
                        new.append(dict(t, R=o["R"], exit=o["exit"], risk_pts=o["risk_pts"]))
        else:
            for t in tr:
                o = perturbed_outcome(*ser(t), t, kw, F)
                if o["R"] is None:
                    dropped += 1
                    continue
                ex_flips += int(o["exit"] != t["exit"])
                new.append(dict(t, R=o["R"], exit=o["exit"]))
        c = criteria(new, foil_means, sticky=False)
        fl = (c["crit"] != base["crit"]) or (c["kill"] != base["kill"]) or (c["futility_fails"] != base["futility_fails"])
        flips_any |= fl
        out["perturbations"][name] = dict(c, exit_flips=ex_flips, dropped_R_none=dropped, verdict_flip=fl)
    out["verdict_flips"] = flips_any
    out["one_sided_exit_leg_flips"] = out["perturbations"]["conservative_one_sided_exit"]["verdict_flip"]
    return out


def cmd_report(root=None, foil_n: int = N_FOIL) -> dict:
    led = Ledger(root); lat = led.latest()
    st = {}
    for r in lat.values():
        st[r["status"]] = st.get(r["status"], 0) + 1
    susp = suspension(lat, led.root)
    counted = counted_rows(led)
    blocks = {}
    for r in lat.values():
        if r.get("block_reason"):
            k2 = f"{r['instrument']} {r['session']} {r['block_reason']}"; blocks[k2] = blocks.get(k2, 0) + 1
    sm = {i: [float(r["spread_measured"]) for r in lat.values() if r["instrument"] == i and r.get("spread_measured")] for i in INSTS}
    ent = {}
    for r in lat.values():
        if r["status"] in ("feed_gap_entry", "no_r_ticket"):
            k3 = f"{r['status']} {r['instrument']} {r['session']}" + (f" {r['not_counted_reasons']}" if r["status"] == "no_r_ticket" else "")
            ent[k3] = ent.get(k3, 0) + 1
    rep = dict(lead=LEAD, feed_disclosure=FEED_DISCLOSURE, holiday_source=HOLIDAY_SOURCE, status_counts=st,
               n_counted=len(counted), entry_minute_and_no_r_counts=ent,
               binding_N=N_DECISION, kill_R=KILL_R, futility_at=FUTILITY_AT, risk_blocks=blocks,
               spread_measured_at_signal={i: dict(n=len(v), median=median(v) if v else None,
                                                  p90=sorted(v)[int(0.9 * (len(v) - 1))] if v else None) for i, v in sm.items()},
               ask_gap_minutes_total=sum(int(r.get("ask_gap_minutes") or 0) for r in lat.values()),
               dropped_sessions=sorted((r["date"], r["instrument"], r["session"], r["status"]) for r in lat.values()
                                       if r["status"] not in ("trade", "no_trade")),
               calendar_identity_failures=sum(1 for r in lat.values() if r.get("calendar_identity_ok") == "False"),
               registration=registration_status(), clearance=cleared(led.root), feed_suspension=susp,
               harness_version=HARNESS_VERSION)
    mon_store = OwnStore(led.root, get=lambda u: (_ for _ in ()).throw(RuntimeError("report never downloads")))
    rep["data_monitor_monthly"] = spread_report(mon_store, [r for r in lat.values() if r["status"] in SCORED])
    if not all(rep["clearance"].values()):
        rep["R"] = "SEALED: DATA_CERTIFIED.json and CASSANDRA_CLEARED.json with this harness_sha256 are required before any R is shown"
        return rep
    tr = counted_trades(led)
    ks = kill_sticky(tr, led.root)                              # F1: sticky; logged kill forces FAILS
    k = {x: ks[x] for x in ("kill", "kill_at_trade", "min_cum", "sticky")}
    tr_eval = ks["eval_trades"]
    rep["kill"] = k
    if ks["sticky"]:
        rep["kill_log"] = ks["log"]
        rep["kill_keys_missing"] = ks["keys_missing"]
    fu = futility_frozen(tr_eval, led.root)
    rep["futility"] = fu
    if fu:
        rep["futility_note"] = "futility catches a zero edge only ~8.2% of the time (simulation); passing it is NOT evidence"
    outs = {(o["date"], o["instrument"], o["session"]): o for o in led.outcomes()}
    gf = [t for t in tr_eval if str(t.get("gap_flag")) == "True"]
    rep["gap_flag_co_report"] = dict(flagged_n=len(gf), flagged_sum_R=sum(t["R"] for t in gf),
                                     headline_excl_flagged_non_binding=dict(
                                         n=len(tr_eval) - len(gf),
                                         mean_R=mean([t["R"] for t in tr_eval if t not in gf]) if len(tr_eval) > len(gf) else None))
    ctxf = [t for t in tr_eval if not (t.get("context_missing_days") or t.get("context_frozen_incomplete"))]
    rep["data_cond4_excl_context_disclosed_non_binding"] = dict(n=len(ctxf), mean_R=mean([t["R"] for t in ctxf]) if ctxf else None)
    ss = [o for (k2, o) in outs.items() if lat.get(k2, {}).get("status") == "short_session"]
    rep["short_session_dropped_trades"] = dict(n=len(ss), sum_R=sum(float(o["R"]) for o in ss))
    per = {i: [t for t in tr_eval if t["instrument"] == i] for i in INSTS}
    rep["per_instrument"] = {i: dict(n=len(x), mean_R=mean([t["R"] for t in x]) if x else None) for i, x in per.items()}
    rs = [t["R"] for t in tr_eval]; n = len(rs); pm = None
    if n:
        bb = binding_bound(tr_eval)
        S = ftn()["stats"]
        rep["pooled"] = dict(n=n, mean_R=mean(rs), binding_cluster_bound=bb,
                             trade_level_co_report_lb95=S.boot_ci(rs, alpha=0.10)[0] if n > 1 else None)
        top = sorted(rs, reverse=True); kk = max(1, n // 100)
        p25 = {i: sorted(t["risk_pts"] for t in per[i])[len(per[i]) // 4] for i in INSTS if per[i]}
        big = [t["R"] for t in tr_eval if t["risk_pts"] >= p25.get(t["instrument"], 0)]
        rep["robustness"] = dict(ex_top1pct=mean(top[kk:]) if n > kk else None, ex_small_stop=mean(big) if big else None)
        f2 = [float(t["R_slip2x"]) for t in tr_eval if t.get("R_slip2x") not in (None, "")]
        ff = [float(t["R_flatcost"]) for t in tr_eval if t.get("R_flatcost") not in (None, "")]
        rc = [float(t["R_conservative"]) for t in tr_eval if t.get("R_conservative") not in (None, "")]
        rep["pooled"]["mean_R_conservative_one_sided_exit"] = mean(rc) if rc else None
        rep["one_sided_exit_co_report"] = dict(version=one_sided.CONSERVATIVE_EXIT_VERSION, flagged_n=sum(1 for t in tr_eval if int(t.get("one_sided_exit_minutes") or 0) > 0),
                                               minutes_total=sum(int(t.get("one_sided_exit_minutes") or 0) for t in tr_eval),
                                               changed_n=sum(1 for t in tr_eval if t.get("exit_conservative") != t.get("exit")),
                                               mean_R_conservative=mean(rc) if rc else None, n_conservative=len(rc))
        rep["cost_ladder"] = dict(correct_side_x1_binding=mean(rs), correct_side_slip_x2=mean(f2) if f2 else None,
                                  flat_cost_co_report=mean(ff) if ff else None)
        rep["running_book_co_report"] = dict(pooled=book_replay(tr_eval, pooled=True)["pooled"],
                                             per_instrument=book_replay(tr_eval, pooled=False))
        for v in [rep["running_book_co_report"]["pooled"], *rep["running_book_co_report"]["per_instrument"].values()]:
            v.pop("taken_keys", None)
        rep["splits"] = {k2: {str(v): (lambda xs: dict(n=len(xs), mean_R=mean(xs) if xs else None))([t["R"] for t in tr_eval if f(t) == v])
                              for v in vals} for k2, f, vals in
                         (("side", lambda t: t["side"], ("buy", "sell")), ("session", lambda t: t["session"], SESSIONS),
                          ("london_dst_mismatch", lambda t: (t["session"], t["dst_mismatch_week"]),
                           (("london", "True"), ("london", "False"))))}
        store = OwnStore(led.root, get=lambda u: (_ for _ in ()).throw(RuntimeError("report never downloads")))
        days = sorted({dt.date.fromisoformat(t["date"]) for t in tr_eval})
        reps = None
        for i in INSTS:
            if not per[i]:
                continue
            fr = foil_with_n(full_series(store, i, "BID", days), full_series(store, i, "ASK", days), per[i], i, n=foil_n)
            reps = fr if reps is None else [(0, a[1] + b[1], a[2] + b[2], a[3] + b[3]) for a, b in zip(reps, fr)]
        pm = [x[2] / x[1] if x[1] else 0.0 for x in reps]
        ns = sorted(x[1] for x in reps)
        rep["foil"] = dict(pct=100.0 * sum(1 for m in pm if m < mean(rs)) / len(pm), median=sorted(pm)[len(pm) // 2],
                           n_per_replicate=dict(min=ns[0], median=ns[len(ns) // 2], max=ns[-1], trades=n),
                           stale_entry_draws_per_replicate=(lambda z: dict(min=z[0], median=z[len(z) // 2], max=z[-1]))(sorted(x[3] for x in reps)))
        rep["h015b_overlap"] = h015b_overlap(tr_eval)
        cands = [dict(r) for r in lat.values() if r["status"] == "no_trade" and r.get("regate_candidate") == "True"
                 and not (susp["since"] and r["date"] >= susp["since"] and not (susp["resume_from"] and r["date"] >= susp["resume_from"]))]
        rep["fill_fragility"] = fill_fragility(store, tr, cands, pm, root=led.root)
    rep["verdict"] = verdict(rep, n, k, fu)
    if k["kill"] and "kill_log" not in rep:
        rep["kill_log"] = ks["log"] or kill_log_once(tr, k, led.root, now_utc())
    p_ = rep.get("pooled", {}).get("binding_cluster_bound", {}).get("p_one_sided")
    rep["family_rule"] = dict(
        text=("PASS is 'PASSES (unadjusted)'; SURVIVES only if p_one_sided clears Holm across the active 3-test family "
              "H013/H014/H016b (research/protocols/FORWARD_FAMILY_RULE_2026-10-04.md, main ebfa83b, 'any later forward test' "
              "clause): 0.0167 / 0.025 / 0.05, smallest p first. ORION ruling (a), 2026-10-04: unfinished, killed or futile "
              "tests enter Holm at p=1; Holm is re-run as each test completes; a granted SURVIVES is never revoked. ORION ruling "
              "(b) with CASSANDRA's stricter points (correct-side co-report must pass; written check needs a non-flipping "
              "fill-fragility co-report). A 'fill-fragile' pass cannot become SURVIVES without replication under a new ID. "
              "Kill and futility are never relaxed. H015b is WITHDRAWN-PRE-DATA; H015b and H016b are REV variants on the same "
              "instruments and sessions, so a pass in one is NOT independent replication of the other"),
        family=FAMILY, holm_thresholds=HOLM_3, p_one_sided=p_,
        holm_note="this harness knows only H016b's p; the family Holm step (others at p=1 until they complete) is ORION's")
    return rep


# ------------------------------------------------------------------ certification helpers
BURNED_TAPE = "/workspace/ftn-demo-output/data"
# DATA K10: DECOMPRESSED-content sha256 of the canonical burned export (gzip bytes carry a header timestamp)
BURNED_CONTENT_SHA256 = {
    "US100_1m_ask.csv.gz": "fcc3c8773fcfbf96d52f44445d22948ea97f953b1d1325e835b53bd08715b18f",
    "US100_1m_bid.csv.gz": "6afa31304cddff11b841e60d280043a8ea3b79954e445657959a0a5389f3f80f",
    "US500_1m_ask.csv.gz": "ff63783f3fdbd75098b2d0928caf6bd7bef2f21f9e31022ff20b6e739d958504",
    "US500_1m_bid.csv.gz": "9d68787c5804d15c423d8ec4289a48c9a30428461743e0edcada92ac6502ef92"}


def content_sha256(path) -> str:
    import gzip
    return hashlib.sha256(gzip.decompress(pathlib.Path(path).read_bytes())).hexdigest()


def burned_trades(inst: str) -> list[dict]:
    return list(csv.DictReader(open(REPO / f"research/evidence/quant/FTN_M9_TRADES_{inst}_base_2026-10-04_h016_fixed_rev_burned.csv")))


def _slice(full, lo_t, hi_t, src):
    lo, hi = full.idx(lo_t), full.idx(hi_t)
    return type(full)(full.symbol, full.t[lo:hi], full.o[lo:hi], full.h[lo:hi], full.l[lo:hi], full.c[lo:hi], src)


def repro_burned(tape_dir: str = BURNED_TAPE, every: int = 1, insts=INSTS, calendar_check: bool = False) -> dict:
    """Per-session path on the BURNED canonical Dukascopy BID/ASK export (2025-08-24 18:00 -> 2026-09-25 17:00 NY) vs the
    committed H016 burned trades CSVs (entry_rule off: the CSVs predate it; the H016b filter exclusions are listed): BID sliced to [d-45d, d 17:00), ASK to the session's UTC days d-1, d, as forward."""
    B = ftn()["bars"]; res = {}
    for f, h in BURNED_CONTENT_SHA256.items():
        if any(f.startswith(i) for i in insts) and content_sha256(f"{tape_dir}/{f}") != h:
            raise RuntimeError(f"burned tape {f} content hash differs from DATA's registered content hash")
    for inst in insts:
        fb = B.load_series(f"{tape_dir}/{inst}_1m_bid.csv.gz", inst); fa = B.load_series(f"{tape_dir}/{inst}_1m_ask.csv.gz", inst)
        if max(fb.t[-1], fa.t[-1]).date() > BURNED_END:
            raise RuntimeError("burned tape extends past 2026-09-25: refusing to read it")
        want = {(r["date"], r["session"]): r for r in burned_trades(inst)}
        days = B.trading_days(fb); sel = days[CONTEXT_SESSIONS::every]
        got, mism, excl = {}, [], []
        for d in sel:
            bid = _slice(fb, ny(d - dt.timedelta(days=CONTEXT_DAYS), 0), ny(d, 17), "tape")
            ask = _slice(fa, ask_start_ny(d), ny(d, 17), "tape_ask")
            for r in score_sessions(bid, ask, d, entry_rule=False, calendar_check=calendar_check):
                if r["outcome"] is not None:
                    got[(d.isoformat(), r["session"])] = r
                    r["one_sided"] = one_sided_fields(bid, ask, inst, r, r["outcome"])
                    kz = [len(s.window(ny(d, KZ[r["session"]][0]), ny(d, KZ[r["session"]][1]))) for s in (bid, ask)]
                    why = [x for x, ok in (("feed_gap_entry", r["entry_bar_bid"] and r["entry_bar_ask"]),
                                           (f"kz_bars {kz[0]}/180", kz[0] >= KZ_MIN), (f"kz_bars_ask {kz[1]}/180", kz[1] >= KZ_MIN),
                                           ("exit_bar_bid", exit_bars_ok(bid, d)), ("exit_bar_ask", exit_bars_ok(ask, d)),
                                           ("calendar_identity", r["calendar_identity_ok"] is not False)) if not ok]
                    if why:
                        excl.append((d.isoformat(), r["session"], why))
        cand = {k: v for k, v in want.items() if dt.date.fromisoformat(k[0]) in set(sel)}
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
        osd = [v["one_sided"] for v in got.values()]
        res[inst] = dict(n_harness=len(got), n_csv=len(cand), mean_R=mean(rs) if rs else None, mismatches=mism[:20],
                         n_mismatch=len(mism), h016b_filter_exclusions=excl,
                         one_sided=dict(flagged=sum(1 for x in osd if x["one_sided_exit_minutes"] > 0),
                                        minutes=sum(x["one_sided_exit_minutes"] for x in osd),
                                        conservative_equals_pinned=sum(1 for v in got.values() if v["one_sided"]["R_conservative"] == repr(v["outcome"]["R"])
                                                                       and v["one_sided"]["exit_conservative"] == v["outcome"]["exit"]),
                                        sum_R_conservative=sum(float(x["R_conservative"]) for x in osd), sum_R=sum(rs)))
    return res


REPULL_DAYS = ("2026-02-17", "2026-02-24", "2026-02-26", "2026-03-06", "2026-03-09", "2026-03-12", "2026-03-18", "2026-03-20",
               "2026-03-23", "2026-03-25", "2026-03-27", "2026-04-06", "2026-04-10", "2026-04-14", "2026-04-21", "2026-05-06",
               "2026-05-14", "2026-05-21", "2026-05-26", "2026-05-29", "2026-06-15", "2026-06-26")   # 22 burned session days
MD_RAW = pathlib.Path("/workspace/marketdata/raw/dukascopy")


def burned_only(get):
    """Wrap a datafeed getter: refuse any URL whose UTC day is after BURNED_END (2026-09-25) or before 2025-08-24."""
    def g(u):
        q = u.split("/datafeed/")[1].split("/")
        day = dt.date(int(q[1]), int(q[2]) + 1, int(q[3]))
        if not (dt.date(2025, 8, 24) <= day <= BURNED_END):
            raise RuntimeError(f"repull refuses non-burned day {day}")
        return get(u)
    return g


def md_raw_get(u):
    """Local source: marketdata's native Dukascopy bi5 bytes (the same vendor files), burned days only (via burned_only)."""
    q = u.split("/datafeed/")[1].split("/")
    sym, y, m0, d, f = q[0], int(q[1]), int(q[2]), int(q[3]), q[4]
    pth = MD_RAW / sym / str(y) / f"{y:04d}{m0 + 1:02d}{d:02d}_{f.split('_')[0]}.bi5"
    return pth.read_bytes() if pth.exists() else None


def cmd_repull(outdir: str, mode: str = "network", days=REPULL_DAYS) -> dict:
    """CASSANDRA F8: re-pull BURNED BID+ASK day files through the harness downloader (OwnStore / duka.Store, network by
    default; refuses any day after 2026-09-25), reproduce the burned H016 trades for those session days through the
    forward path (series_pair -> score_sessions), report BID/ASK minute alignment and input hashes."""
    root = pathlib.Path(outdir); guard_root(root)
    get = burned_only(duka.http_get if mode == "network" else md_raw_get)
    store = OwnStore(root, now=lambda: dt.datetime(2026, 10, 4, 12, tzinfo=duka.UTC), get=get,
                     short_ok=lambda day: calendar_status(day) == "holiday")
    want = {inst: {(r["date"], r["session"]): r for r in burned_trades(inst)} for inst in INSTS}
    out = dict(mode=mode, days=list(days), harness_sha256=harness_digest(), per_day=[], mismatches=[])
    for ds in days:
        d = dt.date.fromisoformat(ds)
        for inst in INSTS:
            g = gather(store, inst, d)
            if g["status"] != "ok" or g["not_final"] or g["problems"]:
                out["mismatches"].append((ds, inst, "gather", g.get("not_final"), g.get("problems")[:2] if g.get("problems") else None))
                continue
            sraw, cman, lst = manifest_for(g["metas"], d)
            bid, ask = series_pair(store, inst, d, lst)
            rows = score_sessions(bid, ask, d, entry_rule=False)
            got = {r["session"]: r for r in rows if r["outcome"] is not None}
            for sname in SESSIONS:
                a, b = want[inst].get((ds, sname)), got.get(sname)
                if (a is None) != (b is None):
                    out["mismatches"].append((ds, inst, sname, "presence", a is not None, b is not None)); continue
                if a is None:
                    continue
                for f in ("entry_time", "entry", "stop"):
                    if str(b[f]) != a[f]:
                        out["mismatches"].append((ds, inst, sname, f, a[f], b[f]))
                if repr(b["outcome"]["R"]) != a["R"] or b["outcome"]["exit"] != a["exit"]:
                    out["mismatches"].append((ds, inst, sname, "R/exit", a["R"], repr(b["outcome"]["R"])))
            # alignment over the session window [d-1 18:00, d 17:00) NY and per killzone
            lo, hi = ny(d - dt.timedelta(days=1), 18), ny(d, 17)
            tb = {bid.t[i] for i in bid.window(lo, hi)}; ta = {ask.t[i] for i in ask.window(lo, hi)}
            kz = {sname: [len(x.window(ny(d, KZ[sname][0]), ny(d, KZ[sname][1]))) for x in (bid, ask)] for sname in SESSIONS}
            bm = {bid.t[i]: i for i in bid.window(lo, hi)}
            crossed = sum(1 for j in ask.window(lo, hi) if ask.t[j] in bm and (bid.o[bm[ask.t[j]]] > ask.o[j] or bid.h[bm[ask.t[j]]] > ask.h[j]
                                                                            or bid.l[bm[ask.t[j]]] > ask.l[j] or bid.c[bm[ask.t[j]]] > ask.c[j]))
            sess_files = [x for x in lst if x[0] in {y.isoformat() for y in session_utc_days(d)}]
            raw_eq = []
            for day_, side, b5, cs in sess_files:
                rp = MD_RAW / duka.SYMBOL[inst] / day_[:4] / f"{day_.replace('-', '')}_{side}.bi5"
                raw_eq.append(None if not rp.exists() else hashlib.sha256(rp.read_bytes()).hexdigest() == b5)
            out["per_day"].append(dict(date=ds, instrument=inst, bid_minutes=len(tb), ask_minutes=len(ta), bid_only=len(tb - ta),
                                       ask_only=len(ta - tb), kz_bars_bid_ask=kz, crossed_bars=crossed,
                                       trades=[{k: got[x][k] for k in ("session", "entry_time", "side")} | dict(
                                           entry_bar_bid=got[x]["entry_bar_bid"], entry_bar_ask=got[x]["entry_bar_ask"])
                                           for x in got],
                                       session_files=sess_files, session_raw_sha256=sraw, context_manifest_sha256=cman,
                                       n_context_files=len(lst), bi5_equal_marketdata_raw=raw_eq))
    out["n_files"] = sum(1 for _ in (root / "raw").glob("*/*/*.bi5"))
    out["n_trades_compared"] = sum(len(x["trades"]) for x in out["per_day"])
    out["ok"] = not out["mismatches"]
    return out


def selfcheck() -> dict:
    m = harness_manifest(); bad = verify_pins()
    return dict(pins_ok=not bad, pin_problems=bad, n_pins=len(pins()), tag=TAG, tag_commit=TAG_COMMIT, harness_manifest=m,
                harness_sha256=harness_digest(m), registration=registration_status(), data_dir=str(DATA_ROOT),
                clearance=cleared(DATA_ROOT), first_date=FIRST_DATE.isoformat(), holiday_source=HOLIDAY_SOURCE,
                unpinned_ftn_modules=unpinned_ftn_modules())


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
    elif cmd == "repull":
        print(json.dumps(cmd_repull(a[1], a[2] if len(a) > 2 else "network"), indent=1, default=str))
    else:
        print(json.dumps(selfcheck(), indent=1, default=str))
