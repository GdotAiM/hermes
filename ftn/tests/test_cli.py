"""CLI entry points: ftn run / prep / brief / live-probe (paper only, isolated dirs)."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from ftn.__main__ import main
from ftn.paths import journal_dir, out_dir

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("cmd", ["run", "prep"])
def test_run_ticket_is_never_actionable_for_mint(cmd, capsys):
    assert main([cmd, "--fixture", str(ROOT / "fixtures" / "sample_eurusd.json"), "--bias", "bullish"]) == 0
    payload = json.loads(capsys.readouterr().out)
    t = payload["ticket"]
    assert t["actionable_for_mint"] is False
    assert t["kind"] in {"ftn_setup_ticket", "no_trade"} and t["kind"] != "entry_candidate"
    assert "side" not in t
    assert Path(payload["dispatch_path"]).parent == out_dir()


def test_same_second_runs_do_not_overwrite(capsys):
    for _ in range(3):
        assert main(["run"]) == 0
    capsys.readouterr()
    assert len(list(out_dir().glob("ftn_*.json"))) == 3
    assert len(list(journal_dir().glob("*_DECISION.md"))) == 3
    assert "not for MINT" in next(journal_dir().glob("*_DECISION.md")).read_text()


def test_run_routes_dtr_fixture_through_month9(capsys):
    """F2: `ftn run` on a DTR fixture is the Month 9 kernel (sole ticket authority), not the legacy four-count."""
    assert main(["run", "--fixture", str(ROOT / "fixtures" / "m9_reconstruction_eurusd.json")]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["engine"] == "month9_kernel"
    t = payload["ticket"]
    assert t["authority"] == "month9_kernel" and t["selected_module"] == "REV"
    assert t["actionable_for_mint"] is False and t["kind"] != "entry_candidate" and "side" not in t
    assert payload["trace"]["schema"] == "ftn.trace.v1"


def test_run_refuses_unknown_fixture_clearly(tmp_path, capsys):
    bad = tmp_path / "bad.json"
    bad.write_text(json.dumps({"symbol": "EURUSD"}))
    assert main(["run", "--fixture", str(bad)]) == 2
    err = capsys.readouterr().err
    assert "KeyError" not in err and "neither a Month 9 DTR fixture" in err


def test_live_probe_refuses_orders(capsys, monkeypatch):
    monkeypatch.delenv("FTN_LIVE_DATA", raising=False)
    assert main(["live-probe"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["data_allowed"] is False
    assert payload["orders"]["ok"] is False and payload["orders"]["reason"] == "live_orders_refused"
