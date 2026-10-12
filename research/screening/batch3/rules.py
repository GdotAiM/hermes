"""Batch 3 rules (PROTOCOL_BATCH3.md). Pure functions on an ftn BID Series (naive NY wall clock, bar time = bar open).
All parameters are module constants fixed in the protocol; nothing here is fitted."""
from __future__ import annotations

from datetime import date, datetime, time, timedelta

from research.screening.batch2.adapters import NYSE_CLOSED

ATR_N = 14              # sessions
MIN_SESSION_BARS = 60   # a session counts for ATR / PD levels only with >= 60 bars
MIN_AM_BARS = 120       # of the 150 bars 09:30-11:59
MIN_RANGE_BARS = 30     # Asia / London range needs >= 30 bars
MIN_OR_BARS = 20        # opening range 09:30-09:59 needs >= 20 bars
RECLAIM_N = 5           # sweep bar + up to 4 more bars to close back inside
BUF_ATR = 0.05          # stop buffer beyond the sweep extreme
RISK_FLOOR_ATR = 0.10   # sweep-trade stop is widened so that risk >= 0.10 ATR
FIXED_STOP_ATR = 0.25   # E3/E4/E5 stop distance
TARGET_R = 2.0
SIG_END = time(11, 30)  # signal bars must open before 11:30
EXIT_T = time(12, 0)    # flat at the close of the last bar before 12:00
RULES = ("E1", "E2", "E3", "E4", "E5")


def _dt(d, hh, mm=0):
    return datetime.combine(d, time(hh, mm))


def _hl(s, rg):
    return (max(s.h[k] for k in rg), min(s.l[k] for k in rg)) if len(rg) else (None, None)


def day_contexts(s, start: date, end: date):
    """Yield per-day context for eligible trade dates in [start, end]."""
    dates = sorted({t.date() for t in s.t if t.weekday() < 5})
    sess = {}
    for d in dates:
        rg = s.window(_dt(d - timedelta(days=1), 18), _dt(d, 17))
        if len(rg) >= MIN_SESSION_BARS:
            sess[d] = _hl(s, rg)
    hist = []          # eligible prior sessions (date, H, L), NYSE closures excluded as trade dates but not as sessions
    for d in dates:
        am = s.window(_dt(d, 9, 30), _dt(d, 12))
        ok = (start <= d <= end and d.isoformat() not in NYSE_CLOSED and len(am) >= MIN_AM_BARS
              and len(hist) >= ATR_N)
        if ok:
            atr = sum(h - l for _, h, l in hist[-ATR_N:]) / ATR_N
            pd_, pdh, pdl = hist[-1]
            asia = s.window(_dt(d - timedelta(days=1), 19), _dt(d, 0))
            lon = s.window(_dt(d, 2), _dt(d, 5))
            ranges = [_hl(s, r) for r in (asia, lon) if len(r) >= MIN_RANGE_BARS]
            orr = s.window(_dt(d, 9, 30), _dt(d, 10))
            yield dict(date=d, am=am, atr=atr, pdh=pdh, pdl=pdl,
                       sh=max(h for h, _ in ranges) if ranges else None, sl=min(l for _, l in ranges) if ranges else None,
                       orh=_hl(s, orr)[0] if len(orr) >= MIN_OR_BARS else None,
                       orl=_hl(s, orr)[1] if len(orr) >= MIN_OR_BARS else None)
        if d in sess and d.isoformat() not in NYSE_CLOSED:
            hist.append((d, *sess[d]))


def _manage(s, ctx, j, side, entry, stop, F):
    """Simulate from bar j+1: stop first if both touched; gap through stop fills at open; time exit at last bar < 12:00."""
    risk = abs(entry - stop)
    tgt = entry + side * TARGET_R * risk
    am = ctx["am"]; last = am[-1]
    exit_px, why = None, "time"
    for k in range(j + 1, last + 1):
        if side > 0:
            if s.l[k] <= stop:
                exit_px, why = min(s.o[k], stop), "stop"; break
            if s.h[k] >= tgt:
                exit_px, why = tgt, "target"; break
        else:
            if s.h[k] >= stop:
                exit_px, why = max(s.o[k], stop), "stop"; break
            if s.l[k] <= tgt:
                exit_px, why = tgt, "target"; break
    if exit_px is None:
        exit_px = s.c[last]
    R = (side * (exit_px - entry) - F) / risk
    return dict(R=R, risk_pts=risk, entry=entry, stop=stop, exit=exit_px, why=why,
                direction="long" if side > 0 else "short", t_entry=s.t[j].isoformat())


def _sweep(s, ctx, hi, lo):
    """First completed sweep-and-reclaim of hi (short) or lo (long) in the signal window; returns (j, side, stop) or None."""
    am = [k for k in ctx["am"] if s.t[k].time() < SIG_END]
    if not am:
        return None
    o0 = s.o[ctx["am"][0]]
    best = []
    for side, lvl in ((-1, hi), (1, lo)):
        if lvl is None or (side < 0 and o0 >= lvl) or (side > 0 and o0 <= lvl):
            continue
        i = next((k for k in am if (s.h[k] > lvl if side < 0 else s.l[k] < lvl)), None)
        if i is None:
            continue
        for j in range(i, min(i + RECLAIM_N, am[-1] + 1)):
            if (s.c[j] < lvl) if side < 0 else (s.c[j] > lvl):
                ext = max(s.h[i:j + 1]) if side < 0 else min(s.l[i:j + 1])
                stop = ext - side * BUF_ATR * ctx["atr"]
                best.append((j, side, stop)); break
    return min(best) if best else None


def _close_beyond(s, ctx, hi, lo, t0):
    for k in ctx["am"]:
        tt = s.t[k].time()
        if tt < t0 or tt >= SIG_END:
            continue
        if s.c[k] > hi:
            return k, 1
        if s.c[k] < lo:
            return k, -1
    return None


def run_rule(rule, sym, s, F, start: date, end: date):
    out = []
    for ctx in day_contexts(s, start, end):
        atr, tr = ctx["atr"], None
        if rule in ("E1", "E2"):
            hi, lo = (ctx["sh"], ctx["sl"]) if rule == "E1" else (ctx["pdh"], ctx["pdl"])
            sw = _sweep(s, ctx, hi, lo)
            if sw:
                j, side, stop = sw
                e = s.c[j]
                stop = e - side * max(abs(e - stop), RISK_FLOOR_ATR * atr)
                tr = _manage(s, ctx, j, side, e, stop, F)
        elif rule == "E3":
            o0 = s.o[ctx["am"][0]]
            if ctx["pdl"] <= o0 <= ctx["pdh"]:
                b = _close_beyond(s, ctx, ctx["pdh"], ctx["pdl"], time(9, 30))
                if b:
                    j, side = b
                    tr = _manage(s, ctx, j, side, s.c[j], s.c[j] - side * FIXED_STOP_ATR * atr, F)
        elif rule in ("E4", "E5") and ctx["orh"] is not None:
            b = _close_beyond(s, ctx, ctx["orh"], ctx["orl"], time(10, 0))
            if b:
                j, side = b
                if rule == "E5":
                    side = -side
                tr = _manage(s, ctx, j, side, s.c[j], s.c[j] - side * FIXED_STOP_ATR * atr, F)
        if tr:
            d = ctx["date"]
            tr.update(symbol=sym, date=d.isoformat(), session="ny_am", weekday=d.weekday())
            out.append(tr)
    return out
