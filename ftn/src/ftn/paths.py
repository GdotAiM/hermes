"""Runtime output locations for FTN (resolved at call time, not import time).

FTN writes scratch artifacts — handoff_latest.json, session_/swing_ tickets,
mint drafts, journals. Defaults are inside the package checkout
(``dispatch/out``, ``dispatch/journal``); override with environment variables:

  FTN_OUT_DIR       handoffs, session/swing tickets, ftn run dispatch tickets
  FTN_JOURNAL_DIR   decision journals (``ftn run``)
  FTN_DRAFT_DIR     legacy MINT drafts (only written when FTN_WRITE_MINT_DRAFT=1)

The test suite points all of them at a per-test tmp_path (tests/conftest.py),
so tests never read or write the real dispatch/ folder. Resolving lazily is the
point: the old module-level ``STORE = ROOT / "dispatch" / "out"`` constants
leaked persisted tickets between test runs.
"""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[2]  # .../ftn


def _env_dir(var: str, default: Path) -> Path:
    val = os.environ.get(var, "").strip()
    return Path(val).expanduser() if val else default


def out_dir(create: bool = True) -> Path:
    p = _env_dir("FTN_OUT_DIR", PACKAGE_ROOT / "dispatch" / "out")
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p


def journal_dir(create: bool = True) -> Path:
    p = _env_dir("FTN_JOURNAL_DIR", PACKAGE_ROOT / "dispatch" / "journal")
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p


def draft_dir(create: bool = True) -> Path:
    p = _env_dir("FTN_DRAFT_DIR", PACKAGE_ROOT / "dispatch" / "drafts")
    if create:
        p.mkdir(parents=True, exist_ok=True)
    return p
