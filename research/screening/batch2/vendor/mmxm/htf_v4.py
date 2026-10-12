"""v4 HTF bias methods: NY midnight open, IPDA 20/40/60-day ranges, ICT weekly profiles.

All functions take the state known at the decision time: `J` = last CLOSED daily bar, `t_now` = last 1m
bar closed before 09:30 NY, `ref` = close of that bar. Nothing after t_now is read.
"""
from __future__ import annotations

import numpy as np

from .indicators import atr

MON, TUE, WED, THU, FRI = range(5)


def _draw_bias(up, dn, ref, one_sided_ok=True):
    if up is not None and dn is not None:
        du, dd = up - ref, ref - dn
        return (1, up, dn) if du < dd else ((-1, dn, up) if dd < du else (0, None, None))
    if up is not None and one_sided_ok:
        return 1, up, None
    if dn is not None and one_sided_ok:
        return -1, dn, None
    return 0, None, None


# ---------------------------------------------------------------------- midnight open
def midnight_open(start_ns: np.ndarray, o: np.ndarray, midnight_ns: int, t_now: int, max_gap_min: int = 15):
    """Open of the first 1m bar starting in [00:00, 00:00 + max_gap_min) NY. Known from 00:00 on."""
    i = int(np.searchsorted(start_ns, midnight_ns, "left"))
    if i >= len(start_ns) or i > t_now or start_ns[i] >= midnight_ns + max_gap_min * 60 * 10**9:
        return None
    return float(o[i])


# ---------------------------------------------------------------------- IPDA ranges
def ipda(Dctx, J: int, t_now: int, ref: float, n: int, one_sided_ok=True):
    """Range = last n CLOSED daily bars (J-n+1..J). Draw candidates: range high/low if not traded through
    since bar J closed (i.e. before 09:30 today), and unfilled daily FVGs whose 3rd candle lies in the window.
    Nearer candidate sets the side. Returns (bias, lvl, opp, range_hi, range_lo)."""
    if J - n + 1 < 0:
        return 0, None, None, None, None
    H, L = Dctx.H[J - n + 1:J + 1], Dctx.L[J - n + 1:J + 1]
    hi, lo = float(H.max()), float(L.min())
    s = Dctx.end_m1[J]
    hi_since = Dctx.h1m[s:t_now + 1].max() if t_now >= s else -np.inf
    lo_since = Dctx.l1m[s:t_now + 1].min() if t_now >= s else np.inf
    ups, dns = [], []
    if hi > ref and hi_since < hi:
        ups.append(hi)
    if lo < ref and lo_since > lo:
        dns.append(lo)
    f = Dctx.f
    m = (f.idx >= J - n + 1) & (f.idx <= J) & (Dctx.f_fill > t_now)
    ups += list(f.bottom[m & (f.bottom > ref)])
    dns += list(f.top[m & (f.top < ref)])
    b, lvl, opp = _draw_bias(min(ups) if ups else None, max(dns) if dns else None, ref, one_sided_ok)
    return b, lvl, opp, hi, lo


# ---------------------------------------------------------------------- weekly profiles
def week_days(Dctx, J: int, today_monday, today_dow: int, t_now: int, o1m):
    """Trading days of the current week known at 09:29 today: closed daily bars of this week
    (index <= J) + today's partial day (from bar J's close up to t_now).
    Returns list of dicts: dow, H, L, O, C, i0, i1 (1m index range), didx (daily index or None)."""
    days = []
    keys = Dctx.b.index
    j = J
    while j >= 0:
        k = keys[j]
        mon = k - np.timedelta64(k.weekday(), "D") if hasattr(k, "weekday") else None
        if mon != today_monday:
            break
        days.append(dict(dow=k.weekday(), H=Dctx.H[j], L=Dctx.L[j], O=Dctx.O[j], C=Dctx.C[j],
                         i0=int(Dctx.b["i0"].iloc[j]), i1=int(Dctx.b["i1"].iloc[j]), didx=j))
        j -= 1
    days.reverse()
    s = Dctx.end_m1[J] if J >= 0 else 0
    if t_now >= s:
        seg_h, seg_l = Dctx.h1m[s:t_now + 1], Dctx.l1m[s:t_now + 1]
        days.append(dict(dow=today_dow, H=float(seg_h.max()), L=float(seg_l.min()), O=float(o1m[s]), C=None,
                         i0=int(s), i1=int(t_now), didx=None))
    return days


def weekly_profiles(Dctx, J: int, t_now: int, ref: float, today_dow: int, days, cfg, daily_atr):
    """Returns dict of profile -> bias (+1 bullish, -1 bearish, 0 none), plus the combined profile and draw levels."""
    out = dict(wp_early_extreme=0, wp_tuesday=0, wp_wed_reversal=0, wp_thu_reversal=0)
    if not days:
        return out, dict(combined=0, lvl=None)
    by = {d["dow"]: d for d in days}
    H1, L1 = Dctx.h1m, Dctx.l1m
    WH = max(d["H"] for d in days); WL = min(d["L"] for d in days)
    wl_day = min(days, key=lambda d: d["L"]); wh_day = max(days, key=lambda d: d["H"])
    # exact 1m index of the week's low / high
    wl_i = wl_day["i0"] + int(np.argmin(L1[wl_day["i0"]:wl_day["i1"] + 1]))
    wh_i = wh_day["i0"] + int(np.argmax(H1[wh_day["i0"]:wh_day["i1"] + 1]))
    hi_after_wl = H1[wl_i + 1:t_now + 1].max() if t_now > wl_i else -np.inf
    lo_after_wh = L1[wh_i + 1:t_now + 1].min() if t_now > wh_i else np.inf

    def last_swing(sw, before_didx):
        m = (sw.confirm <= J) & (sw.pivot < before_didx)
        return float(sw.price[m][-1]) if m.any() else None

    # P1 early extreme: week low (high) printed on Mon/Tue on a PRIOR day, then a daily swing high (low) broken
    bull = bear = False
    if wl_day["dow"] in (MON, TUE) and wl_day["dow"] < today_dow and wl_day["didx"] is not None:
        sh = last_swing(Dctx.sh, wl_day["didx"])
        bull = sh is not None and hi_after_wl > sh
    if wh_day["dow"] in (MON, TUE) and wh_day["dow"] < today_dow and wh_day["didx"] is not None:
        sl = last_swing(Dctx.sl, wh_day["didx"])
        bear = sl is not None and lo_after_wh < sl
    out["wp_early_extreme"] = 1 if bull and not bear else (-1 if bear and not bull else 0)
    # P2 classic Tuesday low (high) of week: WL on Tuesday, Monday's high taken after it; trade Wed-Fri
    if today_dow >= WED and MON in by and TUE in by:
        bull = wl_day["dow"] == TUE and hi_after_wl > by[MON]["H"]
        bear = wh_day["dow"] == TUE and lo_after_wh < by[MON]["L"]
        out["wp_tuesday"] = 1 if bull and not bear else (-1 if bear and not bull else 0)
    # P3 Wednesday reversal: Mon->Tue declined (Tue close < Mon open), WL on Wednesday, then Tuesday's high taken; trade Thu-Fri
    if today_dow >= THU and all(k in by for k in (MON, TUE, WED)):
        bull = by[TUE]["C"] < by[MON]["O"] and wl_day["dow"] == WED and hi_after_wl > by[TUE]["H"]
        bear = by[TUE]["C"] > by[MON]["O"] and wh_day["dow"] == WED and lo_after_wh < by[TUE]["L"]
        out["wp_wed_reversal"] = 1 if bull and not bear else (-1 if bear and not bull else 0)
    # P4 consolidation Thursday reversal: Mon-Wed range <= k x daily ATR14 (at Wed close)
    if today_dow >= THU and all(k in by for k in (MON, TUE, WED)) and by[WED]["didx"] is not None:
        a = daily_atr[by[WED]["didx"]]
        ch = max(by[k]["H"] for k in (MON, TUE, WED)); cl = min(by[k]["L"] for k in (MON, TUE, WED))
        if not np.isnan(a) and ch - cl <= cfg.wp_cons_atr_mult * a and THU in by:
            th = by[THU]
            if today_dow == THU:      # Thursday pre-09:30 ran one side of the consolidation -> expect the reversal
                bull, bear = th["L"] < cl and th["H"] <= ch, th["H"] > ch and th["L"] >= cl
            else:                     # Friday: Thursday swept one side and closed back inside
                bull = th["L"] < cl and th["H"] <= ch and th["C"] is not None and th["C"] > cl and wl_day["dow"] == THU
                bear = th["H"] > ch and th["L"] >= cl and th["C"] is not None and th["C"] < ch and wh_day["dow"] == THU
            out["wp_thu_reversal"] = 1 if bull and not bear else (-1 if bear and not bull else 0)
    comb = 0
    for k in ("wp_thu_reversal", "wp_wed_reversal", "wp_tuesday", "wp_early_extreme"):   # most specific first
        if out[k] != 0:
            comb = out[k]
            break
    lvl = None if comb == 0 else (WH if comb == 1 else WL)
    return out, dict(combined=comb, lvl=lvl, WH=WH, WL=WL)
