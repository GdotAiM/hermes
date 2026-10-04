"""Research bridge: hypotheses, interpretation triggers, REV side check (D18), scorer."""

from __future__ import annotations

import copy
import csv
import gzip
import json
import math
import subprocess
import sys
from dataclasses import fields
from datetime import date, datetime, time, timedelta
from pathlib import Path

import pytest

from ftn.os.candidates import evaluate_candidates  # noqa: I001  (ftn.os before ftn.models)
from ftn.config_load import load_config, repo_root
from ftn.os.contracts import freeze_market_state
from ftn.os.dtr import build_context
from ftn.os.handoff import build_handoff
from ftn.os.mint_draft import direction_gate, draft_from_handoff
from ftn.research import stats
from ftn.research.bars import Series, load_series, m15_bars, trading_days
from ftn.research.daycontext import History, build_raw
from ftn.research.hypotheses import CONTEXT_MONTHS, HYPOTHESES, Hypothesis, by_month
from ftn.research.kernel_log import session_ticket_log, tradeable
from ftn.research.outcomes import simulate

FIX = repo_root() / "fixtures"


def _cfg(**trig):
    cfg = copy.deepcopy(load_config())
    cfg["interpretation_triggers"] = {"conso": False, "bb": False, "pip20": False, **trig}
    return cfg


def _state(raw: dict, tmp_path: Path):
    p = tmp_path / "f.json"
    p.write_text(json.dumps(raw))
    return freeze_market_state(build_context(p))


# --- hypotheses -----------------------------------------------------------------------

def test_every_context_month_emits_a_hypothesis():
    for m in CONTEXT_MONTHS:
        assert by_month(m), f"{m} emits no hypothesis"
    assert not by_month("M9"), "M9 is the ticket authority, not a context claim"


def test_hypotheses_are_typed_unique_and_never_results():
    ids = [h.id for h in HYPOTHESES]
    assert len(ids) == len(set(ids))
    names = {f.name for f in fields(Hypothesis)}
    assert {"id", "source_month", "source_slice", "claim", "metric", "conditioning_variable",
            "expected_direction", "claim_provenance", "operationalisation_provenance"} <= names
    for h in HYPOTHESES:
        assert h.metric in {"mean_R", "win_rate"}
        assert h.expected_direction in {"higher_when_true", "lower_when_true"}
        assert h.operationalisation_provenance == "hermes_interpretation"
        assert h.claim_provenance in {"ict_source", "user_lecture_notes"}
        assert "EXPLORATORY" in h.status
        assert not ({"result", "p_value", "survives"} & set(h.to_dict()))
    m7 = by_month("M7")[0]
    assert m7.conditioning_variable == "m7_osok_profile" and m7.metric == "win_rate"


def test_cli_hypotheses_prints_family():
    out = subprocess.run([sys.executable, "-m", "ftn", "hypotheses"], capture_output=True, text=True,
                         cwd=repo_root(), env={"PYTHONPATH": str(repo_root() / "src"), "PATH": ""})
    assert out.returncode == 0
    assert len(json.loads(out.stdout)) == len(HYPOTHESES)


# --- interpretation triggers ------------------------------------------------------------

def test_triggers_off_by_default_in_config():
    assert load_config()["interpretation_triggers"] == {"conso": False, "bb": False, "pip20": False}


@pytest.mark.parametrize("fx", sorted(p.name for p in FIX.glob("m9_*.json") if not p.name.endswith(".expected.json")))
def test_triggers_off_leave_kernel_unchanged(fx):
    st = freeze_market_state(build_context(FIX / fx))
    off = [(c.module, c.state) for c in evaluate_candidates(st, _cfg())]
    assert off == [(c.module, c.state) for c in evaluate_candidates(st)]
    assert all(c.module == "REV" for c in evaluate_candidates(st, _cfg()) if c.state == "selected")


def test_bb_trigger_selects_only_when_flag_on():
    st = freeze_market_state(build_context(FIX / "m9_rev_unnamed_no_htf.json"))
    assert not [c for c in evaluate_candidates(st, _cfg()) if c.state == "selected"]
    sel = [c for c in evaluate_candidates(st, _cfg(bb=True)) if c.state == "selected"]
    assert [(c.module, c.origin) for c in sel] == [("BB", "hermes_interpretation")]


def test_conso_trigger_close_back_inside(tmp_path):
    raw = json.loads((FIX / "m9_conso_fade_only.json").read_text())
    raw["evidence"]["post_raid_closes"] = [1.1150]
    sel = [c.module for c in evaluate_candidates(_state(raw, tmp_path), _cfg(conso=True)) if c.state == "selected"]
    assert sel == ["CONSO"]
    raw["evidence"]["post_raid_closes"] = [1.1130, 1.1135]
    assert not [c for c in evaluate_candidates(_state(raw, tmp_path), _cfg(conso=True)) if c.state == "selected"]


def test_pip20_trigger_needs_displacement(tmp_path):
    raw = json.loads((FIX / "m9_pip20_ny.json").read_text())
    st = _state(raw, tmp_path)
    assert not [c for c in evaluate_candidates(st, _cfg(pip20=True)) if c.state == "selected"]
    raw["evidence"]["displacement"] = True
    sel = [c.module for c in evaluate_candidates(_state(raw, tmp_path), _cfg(pip20=True)) if c.state == "selected"]
    assert sel == ["PIP20"]


def test_rev_still_preempts_with_all_triggers_on():
    st = freeze_market_state(build_context(FIX / "m9_rev_inside_box.json"))
    sel = [c.module for c in evaluate_candidates(st, _cfg(conso=True, bb=True, pip20=True)) if c.state == "selected"]
    assert sel == ["REV"]


# --- D18: REV direction must oppose the raid -------------------------------------------------

def _ho(level):
    return {"execution_context": {"raid": {"level": level, "price": 1.0, "taken": True}}}


@pytest.mark.parametrize("level,side,ok,reason", [
    ("pdl", "buy", True, "determined"),
    ("week_so_far_low", "buy", True, "determined"),
    ("pdh", "sell", True, "determined"),
    ("pdh", "buy", False, "rev_direction_conflicts_with_raid"),
    ("pdl", "sell", False, "rev_direction_conflicts_with_raid"),
    (None, "buy", False, "rev_raid_level_unknown"),
])
def test_rev_direction_gate(level, side, ok, reason):
    g = direction_gate("REV", side, "x", _ho(level))
    assert g["pass"] is ok and g["reason"] == reason


def test_direction_gate_other_models_unchanged():
    assert direction_gate("BB", "buy", "b", _ho("pdh"))["pass"] is True
    assert direction_gate("REV", None, "b", _ho("pdl"))["reason"] == "undetermined"


# --- stats ------------------------------------------------------------------------------

def test_holm_known_values():
    adj = stats.holm({"a": 0.01, "b": 0.04, "c": 0.03})
    assert adj == {"a": 0.03, "c": 0.06, "b": 0.06}


def test_bootstrap_deterministic_and_brackets_mean():
    xs = [1.0, -1.0, 2.0, -1.0, 0.5, -0.2, 1.5, -1.0]
    a, b = stats.boot_ci(xs, n=2000), stats.boot_ci(xs, n=2000)
    assert a == b and a[0] < sum(xs) / len(xs) < a[1]


def test_diff_test_direction():
    hi, lo = [2.0] * 15 + [-1.0] * 5, [-1.0] * 15 + [2.0] * 5
    r = stats.diff_test(hi, lo, "mean_R", "higher_when_true", n=2000)
    assert r["diff"] > 0 and r["ci95"][0] > 0 and r["p_one_sided"] < 0.01
    r2 = stats.diff_test(hi, lo, "mean_R", "lower_when_true", n=2000)
    assert r2["p_one_sided"] > 0.9


# --- synthetic 1m series ----------------------------------------------------------------

def _series(path: Path, days: int = 40, seed: int = 7) -> Path:
    import random
    rng = random.Random(seed)
    px = 20000.0
    d0 = datetime(2026, 1, 5, 0, 0)  # Monday
    with gzip.open(path, "wt", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Datetime", "Open", "High", "Low", "Close"])
        t = d0 - timedelta(hours=6)
        end = d0 + timedelta(days=days * 7 // 5 + 2)
        while t < end:
            if t.weekday() < 5 and not (time(17, 0) <= t.time() < time(18, 0)):
                o = px
                px += rng.gauss(0, 4)
                hi, lo = max(o, px) + abs(rng.gauss(0, 2)), min(o, px) - abs(rng.gauss(0, 2))
                w.writerow([t.strftime("%Y-%m-%d %H:%M:%S") + "-05:00", f"{o:.2f}", f"{hi:.2f}", f"{lo:.2f}", f"{px:.2f}"])
            t += timedelta(minutes=1)
    return path


@pytest.fixture(scope="module")
def synth(tmp_path_factory):
    d = tmp_path_factory.mktemp("bars")
    return _series(d / "US100_1m.csv.gz"), _series(d / "US500_1m.csv.gz", seed=11)


def test_outcomes_stop_target_time_and_costs():
    t0 = datetime(2026, 1, 6, 9, 0)
    ts = [t0 + timedelta(minutes=i) for i in range(5)]
    s = Series("X", ts, [100] * 5, [101, 101, 101, 111, 101], [99, 99, 99, 99, 89], [100] * 5)
    r = simulate(s, t0, 100.0, 95.0, "buy", 0.0)
    assert r["exit"] == "target" and r["R"] == 2.0
    s2 = Series("X", ts, [100] * 5, [101, 111, 101, 101, 101], [99, 94, 99, 99, 99], [100] * 5)
    assert simulate(s2, t0, 100.0, 95.0, "buy", 0.0)["exit"] == "stop"  # same-bar → stop first
    s3 = Series("X", ts, [100] * 5, [101] * 5, [99] * 5, [100, 100, 100, 100, 102.5])
    r3 = simulate(s3, t0, 100.0, 95.0, "buy", 0.5)
    assert r3["exit"] == "time" and math.isclose(r3["R"], 0.5 - 0.2)
    assert simulate(s3, t0, 100.0, 101.0, "buy", 0.0)["exit"] == "invalid_stop"


def test_daycontext_is_causal(synth):
    s = load_series(synth[0], "US100")
    days = trading_days(s, min_rth_bars=100)
    h = History(s, days)
    d = days[25]
    t = datetime.combine(d, time(8, 0))
    raw = build_raw(h, d, t, "ny_am")
    assert raw is not None
    assert all(b["t"] < t.strftime("%Y-%m-%dT%H:%M:00") for b in raw["bars_m15"])
    assert raw["last"] == s.close_at(t)
    assert raw["evidence"]["provenance"] == "hermes_interpretation"
    assert m15_bars(s, datetime.combine(d, time(0, 0)), t)[-1]["_t"] < t


def test_kernel_log_rows_obey_gate_chain(synth):
    s = load_series(synth[0], "US100")
    h = History(s, trading_days(s, min_rth_bars=100))
    rows = session_ticket_log(h, _cfg())
    assert rows and all(r["session"] in {"london", "ny_am"} for r in rows)
    for r in rows:
        if r["ticket"]:
            assert r["module"] == "REV"
            assert r["blocked_by"] is not None  # allowlist is empty → never actionable
            assert any(g.startswith("allowlist:FAIL") for g in r["gates"])
            if tradeable(r):
                assert r["side"] in {"buy", "sell"} and r["stop"] is not None


def test_score_writes_exploratory_reports(synth, tmp_path, monkeypatch):
    from ftn.research import score as sc
    monkeypatch.setattr(sc, "N_FOIL", 20)
    monkeypatch.setattr(stats, "N_BOOT", 200)
    monkeypatch.setattr(sc, "trading_days", lambda s: trading_days(s, min_rth_bars=100))
    res = sc.score(asof="2026-01-01", bars_us100=str(synth[0]), bars_us500=str(synth[1]),
                   research_dir=tmp_path, with_interp=True)
    assert {"US100_base", "US100_base_legacy_side", "US500_base", "US100_interp"} <= set(res)
    md = (tmp_path / "summaries/2026-01-01_FTN_M9_EXPLORATORY_SCORE.md").read_text()
    assert "EXPLORATORY" in md and "CASSANDRA" in md and "DATA" in md and "SURVIVES language" in md
    pre = json.loads((tmp_path / "protocols/preregs/FTN_HYPOTHESES_EXPLORATORY_2026-01-01.json").read_text())
    assert len(pre["hypotheses"]) == len(HYPOTHESES) and "NOT REGISTERED" in pre["status_at_registration"]
    assert "result" not in json.dumps(pre["hypotheses"]).lower()
    assert (tmp_path / "evidence/quant/FTN_M9_TICKETS_US100_base_2026-01-01.csv").is_file()
    for r in res["US100_base"]["hypotheses"]:
        assert r["status"] == "evaluated" or r["status"].startswith("not_evaluable")
