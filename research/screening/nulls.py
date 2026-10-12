"""S3 null generators (protocol v1 section 3). Synthetic BID+ASK Series built from the burned tape only."""
from __future__ import annotations

from datetime import datetime, time, timedelta

import numpy as np

from ftn.research.bars import Series


def _sessions(bid):
    """Weekday session slots (date, [start, end)) covering the tape: 18:00 prev -> 17:00."""
    d0, d1 = bid.t[0].date(), bid.t[-1].date()
    out, d = [], d0
    while d <= d1:
        if d.weekday() < 5:
            out.append((d, datetime.combine(d - timedelta(days=1), time(18)), datetime.combine(d, time(17))))
        d += timedelta(days=1)
    return out


def shuffled_day(bid: Series, ask: Series, seed: int) -> tuple[Series, Series]:
    """Null A: permute whole sessions, keep each intraday BID/ASK path, re-level additively for continuity."""
    rng = np.random.default_rng(seed)
    slots = _sessions(bid)
    perm = rng.permutation(len(slots))
    bt, bo, bh, bl, bc = [], [], [], [], []
    at, ao, ah, al, ac = [], [], [], [], []
    last = bid.c[0]
    for i, (d, s0, s1) in enumerate(slots):
        sd, ss0, ss1 = slots[perm[i]]
        shift_t = (d - sd)
        rb = bid.window(ss0, ss1)
        if not len(rb):
            continue
        dp = last - bid.o[rb[0]]
        for k in rb:
            bt.append(bid.t[k] + shift_t); bo.append(bid.o[k] + dp); bh.append(bid.h[k] + dp)
            bl.append(bid.l[k] + dp); bc.append(bid.c[k] + dp)
        for k in ask.window(ss0, ss1):
            at.append(ask.t[k] + shift_t); ao.append(ask.o[k] + dp); ah.append(ask.h[k] + dp)
            al.append(ask.l[k] + dp); ac.append(ask.c[k] + dp)
        last = bc[-1]
    return (Series(bid.symbol, bt, bo, bh, bl, bc, f"nullA:{seed}"), Series(ask.symbol, at, ao, ah, al, ac, f"nullA:{seed}"))


def minute_sigma(bid: Series) -> np.ndarray:
    t = bid.t; c = np.array(bid.c)
    mod = np.array([x.hour * 60 + x.minute for x in t])
    gap = np.array([0] + [(t[i] - t[i - 1]).total_seconds() == 60 for i in range(1, len(t))], bool)
    dc = np.r_[0, np.diff(c)]
    sig = np.zeros(1440)
    for m in range(1440):
        x = dc[(mod == m) & gap]
        sig[m] = x.std() if len(x) > 20 else np.nan
    allx = dc[gap]
    if not len(allx):   # no 1-minute steps at all (toy series): per-sqrt-minute scale of all steps
        gm = np.array([1.0] + [max(1.0, (t[i] - t[i - 1]).total_seconds() / 60) for i in range(1, len(t))])
        allx = dc[1:] / np.sqrt(gm[1:])
    sig[np.isnan(sig)] = np.median(np.abs(allx)) * 1.4826
    return sig


def random_walk(bid: Series, ask: Series, seed: int, sig=None) -> tuple[Series, Series]:
    """Null B: matched minute-of-day volatility random walk on the real BID timestamps; ASK = BID + real spread."""
    rng = np.random.default_rng(seed)
    sig = minute_sigma(bid) if sig is None else sig
    t = bid.t; n = len(t)
    mod = np.array([x.hour * 60 + x.minute for x in t])
    gapm = np.array([1.0] + [min(60.0, max(1.0, (t[i] - t[i - 1]).total_seconds() / 60)) for i in range(1, n)])
    s = sig[mod]
    dc = rng.standard_normal(n) * s * np.sqrt(gapm); dc[0] = 0
    c = bid.c[0] + np.cumsum(dc)
    o = np.r_[bid.c[0], c[:-1]]
    h = np.maximum(o, c) + np.abs(rng.standard_normal(n)) * s / 2
    l = np.minimum(o, c) - np.abs(rng.standard_normal(n)) * s / 2
    B = Series(bid.symbol, list(t), o.tolist(), h.tolist(), l.tolist(), c.tolist(), f"nullB:{seed}")
    at, ao, ah, al, ac = [], [], [], [], []
    j = 0
    for i in range(n):
        while j < len(ask.t) and ask.t[j] < t[i]:
            j += 1
        if j < len(ask.t) and ask.t[j] == t[i]:
            sp = ask.c[j] - bid.c[i]
            at.append(t[i]); ao.append(o[i] + sp); ah.append(h[i] + sp); al.append(l[i] + sp); ac.append(c[i] + sp)
    return B, Series(ask.symbol, at, [float(x) for x in ao], [float(x) for x in ah], [float(x) for x in al],
                     [float(x) for x in ac], f"nullB:{seed}")
