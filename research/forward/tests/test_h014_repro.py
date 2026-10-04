"""H014 harness reproduces the FROZEN v5 A rule on the existing Dukascopy BID history:
run_engine() (frozen copy, unchanged config) must give exactly the 48 trades in mmxm/output/v5/trades_A_..._{US100,US500}.csv,
and the per-session path (history cut at d 12:00 NY, 60 days of context) must give the same trade on each trade day."""
import pandas as pd, pytest
from conftest import MMXM_OUT
import h014 as H

PQ = MMXM_OUT / "data"
pytestmark = pytest.mark.skipif(not (PQ / "US100_1m.parquet").exists(), reason="Dukascopy history not on this box")
COLS = ["direction", "order_time_ny", "entry_time_ny", "entry", "stop", "tp1", "draw", "exit_time_ny", "exit_reason", "r_multiple"]


def hist(inst):
    df = pd.read_parquet(PQ / f"{inst}_1m.parquet")
    df.columns = [c.capitalize() for c in df.columns] if "open" in df.columns else df.columns
    return df[["Open", "High", "Low", "Close"]].astype(float)


def frozen(inst):
    return pd.read_csv(MMXM_OUT / f"output/v5/trades_A_overnight_5mFVG_ce_c12_none_{inst}.csv")


@pytest.mark.parametrize("inst", ["US100", "US500"])
def test_full_history_equals_frozen_output(inst):
    tr, _, _ = H.run_engine(H.to_m1(hist(inst)), inst)
    want = frozen(inst)
    assert len(tr) == len(want)
    for c in COLS:
        a, b = tr[c].reset_index(drop=True), want[c].reset_index(drop=True)
        if c in ("entry", "stop", "tp1", "draw", "r_multiple"):
            assert (a.astype(float) - b.astype(float)).abs().max() < 1e-9, c
        else:
            assert (a.astype(str) == b.astype(str)).all(), c


@pytest.mark.parametrize("inst", ["US100", "US500"])
def test_session_path_equals_frozen(inst):
    h = hist(inst); want = frozen(inst)
    reg = dict(registered=True, harness_matches_registered=True, registration_time_ny="2025-01-01 00:00:00-05:00")
    for _, w in want.iloc[::4].iterrows():                       # every 4th trade day (12 sessions per symbol)
        d = str(w.entry_time_ny)[:10]
        sl = h[(h.index >= pd.Timestamp(d, tz="America/New_York") - pd.Timedelta(days=60))]
        rows = [r for r in H.session_rows(sl, d, inst, "FINAL", reg, "t", {}) if r["status"] == "trade"]
        assert len(rows) >= 1, d
        r = next(r for r in rows if str(r["entry_time_ny"]) == str(w.entry_time_ny))
        assert abs(float(r["r_multiple"]) - float(w.r_multiple)) < 1e-9 and r["exit_reason"] == w.exit_reason


def test_holiday_and_min_bar_layer_on_history():
    """DATA fix 3: the three NYSE holiday/early-close trades (US100 2025-11-27, 2025-12-24, 2026-07-03) are excluded by the
    calendar layer; 2026-08-28 US500 (87/90 bars) passes the >= 86/90 rule."""
    pr = H.prereg()
    for d in ("2025-11-27", "2025-12-24", "2026-07-03"):
        # 2025 dates are in historical_additions; 2026-07-03 is a 2026 NYSE closure (Independence Day observed)
        st = H.F.calendar_status(d, {**pr, "holidays_excluded": {**pr["holidays_excluded"],
                                     "full_closures": pr["holidays_excluded"]["full_closures"] + ["2026-07-03"]}})
        assert st != "ok", d
    m1 = H.to_m1(hist("US500"))
    q = H.day_quality(m1, "2026-08-28")
    assert q["bars_0930_1059"] == 87 and q["min_bar_ok"]
