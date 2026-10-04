"""Conditioning variables for FTN hypotheses (all ``hermes_interpretation``).

Each function reads only bars up to the ticket's entry time and returns True / False, or
None when it is undefined for that ticket (e.g. no US500 bars, or a London ticket for an
NY-only hypothesis).
"""

from __future__ import annotations

from datetime import date, datetime, time, timedelta

from ftn.research.bars import m15_bars, session_bounds
from ftn.research.daycontext import History, _block, _dir

LOW_LEVELS = {"pdl", "week_so_far_low", "itl"}
HIGH_LEVELS = {"pdh", "week_so_far_high", "ith"}


def _sgn(side: str) -> int:
    return 1 if side == "buy" else -1


def _fvg(bars: list[dict], side: str):
    for i in range(2, len(bars)):
        if side == "buy" and bars[i]["l"] > bars[i - 2]["h"]:
            return (bars[i - 2]["h"] + bars[i]["l"]) / 2
        if side == "sell" and bars[i]["h"] < bars[i - 2]["l"]:
            return (bars[i]["h"] + bars[i - 2]["l"]) / 2
    return None


def compute(row: dict, hist: History, other: History | None = None) -> dict:
    d = date.fromisoformat(row["date"])
    t = datetime.fromisoformat(row["entry_time"])
    side, entry = row["side"], float(row["entry"])
    s = hist.s
    pd_ = hist.prev(d)
    po, ph, pl, pc = hist.session(pd_)
    eq = (ph + pl) / 2
    midnight = datetime.combine(d, time(0, 0))
    bars = m15_bars(s, midnight, t)
    ridx = row.get("raid_bar_index")
    f: dict = {}
    f["m1_correct_side_of_eq"] = entry < eq if side == "buy" else entry > eq
    if ridx is not None and ridx < len(bars):
        rc = bars[ridx]["c"]
        f["m2_false_breakout"] = (rc > pl) if row["raid_level"] in LOW_LEVELS else (rc < ph)
        fv = _fvg(bars[ridx:], side)
        f["m4_fvg_in_displacement"] = fv is not None
    else:
        f["m2_false_breakout"] = None
        f["m4_fvg_in_displacement"] = None
        fv = None
    f["m3_iof_aligned"] = row.get("iof_confidence") == "aligned"
    last20 = [hist.session(hist.prev(d, k)) for k in range(1, 21)]
    mid20 = (max(x[1] for x in last20) + min(x[2] for x in last20)) / 2
    f["m5_ipda20_discount"] = entry < mid20 if side == "buy" else entry > mid20
    c21 = hist.session(hist.prev(d, 21))[3]
    f["m6_with_20d_swing"] = (pc - c21) * _sgn(side) > 0
    opp = LOW_LEVELS if side == "buy" else HIGH_LEVELS
    f["m7_osok_profile"] = d.weekday() <= 2 and row["raid_level"] in opp
    cb = lambda x: s.hl(datetime.combine(x, time(14, 0)), datetime.combine(x, time(20, 0)))
    cur = cb(pd_)
    hist_cb = [cb(hist.prev(pd_, k)) for k in range(1, 21) if hist.prev(pd_, k)]
    hist_cb = sorted(h - l for h, l in hist_cb if h is not None)
    f["m8_cbdr_tight"] = (cur[0] - cur[1]) < hist_cb[len(hist_cb) // 2] if cur and hist_cb else None
    if row["session"] == "ny_am":
        lo = s.ohlc(datetime.combine(d, time(2, 0)), datetime.combine(d, time(5, 0)))
        f["m8_ny_continues_london"] = (_dir(lo[0], lo[3]) == ("bullish" if side == "buy" else "bearish")) if lo else None
    else:
        f["m8_ny_continues_london"] = None
    # US500 features (disclosure instrument), only if bars are present on that day
    f["m10_us500_confirms"] = None
    f["m11_smt_divergence"] = None
    if other is not None and d in other.pos and other.prev(d):
        ob = m15_bars(other.s, midnight, t)
        if ridx is not None and ridx < len(ob) and ob:
            f["m10_us500_confirms"] = (ob[-1]["c"] - ob[ridx]["c"]) * _sgn(side) > 0
        oo, oh, ol, oc = other.session(other.prev(d))
        hl = other.s.hl(midnight, t)
        if hl:
            f["m11_smt_divergence"] = (hl[1] > ol) if row["raid_level"] in LOW_LEVELS else (hl[0] < oh)
    # top-down: prev ISO week, prev session, last completed 4h block
    wk = [x for x in hist.days if (x.isocalendar()[:2] == (d - timedelta(days=7)).isocalendar()[:2])]
    want = "bullish" if side == "buy" else "bearish"
    if wk:
        wo, wc = hist.session(wk[0])[0], hist.session(wk[-1])[3]
        h4 = s.ohlc(*_block(t, 4))
        f["m12_topdown_agree"] = (_dir(wo, wc) == want and _dir(po, pc) == want
                                  and bool(h4) and _dir(h4[0], h4[3]) == want)
    else:
        f["m12_topdown_agree"] = None
    in_win = time(8, 30) <= t.time() <= time(11, 0)
    f["m13_bridge_window_fvg"] = bool(in_win and fv is not None and ((fv <= eq) if side == "buy" else (fv >= eq)))
    return f
