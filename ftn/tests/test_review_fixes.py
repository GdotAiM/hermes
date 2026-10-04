"""Regression tests for fixes made in the 2026-10-04 review."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fingerprint_stable_across_processes():
    code = (
        "from ftn.os.dtr import build_context;from ftn.os.contracts import freeze_market_state;"
        "print(freeze_market_state(build_context('fixtures/m9_raw_eurusd.json')).fingerprint)"
    )
    outs = set()
    for seed in ("1", "2"):
        env = {**os.environ, "PYTHONHASHSEED": seed, "PYTHONPATH": str(ROOT / "src")}
        outs.add(subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                                capture_output=True, text=True, check=True).stdout.strip())
    assert len(outs) == 1








def test_config_loads_killzones_and_caps():
    from ftn.config_load import load_config
    cfg = load_config()
    assert cfg["killzones"] == ["london", "ny_am"]
    assert cfg["max_trade_risk_pct"] == 0.5
    assert cfg["mode"] == "paper" and cfg["live_enabled"] is False


def test_mint_draft_never_defaults_direction():
    from ftn.os.mint_draft import draft_from_handoff
    for module in ("BB", "PIP20", "CONSO", "REV"):
        h = {"candidates": [{"module": module, "state": "selected"}],
             "market_state": {"institutional": {"state": "unclear"}}}
        d = draft_from_handoff(h)
        assert "side" not in d and d["actionable_for_mint"] is False
        assert d["direction_hypothesis"] == "unclear"
        assert d["blocked_by"].startswith(("kernel_ticket:", "direction:"))
