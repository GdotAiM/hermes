"""MINT logs FTN's research-draft gate chain read-only. Never an entry_candidate, never an order."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from mint.dispatch.ftn_gate import TRADING_ROOT, read_ftn_gate

GATES = [
    {"gate": "kernel_ticket", "pass": True, "reason": "kernel_session_ticket"},
    {"gate": "direction", "pass": True, "reason": "determined"},
    {"gate": "risk", "pass": True, "reason": "within_caps"},
    {"gate": "allowlist", "pass": False, "reason": "not_on_mint_allowlist"},
    {"gate": "mode", "pass": True, "reason": "paper"},
    {"gate": "contract", "pass": False, "reason": "hermes_integration_i0_ftn_never_actionable"},
]


def _draft(d: Path, **kw) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    x = {"kind": "ftn_research_draft", "mode": "paper", "module": "REV", "direction_hypothesis": "bullish",
         "date": "2017-05-30", "symbol": "EURUSD", "actionable_for_mint": False,
         "blocked_by": "allowlist:not_on_mint_allowlist", "gates_before_contract_pass": False, "gates": GATES}
    x.update(kw)
    (d / "ftn_draft_latest.json").write_text(json.dumps(x))
    return d


def test_missing_draft_is_log_only(tmp_path):
    r = read_ftn_gate(tmp_path / "nope")
    assert r["present"] is False and r["mint_decision"] == "log_only"


def test_blocked_draft_is_log_only(tmp_path):
    r = read_ftn_gate(_draft(tmp_path / "d"))
    assert r["consistent"] and r["mint_decision"] == "log_only"
    assert r["reason"] == "ftn_blocked_by:allowlist:not_on_mint_allowlist"
    assert r["orders"].startswith("none") and "side" not in r


def test_all_gates_but_contract_pass_is_still_log_only(tmp_path):
    g = [dict(x, **({"pass": True, "reason": "allowlisted_paper_pilot"} if x["gate"] == "allowlist" else {}))
         for x in GATES]
    r = read_ftn_gate(_draft(tmp_path / "d", gates=g, gates_before_contract_pass=True,
                             blocked_by="contract:hermes_integration_i0_ftn_never_actionable"))
    assert r["consistent"] and r["mint_decision"] == "log_only"


@pytest.mark.parametrize("bad,problem", [
    ({"actionable_for_mint": True}, "claims_actionable"),
    ({"side": "buy"}, "carries_side"),
    ({"blocked_by": "risk:within_caps"}, "blocked_by_not_first_failure"),
    ({"gates": GATES[:5]}, "gate_order"),
    ({"gates": GATES[:5] + [{"gate": "contract", "pass": True, "reason": "x"}]}, "contract_gate_not_failing"),
    ({"mode": "live"}, "non_paper_mode"),
    ({"kind": "mint_paper_draft"}, "kind_not_ftn_research_draft"),
])
def test_inconsistent_or_actionable_claims_are_flagged_and_still_log_only(tmp_path, bad, problem):
    r = read_ftn_gate(_draft(tmp_path / "d", **bad))
    assert r["consistent"] is False and problem in r["problems"]
    assert r["mint_decision"] == "log_only"


def test_module_cannot_return_entry_candidate():
    src = (TRADING_ROOT / "src/mint/dispatch/ftn_gate.py").read_text()
    assert "entry_candidate" not in src.split('"""', 2)[2]  # only the docstring mentions it


FTN_ROOT = TRADING_ROOT.parent / "ftn"


@pytest.mark.skipif(not (FTN_ROOT / "src" / "ftn").is_dir(), reason="ftn/ not in this checkout")
def test_end_to_end_ftn_brief_then_mint_scan(tmp_path):
    env = dict(os.environ, FTN_OUT_DIR=str(tmp_path / "out"), FTN_JOURNAL_DIR=str(tmp_path / "j"),
               FTN_DRAFT_DIR=str(tmp_path / "drafts"), FTN_WRITE_MINT_DRAFT="1",
               PYTHONPATH=str(FTN_ROOT / "src"))
    subprocess.run([sys.executable, "-m", "ftn", "brief", "--fixture", "fixtures/m9_raw_eurusd.json"],
                   cwd=FTN_ROOT, env=env, check=True, capture_output=True)
    r = read_ftn_gate(tmp_path / "drafts")
    assert r["present"] and r["consistent"], r
    assert r["module"] == "REV" and r["direction_hypothesis"] == "bullish"
    assert r["blocked_by"] == "allowlist:not_on_mint_allowlist" and r["mint_decision"] == "log_only"
    from mint.dispatch.scan_clears import main
    research = TRADING_ROOT.parent / "research"
    assert main(["--hermes-x", str(research), "--out", str(tmp_path / "mint"),
                 "--ftn-drafts", str(tmp_path / "drafts")]) == 0
    latest = json.loads((tmp_path / "mint" / "latest.json").read_text())
    assert latest["ftn_gate_chain"]["mint_decision"] == "log_only"
    assert latest["ftn_gate_chain"]["gates"] == r["gates"]
    assert all(t.get("kind") != "entry_candidate" or not str(t.get("strategy_id", "")).startswith("FTN")
               for t in latest.get("tickets", []))
