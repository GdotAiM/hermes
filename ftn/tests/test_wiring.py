"""F2/F3/F4/F5/F7 wiring: `ftn run` through Month 9, pipeline trace, bar-derived context, W%R context,
paper results journal with the H016 seal. Context never feeds REV (see also test_ticket_invariance.py)."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from ftn.__main__ import main
from ftn.journal import results as jr
from ftn.os.briefing import brief_from_fixture
from ftn.paths import journal_dir
from ftn.pipeline import invariance as inv

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src" / "ftn"
FX = ROOT / "fixtures"


# --- F2 -------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("name", ["m9_reconstruction_eurusd.json", "m9_rev_no_raid.json", "m9_conso_fade_only.json",
                                  "integration_m1_m9_eurusd.json", "m13_bridge_eurusd.json"])
def test_run_matches_brief_kernel(name, capsys, tmp_path):
    assert main(["run", "--fixture", str(FX / name)]) == 0
    p = json.loads(capsys.readouterr().out)
    st, cands, _, _ = brief_from_fixture(FX / name)
    sel = next((c.module for c in cands if c.state == "selected"), None)
    t = p["ticket"]
    assert p["engine"] == "month9_kernel" and t["selected_module"] == sel
    assert t["kind"] == ("m9_kernel_ticket" if sel else "no_trade")
    assert [c["module"] for c in t["candidates"]] == [c.module for c in cands]
    assert [c["state"] for c in t["candidates"]] == [c.state for c in cands]
    assert t["actionable_for_mint"] is False and "side" not in t
    jtxt = Path(p["journal_path"]).read_text()
    assert "Pipeline trace" in jtxt and "not for MINT" in jtxt


def test_prep_writes_no_journal(capsys):
    assert main(["prep", "--fixture", str(FX / "m9_reconstruction_eurusd.json")]) == 0
    p = json.loads(capsys.readouterr().out)
    assert p["stages"] == ["PREP"] and "journal_path" not in p


def test_legacy_four_count_still_runs_and_is_labelled(capsys):
    assert main(["run", "--fixture", str(FX / "sample_eurusd.json"), "--bias", "bullish"]) == 0
    p = json.loads(capsys.readouterr().out)
    assert p["engine"] == "legacy_four_count" and p["ticket"]["engine"] == "legacy_four_count_objectives"
    assert "session_ticket" not in p["ticket"]


# --- F3 -------------------------------------------------------------------------------------------------------
def test_trace_roles_and_feeds_rev():
    from ftn.os.handoff import build_handoff
    from ftn.os.mint_draft import draft_from_handoff, gate_input
    from ftn.pipeline.trace import build_trace
    st, cands, _, ftn = brief_from_fixture(FX / "integration_m1_m9_eurusd.json")
    tr = build_trace(st.context, cands, draft_from_handoff(gate_input(st, build_handoff(st, cands, ftn))),
                     fingerprint=st.fingerprint)
    from ftn.pipeline.trace import trace_for_state
    assert trace_for_state(st, cands, ftn, "x")["gates"] == tr["gates"]
    assert tr["schema"] == "ftn.trace.v1"
    assert set(tr) >= {"bias", "context", "setup", "ticket", "gates", "result"}
    assert all(v["feeds_rev"] is False and v["role"] == "annotate" for v in tr["context"].values())
    for k in ("M5_ipda", "M6_swing", "M12_topdown"):
        assert tr["bias"][k]["feeds_rev"] is False
    assert [c["role"] for c in tr["setup"]["candidates"] if c["module"] == "REV"] == ["decide"]
    for m in ("M1", "M2", "M3", "M4", "M8"):           # integration fixture labels M1-M8
        assert tr["context"][m]["available"], m
    assert tr["gates"]["actionable_for_mint"] is False and tr["result"]["status"] == "pending"


def test_brief_cli_renders_trace_summary(capsys, tmp_path):
    assert main(["brief", "--fixture", str(FX / "m9_reconstruction_eurusd.json"), "--out", str(tmp_path / "b.md")]) == 0
    md = (tmp_path / "b.md").read_text()
    assert "## Pipeline trace" in md and "context.M8: role=annotate feeds_rev=False" in md


def test_trace_is_not_in_handoff_or_daycontext():
    from ftn.os.handoff import build_handoff
    st, cands, _, ftn = brief_from_fixture(FX / "m9_reconstruction_eurusd.json")
    h = build_handoff(st, cands, ftn)
    assert "trace" not in json.dumps(h) and "layers" not in h.get("market_state", {})
    assert not hasattr(st.context, "trace")


def test_kernel_code_never_imports_context_layers():
    """Decision code (models/, os/) and the kernel log must not import the trace or the bar-derived layers."""
    pat = re.compile(r"ftn\.pipeline|layers_bar|ftn\.journal\.results")
    offenders = [str(p.relative_to(SRC)) for d in ("models", "os") for p in (SRC / d).glob("*.py")
                 if pat.search(p.read_text())]
    offenders += [p for p in ("research/kernel_log.py", "research/daycontext.py") if pat.search((SRC / p).read_text())]
    assert offenders == []


# --- F7 -------------------------------------------------------------------------------------------------------
GATES_OK = ["kernel_ticket:pass:kernel_session_ticket", "direction:pass:determined", "risk:pass:within_caps",
            "allowlist:FAIL:not_on_mint_allowlist", "mode:pass:paper",
            "contract:FAIL:hermes_integration_i0_ftn_never_actionable"]


def _row(d):
    return {"date": d, "symbol": "US100", "session": "london", "ticket": True, "module": "REV", "side": "sell",
            "stop": 101.0, "entry": 100.0, "entry_time": f"{d}T02:15:00", "gates": GATES_OK,
            "blocked_by": "allowlist:not_on_mint_allowlist", "trace": {"schema": "ftn.trace.v1"}}


def _boom(row):
    raise AssertionError("outcome must not be called for a sealed forward session")


def test_forward_sessions_are_sealed_without_clearance(tmp_path):
    recs = jr.journal_rows([_row("2026-10-05"), _row("2026-09-28")], _boom, None, out=tmp_path)
    assert {r["result"]["status"] for r in recs} == {jr.SEALED}
    assert all(r["result"]["R"] is None and r["trace"]["result"]["status"] == jr.SEALED for r in recs)
    lines = (tmp_path / jr.JOURNAL_NAME).read_text().splitlines()
    assert len(lines) == 2 and all(json.loads(x)["paper_only"] for x in lines)


def test_burned_session_reads_outcome():
    rec = jr.journal_rows([_row("2026-09-25")], lambda r: {"R": -1.0, "exit": "stop"}, write=False)[0]
    assert rec["result"]["status"] == "burned_window" and rec["result"]["R"] == -1.0


def test_blocked_and_no_ticket_rows_read_nothing():
    b = dict(_row("2026-01-05"), gates=GATES_OK[:2] + ["risk:FAIL:stop_below_min_risk"] + GATES_OK[3:],
             blocked_by="risk:stop_below_min_risk")
    n = {"date": "2026-01-05", "symbol": "US100", "session": "ny_am", "ticket": False, "reason": "no_selected_candidate"}
    recs = jr.journal_rows([b, n], _boom, write=False)
    assert [r["result"]["status"] for r in recs] == ["blocked", "no_ticket"]


@pytest.mark.parametrize("text,ok,why", [
    ("H016\nCASSANDRA: CLEARED\nDATA: CLEARED\nSignature: ntloso ngubeni\n", True, "cleared"),
    ("H016\nCASSANDRA: CLEARED\nSignature: x y\n", False, "clearance_missing_data"),
    ("H016\nCASSANDRA: CLEARED\nDATA: CLEARED\nSignature: ____\n", False, "clearance_stamp_unsigned"),
    ("STATUS: UNSIGNED\nH016\nCASSANDRA: CLEARED\nDATA: CLEARED\nSignature: a\n", False, "clearance_stamp_unsigned"),
    ("H015b\nCASSANDRA: CLEARED\nDATA: CLEARED\nSignature: a\n", False, "clearance_stamp_not_for_H016"),
])
def test_clearance_stamp(tmp_path, text, ok, why):
    p = tmp_path / "c.md"
    p.write_text(text)
    assert jr.clearance_ok(p) == (ok, why)
    assert jr.clearance_ok(None) == (False, "no_clearance_stamp")


def test_cleared_forward_session_reads_outcome(tmp_path):
    p = tmp_path / "c.md"
    p.write_text("H016\nCASSANDRA: CLEARED\nDATA: CLEARED\nSignature: ntloso ngubeni\n")
    rec = jr.journal_rows([_row("2026-10-05")], lambda r: {"R": 2.0}, p, write=False)[0]
    assert rec["result"]["status"] == "forward_cleared"


# --- F4/F5 on the burned tape (skipped without it) ------------------------------------------------------------
needs_tape = pytest.mark.skipif(bool(inv.check_data()), reason="burned guard tape unavailable")


@needs_tape
def test_cli_trace_one_burned_day(capsys):
    assert main(["trace", "--date", "2025-09-29", "--symbol", "US100"]) == 0
    recs = json.loads(capsys.readouterr().out)
    lon = next(r for r in recs if r.get("session") == "london")
    assert lon["schema"] == "ftn.trace.v1" and lon["ticket"]["selected_module"] == "REV"
    assert lon["ticket"]["stop_reference"] == 24614.778          # = registration CSV stop
    assert lon["fingerprint"] == "sha256:1903e844bf606b9d"         # = registration CSV fingerprint
    ctx = lon["context"]
    assert ctx["sentiment"]["value"]["wr_kernel"]["state"] == "unavailable"     # kernel W%R unchanged (F5)
    wr = ctx["W%R_prior_evening"]
    assert wr["available"] and wr["value"]["bars_used"] >= 10 and wr["value"]["window"].startswith("2025-09-28T18:00")
    for k in ("M5_ipda", "M6_swing", "M12_topdown"):
        assert lon["bias"][k]["available"] and lon["bias"][k]["feeds_rev"] is False
    assert ctx["M7_week"]["available"] and ctx["features"]["available"]
    reg = (inv.registration_csv("US100").read_text().splitlines()[1])
    assert json.dumps(ctx["features"]["value"]) in reg.replace('""', '"')      # same formulas as the scorer


@needs_tape
def test_cli_results_burned_days_match_registration(capsys):
    assert main(["results", "--from", "2025-09-29", "--to", "2025-09-29", "--symbol", "US100"]) == 0
    recs = json.loads(capsys.readouterr().out)
    got = {r["session"]: r["result"]["R"] for r in recs}
    assert got == {"london": -1.0687994496044038, "ny_am": -1.0235283045503738}
    assert (journal_dir() / jr.JOURNAL_NAME).is_file()
