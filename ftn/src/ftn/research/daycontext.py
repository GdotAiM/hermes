"""Bar-derived DayContext for the Month 9 kernel (causal: nothing after ``t``).

Every field that ICT reads by eye is computed here by a labelled
``hermes_interpretation`` formula (REPORT D16). The kernel then runs unchanged.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from ftn.research.bars import Series, m15_bars, session_bounds

ORIGIN = "hermes_interpretation"


def _dir(o, c) -> str:
    return "bullish" if c > o else "bearish" if c < o else "unclear"


def _block(t: datetime, hours: int) -> tuple[datetime, datetime]:
    """Last completed block of ``hours`` ending at or before t (grid anchored at 18:00 NY)."""
    anchor = datetime.combine(t.date(), time(18, 0))
    while anchor > t:
        anchor -= timedelta(days=1)
    n = int((t - anchor).total_seconds() // (hours * 3600))
    end = anchor + timedelta(hours=hours * n)
    return end - timedelta(hours=hours), end


class History:
    """Per-instrument session lookups shared across days."""

    def __init__(self, s: Series, days: list[date]):
        self.s = s
        self.days = days
        self.pos = {d: i for i, d in enumerate(days)}
        self._ohlc = {}

    def session(self, d: date):
        if d not in self._ohlc:
            a, b = session_bounds(d)
            self._ohlc[d] = self.s.ohlc(a, b)
        return self._ohlc[d]

    def prev(self, d: date, k: int = 1):
        i = self.pos.get(d)
        if i is None or i - k < 0:
            return None
        return self.days[i - k]


def build_raw(hist: History, d: date, t: datetime, session_name: str) -> dict | None:
    s = hist.s
    pd_ = hist.prev(d)
    if pd_ is None or hist.prev(d, 22) is None:
        return None
    po, ph, pl, pc = hist.session(pd_)
    midnight = datetime.combine(d, time(0, 0))
    bars = [{k: v for k, v in b.items() if k != "_t"} for b in m15_bars(s, midnight, t)]
    if len(bars) < 6:
        return None
    last = s.close_at(t)
    asian = s.hl(datetime.combine(d - timedelta(days=1), time(20, 0)), midnight)
    cbdr = s.hl(datetime.combine(pd_, time(14, 0)), datetime.combine(pd_, time(20, 0)))
    # week so far: sessions earlier this ISO week
    wk = [x for x in hist.days[max(0, hist.pos[d] - 5):hist.pos[d]] if x.isocalendar()[:2] == d.isocalendar()[:2]]
    named = {"pdh": ph, "pdl": pl}
    if wk:
        named["week_so_far_high"] = max(hist.session(x)[1] for x in wk)
        named["week_so_far_low"] = min(hist.session(x)[2] for x in wk)
    # daily FVGs from the last 20 sessions (3-candle gaps on session OHLC)
    sess = [hist.prev(d, k) for k in range(22, 0, -1)]
    daily = []
    for i in range(2, len(sess)):
        a, c3 = hist.session(sess[i - 2]), hist.session(sess[i])
        if c3[2] > a[1]:
            daily.append({"id": f"D_FVG_bull_{sess[i]}", "kind": "FVG", "low": a[1], "high": c3[2]})
        elif c3[1] < a[2]:
            daily.append({"id": f"D_FVG_bear_{sess[i]}", "kind": "FVG", "low": c3[1], "high": a[2]})
    # candle-colour daytrade IOF (interpretation)
    h4 = s.ohlc(*_block(t, 4))
    m60 = s.ohlc(*_block(t, 1))
    iof = {"daily": _dir(po, pc), "h4": _dir(h4[0], h4[3]) if h4 else "unclear",
           "m60": _dir(m60[0], m60[3]) if m60 else "unclear"}
    rngs = [hist.session(hist.prev(d, k)) for k in range(1, 6)]
    adr = sum(r[1] - r[2] for r in rngs) / 5
    so_far = s.hl(session_bounds(d)[0], t)
    return {
        "date": d.isoformat(),
        "symbol": s.symbol,
        "timezone": "America/New_York",
        "last": last,
        "focus_pair": s.symbol,
        "calendar": [],
        "watchlist": [s.symbol],
        "pair_institutional": {"sponsorship": {"daily": iof["daily"], "h4": iof["h4"]}, "daytrade_iof": iof},
        "opens": {"ny_midnight": s.close_at(midnight + timedelta(minutes=1))},
        "ranges": {
            "previous_day": {"high": ph, "low": pl, "close": pc},
            **({"asian": {"high": asian[0], "low": asian[1]}} if asian else {}),
            **({"cbdr": {"high": cbdr[0], "low": cbdr[1]}} if cbdr else {}),
            "named_extremes": named,
        },
        "adr5": {"high": None, "low": None,
                 "remaining": max(0.0, adr - (so_far[0] - so_far[1])) if so_far else None},
        "pd_matrix": {"htf": {"daily": daily}, "ltf": {}},
        "evidence": {"session": session_name, "pip": 1.0, "provenance": ORIGIN,
                     "source": "ftn.research.daycontext (bar-derived)"},
        "bars_m15": bars,
    }
