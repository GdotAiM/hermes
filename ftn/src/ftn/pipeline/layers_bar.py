"""Bar-derived month layers for the per-ticket trace (F4/F5). CONTEXT ONLY.

Every value here is a labelled ``hermes_interpretation`` formula over 1m bars up to the ticket's entry
time (causal). They are computed AFTER the Month 9 kernel has selected and gated the ticket and live only in
``trace["layers"]``. Nothing here is written into the DayContext, ``pair_institutional``, the origin PD array,
the ``month5/6/7`` attach triggers in ``os/dtr.py`` or the MarketState fingerprint, so none of it can feed
REV eligibility, direction, stops or gates (guarded by ``tests/test_ticket_invariance.py``).

Layers:
  M5  IPDA 20/40/60-session ranges and where the entry sits (discount / premium of each range)
  M6  20-session swing direction and the previous calendar month's candle
  M7  previous ISO week range/direction, week-so-far extremes, weekday, OSOK-style raid proxy
  M12 top-down candle directions: previous ISO week, previous session, last completed 4h block
  features  the 13 FTN-H001..H013 scoring features (``research/features.compute``, unchanged formulas)
  W%R  Williams %R(10, m15) from the prior evening (18:00 NY) up to the raid bar (F5). The kernel's own
       ``sentiment.indicator`` (bars from 00:00 NY) is left unchanged.
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from ftn.os.wr import williams_r
from ftn.research.bars import m15_bars, session_bounds
from ftn.research.daycontext import History, _block, _dir
from ftn.research.features import compute as compute_features

ORIGIN = "hermes_interpretation"
LOW_LEVELS = {"pdl", "week_so_far_low", "itl"}
HIGH_LEVELS = {"pdh", "week_so_far_high", "ith"}


def layer(value, formula: str, available: bool = True, why: str | None = None, month: str | None = None) -> dict:
    return {"value": value, "available": bool(available), "why_unavailable": None if available else why,
            "role": "annotate", "feeds_rev": False, "origin": ORIGIN, "formula": formula, "month": month}


def _want(side: str | None) -> str | None:
    return {"buy": "bullish", "sell": "bearish"}.get(side or "")


def _sessions(hist: History, d: date, k: int):
    out = []
    for i in range(1, k + 1):
        p = hist.prev(d, i)
        if p is None:
            return None
        out.append(hist.session(p))
    return out


def m5_ipda(hist: History, d: date, entry: float) -> dict:
    v = {}
    for k in (20, 40, 60):
        ss = _sessions(hist, d, k)
        if not ss:
            v[f"ipda{k}"] = None
            continue
        hi, lo = max(x[1] for x in ss), min(x[2] for x in ss)
        mid = (hi + lo) / 2
        v[f"ipda{k}"] = {"high": hi, "low": lo, "eq": mid,
                         "entry_zone": "discount" if entry < mid else "premium" if entry > mid else "equilibrium"}
    ok = v.get("ipda20") is not None
    return layer(v, "IPDA k-session high/low/EQ (k = 20/40/60 previous sessions); entry vs EQ",
                 ok, "fewer_than_20_prior_sessions", "M5")


def m6_swing(hist: History, d: date, side: str | None) -> dict:
    pd_, p21 = hist.prev(d), hist.prev(d, 21)
    v = {"swing20": None, "prev_month_candle": None}
    if pd_ and p21:
        v["swing20"] = _dir(hist.session(p21)[3], hist.session(pd_)[3])
    first = d.replace(day=1)
    prev_m = [x for x in hist.days if x < first and (x.year, x.month) == ((first - timedelta(days=1)).year,
                                                                        (first - timedelta(days=1)).month)]
    if prev_m:
        v["prev_month_candle"] = _dir(hist.session(prev_m[0])[0], hist.session(prev_m[-1])[3])
    w = _want(side)
    v["swing20_with_ticket"] = (v["swing20"] == w) if (w and v["swing20"]) else None
    return layer(v, "swing20 = sign(close[D-1] - close[D-21]); prev_month_candle = first open -> last close of the "
                    "previous calendar month's sessions", v["swing20"] is not None, "fewer_than_21_prior_sessions", "M6")


def m7_week(hist: History, d: date, t: datetime, side: str | None, raid_level: str | None) -> dict:
    iso = d.isocalendar()[:2]
    prev_iso = (d - timedelta(days=7)).isocalendar()[:2]
    pw = [x for x in hist.days if x.isocalendar()[:2] == prev_iso]
    wk = [x for x in hist.days if x < d and x.isocalendar()[:2] == iso]
    v = {"weekday": d.strftime("%a"), "prev_week": None, "week_so_far": None}
    if pw:
        ss = [hist.session(x) for x in pw]
        v["prev_week"] = {"high": max(x[1] for x in ss), "low": min(x[2] for x in ss),
                          "direction": _dir(ss[0][0], ss[-1][3])}
    today = hist.s.hl(session_bounds(d)[0], t)
    hs = [hist.session(x)[1] for x in wk] + ([today[0]] if today else [])
    ls = [hist.session(x)[2] for x in wk] + ([today[1]] if today else [])
    if hs and ls:
        v["week_so_far"] = {"high": max(hs), "low": min(ls)}
    opp = LOW_LEVELS if side == "buy" else HIGH_LEVELS if side == "sell" else set()
    v["osok_proxy"] = bool(d.weekday() <= 2 and raid_level in opp) if side else None
    return layer(v, "previous ISO week H/L/direction; week-so-far H/L incl. today up to entry; OSOK proxy = Mon-Wed "
                    "raid on the side opposite the ticket", bool(pw), "no_previous_iso_week_in_tape", "M7")


def m12_topdown(hist: History, d: date, t: datetime, side: str | None) -> dict:
    prev_iso = (d - timedelta(days=7)).isocalendar()[:2]
    pw = [x for x in hist.days if x.isocalendar()[:2] == prev_iso]
    pd_ = hist.prev(d)
    v = {"weekly": None, "daily": None, "h4": None}
    if pw:
        v["weekly"] = _dir(hist.session(pw[0])[0], hist.session(pw[-1])[3])
    if pd_:
        po, _, _, pc = hist.session(pd_)
        v["daily"] = _dir(po, pc)
    h4 = hist.s.ohlc(*_block(t, 4))
    if h4:
        v["h4"] = _dir(h4[0], h4[3])
    w = _want(side)
    vals = [v["weekly"], v["daily"], v["h4"]]
    v["all_agree_with_ticket"] = (all(x == w for x in vals)) if (w and all(vals)) else None
    return layer(v, "candle direction of the previous ISO week, previous session and last completed 4h block "
                    "(18:00 NY grid)", all(vals), "missing_week_session_or_h4", "M12")


def wr_prior_evening(hist: History, d: date, t: datetime, raid_bar_index) -> dict:
    """F5: W%R(10, m15) with bars from the prior evening (18:00 NY), cut at the raid bar like the kernel's."""
    midnight = datetime.combine(d, time(0, 0))
    cut = midnight + timedelta(minutes=15 * (int(raid_bar_index) + 1)) if raid_bar_index is not None else t
    cut = min(cut, t)
    bars = m15_bars(hist.s, session_bounds(d)[0], cut)
    wr = williams_r(bars)
    return layer({**{k: wr.get(k) for k in ("value", "state", "period", "timeframe")}, "bars_used": len(bars),
                  "window": f"{session_bounds(d)[0].isoformat()} -> {cut.isoformat()}"},
                 "Williams %R(10) on m15 bars from 18:00 NY the prior evening up to the raid bar close",
                 wr.get("value") is not None, "fewer_than_10_m15_bars", "M9-sentiment")


def bar_layers(row: dict, hist: History, other: History | None = None) -> dict:
    """All bar-derived context layers for one ticket row (needs date, entry_time, side, entry, raid_*)."""
    d = date.fromisoformat(row["date"])
    t = datetime.fromisoformat(row["entry_time"])
    side, entry = row.get("side"), float(row["entry"])
    out = {
        "M5_ipda": m5_ipda(hist, d, entry),
        "M6_swing": m6_swing(hist, d, side),
        "M7_week": m7_week(hist, d, t, side, row.get("raid_level")),
        "M12_topdown": m12_topdown(hist, d, t, side),
        "W%R_prior_evening": wr_prior_evening(hist, d, t, row.get("raid_bar_index")),
    }
    if side in ("buy", "sell"):
        f = compute_features(row, hist, other)
        out["features"] = layer(f, "research/features.compute (FTN-H001..H013 conditioning variables, unchanged)",
                                True, None, "M1-M13")
    else:
        out["features"] = layer(None, "research/features.compute", False, "ticket_without_side", "M1-M13")
    return out
