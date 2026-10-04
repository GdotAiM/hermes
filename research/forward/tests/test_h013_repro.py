"""H013 harness reproduces the FROZEN v1 rule on the existing Dukascopy BID history: the harness code path
(consumed() slice -> evaluate()) must give the same trades as the frozen longrun.py outputs
(trades.csv = FILL_THRU 0 as reported; data/trades_cost1x_thru1.csv = FILL_THRU 1, the frozen forward setting)."""
import ast, pathlib
import pandas as pd, pytest
from conftest import DUKA_MU
import h013 as H

pytestmark = pytest.mark.skipif(not (DUKA_MU / "data/US100_1m.parquet").exists(), reason="Dukascopy history not on this box")
COLS = ["date", "direction", "type", "entry_time_ny", "entry", "stop", "t1", "t2", "R_T1", "R_T2", "R_5050", "out_5050", "exit_time_5050"]


def frozen_holidays():
    src = (H.FROZEN / "research/model-u-longrun/scripts/longrun.py").read_text()
    node = next(n for n in ast.parse(src).body if isinstance(n, ast.Assign) and getattr(n.targets[0], "id", "") == "HOLIDAYS")
    return ast.literal_eval(node.value)


def replay(inst, fill_thru, days=None):
    df = pd.read_parquet(DUKA_MU / f"data/{inst}_1m.parquet")[["Open", "High", "Low", "Close"]].astype(float)
    hol = frozen_holidays(); rows = []
    for d in pd.bdate_range("2025-09-02", "2026-09-25"):
        d = d.strftime("%Y-%m-%d")
        if days and d not in days: continue
        if d in hol or H.bars_in_window(df, d) < H.MIN_BARS: continue      # longrun.trading_days()
        r = H.evaluate(H.consumed(df, d), d, inst, fill_thru=fill_thru)
        if r["status"] == "trade": rows.append(r)
    return pd.DataFrame(rows)


def frozen(fname, inst):
    t = pd.read_csv(DUKA_MU / fname)
    t = t[(t.model == "v1 base") & (t.inst == inst) & (t.status == "trade")].rename(columns={})
    return t


@pytest.mark.parametrize("inst", ["US100", "US500"])
@pytest.mark.parametrize("fill_thru,fname", [(1, "data/trades_cost1x_thru1.csv"), (0, "trades.csv")])
def test_harness_equals_frozen_longrun(inst, fill_thru, fname):
    got = replay(inst, fill_thru).reset_index(drop=True)
    want = frozen(fname, inst).reset_index(drop=True)
    assert len(got) == len(want), (len(got), len(want))
    for c in COLS:
        if got[c].dtype.kind == "f":
            assert (got[c] - want[c]).abs().max() < 1e-9, c
        else:
            assert (got[c].astype(str) == want[c].astype(str)).all(), c


def test_engine_pins_and_settings():
    E1, V1 = H.load_engine()
    assert pathlib.Path(E1.__file__).resolve().parent == H.V1_DIR.resolve()
    assert E1.FILL_THRU == 1 and H.costs()["US100"] == 0.8
    assert H.prereg()["engine_settings"] == {"FILL_THRU_ticks": 1, "SLIP_ticks": 3.2, "cost_per_side_pts": 0.8, "tick": 0.25}
