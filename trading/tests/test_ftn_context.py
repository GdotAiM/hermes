"""MINT ↔ FTN DayContext: the reader is context-only and can never emit orders."""
from __future__ import annotations

import ast
import copy
import json
import urllib.request
from pathlib import Path

import pytest

from mint.adapters import alpaca_paper_stub as stub
from mint.dispatch import ftn_context as fc

SAMPLES = sorted((fc.MONOREPO_ROOT / "ftn" / "dispatch" / "samples").glob("handoff_v1_*.json"))
M9 = next(p for p in SAMPLES if "m9_" in p.name)
PAM = next(p for p in SAMPLES if "pam1_" in p.name)



def _spine(root: Path, decision: str) -> Path:
    (root / "summaries").mkdir(parents=True)
    (root / "beliefs").mkdir(parents=True)
    (root / "summaries" / "2026-01-01_HFTN_BOARD_LOCK.md").write_text(
        f"# HFTN\n\n## Decision\n\n{decision}\n", encoding="utf-8"
    )
    (root / "beliefs" / "LEDGER.md").write_text("| date | belief |\n|---|---|\n", encoding="utf-8")
    return root


@pytest.fixture
def no_network_no_orders(monkeypatch):
    """Any broker/network path explodes — proves the reader never reaches one."""
    calls = []

    def boom(*a, **k):
        calls.append((a, k))
        raise AssertionError("ftn_context reached a broker / network path")

    monkeypatch.setattr(urllib.request, "urlopen", boom)
    monkeypatch.setattr(stub, "http_json", boom)
    monkeypatch.setattr(stub, "cmd_place_order", boom)
    monkeypatch.setattr(stub, "cmd_account", boom)
    return calls


def _orderish_keys(obj, path="$"):
    hits = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k.lower() in {"side", "qty", "quantity", "order", "orders", "order_id", "order_type",
                             "limit_price", "stop_price", "time_in_force", "client_order_id", "notional"}:
                hits.append(f"{path}.{k}")
            hits += _orderish_keys(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            hits += _orderish_keys(v, f"{path}[{i}]")
    return hits


@pytest.mark.parametrize("decision", ["FAILS — no edge.", "INCONCLUSIVE — park.", "SURVIVES — cleared by board."])
@pytest.mark.parametrize("sample", SAMPLES, ids=lambda p: p.name)
def test_reader_never_emits_orders(tmp_path, no_network_no_orders, decision, sample):
    """Even with REV selected, a FTN session_ticket, PAM1 required_complete AND a
    board SURVIVES, the reader writes context only: no order intents, no order fields,
    no broker/network call."""
    spine = _spine(tmp_path / "research", decision)
    out = tmp_path / "out"
    rc = fc.main(["--handoff", str(sample), "--hermes-x", str(spine), "--out", str(out)])
    assert rc == 0
    assert no_network_no_orders == []
    files = sorted(p.name for p in out.iterdir())
    assert files == ["ftn_context_latest.json"]  # no dispatch/order/draft files
    rec = json.loads((out / "ftn_context_latest.json").read_text())
    assert rec["kind"] == "ftn_day_context"
    ex = rec["execution"]
    assert ex["actionable_for_mint"] is False
    assert ex["order_intents_emitted"] == 0
    assert ex["pam1_used_for_execution"] is False
    assert ex["ftn_candidates_used_for_execution"] is False
    assert _orderish_keys(rec) == []
    if decision.startswith("SURVIVES"):
        assert rec["board_gate"]["status"] == "cleared_strategies_exist"
        assert "human paper ack" in ex["why"] and "never places" in ex["why"]
    else:
        assert rec["board_gate"]["status"] == "blocked_no_survives"


def test_real_monorepo_board_blocks(tmp_path, no_network_no_orders):
    """Against the real in-repo research spine: whatever the board says, zero order intents."""
    rc = fc.main(["--handoff", str(M9), "--out", str(tmp_path)])
    assert rc == 0
    rec = json.loads((tmp_path / "ftn_context_latest.json").read_text())
    assert rec["execution"]["order_intents_emitted"] == 0
    assert rec["context"]["ftn_session_ticket_id"]  # FTN ticket is carried as context only


@pytest.mark.parametrize(
    "mutate",
    [
        lambda h: h.__setitem__("side", "buy"),
        lambda h: h["candidates"][0].__setitem__("pam_rank", 1),
        lambda h: h["market_state"].__setitem__("best_pam", "pam1"),
        lambda h: h["market_state"]["institutional"].__setitem__("confidence", "high"),
        lambda h: h.__setitem__("broker_instruction", {"x": 1}),
        lambda h: h["session_ticket"].__setitem__("qty", 1),
        lambda h: h["notes"].append("BUY"),
        lambda h: h.__setitem__("kind", "mint_paper_draft"),
    ],
)
def test_banned_handoff_rejected_nothing_written(tmp_path, no_network_no_orders, mutate):
    h = json.loads(M9.read_text())
    bad = copy.deepcopy(h)
    mutate(bad)
    p = tmp_path / "bad.json"
    p.write_text(json.dumps(bad))
    out = tmp_path / "out"
    assert fc.main(["--handoff", str(p), "--out", str(out)]) == 1
    assert not out.exists() or not any(out.iterdir())


def test_ftn_mint_draft_is_not_accepted(tmp_path):
    """FTN also writes mint_draft_*.json (with a side field). It is NOT the contract."""
    draft = {"kind": "mint_paper_draft", "mode": "paper", "side": "buy", "symbol": "EURUSD"}
    p = tmp_path / "mint_draft_latest.json"
    p.write_text(json.dumps(draft))
    with pytest.raises(fc.HandoffRejected):
        fc.load_handoff(p)


def test_module_has_no_broker_or_network_imports():
    tree = ast.parse(Path(fc.__file__).read_text())
    mods = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            mods |= {a.name for a in node.names}
        elif isinstance(node, ast.ImportFrom):
            mods.add(node.module or "")
            mods |= {f"{node.module}.{a.name}" for a in node.names}
    assert not any("alpaca" in m or "urllib" in m or "requests" in m or "http" in m for m in mods), mods
    src = Path(fc.__file__).read_text()
    assert "place_order(" not in src and "cmd_place_order" not in src


def test_paper_limits_are_hard():
    limits = fc.paper_limits_from_config()
    assert limits["starting_usd"] == 100000
    assert limits["max_trade_risk_pct"] == 0.5
    assert limits["max_daily_loss_pct"] == 2.0
    assert limits["max_portfolio_dd_pct"] == 5.0
    assert limits["live_enabled"] is False and limits["mode"] == "paper"
    fc.assert_paper_limits(limits)
    with pytest.raises(SystemExit):
        fc.assert_paper_limits({**limits, "max_trade_risk_pct": 1.0})
    with pytest.raises(SystemExit):
        fc.assert_paper_limits({**limits, "live_enabled": True})


def test_ban_list_matches_ftn_contract():
    """MINT keeps its own copy of the ban list; it must not drift from FTN's."""
    p = fc.MONOREPO_ROOT / "ftn" / "src" / "ftn" / "os" / "handoff_contract.py"
    if not p.is_file():
        pytest.skip("ftn/ not present")
    tree = ast.parse(p.read_text())
    ftn_keys = None
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", "") == "BANNED_KEYS" for t in node.targets):
            ftn_keys = set(ast.literal_eval(node.value.args[0]))
    assert ftn_keys == set(fc.BANNED_KEYS)
