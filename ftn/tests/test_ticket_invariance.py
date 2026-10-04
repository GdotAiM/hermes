"""F1 guard: the Month 9 kernel ticket set stays byte-identical to the H016 registration CSVs.

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
def test_trade_csv_byte_identical_to_h016_registration(base, sym):
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
