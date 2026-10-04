"""Screening pipeline guards (no market data is read by these tests)."""
import datetime as dt
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from research.screening import batch1, core, dl, nulls
from research.screening.s4_h016b import CLEARED, HARNESS_SHA256, SEALED, H016bSealedReader, Sealed
from ftn.research.bars import Series

HERE = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("sym", ["USATECHIDXUSD", "USA500IDXUSD", "US100", "US500", "EURUSD"])
def test_downloader_refuses_non_s1_instruments(sym):
    with pytest.raises(ValueError):
        dl.guard(sym, dt.date(2024, 1, 2))


@pytest.mark.parametrize("day", [dt.date(2022, 12, 30), dt.date(2019, 6, 3), dt.date(2026, 9, 26), dt.date(2026, 10, 5)])
def test_downloader_refuses_dates_outside_window(day):
    with pytest.raises(ValueError):
        dl.guard("DEUIDXEUR", day)


def test_downloader_window_and_root(monkeypatch):
    dl.guard("XAUUSD", dt.date(2023, 1, 2)); dl.guard("USA30IDXUSD", dt.date(2026, 9, 25))
    assert max(dl.days()) == dt.date(2026, 9, 25) and min(dl.days()) == dt.date(2023, 1, 1)
    monkeypatch.setenv("SCREENING_DATA", "/workspace/marketdata/x")
    with pytest.raises(SystemExit):
        dl.root()


def test_no_module_reads_marketdata_or_sealed_paths():
    for p in HERE.glob("*.py"):
        txt = p.read_text()
        for m in re.finditer(r"/workspace/marketdata", txt):
            ctx = txt[max(0, m.start() - 200): m.end() + 80]
            assert p.name == "dl.py" and ("refusing" in ctx or "never" in ctx), p
        assert "model-u-longrun/data" not in txt and "hermes-h016b-harness" not in txt, p


def test_s4_stub_is_sealed_by_default_and_touches_nothing():
    st, why = H016bSealedReader(None).status()
    assert st == SEALED and why == "no_sealed_dir_configured"
    with pytest.raises(Sealed):
        H016bSealedReader(None).results()


def test_s4_refuses_live_harness_dir():
    assert H016bSealedReader(Path("/home/box/hermes-x/forward/H016b/sealed")).status()[0] == SEALED


def test_s4_clearance_rules(tmp_path):
    r = H016bSealedReader(tmp_path)
    assert r.status() == (SEALED, "missing_DATA_CERTIFIED.json")
    (tmp_path / "DATA_CERTIFIED.json").write_text(json.dumps({"harness_sha256": HARNESS_SHA256}))
    (tmp_path / "CASSANDRA_CLEARED.json").write_text(json.dumps({"harness_sha256": "0" * 64}))
    assert r.status() == (SEALED, "digest_mismatch_CASSANDRA_CLEARED.json")
    (tmp_path / "CASSANDRA_CLEARED.json").write_text(json.dumps({"harness_sha256": HARNESS_SHA256}))
    (tmp_path / "log.csv").write_text("date,R\n2026-10-05,1.0\n")
    assert r.status()[0] == CLEARED and r.results() == [{"date": "2026-10-05", "R": "1.0"}]


def test_holm():
    h = core.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert h == pytest.approx({"a": 0.03, "c": 0.06, "b": 0.06})


def _toy(n_days=6):
    t, o, h, l, c, at, ao, ah, al, ac = ([] for _ in range(10))
    p = 100.0
    d0 = datetime(2026, 1, 5, 18, 0) - timedelta(days=1)
    for d in range(n_days * 2):
        base = d0 + timedelta(days=d)
        if base.weekday() in (4, 5):
            continue
        for m in range(0, 23 * 60, 7):
            ts = base + timedelta(minutes=m)
            p += ((m * 7 + d) % 5 - 2) * 0.1
            t.append(ts); o.append(p); h.append(p + .3); l.append(p - .3); c.append(p + .1)
            sp = 0.2 + (m % 3) * 0.05
            at.append(ts); ao.append(p + sp); ah.append(p + .3 + sp); al.append(p - .3 + sp); ac.append(p + .1 + sp)
    return Series("T", t, o, h, l, c), Series("T", at, ao, ah, al, ac)


def test_shuffled_day_keeps_bars_and_spreads():
    b, a = _toy()
    nb, na = nulls.shuffled_day(b, a, 7)
    assert len(nb.t) == len(b.t) and nb.t == sorted(nb.t)
    real = sorted(round(x - y, 9) for x, y in zip(a.c, b.c))
    syn = sorted(round(na.c[na.idx(t)] - nb.c[i], 9) for i, t in enumerate(nb.t))
    assert real == syn


def test_random_walk_keeps_timestamps_and_spread():
    b, a = _toy()
    nb, na = nulls.random_walk(b, a, 3)
    assert nb.t == b.t and na.t == a.t
    assert [round(x - y, 9) for x, y in zip(na.c, nb.c)] == [round(x - y, 9) for x, y in zip(a.c, b.c)]
    assert all(hh >= max(oo, cc) and ll <= min(oo, cc) for oo, hh, ll, cc in zip(nb.o, nb.h, nb.l, nb.c))


def test_constants_match_protocol():
    txt = (HERE / "PROTOCOL.md").read_text()
    assert batch1.ALPHA_SCREEN == 0.10 and "α_screen = 0.10" in txt
    assert batch1.N_NULL == 50 and "50 replicates per null type" in txt
    assert batch1.HOLDOUT_DAYS == {"US100": 1004, "US500": 1612} and "1,004" in txt and "1,612" in txt
    assert batch1.ERA_MULT == 1.5 and batch1.SHRINK == 0.5 and "×1.5" in txt and "0.5 × min(" in txt
    assert set(batch1.CANDIDATES) == {"C1", "C2", "C3"}


def test_power_formula():
    assert batch1.power(-0.1, 1.4, 1.3, 1000) == 0.025
    assert batch1.power(0.1, 1.4, 1.0, batch1.n_for_power(0.1, 1.4, 1.0)) == pytest.approx(0.8, abs=0.01)


def test_batch2_pins_and_params():
    from research.screening.batch2 import adapters as A
    from research.screening import run_batch2 as B
    assert A.verify_pins() == {}
    p = B.params("D6", "US100"); assert (p["tick"], p["min_swing"], p["root"], p["cost_rt"]) == (0.25, 3.0, "NQ", 2.55)
    p = B.params("D6", "US500", "frozen"); assert p["cost_rt"] == 0.5 and p["min_swing"] == 1.0
    p = B.params("D1", "US100", "frozen"); assert p["cost_per_side"] == 0.8
    g = B.params("D1", "XAUUSD"); assert abs(g["tick"] - 0.04241) < 1e-5 and abs(g["cost_rt"] - 1.402) < 1e-9
    assert set(B.HOLDOUT["D1"]) == {"US100"} and len(B.NAMES) == 6
