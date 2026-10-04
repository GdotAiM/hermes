"""H016b prereg self-consistency (registration hygiene only; no bar data is read)."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PREREG = ROOT / "research/protocols/preregs/H016b_FORWARD_PREREG_2026-10-04.json"


def _d():
    return json.loads(PREREG.read_text())


def test_pins_match_files_and_equal_h016_rule_pins():
    d = _d(); h016 = json.loads((ROOT / "research/protocols/preregs/H016_FORWARD_PREREG_2026-10-04.json").read_text())
    for block in ("kernel_and_dtr_sha256", "risk_sha256", "scoring_sha256", "registration_inputs_sha256"):
        for p, h in d["code"][block].items():
            assert hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h, p
    for block in ("kernel_and_dtr_sha256", "risk_sha256", "scoring_sha256"):
        assert d["code"][block] == h016["code"][block]


def test_binding_numbers_match_power_sim():
    d = _d()
    rows = [json.loads(l) for l in (ROOT / "research/evidence/quant/H016b_POWER_SIM_2026-10-04.out").read_text().splitlines() if l.startswith("{")]
    assert rows[0]["trades"] == 254 and d["binding_N"]["decision"] == rows[0]["N_trades"]["0.15"] == 747
    assert max(r["K"] for r in rows[1:8] if r["p_kill"] < 0.01) == -40 and "<= -40R" in d["binding_kill"]["rule"]
    assert d["power_calculation"]["joint_power"]["mu_+0.15"]["p_pass_joint"] == rows[8]["p_pass"]


def test_family_rulings_and_amendments():
    d = _d(); f = d["family_rule"]
    assert f["active_family"] == ["H013", "H014", "H016b"] and "0.0167 / 0.025 / 0.05" in f["applies"]
    assert f["orion_ruling_a"]["attribution"] == "ORION, 2026-10-04" and "p=1" in f["orion_ruling_a"]["text"]
    assert len(f["orion_ruling_b"]["text"]) == 4 and len(f["orion_ruling_b"]["cassandra_stricter_points_take_precedence"]["text"]) == 2
    assert "WITHDRAWN-PRE-DATA" in f["h015b"] and "NOT independent replication" in f["not_independent"]
    assert "feed_gap_entry" in d["rule"]["entry_minute"] and "[15:45, 16:00)" in d["counting_rules"]["exit_bar_rule"]
    assert "fill-fragile" in d["verdict_wording"]["fill_fragile"] and len(d["fill_fragility_co_report"]["perturbations"]) == 4
    assert "harness registration" in d["counting_rules"]["computed_after_harness_registration"]
    assert "sealed/FUTILITY_SET.json" in d["binding_futility"]["frozen_set"] and "KILL_LOG" in d["binding_kill"]["kill_log"]
    assert (ROOT / "research/summaries/2026-10-04_H015b_WITHDRAWAL.md").exists()
