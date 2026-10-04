"""F1 guard: the Month 9 kernel ticket set must stay byte-identical to the H016 registration.

Re-runs the base streams exactly as they were registered (``prereg-H016``, rule commit ``9bed235``):
bar-derived DayContext with the FOMC/CPI/NFP calendar, interpretation triggers off, flat book, correct-side
BID/ASK fills, burned window 2025-08-25 -> 2026-09-25. It writes the trade CSV with the unchanged
``score.write_ticket_csv`` and compares the bytes to
``research/evidence/quant/FTN_M9_TRADES_US{100,500}_base_2026-10-04_h016_fixed_rev_burned.csv``.

Burned data only. Every R in those CSVs was already published at registration, so this reads no new R.
The guard checks that the wiring branch (pipeline trace, bar-derived context layers, W%R context, results
journal) never changes which tickets REV takes, their stops, gates, fingerprints or outcomes.
``trace=True`` re-runs the same streams with the per-ticket trace attached (``pipeline.kernel_trace``) and must
give the same bytes.
"""

from __future__ import annotations

import hashlib
import os
from copy import deepcopy
from pathlib import Path

BURNED_START, BURNED_END = "2025-08-25", "2026-09-25"
REG_TAG = "2026-10-04_h016_fixed_rev_burned"
DATA_DIR_DEFAULT = "/workspace/ftn-demo-output/data"
# sha256 of the canonical burned-window tape used for the H016 registration re-score
DATA_SHA256 = {
    "US100_1m_bid.csv.gz": "f7d2d2d38c0919d6c1436f0dca985b42228900e0bcb330d045f695c415a07301",
    "US100_1m_ask.csv.gz": "d242f48cb4caa37eb5a560ced984f75908bfbbc49156fbbdae6f1d70b298df2e",
    "US500_1m_bid.csv.gz": "140e89747c52b2db5108d039f3c7ae49aea9155f3f7721bee3dbdeee0668a86f",
    "US500_1m_ask.csv.gz": "c5408e7ff81213a4cd8e317c5e3e5adef8f5fbf3f11e2b4fb1d59126df10bcb6",
}


def data_dir() -> Path:
    return Path(os.environ.get("FTN_GUARD_DATA_DIR") or DATA_DIR_DEFAULT)


def registration_csv(sym: str) -> Path:
    from ftn.config_load import repo_root
    return repo_root().parent / "research" / "evidence" / "quant" / f"FTN_M9_TRADES_{sym}_base_{REG_TAG}.csv"


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_data() -> list[str]:
    """Problems with the guard's input tape ([] = OK)."""
    d = data_dir()
    bad = []
    for name, want in DATA_SHA256.items():
        p = d / name
        if not p.is_file():
            bad.append(f"missing {p}")
        elif _sha(p) != want:
            bad.append(f"sha256 differs {p}")
    return bad


def load_histories():
    from ftn.research.score import load_history
    d = data_dir()
    hists = {}
    for sym in ("US100", "US500"):
        h = load_history(sym, str(d / f"{sym}_1m_bid.csv.gz"), str(d / f"{sym}_1m_ask.csv.gz"))
        h.calendar = True
        if h.days[0].isoformat() != BURNED_START or h.days[-1].isoformat() != BURNED_END:
            raise RuntimeError(f"{sym}: tape {h.days[0]}..{h.days[-1]} is not the burned window")
        hists[sym] = h
    return hists


def base_cfg() -> dict:
    from ftn.config_load import load_config
    cfg = deepcopy(load_config())
    cfg["interpretation_triggers"] = {"conso": False, "bb": False, "pip20": False}
    return cfg


def regenerate(out_dir: Path, hists=None, trace: bool = False) -> dict:
    """Write the two base trade CSVs into ``out_dir``; return {sym: {"path", "log", "trades"}}."""
    from ftn.research.kernel_log import session_ticket_log
    from ftn.research.score import run_series, write_ticket_csv
    hists = hists or load_histories()
    cfg = base_cfg()
    res = {}
    for sym, other in (("US100", hists["US500"]), ("US500", None)):
        h = hists[sym]
        log = None
        if trace:
            from ftn.pipeline.kernel_trace import trace_rows
            log = trace_rows(session_ticket_log(h, cfg), h, cfg, other)
        _, log, trades = run_series(sym, h.s.source, cfg, other, False, hist=h, log=log, cost_model="correct_side")
        p = Path(out_dir) / f"FTN_M9_TRADES_{sym}_base_{REG_TAG}.csv"
        write_ticket_csv(p, trades)
        res[sym] = {"path": p, "log": log, "trades": trades}
    return res


def compare(res: dict) -> dict:
    """{sym: {"identical": bool, "regenerated_sha256", "registration_sha256", "n_trades", "n_tickets"}}."""
    out = {}
    for sym, r in res.items():
        reg = registration_csv(sym)
        out[sym] = {"identical": r["path"].read_bytes() == reg.read_bytes(),
                    "regenerated_sha256": _sha(r["path"]), "registration_sha256": _sha(reg),
                    "n_trades": len(r["trades"]), "n_tickets": sum(1 for x in r["log"] if x["ticket"])}
    return out
