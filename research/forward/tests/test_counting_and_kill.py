"""Counting rules (both leads) and the H014 -5R kill, exercised end-to-end in a sandbox data dir with a fake CAPITALCOM fetch
that serves historical Dukascopy bars (so the outcome is known). No network, no orders."""
import json, pathlib
import pandas as pd, pytest
from conftest import DUKA_MU, MMXM_OUT
import h013 as H13
import h014 as H14
from common import fwdlib as F

NY = "America/New_York"
REG_OK = dict(registered=True, registration_commit="x", registration_time_ny="2025-01-01 00:00:00-05:00",
              harness_matches_registered=True)
needs_mu = pytest.mark.skipif(not (DUKA_MU / "data/US100_1m.parquet").exists(), reason="no Dukascopy history")
needs_mx = pytest.mark.skipif(not (MMXM_OUT / "data/US100_1m.parquet").exists(), reason="no Dukascopy history")


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    monkeypatch.setattr(F, "DATA_ROOT", tmp_path)
    return tmp_path


def duka(root, inst):
    df = pd.read_parquet(root / f"data/{inst}_1m.parquet")
    df.columns = [c.capitalize() for c in df.columns]
    return df[["Open", "High", "Low", "Close"]].astype(float)


def fake_fetch(frames, upto):
    """Serve frames[inst] up to the clock `upto()` (exclusive of the forming bar) like the TradingView socket would."""
    def f(sym, n=1500):
        inst = sym.split(":")[1]
        x = frames[inst]
        x = x[x.index + pd.Timedelta(minutes=1) <= upto()]
        return x.iloc[-n:]
    return f


class Clock:
    def __init__(self, t): self.t = t
    def __call__(self): return self.t
    def sleep(self, s): self.t = self.t + pd.Timedelta(minutes=1)


def h013_trade_day():
    t = pd.read_csv(DUKA_MU / "data/trades_cost1x_thru1.csv")
    t = t[(t.model == "v1 base") & (t.inst == "US100") & (t.status == "trade") & (t.exit_time_5050 > "09:40")]
    return t.iloc[3]


# ------------------------------------------------------------------ H013
@needs_mu
def test_h013_live_alert_then_final_counts_only_us100(sandbox, monkeypatch):
    w = h013_trade_day(); d = w.date
    frames = {i: duka(DUKA_MU, i) for i in ("US100", "US500")}
    clk = Clock(F.at(d, "09:00"))
    monkeypatch.setattr(F, "now_sast", lambda: clk().tz_convert(F.SAST))
    polls = H13.cmd_watch(d, until="11:31", fetch=fake_fetch(frames, clk), sleep=clk.sleep, now_fn=clk)
    assert polls >= 150
    alerts = F.read_jsonl(sandbox / "H013/alerts.jsonl")
    fill = [a for a in alerts if a["event"] == "FILL" and a["instrument"] == "US100"]
    assert len(fill) == 1 and fill[0]["fill_time_ny"] == w.entry_time_ny
    raw = sandbox / fill[0]["raw_file"]
    assert raw.exists() and F.sha256_file(raw) == fill[0]["raw_sha256"]          # live snapshot persisted + hashed
    clk.t = F.at(d, "12:05")
    monkeypatch.setattr(F, "registration_status", lambda *a, **k: REG_OK)
    rows = {r["instrument"]: r for r in H13.cmd_final(d, fetch=fake_fetch(frames, clk), fetch_remote=False)}
    us = rows["US100"]
    assert us["status"] == "trade" and abs(us["R_5050"] - w.R_5050) < 1e-9
    assert us["live_alerted"] is True and us["counted"] is True, us["not_counted_reasons"]
    assert F.sha256_file(sandbox / us["raw_file"]) == us["raw_sha256"]
    assert rows["US500"]["counted"] is False and "disclosure_series" in rows["US500"]["not_counted_reasons"]
    rep = H13.cmd_report()
    assert rep["US100"]["n"] == 1 and abs(rep["US100"]["cum_R"] - w.R_5050) < 1e-9


@needs_mu
def test_h013_backfill_and_missing_alert_never_count(sandbox, monkeypatch):
    w = h013_trade_day(); d = w.date
    frames = {i: duka(DUKA_MU, i) for i in ("US100", "US500")}
    clk = Clock(F.at(d, "12:05"))
    monkeypatch.setattr(F, "registration_status", lambda *a, **k: REG_OK)
    bf = {r["instrument"]: r for r in H13.cmd_final(d, "BACKFILL", fetch=fake_fetch(frames, clk), fetch_remote=False)}
    assert bf["US100"]["counted"] is False and "backfill_never_counted" in bf["US100"]["not_counted_reasons"]
    fin = {r["instrument"]: r for r in H13.cmd_final(d, fetch=fake_fetch(frames, clk), fetch_remote=False)}
    assert fin["US100"]["counted"] is False and "no_live_alert_before_exit" in fin["US100"]["not_counted_reasons"]
    assert H13.cmd_report()["US100"]["n"] == 0 and H13.cmd_report()["backfill_rows_never_counted"] == 2


def _row(**k):
    base = dict(date="2025-10-15", inst="US100", status="trade", direction="long", entry=100.0, entry_time_ny="09:10",
                exit_time_5050="09:40", bars_0700_1159=300, session_complete=True)
    return {**base, **k}


def test_h013_counting_reasons_table():
    alert = [dict(event="FILL", key="2025-10-15|US100|long|100.00|09:10", alert_time_ny="2025-10-15 09:11:05-04:00",
                  alert_time_sast="x")]
    c = H13.counting(_row(), "FINAL", REG_OK, alert, True)
    assert c["counted"] is True
    late = [dict(alert[0], alert_time_ny="2025-10-15 09:45:00-04:00")]
    assert "alert_after_exit" in H13.counting(_row(), "FINAL", REG_OK, late, True)["not_counted_reasons"]
    assert "min_bars:284<285" in H13.counting(_row(bars_0700_1159=284), "FINAL", REG_OK, alert, True)["not_counted_reasons"]
    assert "calendar:nyse_full_closure" in H13.counting(_row(date="2026-11-26"), "FINAL", REG_OK, [], True)["not_counted_reasons"]
    assert "calendar:historical_exclusion" in H13.counting(_row(date="2025-12-24"), "FINAL", REG_OK, [], True)["not_counted_reasons"]
    assert "calendar:calendar_not_covered" in H13.counting(_row(date="2028-01-03"), "FINAL", REG_OK, [], True)["not_counted_reasons"]
    late_reg = dict(REG_OK, registration_time_ny="2025-10-15 07:00:00-04:00")
    assert "registered_after_session_start" in H13.counting(_row(), "FINAL", late_reg, alert, True)["not_counted_reasons"]
    assert "harness_hash_mismatch" in H13.counting(_row(), "FINAL", dict(REG_OK, harness_matches_registered=False), alert, True)["not_counted_reasons"]
    assert "harness_not_registered_on_main" in H13.counting(_row(), "FINAL", dict(registered=False), alert, True)["not_counted_reasons"]
    assert "session_incomplete" in H13.counting(_row(session_complete=False), "FINAL", REG_OK, alert, True)["not_counted_reasons"]


def test_feed_failure_is_a_gap_never_a_fallback(sandbox, monkeypatch):
    def boom(sym, n=1500): raise ConnectionError("socket closed")
    monkeypatch.setattr(F, "registration_status", lambda *a, **k: REG_OK)
    rows = H13.cmd_final("2026-10-05", fetch=boom, fetch_remote=False)
    assert {r["status"] for r in rows} == {"feed_gap"} and not any(r["counted"] for r in rows)
    assert set(F.FEEDS.values()) == {"CAPITALCOM:US100", "CAPITALCOM:US500"}


# ------------------------------------------------------------------ H014
def test_kill_walk_at_minus_5R():
    t = pd.DataFrame(dict(entry_time_ny=[f"2026-10-0{i} 10:00:00-04:00" for i in range(5, 10)], r_multiple=[1, -2, -2, -2, 1],
                          instrument=["US100", "US500", "US100", "US500", "US100"]))
    w = H14.kill_walk(t)
    assert list(w.cum_pooled_R) == [1, -1, -3, -5, -4]          # exactly -5 triggers (<= -5R)
    assert list(w.after_kill) == [False, False, False, False, True]
    w2 = H14.kill_walk(t.assign(r_multiple=[1, -2, -2, -1.9, 1]))
    assert not (w2.cum_pooled_R <= -5).any()


def test_h014_report_per_symbol_latest_run_and_kill():
    rows = []
    for i, (inst, r) in enumerate([("US100", -2.0), ("US500", -1.5), ("US100", -1.6), ("US500", 0.5)]):
        rows.append(dict(run_id=f"r{i}", date=f"2026-10-0{5+i}", instrument=inst, status="trade", counted=True, backfilled=False,
                         entry_time_ny=f"2026-10-0{5+i} 10:00:00-04:00", r_multiple=r))
    rows.append(dict(rows[0], run_id="r9", r_multiple=-0.1))    # later FINAL re-run of the same session supersedes r0
    rep = H14.cmd_report(pd.DataFrame(rows))
    assert rep["US100"]["n"] == 2 and abs(rep["US100"]["total_R"] - (-1.7)) < 1e-9
    assert rep["US500"]["n"] == 2 and not rep["kill_triggered"]
    rows.append(dict(rows[1], run_id="r10", date="2026-10-12", entry_time_ny="2026-10-12 10:00:00-04:00", r_multiple=-2.5))   # cum -5.2
    rep = H14.cmd_report(pd.DataFrame(rows))
    assert rep["kill_triggered"] and rep["status"].startswith("FAILS")


@needs_mx
def test_h014_final_on_fake_capitalcom_counts_and_baseline(sandbox, monkeypatch):
    want = pd.read_csv(MMXM_OUT / "output/v5/trades_A_overnight_5mFVG_ce_c12_none_US500.csv").iloc[5]
    d = str(want.entry_time_ny)[:10]
    frames = {i: duka(MMXM_OUT, i).loc[str(pd.Timestamp(d) - pd.Timedelta(days=30))[:10]:] for i in ("US100", "US500")}
    clk = Clock(F.at(d, "12:05"))
    monkeypatch.setattr(F, "registration_status", lambda *a, **k: REG_OK)
    rows = [r for r in H14.cmd_final(d, fetch=fake_fetch(frames, clk), fetch_remote=False) if r["instrument"] == "US500"]
    tr = [r for r in rows if r["status"] == "trade"]
    assert len(tr) == 1 and abs(float(tr[0]["r_multiple"]) - float(want.r_multiple)) < 1e-9
    assert tr[0]["counted"] is True and tr[0]["baseline_n"] > 50 and len(json.loads(tr[0]["baseline_outcomes"])) == tr[0]["baseline_n"]
    assert F.sha256_file(sandbox / tr[0]["raw_file"]) == tr[0]["raw_sha256"]
    late = dict(REG_OK, registration_time_ny=str(F.at(d, "08:00")))       # registered after Sunday/prior-day 18:00
    m1 = H14.to_m1(frames["US500"][frames["US500"].index < F.at(d, "12:00")])
    _, reasons = H14.eligibility(m1, d, late, True)
    assert "registered_after_session_data_began" in reasons


def test_h014_calendar_and_min_bars_block_counting():
    idx = pd.date_range(F.at("2026-10-05", "00:00") - pd.Timedelta(hours=6), F.at("2026-10-05", "11:59"), freq="1min")
    m1 = pd.DataFrame(dict(open=1.0, high=1.0, low=1.0, close=1.0, volume=float("nan")), index=idx)
    q, reasons = H14.eligibility(m1, "2026-10-05", REG_OK, True)
    assert q["bars_0930_1059"] == 90 and q["bars_overnight"] == 930 and not reasons
    thin = m1.drop(m1.index[(m1.index >= F.at("2026-10-05", "09:30")) & (m1.index < F.at("2026-10-05", "09:35"))])
    assert any(r.startswith("min_bars") for r in H14.eligibility(thin, "2026-10-05", REG_OK, True)[1])
    hol = m1.copy(); hol.index = hol.index + pd.Timedelta(days=52)        # 2026-11-26 Thanksgiving
    assert "calendar:nyse_full_closure" in H14.eligibility(hol, "2026-11-26", REG_OK, True)[1]
