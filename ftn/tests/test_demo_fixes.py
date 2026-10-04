"""Post-H015b demo fixes (branch ftn/demo-fixes; NOT part of H015b). One block per fix."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta

import pytest

from ftn.config_load import ConfigError, load_config
from ftn.os.instruments import INSTRUMENTS, rev_stop_buffer, spec, to_pips
from ftn.os.m8_contracts import CbdrState, classify_cbdr
from ftn.os.m8_detect import derive_month8_measures, london_gate_from_measures
from ftn.os.m8_project import project_daily_extreme
from ftn.os.mint_draft import risk_gate
from ftn.research.bars import Series
from ftn.research.book import RunningBook
from ftn.research.events import day_events, load_events
from ftn.research.outcomes import simulate, simulate_both

FLAT = {"daily_loss_pct": 0.0, "drawdown_pct": 0.0, "source": "test"}


# --- fix 1: Month 8 in instrument units -------------------------------------------------------------

def _m8_raw(sym, cb_hi, cb_lo, as_hi=None, as_lo=None, pip=None, calendar=None):
    raw = {"symbol": sym, "ranges": {"cbdr": {"high": cb_hi, "low": cb_lo}}, "evidence": {}}
    if pip is not None:
        raw["evidence"]["pip"] = pip
    if as_hi is not None:
        raw["ranges"]["asian"] = {"high": as_hi, "low": as_lo}
    if calendar:
        raw["calendar"] = calendar
    return raw


def test_m8_index_cbdr_measured_in_points_not_fx_pips():
    st = derive_month8_measures(_m8_raw("US100", 25590.6, 25491.6, 25284.3, 25208.4))
    assert math.isclose(st.cbdr.height_pips, 99.0) and st.cbdr.classification == "ideal"   # was 990010 → wide
    assert st.cbdr.origin == "hermes_interpretation"
    assert math.isclose(st.asian_height_pips, 75.9, abs_tol=0.05)
    assert st.london_session_gate.allowed is True


def test_m8_index_thresholds_scale_by_daily_range_ratio():
    us100, us500 = INSTRUMENTS["US100"], INSTRUMENTS["US500"]
    assert math.isclose(us100.range_scale, 414.7 / 61.5, abs_tol=1e-3)
    assert us100.cbdr_ideal_lt == round(40 * us100.range_scale, 1) and us100.cbdr_wide_ge == round(50 * us100.range_scale, 1)
    assert classify_cbdr(400, us100.cbdr_ideal_lt, us100.cbdr_wide_ge) == "wide"
    assert classify_cbdr(300, us100.cbdr_ideal_lt, us100.cbdr_wide_ge) == "expanded"
    assert derive_month8_measures(_m8_raw("US500", 6600.0, 6540.0)).cbdr.classification == "expanded"   # 60 pt


def test_m8_fx_unchanged():
    st = derive_month8_measures(_m8_raw("EURUSD", 1.1180, 1.1150, 1.1176, 1.1151))
    assert math.isclose(st.cbdr.height_pips, 30.0) and st.cbdr.classification == "ideal"
    assert st.cbdr.origin == "ict_source" and math.isclose(st.asian_height_pips, 25.0)
    assert classify_cbdr(26) == "ideal" and classify_cbdr(45) == "expanded" and classify_cbdr(55) == "wide"
    assert to_pips(0.0030, "EURUSD") == 30.0 and to_pips(30.0, "US100") == 30.0


def test_m8_projection_uses_instrument_pip():
    cb = CbdrState(height_pips=100.0, wick_high=25600.0, wick_low=25500.0, classification="ideal")
    proj = project_daily_extreme(cb, "bearish", pip=1.0)
    assert proj.sd_levels and math.isclose(proj.sd_levels[0]["price"], 25700.0)
    fx = project_daily_extreme(CbdrState(height_pips=20.0, wick_high=1.1200, classification="ideal"), "bearish")
    assert math.isclose(fx.sd_levels[0]["price"], 1.1220)


# --- fix 2: minimum stop distance --------------------------------------------------------------------

def _rev(sym, side, last, ext, level, pip=1.0, spread=None):
    return {"symbol": sym, "last": last, "execution_context": {
        "raid": {"level": level, "price": ext, "taken": True, "also": []},
        "raid_extreme": {"side": "high" if side == "sell" else "low", "price": ext, "from_bar": 0, "to_bar": 3},
        "pip": pip, "stop_reference": None, "symbol": sym, "spread_measured": spread}}


def test_min_risk_rule_values():
    assert math.isclose(INSTRUMENTS["US100"].min_risk, 4 * (1.55 + 2 * 0.50))   # 10.2
    assert math.isclose(INSTRUMENTS["US500"].min_risk, 4 * (0.72 + 2 * 0.25))   # 4.88
    assert spec("EURUSD").min_risk is None


def test_risk_gate_blocks_stop_below_min_risk():
    cfg = load_config()
    r = risk_gate("REV", "sell", _rev("US100", "sell", 26176.0, 26176.5, "pdh"), cfg, FLAT)   # the 2025-10-29 case
    assert r["pass"] is False and r["reason"] == "stop_below_min_risk" and r["min_risk"] == 10.2
    ok = risk_gate("REV", "sell", _rev("US100", "sell", 26150.0, 26176.5, "pdh"), cfg, FLAT)
    assert ok["pass"] and ok["stop_distance"] >= 10.2
    fx = risk_gate("REV", "buy", _rev("EURUSD", "buy", 1.1137, 1.1135, "pdl", pip=0.0001), cfg, FLAT)
    assert fx["pass"]   # no FX minimum: reconstructions unchanged


# --- fix 3: stop buffer covers spread + slippage (shorts stopped on the ask) ------------------------

def test_rev_buffer_index_short_covers_spread_plus_slippage():
    buf, src = rev_stop_buffer("US100", "sell", 1.0)
    assert math.isclose(buf, 1.55 + 0.50) and src == "spread_plus_slip_ask_side"
    assert math.isclose(rev_stop_buffer("US100", "sell", 1.0, spread_measured=3.0)[0], 3.5)
    assert math.isclose(rev_stop_buffer("US100", "buy", 1.0)[0], 1.0)            # long: bid side, slip 0.5 < 1 pt
    assert math.isclose(rev_stop_buffer("US500", "sell", 1.0)[0], 1.0)           # 0.72 + 0.25 < 1 pt
    assert math.isclose(rev_stop_buffer("EURUSD", "sell", 0.0001)[0], 0.0001)    # FX keeps D22 1 pip


def test_rev_stop_uses_new_buffer_in_gate():
    r = risk_gate("REV", "sell", _rev("US100", "sell", 29617.2, 29660.054, "pdh", spread=1.17), load_config(), FLAT)
    assert r["pass"] and math.isclose(r["stop_reference"], 29660.054 + 2.05)


# --- fix 4: running book -----------------------------------------------------------------------------

def test_running_book_dd_cap_binds_and_resets_next_month():
    cfg = load_config()
    b = RunningBook(0.5, reset="next_calendar_month")
    t = datetime(2026, 1, 5, 7, 15)
    for i in range(10):                                   # ten -1R losses → ~4.9% drawdown
        b.record(t + timedelta(days=i, hours=1), -1.0)
    st = b.state(datetime(2026, 1, 20, 7, 0))
    assert st["drawdown_pct"] > 4.5 and st["source"] == "scorer_running_book"
    r = risk_gate("REV", "sell", _rev("US100", "sell", 26150.0, 26176.5, "pdh"), cfg, st)
    assert r["pass"] is False and r["reason"] == "max_drawdown_cap"
    b.blocked(datetime(2026, 1, 20, 7, 0), "max_drawdown_cap")
    assert b.state(datetime(2026, 1, 30, 7, 0))["drawdown_pct"] > 4.5          # halted for the rest of January
    assert b.state(datetime(2026, 2, 2, 7, 0))["drawdown_pct"] == 0.0          # reset in February
    assert [e["event"] for e in b.events] == ["drawdown_cap_tripped", "drawdown_reset"]


def test_running_book_no_reset_and_daily_loss():
    b = RunningBook(0.5, reset="none")
    for i in range(10):
        b.record(datetime(2026, 1, 5 + i, 9, 0), -1.0)
    b.blocked(datetime(2026, 1, 20), "max_drawdown_cap")
    assert b.state(datetime(2026, 3, 2))["drawdown_pct"] > 4.5
    d = RunningBook(0.5)
    d.record(datetime(2026, 1, 5, 3, 0), -4.0)            # a -4R loss (gap through the stop) at 03:00
    st = d.state(datetime(2026, 1, 5, 7, 15))
    assert math.isclose(st["daily_loss_pct"], 2.0) and d.state(datetime(2026, 1, 6, 2, 15))["daily_loss_pct"] == 0.0
    with pytest.raises(ValueError):
        RunningBook(reset="weekly")


def test_ticket_log_requires_outcome_with_book():
    from ftn.research.kernel_log import session_ticket_log
    with pytest.raises(ValueError):
        session_ticket_log(None, {}, book=RunningBook())


def test_config_drawdown_reset_validated(tmp_path):
    from pathlib import Path
    text = (Path(__file__).resolve().parents[1] / "config.yaml").read_text()
    assert load_config()["drawdown_reset"] == "next_calendar_month"
    p = tmp_path / "c.yaml"
    p.write_text(text.replace("drawdown_reset: next_calendar_month", "drawdown_reset: weekly"))
    with pytest.raises(ConfigError):
        load_config(p)


# --- correct-side fills (default cost model) ---------------------------------------------------------

def _two(ts, bid, ask):
    mk = lambda rows: Series("US100", ts, [r[0] for r in rows], [r[1] for r in rows], [r[2] for r in rows], [r[3] for r in rows])
    return mk(bid), mk(ask)


def test_simulate_both_short_stopped_on_ask_not_bid():
    t0 = datetime(2026, 1, 6, 8, 59)
    ts = [t0 + timedelta(minutes=i) for i in range(4)]
    bid = [(100, 100, 100, 100), (100, 100.9, 99.5, 100), (100, 100.5, 99.5, 100), (100, 100.5, 99.5, 100)]
    ask = [(101.2, 101.2, 101.2, 101.2), (101.2, 102.1, 100.7, 101.2), (101.2, 101.7, 100.7, 101.2), (101.2, 101.7, 100.7, 101.2)]
    b, a = _two(ts, bid, ask)
    sl = {"market": 0.5, "stop": 0.5, "limit": 0.25}
    r = simulate_both(b, a, ts[1], 100.0, 101.0, "sell", sl)            # bid never reaches 101, ask does
    assert r["exit"] == "stop" and math.isclose(r["fill_in"], 99.5) and math.isclose(r["fill_out"], 101.7)  # ask opened above the stop: gap fill
    assert math.isclose(r["R"], -2.2) and r["exit_time"] == ts[1].isoformat()
    assert simulate(b, ts[1], 100.0, 101.0, "sell", 0.0)["exit"] == "time"   # flat bid-only model misses it


def test_simulate_both_long_target_trades_through_and_entry_on_ask():
    t0 = datetime(2026, 1, 6, 8, 59)
    ts = [t0 + timedelta(minutes=i) for i in range(3)]
    bid = [(100, 100, 100, 100), (100, 110, 99.5, 100), (100, 110.5, 99.5, 110)]
    ask = [(101, 101, 101, 101), (101, 111, 100.5, 101), (101, 111.5, 100.5, 111)]
    b, a = _two(ts, bid, ask)
    r = simulate_both(b, a, ts[1], 100.0, 95.0, "buy", {"market": 0.5, "stop": 0.5, "limit": 0.25})
    assert r["exit"] == "target" and r["exit_time"] == ts[2].isoformat()   # 110 touched at ts[1] but not through
    assert math.isclose(r["fill_in"], 101.5) and math.isclose(r["R"], (109.75 - 101.5) / 5.0)


def test_scorer_default_is_correct_side_and_needs_asks():
    import inspect
    from ftn.research import score as sc
    assert inspect.signature(sc.score).parameters["cost_model"].default == "correct_side"
    from ftn.research.daycontext import History
    b, _ = _two([datetime(2026, 1, 6, 9)], [(1, 1, 1, 1)], [(1, 1, 1, 1)])
    with pytest.raises(ValueError, match="ASK"):
        sc.make_sim("US100", History(b, []), "correct_side")
    assert sc.make_sim("US100", History(b, []), "flat")


# --- fix 5: calendar wired, unavailable layers stay unavailable --------------------------------------

def test_calendar_events_loaded_and_attached():
    ev = load_events()
    assert any(e["kind"] == "nfp" for e in ev[date(2026, 9, 4)])
    nfp = day_events(date(2026, 9, 4), "US100")
    assert nfp and nfp[0]["impact"] == "high" and nfp[0]["killzone"] == "ny_am" and nfp[0]["pair"] == "US100"
    assert day_events(date(2026, 9, 3), "US100") == []
    st = derive_month8_measures(_m8_raw("US100", 25590.6, 25491.6, calendar=nfp))
    assert st.london_session_gate.reason == "news"


def test_bar_context_attaches_calendar_and_measured_spread(tmp_path):
    from ftn.research.daycontext import History, build_raw
    from datetime import time
    days = [date(2026, 8, 3) + timedelta(days=i) for i in range(40) if (date(2026, 8, 3) + timedelta(days=i)).weekday() < 5]
    ts = []
    for d in [days[0] - timedelta(days=3)] + days:
        start = datetime.combine(d - timedelta(days=1), time(18, 0))
        ts += [start + timedelta(minutes=m) for m in range(0, 23 * 60, 1)]
    ts = sorted(set(ts))
    n = len(ts)
    bid = Series("US100", ts, [100.0] * n, [101.0] * n, [99.0] * n, [100.0] * n)
    ask = Series("US100", ts, [101.0] * n, [102.0] * n, [100.0] * n, [101.2] * n)
    h = History(bid, days, ask=ask)
    d = date(2026, 9, 4)
    raw = build_raw(h, d, datetime.combine(d, time(7, 15)), "ny_am")
    assert raw["calendar"] and raw["calendar"][0]["kind"] == "nfp"
    assert math.isclose(raw["evidence"]["spread_measured"], 1.2)
    h.calendar = False
    assert build_raw(h, d, datetime.combine(d, time(7, 15)), "ny_am")["calendar"] == []


def test_dxy_stays_unavailable_without_data():
    from ftn.os.dxy import dxy_relationship
    assert dxy_relationship("US100", "bullish", None) == "unavailable"


def _ask_file(bid_path, out, spread=1.2):
    import csv, gzip
    with gzip.open(bid_path, "rt") as fi, gzip.open(out, "wt", newline="") as fo:
        r, w = csv.reader(fi), csv.writer(fo)
        w.writerow(next(r))
        for row in r:
            w.writerow([row[0]] + [f"{float(x) + spread:.2f}" for x in row[1:5]])
    return out


def test_score_correct_side_default_with_flatcost_and_running_book(tmp_path, monkeypatch):
    from tests.test_research_bridge import _series
    from ftn.research import score as sc, stats
    from ftn.research.bars import trading_days
    b100, b500 = _series(tmp_path / "US100_1m.csv.gz"), _series(tmp_path / "US500_1m.csv.gz", seed=11)
    a100, a500 = _ask_file(b100, tmp_path / "US100_ask.csv.gz"), _ask_file(b500, tmp_path / "US500_ask.csv.gz", 0.6)
    monkeypatch.setattr(sc, "N_FOIL", 10)
    monkeypatch.setattr(stats, "N_BOOT", 100)
    monkeypatch.setattr(sc, "trading_days", lambda s: trading_days(s, min_rth_bars=100))
    res = sc.score(asof="2026-01-01", bars_us100=str(b100), bars_us500=str(b500), asks_us100=str(a100),
                   asks_us500=str(a500), research_dir=tmp_path / "r", with_interp=False, book="both")
    assert res["_config"]["cost_model"] == "correct_side" and "NOT part of H015b" in res["_config"]["label"]
    for sym in ("US100", "US500"):
        assert res[f"{sym}_base"]["cost_model"] == "correct_side"
        assert res[f"{sym}_base_flatcost"]["cost_model"] == "flat"
        assert res[f"{sym}_base_runningbook"]["book"] == "running"
        assert res[f"{sym}_base"]["tickets"] == res[f"{sym}_base_flatcost"]["tickets"] == res[f"{sym}_base_runningbook"]["tickets"]
        assert res[f"{sym}_base_runningbook"]["summary"].get("n", 0) <= res[f"{sym}_base"]["summary"].get("n", 0)
    md = (tmp_path / "r/summaries/2026-01-01_FTN_M9_EXPLORATORY_SCORE.md").read_text()
    assert "correct_side" in md and "NOT part of H015b" in md
