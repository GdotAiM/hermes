"""Test isolation: every test gets its own FTN output dirs.

Root cause of the old order-dependence: session_ticket.py / m7_swing.py /
handoff.py resolved ``ROOT / "dispatch" / "out"`` at import time and the
suite persisted session/swing tickets there, so a second run found last
run's tickets (e.g. test_month7_slice7_swing saw a swing_ticket on a
persist=False call). Paths are now resolved at call time (ftn.paths) and
redirected here to tmp_path, so tests never touch the real dispatch/ folder.
"""

import pytest


@pytest.fixture(autouse=True)
def _isolated_ftn_dirs(tmp_path, monkeypatch):
    monkeypatch.setenv("FTN_OUT_DIR", str(tmp_path / "out"))
    monkeypatch.setenv("FTN_JOURNAL_DIR", str(tmp_path / "journal"))
    monkeypatch.setenv("FTN_DRAFT_DIR", str(tmp_path / "drafts"))
    monkeypatch.delenv("FTN_WRITE_MINT_DRAFT", raising=False)
    yield tmp_path
