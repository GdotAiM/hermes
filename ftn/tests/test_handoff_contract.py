"""handoff.v1 contract tests (monorepo integration).

The single contract is ftn/dispatch/out/handoff_latest.json. These tests
enforce, recursively, the HERMES_INTEGRATION_I0 handoff bans: no BUY/SELL
calls, no confidence, no best_pam / pam_rank, no broker or order fields.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from ftn.os.handoff_contract import (
    SCHEMA_PATH,
    find_ban_violations,
    validate_file,
    validate_handoff,
)

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = sorted((ROOT / "dispatch" / "samples").glob("handoff_v1_*.json"))
FIXTURES = sorted(
    p for p in (ROOT / "fixtures").glob("*.json")
    if not p.name.endswith(".expected.json") and p.name != "sample_eurusd.json"
)


def _built(fixture: Path) -> dict:
    from ftn.os.briefing import brief_from_fixture
    from ftn.os.handoff import build_handoff
    state, cands, _md, ftn = brief_from_fixture(fixture)
    return build_handoff(state, cands, ftn or {})


def test_samples_exist():
    assert len(SAMPLES) >= 2


@pytest.mark.parametrize("path", SAMPLES, ids=lambda p: p.name)
def test_committed_samples_validate(path):
    assert validate_file(path) == []


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda p: p.name)
def test_every_fixture_handoff_is_contract_clean(fixture):
    h = _built(fixture)
    assert validate_handoff(h) == [], fixture.name
    # serialized form (what consumers read) is clean too
    assert find_ban_violations(json.loads(json.dumps(h, default=str))) == []


def test_written_latest_is_the_contract():
    from ftn.paths import out_dir
    _built(ROOT / "fixtures" / "m9_reconstruction_eurusd.json")
    latest = out_dir() / "handoff_latest.json"
    assert latest.exists()
    assert validate_file(latest) == []


def test_institutional_label_exported_as_qualification():
    h = _built(ROOT / "fixtures" / "m9_reconstruction_eurusd.json")
    inst = h["market_state"]["institutional"]
    assert "confidence" not in inst
    assert isinstance(inst["qualification"], str)


# --- the bans, recursively: each injected violation must be caught -------------

BASE = json.loads(SAMPLES[0].read_text()) if SAMPLES else {}

INJECTIONS = [
    ("top BUY key", lambda h: h.__setitem__("BUY", True)),
    ("top SELL key", lambda h: h.__setitem__("SELL", "EURUSD")),
    ("buy/sell value deep", lambda h: h["market_state"]["sentiment"].__setitem__("call", "SELL")),
    ("strong buy value in list", lambda h: h["notes"].append("strong buy")),
    ("side in candidate", lambda h: h["candidates"][0].__setitem__("side", "long")),
    ("confidence top", lambda h: h.__setitem__("confidence", 0.8)),
    ("confidence nested", lambda h: h["market_state"]["institutional"].__setitem__("confidence", "high")),
    ("confidence null still banned", lambda h: h["market_state"].__setitem__("confidence", None)),
    ("model_confidence substring", lambda h: h["candidates"][1].__setitem__("model_confidence", 0.3)),
    ("best_pam", lambda h: h["market_state"].__setitem__("best_pam", "pam1")),
    ("pam_rank in candidate", lambda h: h["candidates"][0].__setitem__("pam_rank", 1)),
    ("rank deep in list", lambda h: h["ftn_annotation"]["four"][0].__setitem__("rank", 1)),
    ("broker_instruction", lambda h: h.__setitem__("broker_instruction", {"route": "alpaca"})),
    ("broker substring nested", lambda h: h["session_ticket"].__setitem__("alpaca_broker_ref", "x")),
    ("order object", lambda h: h.__setitem__("order", {"symbol": "EURUSD"})),
    ("order fields in ticket", lambda h: h["session_ticket"].update({"qty": 1, "limit_price": 1.1})),
    ("stop_loss / take_profit", lambda h: h["ftn_annotation"].update({"stop_loss": 1.1, "take_profit": 1.2})),
    ("time_in_force deep", lambda h: h["market_state"]["opens"].__setitem__("time_in_force", "day")),
]


@pytest.mark.parametrize("name,mutate", INJECTIONS, ids=[n for n, _ in INJECTIONS])
def test_ban_walk_catches_injected_violation(name, mutate):
    h = copy.deepcopy(BASE)
    assert validate_handoff(h) == []
    mutate(h)
    assert find_ban_violations(h), f"ban walk missed: {name}"
    assert validate_handoff(h), f"validator missed: {name}"


def test_ict_vocabulary_is_not_a_false_positive():
    """buy_side / sell_side liquidity, 'sell-side probe', institutional_order_flow are ICT
    descriptors, not trade calls or order fields."""
    h = copy.deepcopy(BASE)
    h["market_state"]["x_liquidity"] = {"buy_side": "unclear", "sell_side": "taken",
                                        "institutional_order_flow": True, "judas_side": "sell_side"}
    h["notes"].append("sell-side probe under Asia")
    assert find_ban_violations(h) == []


def test_structure_rejects_wrong_kind_and_mode():
    h = copy.deepcopy(BASE)
    h["kind"] = "month9_handoff"
    h["mode"] = "live"
    errs = validate_handoff(h)
    assert any("kind" in e for e in errs) and any("mode" in e for e in errs)


def test_jsonschema_agrees_on_samples():
    jsonschema = pytest.importorskip("jsonschema")
    schema = json.loads(SCHEMA_PATH.read_text())
    for p in SAMPLES:
        jsonschema.validate(json.loads(p.read_text()), schema)
    bad = copy.deepcopy(BASE)
    bad["BUY"] = True
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


@pytest.mark.parametrize(
    "fixture,sample",
    [
        ("m9_reconstruction_eurusd.json", "handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json"),
        ("pam1_evidence_eurusd.json", "handoff_v1_pam1_evidence_eurusd_2018-01-10.json"),
    ],
)
def test_committed_samples_match_regeneration(fixture, sample):
    """Samples are real FTN output, not hand-edited: regenerating gives the same
    payload, fingerprint included (sha256 over canonical JSON — deterministic)."""
    fresh = json.loads(json.dumps(_built(ROOT / "fixtures" / fixture), default=str))
    committed = json.loads((ROOT / "dispatch" / "samples" / sample).read_text())
    assert committed["fingerprint"].startswith("sha256:")
    assert fresh == committed


def test_fingerprint_independent_of_pythonhashseed(tmp_path):
    """Two fresh interpreters with different PYTHONHASHSEED give the same fingerprint."""
    import os
    import subprocess
    import sys

    code = (
        "from ftn.os.briefing import brief_from_fixture;"
        "print(brief_from_fixture('fixtures/m9_reconstruction_eurusd.json')[0].fingerprint)"
    )
    fps = set()
    for seed in ("0", "1", "987654"):
        env = dict(os.environ, PYTHONHASHSEED=seed, PYTHONPATH=str(ROOT / "src"),
                   FTN_OUT_DIR=str(tmp_path / f"out{seed}"), FTN_JOURNAL_DIR=str(tmp_path / "j"))
        fps.add(subprocess.run([sys.executable, "-c", code], cwd=ROOT, env=env,
                               capture_output=True, text=True, check=True).stdout.strip())
    assert len(fps) == 1 and next(iter(fps)).startswith("sha256:"), fps


def test_brief_writes_no_mint_draft_by_default(monkeypatch):
    from ftn.os.briefing import brief_from_fixture
    from ftn.paths import draft_dir, out_dir

    brief_from_fixture(ROOT / "fixtures" / "m9_reconstruction_eurusd.json")
    assert not list(out_dir().glob("*draft*")) and not list(draft_dir().glob("*.json"))


def test_opt_in_draft_goes_to_drafts_not_out(monkeypatch):
    from ftn.os.briefing import brief_from_fixture
    from ftn.paths import draft_dir, out_dir

    monkeypatch.setenv("FTN_WRITE_MINT_DRAFT", "1")
    brief_from_fixture(ROOT / "fixtures" / "m9_reconstruction_eurusd.json")
    assert not list(out_dir().glob("*draft*"))
    d = json.loads((draft_dir() / "ftn_draft_latest.json").read_text())
    assert "side" not in d and d["actionable_for_mint"] is False
    assert d["direction_hypothesis"] in {"bullish", "bearish", "unclear"}
    assert find_ban_violations(d) == []


@pytest.mark.parametrize(
    "name,needle",
    [
        ("sample_eurusd.json", "ftn run"),
        ("m9_bb_offset.expected.json", "gold oracle"),
    ],
)
def test_brief_refuses_non_fixtures_clearly(name, needle, capsys):
    from ftn.__main__ import main

    assert main(["brief", "--fixture", str(ROOT / "fixtures" / name)]) == 2
    err = capsys.readouterr().err
    assert "KeyError" not in err and needle in err


def test_brief_refuses_handoff_sample(capsys):
    from ftn.__main__ import main

    sample = next((ROOT / "dispatch" / "samples").glob("handoff_v1_*.json"))
    assert main(["brief", "--fixture", str(sample)]) == 2
    assert "handoff.v1 output" in capsys.readouterr().err


def test_brief_runs_on_every_input_fixture(tmp_path):
    from ftn.__main__ import main

    fixtures = [p for p in sorted((ROOT / "fixtures").glob("*.json"))
                if not p.name.endswith(".expected.json") and p.name != "sample_eurusd.json"]
    assert len(fixtures) >= 40
    for p in fixtures:
        assert main(["brief", "--fixture", str(p), "--out", str(tmp_path / "b.md")]) == 0, p.name
