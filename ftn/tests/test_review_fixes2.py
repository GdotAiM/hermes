"""Config parser hardening, journal collisions, undetermined bias, desk snapshot."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ftn.config_load import ConfigError, load_config, parse_yaml_subset

ROOT = Path(__file__).resolve().parents[1]


def _cfg(tmp_path, text):
    p = tmp_path / "config.yaml"
    p.write_text(text)
    return p


BASE = (ROOT / "config.yaml").read_text()


def test_repo_config_parses_and_validates():
    cfg = load_config()
    assert cfg["raw"]["sessions"]["ny_am"] == {"start": "07:00", "end": "10:00"}
    assert cfg["mint_allowlist"] == [] and cfg["equity_usd"] == 100000.0
    assert cfg["max_daily_loss_pct"] == 2.0 and cfg["max_portfolio_dd_pct"] == 5.0


@pytest.mark.parametrize("mutate,msg", [
    (lambda t: t.replace("mode: paper", "mode: paperr"), "not in"),
    (lambda t: t.replace("live_enabled: false", "live_enabled: nope"), "expected true/false"),
    (lambda t: t.replace("max_trade_risk_pct: 0.5", "max_trade_risk_pct: 150"), "above maximum"),
    (lambda t: t.replace("max_trade_risk_pct: 0.5", "max_trade_risk_pct: half"), "expected a number"),
    (lambda t: t.replace("raise_requires: human", "raise_requires: agent"), "not in"),
    (lambda t: t + "\nsurprise_key: 1\n", "unknown key"),
    (lambda t: t.replace("  - ny_am\n", "  - tokyo\n", 1), "not defined under sessions"),
    (lambda t: t.replace('ny_am: { start: "07:00", end: "10:00" }', 'ny_am: { start: "7am", end: "10:00" }'), "HH:MM"),
    (lambda t: t + "\nmode: paper\n", "duplicate key"),
    (lambda t: t.replace("mint_allowlist: []", "mint_allowlist:\n  - { id: FTN, kind: paper_pilot }"), "not an M9 entry model"),
    (lambda t: t.replace("mint_allowlist: []", "mint_allowlist:\n  - { id: REV, kind: paper_pilot }"), "requires stamp"),
    (lambda t: t.replace("mint_allowlist: []", "mint_allowlist:\n  - { id: REV, kind: vibes }"), "kind"),
    (lambda t: t.replace("mint_allowlist: []", "mint_allowlist:\n  - { id: REV, kind: survives }"), "board_ref"),
    (lambda t: t.replace("mode: paper", "mode: live"), "requires live_enabled"),
])
def test_config_errors_are_clear(tmp_path, mutate, msg):
    with pytest.raises(ConfigError) as e:
        load_config(_cfg(tmp_path, mutate(BASE)))
    assert msg in str(e.value) and "config.yaml" in str(e.value)


def test_parser_rejects_unsupported_yaml(tmp_path):
    for bad in ("a: [1, 2]\n", "a: &x 1\n", "a:\n\tb: 1\n", "a: {b: 1\n"):
        with pytest.raises(ConfigError):
            parse_yaml_subset(bad)


def test_parser_subset():
    doc = parse_yaml_subset('a: 1\nb:\n  c: "x # not comment"  # comment\n  d: [ ]\nl:\n  - p\n  - { id: R, n: 2 }\n'.replace("[ ]", "[]"))
    assert doc == {"a": 1, "b": {"c": "x # not comment", "d": []}, "l": ["p", {"id": "R", "n": 2}]}


def test_ftn_config_env(tmp_path, monkeypatch):
    monkeypatch.setenv("FTN_CONFIG", str(_cfg(tmp_path, BASE.replace("min_atr_pips: 20", "min_atr_pips: 33"))))
    assert load_config()["min_atr_pips"] == 33.0




def test_bias_undetermined_withholds_four(tmp_path):
    from ftn.engine.levels import build_families, count_four, detect_bias
    from ftn.workflow.orchestrator import run_workflow
    raw = json.loads((ROOT / "fixtures/sample_eurusd.json").read_text())
    raw.pop("htf_bias")
    assert detect_bias(raw, "auto") == "undetermined"
    assert count_four(build_families(raw), bias="undetermined", price=raw["last"]) == []
    fx = tmp_path / "nobias.json"
    fx.write_text(json.dumps(raw))
    out = run_workflow(symbol="EURUSD", fixture=fx, bias="auto", price=None, stage="all", out_dir=tmp_path)
    t = out["ticket"]
    assert t["four_levels"] == [] and t["bias"] == "undetermined"
    assert "bias_undetermined" in t["no_trade_reasons"] and t["kind"] == "no_trade"
    out2 = run_workflow(symbol="EURUSD", fixture=fx, bias="bearish", price=None, stage="all", out_dir=tmp_path)
    assert len(out2["ticket"]["four_levels"]) == 4  # explicit --bias still counts


def test_kernel_ftn_undetermined_in_briefing(tmp_path, monkeypatch):
    from ftn.os.briefing import brief_from_fixture
    raw = json.loads((ROOT / "fixtures/m9_reconstruction_eurusd.json").read_text())
    raw["pair_institutional"]["daytrade_iof"] = {"daily": "unclear", "h4": "unclear", "m60": "unclear"}
    raw["pair_institutional"]["state"] = "unclear"
    fx = tmp_path / "unclear.json"
    fx.write_text(json.dumps(raw))
    st, cands, md, ftn = brief_from_fixture(fx)
    assert st.context.pair_institutional.state == "unclear"
    assert ftn["four"] == [] and ftn["four_reason"] == "bias_undetermined"
    assert "bias undetermined" in md and "withheld" in md



