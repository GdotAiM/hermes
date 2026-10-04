"""Tests for the H013 forward harness. Run: cd forward-test && .venv/bin/python -m pytest -q tests_h013"""
import json, pathlib, sys, importlib
import numpy as np, pandas as pd, pytest
FT = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(FT))
import h013_harness as H

PREREG = json.load(open(H.HERMES / H.PREREG_PATH))
ARCH = sorted((FT / "raw/forward/archive").glob("CAPITALCOM_US100_1m_fetch_*.csv"))
LEGACY = FT / "forward_log.csv"
LR = H.LR

@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(H, "LOG", tmp_path / "log.csv"); monkeypatch.setattr(H, "ALERTS", tmp_path / "alerts.jsonl")
    monkeypatch.setattr(H, "RAW", tmp_path / "raw"); monkeypatch.setattr(H, "FT", tmp_path)
    return tmp_path

# ---------------- prereg conformance
def test_rule_hashes_match_prereg_and_files():
    assert H.RULE_SHA256 == PREREG["rule_object_sha256"]
    assert H.verify_rule_objects()

def test_engine_settings_match_prereg():
    E1, V1 = H.load_engine(); es = PREREG["engine_settings"]
    assert E1.FILL_THRU == es["FILL_THRU_ticks"] == 1 and E1.TICK == es["tick"]
    H.set_cost(E1, "US100"); assert E1.SLIP == es["SLIP_ticks"] == 3.2 and H.COST["US100"] == es["cost_per_side_pts"]
    assert PREREG["invocation"] == 'best_trade(ctx, "11:00", False, False, True)' and H.INVOCATION == ("11:00", False, False, True)

def test_calendar_matches_prereg():
    h = PREREG["holidays_excluded"]
    assert H.HOLIDAYS_FULL == set(h["full_closures"]) and H.HOLIDAYS_EARLY == set(h["early_closes"]) and H.HOLIDAYS_HIST == set(h["historical_additions"])
    assert H.calendar_status("2026-10-05") == "ok" and H.calendar_status("2026-10-04") == "weekend"
    assert H.calendar_status("2026-12-24") == "holiday_early_close" and H.calendar_status("2026-12-25") == "holiday_full_closure"
    assert H.calendar_status("2025-12-24") == "holiday_historical_exclusion" and H.calendar_status("2028-01-03") == "calendar_not_covered"

def test_feed_is_capitalcom_only():
    assert H.FEED == {"US100": "CAPITALCOM:US100", "US500": "CAPITALCOM:US500"}
    assert PREREG["forward_feed"]["fallback_feeds_allowed_for_counted_rows"] is False
    src = (FT / "tv_final.py").read_text() + (FT / "backfill_tv.py").read_text() + (FT / "h013_harness.py").read_text() + (FT / "h013_live_watch.py").read_text()
    for bad in ('"PEPPERSTONE:', '"OANDA:', "finance.yahoo.com", '"NQ=F"', '"ES=F"'): assert bad not in src

def test_fetch_failure_is_gap_not_fallback(monkeypatch):
    import tv_feed
    calls = []
    def boom(sym, n=500, **k): calls.append(sym); raise RuntimeError("down")
    monkeypatch.setattr(tv_feed, "fetch_tv", boom)
    with pytest.raises(H.FeedError): H.fetch("US100", n=10)
    assert calls == ["CAPITALCOM:US100"]

# ---------------- filters
def _day(d, n_bars, start="07:00"):
    idx = pd.date_range(H.at(d, start), periods=n_bars, freq="1min")
    return pd.DataFrame({"Open": 1.0, "High": 1.5, "Low": 0.5, "Close": 1.0}, index=idx)

def test_min_bar_filter():
    df = _day("2026-10-05", 300); assert H.window_bars(df, "2026-10-05") == (300, [])
    df2 = df.drop(df.index[10:26]); n, miss = H.window_bars(df2, "2026-10-05")
    assert n == 284 and len(miss) == 16 and n < H.MIN_BARS and miss[0] == "07:10"

# ---------------- raw bars + append-only log
def test_save_raw_never_overwrites(sandbox):
    a = _day("2026-10-05", 5); r1, h1 = H.save_raw(a, "US100_2026-10-05"); r1b, h1b = H.save_raw(a, "US100_2026-10-05")
    assert (r1, h1) == (r1b, h1b)
    b = a.copy(); b.iloc[0, 0] = 2.0; r2, h2 = H.save_raw(b, "US100_2026-10-05")
    assert r2 != r1 and h2 != h1 and H.sha256_file(sandbox / r1) == h1 and H.sha256_file(sandbox / r2) == h2

def _replay_frames(d):
    f100 = H.load_raw(ARCH[-1]); f500 = H.load_raw(str(ARCH[-1]).replace("US100", "US500"))
    return {"US100": f100[f100.index <= H.at(d, "16:59")], "US500": f500[f500.index <= H.at(d, "16:59")]}

needs_arch = pytest.mark.skipif(not ARCH, reason="no saved CAPITALCOM archive")

@needs_arch
def test_append_only_and_duplicates(sandbox):
    d = "2026-10-02"; fr = _replay_frames(d); meta = {k: dict(feed="TradingView " + H.FEED[k], fetch_time_sast="t") for k in fr}
    reg = dict(ok=True, main_commit="x", landed_ny=str(H.at("2026-10-01", "00:00")))
    r1 = H.finalize_session(d, "FINAL", fr, meta, reg); before = H.LOG.read_bytes()
    r2 = H.finalize_session(d, "FINAL", fr, meta, reg); after = H.LOG.read_bytes()
    assert after.startswith(before) and len(pd.read_csv(H.LOG)) == 4
    assert r2[0]["duplicate_of_run"] == r1[0]["run_id"] and r2[0]["counted"] is False
    assert r1[0]["raw_sha256"] == r2[0]["raw_sha256"] and r1[0]["raw_file"] == r2[0]["raw_file"]
    assert "before first eligible session" in r1[0]["not_counted_reasons"]
    pd.read_csv(H.LOG).drop(columns=["note"]).to_csv(H.LOG, index=False)
    with pytest.raises(SystemExit): H.finalize_session(d, "FINAL", fr, meta, reg)

@needs_arch
def test_counting_rules(sandbox, monkeypatch):
    """A Monday-style session: live alert before exit + registered before 07:00 -> counted (US100 only)."""
    d = "2026-10-02"; fr = _replay_frames(d); meta = {k: dict(feed="TradingView " + H.FEED[k]) for k in fr}
    monkeypatch.setattr(H, "FIRST_POSSIBLE_SESSION", "2026-10-01")
    E1, V1 = H.load_engine(); res, t = H.evaluate(E1, V1, fr["US100"], d, "US100")
    key = H.trade_key(d, "US100", res["direction"], res["entry"], res["entry_time_ny"])
    exit_sast = pd.Timestamp(res["exit_time_5050_ny"]).tz_convert(H.SAST)
    reg_ok = dict(ok=True, main_commit="x", landed_ny=str(H.at(d, "06:00")))
    H.append_alert(dict(event="FILL", key=key, alert_sast=(exit_sast - pd.Timedelta(seconds=30)).strftime("%Y-%m-%d %H:%M:%S")))
    rows = H.finalize_session(d, "FINAL", fr, meta, reg_ok)
    assert rows[0]["live_alerted"] is True and rows[0]["counted"] is True, rows[0]["not_counted_reasons"]
    assert rows[1]["counted"] is False and "disclosure" in rows[1]["not_counted_reasons"]
    late = dict(reg_ok, landed_ny=str(H.at(d, "08:00")))
    rows = H.finalize_session(d, "BACKFILL", fr, meta, late)
    assert not rows[0]["counted"] and "BACKFILL" in rows[0]["not_counted_reasons"] and "after session start" in rows[0]["not_counted_reasons"]

def test_live_alert_after_exit_does_not_count(sandbox):
    H.append_alert(dict(event="FILL", key="k", alert_sast="2026-10-05 15:20:00"))
    assert H.first_fill_alert("x", "y", "z", 1, "q") is None

def test_registration_pending_on_current_main():
    r = H.registration_status(fetch_remote=False)
    assert r["ok"] is False or r["landed_ny"] is not None

# ---------------- reproduction of the frozen historical run (engine invoked exactly as longrun.py)
def _hist_days(df):
    sys.path.insert(0, str(LR / "scripts"))
    import os; cwd = os.getcwd(); os.chdir(LR)
    try: import longrun as LRUN; days, _ = LRUN.trading_days(df)
    finally: os.chdir(cwd)
    return days

@pytest.mark.parametrize("thru,ref", [(1, "data/trades_cost1x_thru1.csv"), (0, "trades.csv")])
def test_reproduces_longrun_us100(thru, ref):
    E1, V1 = H.load_engine(); E1.FILL_THRU = thru
    df = pd.read_parquet(LR / "data/US100_1m.parquet")[["Open", "High", "Low", "Close"]].astype(float)
    exp = pd.read_csv(LR / ref); exp = exp[(exp.model == "v1 base") & (exp.inst == "US100")].set_index("date")
    try:
        got = {}
        for d in _hist_days(df):
            got[d] = H.evaluate(E1, V1, df, d, "US100", fill_thru=thru)[0]
    finally: E1.FILL_THRU = 1
    tr = {d: r for d, r in got.items() if r["status"] == "trade"}
    assert set(tr) == set(exp[exp.status == "trade"].index)
    for d, r in tr.items():
        e = exp.loc[d]
        assert (r["entry_time_ny"], r["direction"]) == (e.entry_time_ny, e.direction)
        assert abs(r["entry"] - e.entry) < 1e-9 and abs(r["R_5050"] - e.R_5050) < 1e-9

# ---------------- dry-run on recent saved raw data (CAPITALCOM archive fetched 2026-10-04)
@needs_arch
@pytest.mark.parametrize("d", ["2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02"])
def test_dry_run_replay_matches_legacy_at_thru0(d, sandbox):
    """At FILL_THRU=0 the harness reproduces the legacy (pre-registration) v1 rows; at FILL_THRU=1 it is the frozen rule."""
    E1, V1 = H.load_engine(); fr = _replay_frames(d)
    leg = pd.read_csv(LEGACY); leg = leg[(leg.variant == "v1") & (leg.date == d)].set_index("instrument")
    try:
        for nm in ("US100", "US500"):
            r0, _ = H.evaluate(E1, V1, fr[nm], d, nm, fill_thru=0); e = leg.loc[nm]
            assert r0["status"] == e.status
            if r0["status"] == "trade":
                assert (r0["direction"], r0["entry_time_ny"]) == (e.direction, e.entry_time_ny)
                assert abs(r0["entry"] - e.entry) < 1e-9 and abs(r0["R_5050"] - e.R_5050) < 1e-6
    finally: E1.FILL_THRU = 1
    rows = H.finalize_session(d, "REPLAY", fr, {k: dict(feed="replay") for k in fr}, dict(ok=False), dry=True)
    assert not H.LOG.exists() and all(not r["counted"] for r in rows) and all(r["bars_0700_1159"] == 300 for r in rows)

@needs_arch
@pytest.mark.parametrize("d", ["2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02"])
def test_live_watch_is_causal(d):
    """The first fill seen on bars truncated just after the fill bar equals the final first fill (watcher alerts are stable)."""
    E1, V1 = H.load_engine(); fr = _replay_frames(d)
    for nm in ("US100", "US500"):
        full, _ = H.evaluate(E1, V1, fr[nm], d, nm)
        if full["status"] != "trade": continue
        cut = H.at(d, full["entry_time_ny"])
        part, _ = H.evaluate(E1, V1, fr[nm][fr[nm].index <= cut], d, nm)
        assert (part["direction"], part["entry"], part["entry_time_ny"]) == (full["direction"], full["entry"], full["entry_time_ny"])
