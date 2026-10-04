"""Model 13 ("Month 13") bridge: never a PAM, never a ticket, none by default."""

from __future__ import annotations

import copy
import json
from pathlib import Path

from ftn.os.briefing import brief_from_fixture
from ftn.os.contracts import load_day_context
from ftn.os.dtr import build_context
from ftn.os.m13_contracts import REQUIRED, explicit_bridge, parse_model13_card
from ftn.os.m13_context import model13_annotation
from ftn.os.pam_contracts import PAM_IDS, parse_charter
from ftn.os.pam_recognize import derive_charter

ROOT = Path(__file__).resolve().parents[1]
FX = ROOT / "fixtures/m13_bridge_eurusd.json"


def _raw():
    return json.loads(FX.read_text())


def test_model13_is_never_a_pam_id():
    assert "pam13" not in PAM_IDS
    assert not any("13" in p for p in PAM_IDS)
    st = parse_charter({"charter": {"identified_pam": "present", "recognized_pams": ["pam13", "model13"]}})
    assert st.recognized_pams == ()
    raw = _raw()
    raw["evidence"]["recognized_pams"] = ["pam13"]
    raw["evidence"]["identified_pam"] = "present"
    ch = derive_charter(raw)
    assert ch.recognized_pams == ()
    assert ch.charter_recognition.flag is False  # bridge never mints recognition


def test_model13_none_by_default():
    for name in ("m9_reconstruction_eurusd.json", "charter_evidence_eurusd.json",
                 "charter_reconstruction_eurusd.json", "pam1_evidence_eurusd.json"):
        ctx = build_context(ROOT / "fixtures" / name)
        if ctx.charter is not None:
            assert ctx.charter.model13_bridge == "none"
            assert ctx.charter.model13 is None
    assert build_context(ROOT / "fixtures/m9_reconstruction_eurusd.json").charter is None


def test_model13_requires_explicit_identification():
    for v in (True, "yes", "pam13", "Present", 1, None):
        assert explicit_bridge(v) == "none"
    assert explicit_bridge("present") == "present"
    raw = _raw()
    raw["evidence"].pop("model13_bridge")
    ctx = build_context_from(raw)
    # a complete card alone does not mint the bridge
    assert ctx.charter.model13 is not None
    assert ctx.charter.model13.required_missing == ()
    assert ctx.charter.model13_bridge == "none"


def build_context_from(raw, tmp=ROOT / ".pytest_m13_tmp.json"):
    tmp.write_text(json.dumps(raw))
    try:
        return build_context(tmp)
    finally:
        tmp.unlink()


def test_model13_explicit_bridge_attaches_without_recognition():
    ctx = build_context(FX)
    ch = ctx.charter
    assert ch.model13_bridge == "present"
    assert ch.identified_pam == "none" and ch.recognized_pams == ()
    assert ch.charter_recognition.flag is False
    card = ch.model13
    assert card.reference == "kNlySn81dmo"
    assert card.direction == "bearish"
    assert card.reason == "required_notes_complete"
    assert set(card.confirming_present) == {"fvg_eq_side_note", "target_ladder_note"}
    # raw loader only parses a top-level charter block; evidence labels attach via DTR
    assert load_day_context(FX).charter is None


def test_model13_card_completeness_is_descriptive():
    raw = _raw()
    raw["evidence"]["model13_context"]["short_term_mss_note"] = "maybe"
    card = parse_model13_card(raw)
    assert card.short_term_mss_note == "none"
    assert "short_term_mss_note" in card.required_missing
    assert card.reason == "required_notes_incomplete"
    assert set(card.required_missing) <= set(REQUIRED)


def test_model13_never_makes_a_ticket():
    from ftn.paths import out_dir
    out = out_dir()
    before = set(p.name for p in out.glob("*")) if out.exists() else set()
    st, cands, md, _ = brief_from_fixture(FX)
    assert all(c.state != "selected" for c in cands)
    assert st.context.session_ticket is None
    after = set(p.name for p in out.glob("*"))
    new = after - before
    assert not any(n.startswith(("session_", "swing_", "mint_draft_")) for n in new)
    assert "Model 13 card" in md and "not a PAM" in md
    # candidate set identical with and without Model 13 labels
    raw = _raw()
    raw["evidence"].pop("model13_bridge")
    raw["evidence"].pop("model13_context")
    tmp = ROOT / ".pytest_m13_plain.json"
    tmp.write_text(json.dumps(raw))
    try:
        _, cands2, _, _ = brief_from_fixture(tmp)
    finally:
        tmp.unlink()
    assert [(c.module, c.state, c.reason) for c in cands] == [(c.module, c.state, c.reason) for c in cands2]


def test_model13_orchestrator_off_by_default_and_never_changes_ticket(tmp_path, monkeypatch):
    import ftn.workflow.orchestrator as orch
    from ftn.config_load import load_config

    sample = json.loads((ROOT / "fixtures/sample_eurusd.json").read_text())
    fx = tmp_path / "s.json"
    with_m13 = copy.deepcopy(sample)
    with_m13["evidence"] = _raw()["evidence"]
    fx.write_text(json.dumps(with_m13))
    off = orch.run_workflow(symbol="EURUSD", fixture=fx, bias="auto", price=None, stage="all", out_dir=tmp_path)
    assert load_config()["model13_bridge_enabled"] is False
    assert off["annotations"] == {}
    base = load_config()
    monkeypatch.setattr(orch, "load_config", lambda: {**base, "model13_bridge_enabled": True})
    on = orch.run_workflow(symbol="EURUSD", fixture=fx, bias="auto", price=None, stage="all", out_dir=tmp_path)
    assert on["annotations"]["model13"]["model13_bridge"] == "present"
    for k in ("kind", "actionable_for_mint", "no_trade_reasons", "four_levels", "family"):
        assert on["ticket"][k] == off["ticket"][k]
    assert model13_annotation({})["model13_bridge"] == "none"


def test_model13_handoff_carries_bridge_not_pam():
    from ftn.os.handoff import build_handoff
    st, cands, _, ftn = brief_from_fixture(FX)
    h = build_handoff(st, cands, ftn)
    ch = h["market_state"]["charter"]
    assert ch["model13_bridge"] == "present"
    assert list(ch["recognized_pams"]) == []
    assert h["session_ticket"] is None
