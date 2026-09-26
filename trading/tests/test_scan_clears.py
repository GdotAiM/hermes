"""Smoke tests for mint.dispatch.scan_clears in the GdotAiM/hermes monorepo."""
from __future__ import annotations

import json
from pathlib import Path

from mint.dispatch import scan_clears as sc


def _make_spine(root: Path) -> Path:
    (root / "summaries").mkdir(parents=True)
    (root / "beliefs").mkdir(parents=True)
    (root / "summaries" / "2026-01-01_HX1_BOARD_LOCK.md").write_text(
        "# HX1\n\n## Decision\n\nFAILS — no edge.\n", encoding="utf-8"
    )
    (root / "summaries" / "2026-01-02_HX2_BOARD_LOCK.md").write_text(
        "# HX2\n\n## Decision\n\nINCONCLUSIVE — park.\n", encoding="utf-8"
    )
    (root / "summaries" / "_BOARD_LOCK_TEMPLATE.md").write_text("## Decision\nSURVIVES\n", encoding="utf-8")
    (root / "beliefs" / "LEDGER.md").write_text("| date | belief |\n|---|---|\n", encoding="utf-8")
    return root


def test_default_research_root_is_monorepo_sibling():
    assert sc.DEFAULT_RESEARCH == sc.TRADING_ROOT.parent / "research"
    assert sc.TRADING_ROOT.name == "trading"


def test_env_override(monkeypatch, tmp_path):
    monkeypatch.delenv("HERMES_RESEARCH_PATH", raising=False)
    monkeypatch.setenv("HERMES_X_PATH", str(tmp_path))
    assert sc.resolve_research_root(None) == tmp_path.resolve()
    monkeypatch.setenv("HERMES_RESEARCH_PATH", str(tmp_path / "r"))
    assert sc.resolve_research_root(None) == (tmp_path / "r").resolve()
    assert sc.resolve_research_root(tmp_path / "cli") == (tmp_path / "cli").resolve()


def test_scan_writes_latest(tmp_path):
    spine = _make_spine(tmp_path / "research")
    out = tmp_path / "out"
    rc = sc.main(["--hermes-x", str(spine), "--out", str(out)])
    assert rc == 0
    data = json.loads((out / "latest.json").read_text())
    kinds = {t["hypothesis_hint"]: t["kind"] for t in data["tickets"]}
    assert kinds["2026-01-01_HX1_BOARD_LOCK"] == "demote_filter"
    assert kinds["2026-01-02_HX2_BOARD_LOCK"] == "ignore"
    assert "_BOARD_LOCK_TEMPLATE" not in kinds
    assert data["entry_candidates"] == 0


def test_missing_spine_fails_loudly(tmp_path, capsys):
    rc = sc.main(["--hermes-x", str(tmp_path / "nope"), "--out", str(tmp_path / "out")])
    assert rc == 2
    assert "research spine not found" in capsys.readouterr().err


def test_real_monorepo_research_spine_scans(tmp_path):
    """The in-repo research/ spine must be discoverable with no flags."""
    assert (sc.DEFAULT_RESEARCH / "summaries").is_dir()
    assert (sc.DEFAULT_RESEARCH / "beliefs" / "LEDGER.md").is_file()
    rc = sc.main(["--out", str(tmp_path)])
    assert rc == 0
    data = json.loads((tmp_path / "latest.json").read_text())
    assert data["ticket_count"] >= 1


def test_decision_section_is_bounded():
    text = (
        "# H9\n\n## Decision (locked)\n**H9 = INCONCLUSIVE.** Parked.\n\n"
        "## KEY FINDINGS\n1. H3 **FAILS** vs foil.\n"
    )
    assert sc._decision_status(text) == "INCONCLUSIVE"
    assert sc._decision_status("## Decision\nH2b FAILS.\n") == "FAILS"
    assert sc._decision_status("## Decision\nH1 SURVIVES board.\n") == "SURVIVES"
