"""Tests for the H014 forward harness. Run: cd /workspace/mmxm/forward && ../.venv/bin/python -m pytest -q tests"""
import json, pathlib, sys
import numpy as np, pandas as pd, pytest
HERE = pathlib.Path(__file__).resolve().parents[1]; sys.path.insert(0, str(HERE))
import h014_forward as F

PREREG = json.load(open(F.HERMES / F.PREREG_PATH))
ARCH = sorted((F.TVFEED_DIR / "raw/forward/archive").glob("CAPITALCOM_US100_1m_fetch_*.csv"))
needs_arch = pytest.mark.skipif(not ARCH, reason="no saved CAPITALCOM archive")
ENG = F.load_engine()

@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "LOG", tmp_path / "log.csv"); monkeypatch.setattr(F, "RAW", tmp_path / "raw"); monkeypatch.setattr(F, "HERE", tmp_path)
    return tmp_path

def test_rule_hashes_match_prereg():
    assert F.RULE_SHA256 == PREREG["rule_object_sha256"] and F.verify_rule_objects()
    for k, h in F.WARMUP_SHA256.items(): assert F.sha256_file(F.MM / k) == h

def test_frozen_settings_match_prereg():
    cfg = ENG[0]; es = PREREG["engine_settings"]
    assert cfg.fill_through_ticks == es["fill_through_ticks"] == 1 and cfg.stop_slippage_ticks == es["stop_slippage_ticks"] == 0
    assert cfg.cost_points_round_trip == {"NQ": es["cost_round_trip_pts"]["US100"], "ES": es["cost_round_trip_pts"]["US500"]}
    assert cfg.htf_bias == "none" and cfg.entry_model == "5m_fvg" and cfg.entry_level == "ce" and cfg.entry_cancel_5m_bars == 12
    assert cfg.session_range == "overnight" and cfg.entry_start == "09:30" and cfg.flat_time == "11:00"

def test_spread_proxy_matches_DATA_script():
    src = pathlib.Path("/home/box/hermes-x/investigations/POST-WAVE1-LEADS/scripts/mmxm_spread_proxy.py")
    if not src.exists(): pytest.skip("DATA script not on box")
    assert '"US100": (6, 4, 0.5), "US500": (3, 2, 0.5)' in src.read_text()
    assert {k: (v["fill_through_ticks"], v["stop_slippage_ticks"], v["cost"]) for k, v in F.SPREAD_PROXY.items()} == {"US100": (6, 4, 0.5), "US500": (3, 2, 0.5)}
    assert F.MEASURED_COST_RT == {"US100": 1.617, "US500": 1.01}

def test_calendar_and_kill_match_prereg():
    h = PREREG["holidays_excluded"]
    assert F.HOLIDAYS_FULL == set(h["full_closures"]) and F.HOLIDAYS_EARLY == set(h["early_closes"]) and F.HOLIDAYS_HIST == set(h["historical_additions"])
    assert "-5R" in PREREG["binding_kill"] and F.KILL_R == -5.0
    assert "86 of 90" in PREREG["counting_rules"]["min_bar_filter"] and "791 of 930" in PREREG["counting_rules"]["min_bar_filter"]
    assert (F.MIN_RTH, F.N_RTH, F.MIN_ON, F.N_ON) == (86, 90, 791, 930)
    assert F.calendar_status("2026-07-03") == "holiday_historical_exclusion" and F.calendar_status("2026-11-27") == "holiday_early_close"

def test_monday_session_start_is_sunday_1800():
    assert F.session_start("2026-10-05") == pd.Timestamp("2026-10-04 18:00", tz=F.TZ)

def test_min_bar_counts():
    d = "2026-10-05"; idx = pd.date_range(F.session_start(d), F.at(d, "16:59"), freq="1min")
    m1 = pd.DataFrame({"open": 1.0, "high": 1.0, "low": 1.0, "close": 1.0}, index=idx)
    assert F.bar_counts(m1, d)[:2] == (90, 930)
    m2 = m1.drop(m1.index[(m1.index >= F.at(d, "10:00")) & (m1.index < F.at(d, "10:05"))])
    nr, no, miss = F.bar_counts(m2, d); assert nr == 85 and nr < F.MIN_RTH and miss[0] == "10:00"

def test_no_fallback(monkeypatch):
    sys.path.insert(0, str(F.TVFEED_DIR)); import tv_feed
    calls = []
    def boom(sym, n=500, **k): calls.append(sym); raise RuntimeError("down")
    monkeypatch.setattr(tv_feed, "fetch_tv", boom)
    with pytest.raises(F.FeedError): F.fetch("US500")
    assert calls == ["CAPITALCOM:US500"]
    src = (HERE / "h014_forward.py").read_text()
    for bad in ('"PEPPERSTONE:', '"OANDA:', "yfinance", "load_futures"): assert bad not in src

# ----- historical reproduction: the harness's 60-day input window reproduces every frozen v5 A trade exactly
TR = pd.concat([pd.read_csv(F.MM / f"output/v5/trades_A_overnight_5mFVG_ce_c12_none_{s}.csv") for s in F.SYMS])

@pytest.mark.parametrize("sym,date", sorted({(r.symbol, r.date_ny) for r in TR.itertuples()}))
def test_reproduces_frozen_trades(sym, date):
    cfg, D, run_backtest, _ = ENG
    m1, src = F.build_input(sym, date, pd.DataFrame(columns=["open", "high", "low", "close"]), D)
    tr, _ = F.day_trades(run_backtest, m1, cfg, sym, date)
    exp = TR[(TR.symbol == sym) & (TR.date_ny == date)]
    assert len(tr) == len(exp)
    for (_, a), (_, b) in zip(tr.iterrows(), exp.iterrows()):
        assert str(pd.Timestamp(a.entry_time_ny)) == str(pd.Timestamp(b.entry_time_ny)) and a.direction == b.direction
        assert abs(a.entry - b.entry) < 1e-6 and abs(a.stop - b.stop) < 1e-6 and abs(a.r_multiple - b.r_multiple) < 1e-9

# ----- append-only log, raw bars, kill
def _fetched(d):
    f = {s: F.read_csv_bars(str(ARCH[-1]).replace("US100", s)) for s in F.SYMS}
    return {s: v[v.index <= F.at(d, "16:59")] for s, v in f.items()}

REG_OK = dict(ok=True, main_commit="x", landed_ny=str(pd.Timestamp("2026-09-01", tz=F.TZ)))

@needs_arch
def test_append_only_raw_and_duplicates(sandbox, monkeypatch):
    monkeypatch.setattr(F, "FIRST_POSSIBLE_SESSION", "2026-09-28")
    d = "2026-10-02"; fe = _fetched(d); meta = {s: dict(feed="TradingView " + F.FEED[s]) for s in F.SYMS}
    r1 = F.run_session(d, "FINAL", fe, meta, REG_OK); b = F.LOG.read_bytes()
    r2 = F.run_session(d, "FINAL", fe, meta, REG_OK); a = F.LOG.read_bytes()
    assert a.startswith(b) and len(pd.read_csv(F.LOG)) == len(r1) + len(r2)
    assert all(r["counted"] for r in r1) and not any(r["counted"] for r in r2)
    assert r1[0]["raw_file"] == r2[0]["raw_file"] and F.sha256_file(sandbox / r1[0]["raw_file"]) == r1[0]["raw_sha256"]
    raw = pd.read_csv(sandbox / r1[0]["raw_file"]); assert set(raw.src) == {"CAPITALCOM", "DUKASCOPY_BID_WARMUP"}
    us500 = [r for r in r1 if r["instrument"] == "US500"][0]
    assert us500["status"] == "trade" and us500["cum_R_US500_counted"] == pytest.approx(us500["R_frozen"]) and us500["cum_R_US100_counted"] == 0

@needs_arch
def test_kill_at_minus_5R(sandbox, monkeypatch):
    monkeypatch.setattr(F, "FIRST_POSSIBLE_SESSION", "2026-09-28")
    pd.DataFrame([dict({c: None for c in F.COLUMNS}, run_id="old", run_kind="FINAL", date="2026-09-30", instrument="US500", status="trade",
                       R_frozen=-4.0, counted=True, kill_triggered=False)])[F.COLUMNS].to_csv(F.LOG, index=False)
    d = "2026-10-02"; rows = F.run_session(d, "FINAL", _fetched(d), {s: {} for s in F.SYMS}, REG_OK)
    assert rows[0]["cum_R_pooled_counted"] < -5 and all(r["kill_triggered"] for r in rows)
    rows2 = F.run_session("2026-10-01", "BACKFILL", _fetched("2026-10-01"), {s: {} for s in F.SYMS}, REG_OK)
    assert all("already killed" in r["not_counted_reasons"] for r in rows2)

@needs_arch
def test_registration_after_session_start_not_counted(sandbox, monkeypatch):
    monkeypatch.setattr(F, "FIRST_POSSIBLE_SESSION", "2026-09-28")
    d = "2026-10-02"; late = dict(REG_OK, landed_ny=str(F.at("2026-10-01", "19:00")))
    rows = F.run_session(d, "FINAL", _fetched(d), {s: {} for s in F.SYMS}, late, dry=True)
    assert all(not r["counted"] and "after session start" in r["not_counted_reasons"] for r in rows)

# ----- dry-run on recent saved raw CAPITALCOM data
@needs_arch
@pytest.mark.parametrize("d", ["2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02"])
def test_dry_run_replay(d, sandbox):
    rows = F.run_session(d, "REPLAY", _fetched(d), {s: {} for s in F.SYMS}, dict(ok=False, mismatches="PENDING"), dry=True)
    assert not F.LOG.exists() and not (sandbox / "raw").exists()
    assert {r["instrument"] for r in rows} == set(F.SYMS) and all(r["session_bars_all_capitalcom"] for r in rows)
    assert all(r["bars_0930_1059"] == 90 and r["bars_overnight"] == 930 and not r["counted"] for r in rows)
