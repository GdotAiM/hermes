"""F1 guard: the Month 9 kernel ticket set stays byte-identical to the H016b registration inputs (the burned H016
trade CSVs; H016b superseded H016 pre-data with the same rule pins), and H016b's own eligibility filters drop
exactly the 4 trades its prereg lists (258 -> 254).

Burned window 2025-08-25 -> 2026-09-25 only (the R in those CSVs was published at registration).
Skipped, loudly, when the canonical burned tape is not on the machine (e.g. CI).
"""
from __future__ import annotations

import pytest

from ftn.pipeline import invariance as inv

pytestmark = pytest.mark.skipif(bool(inv.check_data()), reason=f"burned guard tape unavailable: {inv.check_data()}")


@pytest.fixture(scope="module")
def hists():
    return inv.load_histories()


@pytest.fixture(scope="module")
def base(hists, tmp_path_factory):
    return inv.regenerate(tmp_path_factory.mktemp("guard_base"), hists)


@pytest.fixture(scope="module")
def traced(hists, tmp_path_factory):
    return inv.regenerate(tmp_path_factory.mktemp("guard_trace"), hists, trace=True)


@pytest.mark.parametrize("sym", ["US100", "US500"])
def test_trade_csv_byte_identical_to_h016b_registration_inputs(base, sym):
    c = inv.compare(base)[sym]
    assert c["identical"], c
    assert c["n_trades"] == {"US100": 146, "US500": 112}[sym]
    assert c["n_tickets"] == {"US100": 185, "US500": 167}[sym]


@pytest.mark.parametrize("sym", ["US100", "US500"])
def test_trace_does_not_change_tickets(base, traced, sym):
    """With the per-ticket trace + bar-derived context layers attached, the bytes are the same."""
    assert inv.compare(traced)[sym]["identical"]
    strip = lambda log: [{k: v for k, v in r.items() if k != "trace"} for r in log]
    assert strip(traced[sym]["log"]) == strip(base[sym]["log"])
    with_trace = [r for r in traced[sym]["log"] if r["ticket"]]
    assert with_trace and all("trace" in r for r in with_trace)


def test_guard_references_h016b_prereg():
    import hashlib
    d = inv.prereg()
    assert d["id"] == "H016b" and inv.PREREG_ID == "H016b"
    for sym in ("US100", "US500"):
        p = inv.registration_csv(sym)
        rel = str(p.relative_to(p.parents[3]))
        assert d["code"]["registration_inputs_sha256"][rel] == hashlib.sha256(p.read_bytes()).hexdigest()


def test_h016b_filters_drop_exactly_the_prereg_list(hists):
    e = inv.h016b_eligibility(hists)
    assert e["n_trades"] == 258 and e["n_eligible"] == 254 and len(e["dropped"]) == 4
    assert e["matches_prereg"], e
    assert set(e["prereg_list"]) == {"US100 2026-03-23 ny_am", "US100 2026-05-29 london",
                                     "US500 2026-04-10 ny_am", "US500 2026-05-29 london"}
    # the same 4 as the registered power sim's EXCLUDE set, and its 254-trade burned mean (+0.0828)
    import csv, re
    sim = (inv.registration_csv("US100").parent / "H016b_POWER_SIM_2026-10-04.py").read_text()
    excl = set(re.findall(r'\("(US\d00)", "(\d{4}-\d\d-\d\d)", "(\w+)"\)', sim))
    assert {" ".join(k) for k in excl} == set(e["dropped"])
    rs = [float(r["R"]) for s in ("US100", "US500") for r in csv.DictReader(open(inv.registration_csv(s)))
          if f"{s} {r['date']} {r['session']}" not in e["dropped"]]
    assert len(rs) == 254 and abs(sum(rs) / 254 - inv.prereg()["power_calculation"]
                                  ["measured_on_filter_eligible_burned_trades"]["mean_R_burned"]) < 5e-5
    assert "feed_gap_entry_BID" in e["dropped"]["US100 2026-03-23 ny_am"]["why"]   # the F1 stale-entry phantom fill
