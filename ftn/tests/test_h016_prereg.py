"""H016 prereg self-consistency (registration hygiene only; no bar data is read)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "research/protocols/preregs/H016_FORWARD_PREREG_2026-10-04.json"


def _d():
    return json.loads(PREREG.read_text())


def test_pins_match_files():
    d = _d()
    for block in ("kernel_and_dtr_sha256", "risk_sha256", "scoring_sha256", "registration_inputs_sha256"):
        for p, h in d["code"][block].items():
            assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h, p


def test_every_ftn_source_file_is_pinned():
    d = _d()
    pinned = set(d["code"]["kernel_and_dtr_sha256"]) | set(d["code"]["scoring_sha256"])
    for sub in ("models", "os", "engine", "research"):
        for f in (ROOT / "ftn/src/ftn" / sub).glob("*.py"):
            assert str(f.relative_to(ROOT)) in pinned, f


def test_binding_numbers_match_power_sim():
    d = _d()
    rows = [json.loads(l) for l in (ROOT / "research/evidence/quant/H016_POWER_SIM_2026-10-04.out").read_text().splitlines() if l.startswith("{")]
    stats = rows[0]
    assert d["binding_N"]["decision"] == stats["N_trades"]["0.15"] == 738
    kill = [r for r in rows[1:8]]
    ok = [r["K"] for r in kill if r["p_kill"] < 0.01]
    assert max(ok) == -40 and "<= -40R" in d["binding_kill"]["rule"]
    assert d["power_calculation"]["joint_power"]["mu_+0.15"]["p_pass_joint"] == rows[8]["p_pass"]


def test_family_and_bound():
    d = _d()
    assert d["family_rule"]["active_family"] == ["H013", "H014", "H015b", "H016"]
    assert "0.0125 / 0.0167 / 0.025 / 0.05" in d["family_rule"]["applies"]
    assert "v[500]" in d["statistical_test"]["binding_call"] and "v[9749]" in d["binding_futility"]["rule"]
    assert d["data_source"]["fallback_feeds_allowed"] is False
    assert "correct-side" in d["costs"]["binding"]
