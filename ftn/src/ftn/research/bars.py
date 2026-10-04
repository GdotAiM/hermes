"""1m OHLC loader and NY-session helpers for the exploratory scorer.

Input: CSV (optionally .gz) with ``Datetime,Open,High,Low,Close`` where Datetime carries
an America/New_York offset, e.g. ``2025-08-25 00:00:00-04:00`` (the ict-blueprint
``model-u-longrun/data/US100_1m.csv.gz`` / ``US500_1m.csv.gz`` Dukascopy BID series).
Wall-clock NY time is used as-is (the offset is DST-correct in the source).
"""

from __future__ import annotations

import bisect
import csv
import gzip
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path

SESSION_START = time(18, 0)   # CFD index session: 18:00 NY (prev evening) → 16:59 NY


@dataclass
class Series:
    symbol: str
    t: list          # naive NY wall-clock datetimes, sorted
    o: list
    h: list
    l: list
    c: list
    source: str = ""

    def idx(self, dt: datetime) -> int:
        return bisect.bisect_left(self.t, dt)

    def window(self, start: datetime, end: datetime) -> range:
        """Indices with start <= t < end."""
        return range(self.idx(start), self.idx(end))

    def hl(self, start: datetime, end: datetime):
        r = self.window(start, end)
        if not len(r):
            return None
        return max(self.h[i] for i in r), min(self.l[i] for i in r)

    def ohlc(self, start: datetime, end: datetime):
        r = self.window(start, end)
        if not len(r):
            return None
        return (self.o[r[0]], max(self.h[i] for i in r), min(self.l[i] for i in r), self.c[r[-1]])

    def close_at(self, dt: datetime):
        """Close of the last bar strictly before ``dt``."""
        i = self.idx(dt) - 1
        return self.c[i] if i >= 0 else None


def load_series(path: str | Path, symbol: str) -> Series:
    path = Path(path)
    opener = gzip.open if path.suffix == ".gz" else open
    t, o, h, l, c = [], [], [], [], []
    with opener(path, "rt", newline="") as fh:
        for row in csv.DictReader(fh):
            t.append(datetime.strptime(row["Datetime"][:19], "%Y-%m-%d %H:%M:%S"))
            o.append(float(row["Open"])); h.append(float(row["High"]))
            l.append(float(row["Low"])); c.append(float(row["Close"]))
    order = sorted(range(len(t)), key=t.__getitem__)
    return Series(symbol, [t[i] for i in order], [o[i] for i in order], [h[i] for i in order],
                  [l[i] for i in order], [c[i] for i in order], str(path))


def session_bounds(d: date) -> tuple[datetime, datetime]:
    return datetime.combine(d - timedelta(days=1), SESSION_START), datetime.combine(d, time(17, 0))


def trading_days(s: Series, min_rth_bars: int = 300) -> list[date]:
    """Weekdays with at least ``min_rth_bars`` 1m bars in 09:30–15:59 NY."""
    days = sorted({dt.date() for dt in s.t if dt.weekday() < 5})
    out = []
    for d in days:
        n = len(s.window(datetime.combine(d, time(9, 30)), datetime.combine(d, time(16, 0))))
        if n >= min_rth_bars:
            out.append(d)
    return out


def m15_bars(s: Series, start: datetime, end: datetime) -> list[dict]:
    """15m bars aggregated from 1m in [start, end), keyed on the 15m bucket start."""
    out: list[dict] = []
    cur = None
    for i in s.window(start, end):
        dt = s.t[i]
        b0 = dt.replace(minute=dt.minute - dt.minute % 15, second=0)
        if cur is None or cur["_t"] != b0:
            if cur:
                out.append(cur)
            cur = {"_t": b0, "t": b0.strftime("%Y-%m-%dT%H:%M:00"), "o": s.o[i], "h": s.h[i], "l": s.l[i], "c": s.c[i]}
        else:
            cur["h"] = max(cur["h"], s.h[i]); cur["l"] = min(cur["l"], s.l[i]); cur["c"] = s.c[i]
    if cur:
        out.append(cur)
    return out
