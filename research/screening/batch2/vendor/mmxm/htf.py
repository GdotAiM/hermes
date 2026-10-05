"""v3 higher-timeframe (daily / weekly) bias.

Daily bars use the futures trading day: trading day D = [D-1 18:00, D 18:00) America/New_York.
Weekly bars start on the Sunday 18:00 NY open: week W = [Sun 18:00, next Sun 18:00).
A bar is usable only once closed (its `end` <= now). The bias for trading day D is decided ONCE at
`session_model_start` (09:30 NY) using closed HTF bars, and 1m prices strictly before 09:30 for
"untouched"/"unfilled" status and the reference price.
"""
from __future__ import annotations

from typing import Dict, Optional

import numpy as np
import pandas as pd

from .indicators import swings, fvgs, first_cross, atr

NY = "America/New_York"


def _hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def htf_bars(m1: pd.DataFrame, kind: str, boundary: str = "18:00") -> pd.DataFrame:
    """kind: 'D' (trading day, 18:00 boundary) or 'W' (week opening Sunday 18:00).
    Index = trading date (D) or Monday date (W) of the bar; columns open high low close, i0/i1 (1m index
    range), start, end (tz-aware close time). The still-forming last bar is dropped."""
    ny = pd.DatetimeIndex(m1.index).tz_convert(NY).tz_localize(None)
    shift = pd.Timedelta(hours=24) - pd.Timedelta(minutes=_hm(boundary))
    key = (ny + shift).normalize()
    if kind == "W":
        key = key - pd.to_timedelta(key.weekday, unit="D")
    df = pd.DataFrame({"k": key, "o": m1["open"].to_numpy(), "h": m1["high"].to_numpy(),
                       "l": m1["low"].to_numpy(), "c": m1["close"].to_numpy(), "i": np.arange(len(m1))})
    g = df.groupby("k", sort=True)
    b = pd.DataFrame({"open": g["o"].first(), "high": g["h"].max(), "low": g["l"].min(), "close": g["c"].last(),
                      "i0": g["i"].min(), "i1": g["i"].max()})
    off = pd.Timedelta(minutes=_hm(boundary))
    end_naive = b.index + (pd.Timedelta(days=6) if kind == "W" else pd.Timedelta(0)) + off
    b["end"] = pd.DatetimeIndex(end_naive).tz_localize(NY)
    last_close = m1.index[-1] + pd.Timedelta(minutes=1)
    b = b[b["end"] <= last_close]
    return b


class HTFContext:
    def __init__(self, m1: pd.DataFrame, kind: str, cfg):
        self.cfg = cfg
        self.kind = kind
        self.b = htf_bars(m1, kind, cfg.htf_day_boundary)
        self.h1m = m1["high"].to_numpy(float)
        self.l1m = m1["low"].to_numpy(float)
        self.start1m = pd.DatetimeIndex(m1.index).tz_convert("UTC").as_unit("ns").asi8
        b = self.b
        self.H, self.L = b["high"].to_numpy(float), b["low"].to_numpy(float)
        self.O, self.C = b["open"].to_numpy(float), b["close"].to_numpy(float)
        self.end_ns = pd.DatetimeIndex(b["end"]).tz_convert("UTC").as_unit("ns").asi8
        self.end_m1 = np.searchsorted(self.start1m, self.end_ns, "left")   # first 1m bar after the HTF bar closes
        k = cfg.swing_strength
        self.sh, self.sl = swings(self.H, self.L, k, None)
        self.sh_touch = np.array([first_cross(self.h1m, self.end_m1[p], v, True) for p, v in zip(self.sh.pivot, self.sh.price)], dtype=int)
        self.sl_touch = np.array([first_cross(self.l1m, self.end_m1[p], v, False) for p, v in zip(self.sl.pivot, self.sl.price)], dtype=int)
        self.f = fvgs(self.H, self.L)
        full = cfg.fvg_filled_mode == "full"
        fill = []
        for i, t, bo, bull in zip(self.f.idx, self.f.top, self.f.bottom, self.f.bullish):
            s = self.end_m1[i]
            fill.append(first_cross(self.l1m, s, bo if full else t, False) if bull
                        else first_cross(self.h1m, s, t if full else bo, True))
        self.f_fill = np.array(fill, dtype=int)
        self.lookback = cfg.htf_lookback_days if kind == "D" else cfg.htf_lookback_weeks

    def last_closed(self, now_ns: int) -> int:
        return int(np.searchsorted(self.end_ns, now_ns, "right")) - 1

    def draws(self, now_ns: int, t_now: int, ref: float):
        """Nearest draw above and below `ref` (levels or None). t_now = last 1m bar closed before now."""
        J = self.last_closed(now_ns)
        if J < 0:
            return None, None, J
        lo_bar = J - self.lookback
        ups, dns = [], []
        m = (self.sh.confirm <= J) & (self.sh.pivot >= lo_bar) & (self.sh.price > ref) & (self.sh_touch > t_now)
        ups += list(self.sh.price[m])
        m = (self.sl.confirm <= J) & (self.sl.pivot >= lo_bar) & (self.sl.price < ref) & (self.sl_touch > t_now)
        dns += list(self.sl.price[m])
        if self.cfg.htf_use_prior_bar_hl:
            s = self.end_m1[J]
            hi_since = self.h1m[s:t_now + 1].max() if t_now >= s else -np.inf
            lo_since = self.l1m[s:t_now + 1].min() if t_now >= s else np.inf
            if self.H[J] > ref and hi_since < self.H[J]:
                ups.append(self.H[J])
            if self.L[J] < ref and lo_since > self.L[J]:
                dns.append(self.L[J])
        f = self.f
        m = (f.idx <= J) & (f.idx >= lo_bar) & (self.f_fill > t_now)
        lvl_up = {"proximal": f.bottom, "ce": 0.5 * (f.top + f.bottom), "distal": f.top}[self.cfg.draw_fvg_level]
        lvl_dn = {"proximal": f.top, "ce": 0.5 * (f.top + f.bottom), "distal": f.bottom}[self.cfg.draw_fvg_level]
        ups += list(lvl_up[m & (f.bottom > ref)])
        dns += list(lvl_dn[m & (f.top < ref)])
        return (min(ups) if ups else None), (max(dns) if dns else None), J

    def dealing_mid(self, J: int) -> Optional[float]:
        ih = np.searchsorted(self.sh.confirm, J, "right") - 1
        il = np.searchsorted(self.sl.confirm, J, "right") - 1
        if J < 0 or ih < 0 or il < 0:
            return None
        return 0.5 * (self.sh.price[ih] + self.sl.price[il])


def _draw_bias(up, dn, ref, one_sided_ok):
    if up is not None and dn is not None:
        du, dd = up - ref, ref - dn
        return (1, up, dn) if du < dd else ((-1, dn, up) if dd < du else (0, None, None))
    if up is not None and one_sided_ok:
        return 1, up, None
    if dn is not None and one_sided_ok:
        return -1, dn, None
    return 0, None, None


def bias_table(m1: pd.DataFrame, cfg) -> pd.DataFrame:
    """One row per NY calendar date that has 1m data before and after `session_model_start`.
    Columns per method: bias (+1/-1/0), draw level, opposite level, plus outcomes (for hit-rate stats)."""
    ny = pd.DatetimeIndex(m1.index).tz_convert(NY)
    start_ns = pd.DatetimeIndex(m1.index).tz_convert("UTC").as_unit("ns").asi8
    c = m1["close"].to_numpy(float); h = m1["high"].to_numpy(float); l = m1["low"].to_numpy(float)
    D = HTFContext(m1, "D", cfg)
    W = HTFContext(m1, "W", cfg)
    o1 = m1["open"].to_numpy(float)
    datr = atr(D.H, D.L, D.C, cfg.atr_period, cfg.atr_method) if len(D.H) else np.array([])
    one = cfg.htf_draw_one_sided_ok
    dates = pd.Index(ny.tz_localize(None).normalize().unique())
    rows = []
    for d in dates:
        if d.weekday() >= 5:
            continue
        now = pd.Timestamp(d + pd.Timedelta(minutes=_hm(cfg.session_model_start))).tz_localize(NY)
        now_ns = now.value
        t_now = int(np.searchsorted(start_ns, now_ns - 60_000_000_000, "right")) - 1   # last bar with end <= now
        if t_now < 0 or start_ns[t_now] < now_ns - 3 * 3600 * 10**9:
            continue
        ref = c[t_now]
        day_end = pd.Timestamp(d + pd.Timedelta(minutes=_hm(cfg.htf_day_boundary))).tz_localize(NY).value
        t_end = int(np.searchsorted(start_ns, day_end, "left")) - 1
        if t_end <= t_now:
            continue
        r = dict(date=d.date(), ref=ref, day_close=c[t_end], t_now=t_now, t_end=t_end)
        du, dd, Jd = D.draws(now_ns, t_now, ref)
        wu, wd, Jw = W.draws(now_ns, t_now, ref)
        r["daily_draw"], r["daily_draw_lvl"], r["daily_draw_opp"] = _draw_bias(du, dd, ref, one)
        r["weekly_draw"], r["weekly_draw_lvl"], r["weekly_draw_opp"] = _draw_bias(wu, wd, ref, one)
        a, b = r["daily_draw"], r["weekly_draw"]
        r["daily_weekly"] = a if (a == b and a != 0) else 0
        r["daily_weekly_lvl"] = r["daily_draw_lvl"] if r["daily_weekly"] else None
        mid = D.dealing_mid(Jd)
        r["daily_pd"] = 0 if mid is None else (1 if ref < mid else (-1 if ref > mid else 0))
        r["daily_pd_mid"] = mid
        r["prev_day_candle"] = 0 if Jd < 0 else int(np.sign(D.C[Jd] - D.O[Jd]))
        _v4_columns(r, D, Jd, t_now, ref, d, start_ns, o1, cfg, datr)
        # outcomes (NOT used by the engine; for bias hit-rate statistics only)
        r["day_high_after"] = h[t_now + 1:t_end + 1].max()
        r["day_low_after"] = l[t_now + 1:t_end + 1].min()
        wk_end_ns = pd.Timestamp((d - pd.Timedelta(days=d.weekday()) + pd.Timedelta(days=4, minutes=_hm(cfg.htf_day_boundary)))).tz_localize(NY).value
        t_wend = int(np.searchsorted(start_ns, wk_end_ns, "left")) - 1
        r["week_high_after"] = h[t_now + 1:t_wend + 1].max() if t_wend > t_now else np.nan
        r["week_low_after"] = l[t_now + 1:t_wend + 1].min() if t_wend > t_now else np.nan
        rows.append(r)
    return pd.DataFrame(rows).set_index("date")


V3_METHODS = ("daily_draw", "weekly_draw", "daily_weekly", "daily_pd", "prev_day_candle")
V4_METHODS = ("midnight_open", "midnight_daily_draw", "ipda20_draw", "ipda40_draw", "ipda60_draw", "ipda20_pd",
              "ipda20_40_draw", "weekly_profile", "wp_early_extreme", "wp_tuesday", "wp_wed_reversal", "wp_thu_reversal")


def hit_rates(tab: pd.DataFrame, methods=V3_METHODS) -> Dict[str, dict]:
    """Per method: days with a bias, direction hit rate (day close vs 09:30 ref), and for draw methods
    whether the draw was reached within the day / week, vs the opposite-side draw."""
    out = {}
    up = tab["day_close"] > tab["ref"]
    dn = tab["day_close"] < tab["ref"]
    for m in methods:
        b = tab[m]
        has = b != 0
        corr = ((b == 1) & up) | ((b == -1) & dn)
        r = dict(days=int(len(tab)), days_with_bias=int(has.sum()), long_days=int((b == 1).sum()), short_days=int((b == -1).sum()),
                 direction_hit=float(corr[has].mean()) if has.any() else None)
        lv = m + "_lvl"
        if lv in tab:
            L = tab[lv].astype(float)
            reach_d = ((b == 1) & (tab["day_high_after"] >= L)) | ((b == -1) & (tab["day_low_after"] <= L))
            reach_w = ((b == 1) & (tab["week_high_after"] >= L)) | ((b == -1) & (tab["week_low_after"] <= L))
            r["draw_reached_same_day"] = float(reach_d[has].mean()) if has.any() else None
            r["draw_reached_same_week"] = float(reach_w[has].mean()) if has.any() else None
            opp = m + "_opp"
            if opp in tab:
                O = tab[opp].astype(float)
                ho = has & O.notna()
                ro = ((b == 1) & (tab["day_low_after"] <= O)) | ((b == -1) & (tab["day_high_after"] >= O))
                r["opposite_draw_reached_same_day"] = float(ro[ho].mean()) if ho.any() else None
                r["days_with_both_sides"] = int(ho.sum())
        out[m] = r
    return out


def _v4_columns(r, D, Jd, t_now, ref, d, start_ns, o1, cfg, datr):
    """v4 day-level columns (decided with data up to t_now = the 09:29 bar)."""
    from . import htf_v4 as V
    mid_ns = pd.Timestamp(d).tz_localize(NY).value
    mo = V.midnight_open(start_ns, o1, mid_ns, t_now)
    r["midnight_open_lvl"] = mo
    r["midnight_open"] = 0 if mo is None else (1 if ref < mo else (-1 if ref > mo else 0))
    r["midnight_daily_draw"] = r["midnight_open"] if (r["midnight_open"] == r["daily_draw"] and r["midnight_open"] != 0) else 0
    r["midnight_daily_draw_lvl"] = r["daily_draw_lvl"] if r["midnight_daily_draw"] else None
    for n in (20, 40, 60):
        b, lvl, opp, hi, lo = V.ipda(D, Jd, t_now, ref, n, cfg.htf_draw_one_sided_ok)
        r[f"ipda{n}_draw"], r[f"ipda{n}_draw_lvl"], r[f"ipda{n}_draw_opp"] = b, lvl, opp
        if n == 20:
            mid = None if hi is None else 0.5 * (hi + lo)
            r["ipda20_pd"] = 0 if mid is None else (1 if ref < mid else (-1 if ref > mid else 0))
            r["ipda20_pd_mid"] = mid
    a, b = r["ipda20_draw"], r["ipda40_draw"]
    r["ipda20_40_draw"] = a if (a == b and a != 0) else 0
    r["ipda20_40_draw_lvl"] = r["ipda20_draw_lvl"] if r["ipda20_40_draw"] else None
    monday = np.datetime64(pd.Timestamp(d).date(), "D") - np.timedelta64(pd.Timestamp(d).weekday(), "D")
    days = V.week_days(D, Jd, pd.Timestamp(monday), pd.Timestamp(d).weekday(), t_now, o1) if Jd >= 0 else []
    prof, c = V.weekly_profiles(D, Jd, t_now, ref, pd.Timestamp(d).weekday(), days, cfg, datr)
    r.update(prof)
    r["weekly_profile"] = c["combined"]
    r["weekly_profile_lvl"] = c["lvl"]
    for k in prof:
        r[k + "_lvl"] = None if prof[k] == 0 else (c["WH"] if prof[k] == 1 else c["WL"])
