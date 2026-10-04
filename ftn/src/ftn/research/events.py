"""US high-impact macro calendar (FOMC / CPI / NFP) for the bar-derived DayContext (post-H015b fix 5).

Source: ``data/us_macro_events.csv``, exported from ``/workspace/marketdata`` ``calendar("events")``
(federalreserve.gov, BLS archives). Scheduled release times are public in advance, so attaching the whole day's
schedule at any time ``t`` is causal. Context only: the Month 9 kernel does not read the calendar; Month 8 uses any
high-impact event to set the London gate to ``news`` and ``pick_focus`` records the calendar as the focus source.
``FTN_EVENTS_CSV`` overrides the file.
"""

from __future__ import annotations

import csv
import os
from datetime import date, time
from functools import lru_cache
from pathlib import Path

DEFAULT = Path(__file__).with_name("data") / "us_macro_events.csv"
USD_SENSITIVE = {"US100", "US500", "EURUSD", "GBPUSD", "XAUUSD", "USDJPY", "NQ", "ES"}


def _killzone(t: time) -> str:
    if time(2, 0) <= t < time(5, 0):
        return "london"
    if time(7, 0) <= t < time(10, 0):
        return "ny_am"
    if time(13, 30) <= t < time(16, 0):
        return "ny_pm"
    return "none"


@lru_cache(maxsize=4)
def load_events(path: str | None = None) -> dict[date, tuple]:
    p = Path(path or os.environ.get("FTN_EVENTS_CSV") or DEFAULT)
    out: dict[date, list] = {}
    if not p.is_file():
        return {}
    with p.open() as fh:
        rows = csv.DictReader(line for line in fh if not line.startswith("#"))
        for r in rows:
            d = date.fromisoformat(r["date"][:10])
            hh, mm = (int(x) for x in (r.get("time_ny") or "00:00").split(":")[:2])
            out.setdefault(d, []).append({"event": r["event"], "kind": r["kind"], "time_ny": f"{hh:02d}:{mm:02d}",
                                          "impact": "high", "killzone": _killzone(time(hh, mm)),
                                          "source": r.get("source") or "marketdata calendar"})
    return {k: tuple(v) for k, v in out.items()}


def day_events(d: date, symbol: str, path: str | None = None) -> list[dict]:
    if symbol.upper() not in USD_SENSITIVE:
        return []
    return [dict(e, pair=symbol) for e in load_events(path).get(d, ())]
