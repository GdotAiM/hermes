"""Research-draft gate chain: kernel_ticket → direction → risk → allowlist → mode → contract.

Every gate is exercised passing and blocked. Main's HERMES_INTEGRATION_I0 stays
authoritative: the draft never carries a buy/sell side and is never MINT-actionable
(gate 6, ``contract``). brief markdown, the written draft and ``draft_status`` agree.
"""

from __future__ import annotations

import copy
import json
from datetime import date
from pathlib import Path

import pytest

from ftn.config_load import load_config
from ftn.os.briefing import brief_from_fixture, draft_status
from ftn.os.handoff import build_handoff
from ftn.os.mint_draft import allowlist_gate, draft_from_handoff, gate_input, mode_gate, risk_gate

ROOT = Path(__file__).resolve().parents[1]
REV_FX = ROOT / "fixtures/m9_raw_eurusd.json"
FLAT = {"daily_loss_pct": 0.0, "drawdown_pct": 0.0, "source": "test"}


def _pilot_cfg(tmp_path, ids=("REV", "CONSO", "BB", "PIP20"), expires="2099-01-01"):
    stamp = tmp_path / "stamp.md"
    stamp.write_text("pilot stamp (test)\nSignature: Test Human\n")
    cfg = load_config()
    cfg["mint_allowlist"] = [
        {"id": m, "kind": "paper_pilot", "stamp": str(stamp), "expires": expires, "kill": "test"}
        for m in ids
    ]
    return cfg


def _pilot_config_file(tmp_path, ids=("REV",)):
    stamp = tmp_path / "stamp.md"
    stamp.write_text("pilot stamp (test)\nSignature: Test Human\n")
    text = (ROOT / "config.yaml").read_text()
    entries = "\n".join(
        f'  - {{ id: {m}, kind: paper_pilot, stamp: "{stamp}", expires: "2099-01-01", kill: "test" }}'
        for m in ids
    )
    text = text.replace("mint_allowlist: []", "mint_allowlist:\n" + entries)
    p = tmp_path / "config.yaml"
    p.write_text(text)
    return p


def _handoff(fx=REV_FX):
    st, cands, _, ftn = brief_from_fixture(fx)
    return gate_input(st, build_handoff(st, cands, ftn))


@pytest.fixture
def fresh(tmp_path):
    return tmp_path  # conftest already isolates FTN_OUT_DIR / FTN_DRAFT_DIR per test


CONTRACT = "contract:hermes_integration_i0_ftn_never_actionable"


def _gate(d, name):
    return next(g for g in d["gates"] if g["gate"] == name)


# ---------------------------------------------------------- whole chain

def test_default_config_blocks_on_allowlist(fresh):
    d = draft_from_handoff(_handoff(), book=FLAT)
    assert d["actionable_for_mint"] is False
    assert d["blocked_by"] == "allowlist:not_on_mint_allowlist"
    assert [g["gate"] for g in d["gates"]] == ["kernel_ticket", "direction", "risk", "allowlist", "mode", "contract"]
    assert d["blocked"] == ["allowlist:not_on_mint_allowlist", CONTRACT]
    assert "side" not in d and d["kind"] == "ftn_research_draft"


def test_full_chain_with_human_pilot_still_stops_at_contract(fresh):
    d = draft_from_handoff(_handoff(), cfg=_pilot_cfg(fresh), book=FLAT)
    assert d["actionable_for_mint"] is False  # I0: FTN is never MINT-actionable
    assert d["gates_before_contract_pass"] is True
    assert d["blocked_by"] == CONTRACT and d["blocked"] == [CONTRACT]
    assert d["direction_hypothesis"] == "bullish" and d["module"] == "REV" and "side" not in d
    assert d["risk_pct"] == 0.5 and abs(d["risk_usd"] - 500.0) < 1e-9
    assert d["stop_reference"] < d["entry_reference"]


# ---------------------------------------------------------- gate 1 kernel_ticket

def test_kernel_ticket_gate(fresh):
    h = _handoff()
    cfg = _pilot_cfg(fresh)
    assert _gate(draft_from_handoff(h, cfg, FLAT), "kernel_ticket")["pass"] is True
    no_ticket = {**h, "session_ticket": None}
    d = draft_from_handoff(no_ticket, cfg, FLAT)
    assert d["blocked_by"] == "kernel_ticket:no_session_ticket" and not d["actionable_for_mint"]
    other = {**h, "session_ticket": {**h["session_ticket"], "module": "CONSO"}}
    assert draft_from_handoff(other, cfg, FLAT)["blocked_by"] == "kernel_ticket:session_ticket_module_mismatch"
    nothing = {**h, "candidates": [{**c, "state": "ineligible"} for c in h["candidates"]]}
    assert draft_from_handoff(nothing, cfg, FLAT) is None


def test_context_layers_never_issue_tickets(fresh):
    """Months 1–8, 10–12, Charter, Model 13: context only → no draft, ever."""
    for name in ("integration_m1_m9_eurusd.json", "m13_bridge_eurusd.json", "charter_evidence_eurusd.json",
                 "m12_evidence_eurusd.json", "m7_path_eurusd.json", "m8_path_eurusd.json"):
        h = _handoff(ROOT / "fixtures" / name)
        assert draft_from_handoff(h, _pilot_cfg(fresh), FLAT) is None, name
        assert draft_status(h)["blocked_by"] == "kernel_ticket:no_selected_candidate"


def test_context_layers_do_not_change_gate_result(fresh, tmp_path):
    raw = json.loads(REV_FX.read_text())
    ctx_raw = copy.deepcopy(raw)
    ctx_raw["month12"] = {"identified_top_down": "present", "long_term_note": "present"}
    ctx_raw["evidence"]["model13_bridge"] = "present"
    fx = tmp_path / "with_ctx.json"
    fx.write_text(json.dumps(ctx_raw))
    cfg = _pilot_cfg(fresh)
    a = draft_from_handoff(_handoff(REV_FX), cfg, FLAT)
    b = draft_from_handoff(_handoff(fx), cfg, FLAT)
    for k in ("actionable_for_mint", "blocked_by", "direction_hypothesis", "module", "stop_reference", "risk_usd"):
        assert a[k] == b[k], k


# ---------------------------------------------------------- gate 2 direction

def test_direction_gate(fresh):
    """REV direction comes from the raid (D18 fix), BB/PIP20 from the daytrade IOF."""
    h = _handoff()
    cfg = _pilot_cfg(fresh)
    bear = copy.deepcopy(h)
    bear["market_state"]["institutional"]["state"] = "bearish"  # IOF no longer sets REV direction
    d = draft_from_handoff(bear, cfg, FLAT)
    assert d["direction_hypothesis"] == "bullish" and d["direction_source"] == "raid"
    assert d["gates_before_contract_pass"] is True
    both = copy.deepcopy(h)
    both["execution_context"]["raid"]["also"] = ["pdh"]
    d = draft_from_handoff(both, cfg, FLAT)
    assert d["direction_hypothesis"] == "unclear" and d["blocked_by"] == "direction:undetermined"
    none = copy.deepcopy(h)
    none["execution_context"]["raid"] = {"level": None, "price": None, "taken": False, "also": None}
    assert draft_from_handoff(none, cfg, FLAT)["blocked_by"] == "direction:undetermined"
    bb = copy.deepcopy(h)
    bb["candidates"] = [{**x, "state": "selected" if x["module"] == "BB" else "ineligible"} for x in bb["candidates"]]
    bb["session_ticket"] = {**bb["session_ticket"], "module": "BB"}
    bb["market_state"]["institutional"]["state"] = "unclear"
    d = draft_from_handoff(bb, cfg, FLAT)
    assert d["direction_hypothesis"] == "unclear" and d["blocked_by"] == "direction:undetermined"


def test_plain_handoff_has_no_gate_evidence(fresh):
    """Without the in-memory execution context, REV direction is undetermined; the draft
    keeps main's I0 meaning (IOF label, context only) and says so."""
    st, cands, _, ftn = brief_from_fixture(REV_FX)
    d = draft_from_handoff(build_handoff(st, cands, ftn), _pilot_cfg(fresh), FLAT)
    assert d["blocked_by"] == "direction:undetermined"
    assert d["direction_source"] == "iof_label_only_no_execution_context"


def _conso_handoff(h, edge, box=(1.1211, 1.1142)):
    c = copy.deepcopy(h)
    c["candidates"] = [{**x, "state": "selected" if x["module"] == "CONSO" else "ineligible"} for x in c["candidates"]]
    c["session_ticket"] = {**c["session_ticket"], "module": "CONSO"}
    c["execution_context"]["box"] = {"high": box[0], "low": box[1]}
    c["execution_context"]["conso_raided_edge"] = edge
    return c


def test_conso_side_from_raided_edge_not_iof(fresh):
    h = _handoff()
    cfg = _pilot_cfg(fresh)
    low = _conso_handoff(h, "low")
    low["market_state"]["institutional"]["state"] = "bearish"  # IOF must not matter
    d = draft_from_handoff(low, cfg, FLAT)
    assert d["direction_hypothesis"] == "bullish" and d["stop_reference"] == 1.1142
    assert d["gates_before_contract_pass"] is True and d["actionable_for_mint"] is False
    high = _conso_handoff(h, "high")
    high["last"] = 1.1200
    high["market_state"]["institutional"]["state"] = "bullish"
    d = draft_from_handoff(high, cfg, FLAT)
    assert d["direction_hypothesis"] == "bearish" and d["stop_reference"] == 1.1211
    none = _conso_handoff(h, None)
    d = draft_from_handoff(none, cfg, FLAT)
    assert d["direction_hypothesis"] == "unclear" and d["blocked_by"] == "direction:undetermined"


def test_raided_edge_helper():
    from ftn.models.conso import conso_side, raided_edge
    box = {"high": 1.12, "low": 1.11}
    assert raided_edge(box, {"taken": True, "price": 1.11}) == "low"
    assert raided_edge(box, {"taken": True, "price": 1.1095}) == "low"
    assert raided_edge(box, {"taken": True, "price": 1.1201}) == "high"
    assert raided_edge(box, {"taken": True, "price": 1.115}) is None
    assert raided_edge(box, {"taken": False, "price": 1.11}) is None
    assert raided_edge(None, {"taken": True, "price": 1.11}) is None
    assert raided_edge(box, {"taken": True, "level": "box_high"}) == "high"
    assert conso_side(box, {"taken": True, "price": 1.11}) == "buy"
    assert conso_side(box, {"taken": True, "price": 1.115}) is None


def test_conso_raided_edge_on_fixtures(fresh):
    from ftn.os.contracts import freeze_market_state
    from ftn.os.dtr import build_context
    from ftn.models.conso import evaluate_conso
    st = freeze_market_state(build_context(ROOT / "fixtures/m9_conso_fade_only.json"))
    assert evaluate_conso(st)["raided_edge"] == "low"
    h = _handoff(ROOT / "fixtures/m9_conso_fade_only.json")
    assert h["execution_context"]["conso_raided_edge"] == "low"


# ---------------------------------------------------------- gate 3 risk

def test_risk_gate_pass_and_blocks(fresh):
    h = _handoff()
    cfg = load_config()
    ok = risk_gate("REV", "buy", h, cfg, FLAT)
    assert ok["pass"] and ok["reason"] == "within_caps" and ok["risk_pct"] == cfg["max_trade_risk_pct"]
    assert risk_gate("REV", "buy", h, cfg, {**FLAT, "daily_loss_pct": 1.6})["reason"] == "daily_loss_cap"
    assert risk_gate("REV", "buy", h, cfg, {**FLAT, "daily_loss_pct": 1.5})["pass"]  # 1.5 + 0.5 = 2.0 cap
    assert risk_gate("REV", "buy", h, cfg, {**FLAT, "drawdown_pct": 4.6})["reason"] == "max_drawdown_cap"
    assert risk_gate("REV", "sell", h, cfg, FLAT)["reason"] == "stop_not_protective"
    nostop = copy.deepcopy(h)
    nostop["execution_context"]["raid"] = {"level": None, "price": None, "taken": False}
    assert risk_gate("REV", "buy", nostop, cfg, FLAT)["reason"] == "hold_missing_stop_or_entry"
    assert risk_gate("REV", None, h, cfg, FLAT)["reason"] == "hold_side_undetermined"
    nocap = {k: v for k, v in cfg.items() if k != "max_daily_loss_pct"}
    assert risk_gate("REV", "buy", h, nocap, FLAT)["reason"] == "hold_missing_risk_caps"
    lab = copy.deepcopy(h)
    lab["execution_context"]["stop_reference"] = 1.1170
    assert risk_gate("REV", "buy", lab, cfg, FLAT)["stop_source"] == "labeled_stop_reference"


def test_pip20_stop_is_20_pips(fresh):
    h = _handoff()
    r = risk_gate("PIP20", "buy", h, load_config(), FLAT)
    assert r["pass"] and abs((h["last"] - r["stop_reference"]) - 0.0020) < 1e-9


def test_risk_block_through_book_file(fresh):
    from ftn.paths import out_dir
    out = out_dir()
    (out / "paper_book.json").write_text(json.dumps({"daily_loss_pct": 1.9, "drawdown_pct": 0}))
    d = draft_from_handoff(_handoff(), cfg=_pilot_cfg(fresh))
    assert d["blocked_by"] == "risk:daily_loss_cap" and not d["actionable_for_mint"]


# ---------------------------------------------------------- gate 4 allowlist

def test_allowlist_gate(tmp_path):
    cfg = _pilot_cfg(tmp_path, ids=("REV",))
    assert allowlist_gate("REV", cfg)["pass"]
    assert allowlist_gate("CONSO", cfg)["reason"] == "not_on_mint_allowlist"
    exp = _pilot_cfg(tmp_path, ids=("REV",), expires="2020-01-01")
    assert allowlist_gate("REV", exp, today=date(2026, 10, 4))["reason"] == "paper_pilot_expired"
    missing = {**cfg, "mint_allowlist": [{**cfg["mint_allowlist"][0], "stamp": "nope/missing.md"}]}
    assert allowlist_gate("REV", missing)["reason"] == "paper_pilot_reference_missing"
    board = tmp_path / "BOARD_LOCK.md"
    board.write_text("SURVIVES")
    surv = {**cfg, "mint_allowlist": [{"id": "REV", "kind": "survives", "board_ref": str(board)}]}
    assert allowlist_gate("REV", surv)["reason"] == "allowlisted_survives"
    assert allowlist_gate("REV", load_config())["reason"] == "not_on_mint_allowlist"  # today: empty


# ---------------------------------------------------------- gate 5 mode

def test_mode_gate(fresh):
    assert mode_gate({"mode": "paper"})["pass"]
    assert mode_gate({"mode": "live"})["reason"] == "non_paper_mode_refused"
    cfg = {**_pilot_cfg(fresh), "mode": "live"}
    d = draft_from_handoff(_handoff(), cfg, FLAT)
    assert d["blocked_by"] == "mode:non_paper_mode_refused" and not d["actionable_for_mint"]


def test_live_orders_still_refused():
    from ftn.adapters.live import refuse_live_orders
    assert refuse_live_orders()["ok"] is False


# ---------------------------------------------------------- cross-path harmony

DATED = sorted(p for p in (ROOT / "fixtures").glob("*.json")
               if not p.name.endswith(".expected.json") and json.loads(p.read_text()).get("date"))


def _brief_and_written(fx, monkeypatch):
    from ftn.paths import draft_dir
    monkeypatch.setenv("FTN_WRITE_MINT_DRAFT", "1")
    st, cands, md, ftn = brief_from_fixture(fx)
    status = draft_status(gate_input(st, build_handoff(st, cands, ftn)))
    files = sorted(draft_dir().glob("ftn_draft_latest.json"))
    written = json.loads(files[0].read_text()) if files else None
    return status, written, md


@pytest.mark.parametrize("fx", DATED, ids=lambda p: p.name)
def test_brief_markdown_written_draft_and_status_agree(fx, monkeypatch):
    status, written, md = _brief_and_written(fx, monkeypatch)
    assert status["actionable_for_mint"] is False
    assert f"**blocked_by:** {status['blocked_by']}" in md
    if status["draft"]:
        assert written is not None and written["blocked_by"] == status["blocked_by"]
        assert [f"{g['gate']}:{'pass' if g['pass'] else 'FAIL'}:{g['reason']}" for g in written["gates"]] == status["gates"]
        assert "side" not in written and status["blocked_by"] == "allowlist:not_on_mint_allowlist"
    else:
        assert written is None


def test_handoff_stays_contract_clean_with_gate_chain(monkeypatch):
    from ftn.os.handoff_contract import find_ban_violations
    st, cands, _, ftn = brief_from_fixture(REV_FX)
    h = build_handoff(st, cands, ftn)
    assert "execution_context" not in h and "last" not in h
    assert find_ban_violations(h) == []


@pytest.mark.parametrize("fx", [REV_FX, ROOT / "fixtures/m9_rev_no_raid.json"], ids=lambda p: p.name)
def test_run_never_issues_kernel_tickets(fx, capsys):
    """Main's `ftn run` refuses DTR fixtures (use `ftn brief`): one ticket authority."""
    from ftn.__main__ import main
    assert main(["run", "--fixture", str(fx)]) == 2
    assert "ftn brief" in capsys.readouterr().err


# --- unsigned stamps never clear the allowlist gate -------------------------------------

from ftn.os.mint_draft import allowlist_gate, stamp_is_signed  # noqa: E402


def test_stamp_signature_rules():
    assert stamp_is_signed("x\nSignature: N. Ngubeni\n")
    assert not stamp_is_signed("x\nSignature: ____________________\n")
    assert not stamp_is_signed("x\nSignature:\n")
    assert not stamp_is_signed("x\nSignature: <name>\n")
    assert not stamp_is_signed("no signature line")
    assert not stamp_is_signed("STATUS: UNSIGNED\nSignature: Someone\n")


def test_unsigned_pilot_stamp_blocks(tmp_path):
    stamp = tmp_path / "stamp.md"
    stamp.write_text("STATUS: UNSIGNED\nSignature: ____\n")
    cfg = {"mint_allowlist": [{"id": "REV", "kind": "paper_pilot", "stamp": str(stamp),
                               "expires": "2099-01-01", "kill": "k"}]}
    g = allowlist_gate("REV", cfg)
    assert g["pass"] is False and g["reason"] == "paper_pilot_stamp_unsigned"


def test_repo_rev_stamp_is_unsigned_and_not_allowlisted():
    from ftn.config_load import load_config
    from ftn.config_load import repo_root
    p = repo_root() / "docs/pilots/REV_PAPER_PILOT_STAMP_UNSIGNED.md"
    assert p.is_file() and not stamp_is_signed(p.read_text(encoding="utf-8"))
    assert not any(e.get("id") == "REV" for e in load_config().get("mint_allowlist") or [])
    cfg = {"mint_allowlist": [{"id": "REV", "kind": "paper_pilot", "stamp": str(p),
                               "expires": "2099-01-01", "kill": "k"}]}
    assert allowlist_gate("REV", cfg)["reason"] == "paper_pilot_stamp_unsigned"


def test_stamp_suggested_allowlist_entry_parses(tmp_path):
    """The YAML snippet in the unsigned stamp is valid for the strict config parser."""
    import re
    from ftn.config_load import repo_root
    text = (repo_root() / "docs/pilots/REV_PAPER_PILOT_STAMP_UNSIGNED.md").read_text(encoding="utf-8")
    entry = re.search(r"```yaml\n(.*?)```", text, re.S).group(1)
    base = (repo_root() / "config.yaml").read_text(encoding="utf-8")
    base = re.sub(r"^mint_allowlist:.*$", "", base, flags=re.M)
    signed = tmp_path / "REV_PAPER_PILOT_STAMP.md"
    signed.write_text("STATUS: SIGNED\nSignature: Test Human\n")
    cfgfile = tmp_path / "c.yaml"
    cfgfile.write_text(base + "\n" + entry.replace("docs/pilots/REV_PAPER_PILOT_STAMP.md", str(signed)))
    cfg = load_config(cfgfile)
    assert cfg["mint_allowlist"][0]["id"] == "REV"
    assert allowlist_gate("REV", cfg, today=date(2026, 10, 4))["pass"] is True
    assert allowlist_gate("REV", cfg, today=date(2026, 11, 5))["reason"] == "paper_pilot_expired"
