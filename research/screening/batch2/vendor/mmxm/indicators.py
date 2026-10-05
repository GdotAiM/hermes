"""Pure, index-based primitives. Everything returns the index at which information becomes
KNOWN (`confirm`), so callers can never use it early."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

import numpy as np


def atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14, method: str = "wilder") -> np.ndarray:
    """ATR at bar i uses bars <= i only. NaN until `period` true ranges exist."""
    n = len(close)
    if n == 0:
        return np.full(0, np.nan)
    tr = np.empty(n)
    tr[0] = high[0] - low[0]
    if n > 1:
        pc = close[:-1]
        tr[1:] = np.maximum(high[1:] - low[1:], np.maximum(np.abs(high[1:] - pc), np.abs(low[1:] - pc)))
    out = np.full(n, np.nan)
    if n < period:
        return out
    if method == "sma":
        c = np.cumsum(np.insert(tr, 0, 0.0))
        out[period - 1:] = (c[period:] - c[:-period]) / period
        return out
    out[period - 1] = tr[:period].mean()
    for i in range(period, n):
        out[i] = (out[i - 1] * (period - 1) + tr[i]) / period
    return out


@dataclass
class Swings:
    """Accepted swing points of one kind (highs or lows)."""
    pivot: np.ndarray    # bar index of the pivot
    confirm: np.ndarray  # bar index after whose close the swing is known (= pivot + strength)
    price: np.ndarray

    def __len__(self):
        return len(self.pivot)


def raw_pivots(high: np.ndarray, low: np.ndarray, k: int = 2):
    """Swing high at i: high[i] > high of k bars on each side (strict). Mirror for lows.
    Returns (hi_idx, lo_idx). Pivots within k bars of the end are not returned (unconfirmed)."""
    n = len(high)
    his, los = [], []
    for i in range(k, n - k):
        h = high[i]
        if all(h > high[i - j] for j in range(1, k + 1)) and all(h > high[i + j] for j in range(1, k + 1)):
            his.append(i)
        lo = low[i]
        if all(lo < low[i - j] for j in range(1, k + 1)) and all(lo < low[i + j] for j in range(1, k + 1)):
            los.append(i)
    return np.array(his, dtype=int), np.array(los, dtype=int)


def swings(high: np.ndarray, low: np.ndarray, k: int = 2, min_dist=None):
    """Confirmed swings with optional distance filter.

    min_dist: None (no filter), a float, or an array (per-bar threshold, e.g. ATR-scaled,
    read at the swing's confirmation bar). A swing high is accepted only if it is >= min_dist
    above the last ACCEPTED swing low (and a swing low >= min_dist below the last accepted swing
    high). Processing is in pivot order, so the filter only uses already-known swings."""
    hi, lo = raw_pivots(high, low, k)
    ev = [(i, 0) for i in hi] + [(i, 1) for i in lo]
    ev.sort()
    last_hi = last_lo = None
    acc_h, acc_l = [], []
    for i, kind in ev:
        if min_dist is None:
            d = None
        elif np.ndim(min_dist) == 0:
            d = float(min_dist)
        else:
            d = float(min_dist[min(i + k, len(min_dist) - 1)])
            if np.isnan(d):
                continue
        if kind == 0:
            p = high[i]
            if d is None or last_lo is None or p - last_lo >= d:
                acc_h.append(i)
                last_hi = p
        else:
            p = low[i]
            if d is None or last_hi is None or last_hi - p >= d:
                acc_l.append(i)
                last_lo = p
    ah = np.array(acc_h, dtype=int)
    al = np.array(acc_l, dtype=int)
    return (Swings(ah, ah + k, high[ah] if len(ah) else np.array([])),
            Swings(al, al + k, low[al] if len(al) else np.array([])))


@dataclass
class FVGs:
    """3-candle gaps. `idx` is bar3 (known after bar3 closes)."""
    idx: np.ndarray
    top: np.ndarray
    bottom: np.ndarray
    bullish: np.ndarray  # bool

    def __len__(self):
        return len(self.idx)


def fvgs(high: np.ndarray, low: np.ndarray) -> FVGs:
    """Bullish: high[i-2] < low[i] (gap = [high[i-2], low[i]]).
    Bearish: low[i-2] > high[i]   (gap = [high[i], low[i-2]])."""
    h1, l1, h3, l3 = high[:-2], low[:-2], high[2:], low[2:]
    bull = h1 < l3
    bear = l1 > h3
    i_bull = np.nonzero(bull)[0] + 2
    i_bear = np.nonzero(bear)[0] + 2
    idx = np.concatenate([i_bull, i_bear])
    top = np.concatenate([low[i_bull], low[i_bear - 2]])
    bot = np.concatenate([high[i_bull - 2], high[i_bear]])
    isb = np.concatenate([np.ones(len(i_bull), bool), np.zeros(len(i_bear), bool)])
    o = np.argsort(idx, kind="stable")
    return FVGs(idx[o], top[o], bot[o], isb[o])


def first_cross(arr: np.ndarray, start: int, level: float, above: bool, chunk: int = 4096) -> int:
    """First index j >= start with arr[j] >= level (above=True) or arr[j] <= level. len(arr) if never."""
    n = len(arr)
    s = start
    while s < n:
        seg = arr[s:s + chunk]
        m = seg >= level if above else seg <= level
        if m.any():
            return s + int(np.argmax(m))
        s += chunk
    return n
