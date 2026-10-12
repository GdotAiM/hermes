"""MMXM rule engine + bar-by-bar backtester.

Design
------
* The long model is implemented once. The short model runs the SAME code on a mirrored price
  series (open/close negated, high<->low swapped and negated), so the sell side is an exact mirror.
* The loop walks 1m bars. At step t the wall clock is end[t] (= close of 1m bar t). At each step:
    1. the pending order / open position is marked against bar t (orders were placed at <= t-1),
    2. every 5m bar with end <= end[t] is fed to each side's 5m state machine,
    3. each side's 1m MSS logic runs on bar t and may place an order (active from t+1).
* Swings are usable only from their confirmation bar (pivot + 2) on; 5m/1H bars only once closed.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

from .config import Config
from .data import resample
from .indicators import atr, swings, fvgs, first_cross, Swings

NS_MIN = 60_000_000_000


def _hm(s: str) -> int:
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def mirror(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["open"] = -df["open"]
    out["close"] = -df["close"]
    out["high"] = -df["low"]
    out["low"] = -df["high"]
    return out


class Prepared:
    """All precomputed, lookahead-tagged structures for one (possibly mirrored) series."""

    def __init__(self, m1: pd.DataFrame, cfg: Config, root: str):
        self.cfg = cfg
        k = cfg.swing_strength
        self.o = m1["open"].to_numpy(float)
        self.h = m1["high"].to_numpy(float)
        self.l = m1["low"].to_numpy(float)
        self.c = m1["close"].to_numpy(float)
        self.start = pd.DatetimeIndex(m1.index).tz_convert("UTC").as_unit("ns").asi8
        self.end = self.start + NS_MIN
        self.n = len(self.c)

        def dist(hh, ll, cc):
            if cfg.swing_filter_mode == "atr":
                return cfg.min_swing_dist_atr_mult * atr(hh, ll, cc, cfg.atr_period, cfg.atr_method)
            return cfg.min_dist(root)

        # ---- 1m
        self.sh1, self.sl1 = swings(self.h, self.l, k, dist(self.h, self.l, self.c))
        self.fvg1 = fvgs(self.h, self.l)
        bm = self.fvg1.bullish
        self.bf_idx, self.bf_top, self.bf_bot = self.fvg1.idx[bm], self.fvg1.top[bm], self.fvg1.bottom[bm]

        # ---- 5m
        m5 = resample(m1, cfg.tf_model)
        self.m5 = m5
        self.h5, self.l5, self.c5 = (m5[c].to_numpy(float) for c in ("high", "low", "close"))
        self.s5 = pd.DatetimeIndex(m5.index).tz_convert("UTC").as_unit("ns").asi8
        self.e5 = pd.DatetimeIndex(m5["end"]).tz_convert("UTC").as_unit("ns").asi8
        self.atr5 = atr(self.h5, self.l5, self.c5, cfg.atr_period, cfg.atr_method)
        self.o5 = m5["open"].to_numpy(float)
        _f5 = fvgs(self.h5, self.l5)
        self.fvg5b = (_f5.idx[_f5.bullish], _f5.top[_f5.bullish], _f5.bottom[_f5.bullish])   # (bar3 idx, top, bottom)
        self.sh5, self.sl5 = swings(self.h5, self.l5, k, dist(self.h5, self.l5, self.c5))
        # m1 index of first 1m bar starting at/after a 5m bar's start / end
        self.s5_m1 = np.searchsorted(self.start, self.s5, "left")
        self.e5_m1 = np.searchsorted(self.start, self.e5, "left")      # first 1m bar after the 5m bar
        # step at which 5m bar j is fed: the last 1m bar with end <= e5 -> index e5_m1-1
        self.feed5 = self.e5_m1 - 1
        # 5m swing-high touch (in m1 index) for TP1 selection
        self.sh5_known_ns = self.e5[self.sh5.confirm] if len(self.sh5) else np.array([], dtype=np.int64)
        self.sh5_touch = np.array([first_cross(self.h, self.e5_m1[p], v, True) for p, v in zip(self.sh5.pivot, self.sh5.price)], dtype=int)

        if cfg.cons_mode == "session":
            self._session_ranges(m1)
        # ---- 1H
        h1 = resample(m1, cfg.tf_bias)
        self.hh, self.hl, self.hc = (h1[c].to_numpy(float) for c in ("high", "low", "close"))
        self.he = pd.DatetimeIndex(h1["end"]).tz_convert("UTC").as_unit("ns").asi8
        self.he_m1 = np.searchsorted(self.start, self.he, "left")
        self.atr1 = atr(self.hh, self.hl, self.hc, cfg.atr_period, cfg.atr_method)
        self.shH, self.slH = swings(self.hh, self.hl, k, None)  # no distance filter on 1H
        self.shH_touch = np.array([first_cross(self.h, self.he_m1[p], v, True) for p, v in zip(self.shH.pivot, self.shH.price)], dtype=int)
        f = fvgs(self.hh, self.hl)
        self.fH = f
        full = cfg.fvg_filled_mode == "full"
        fill = []
        for i, t, b, bull in zip(f.idx, f.top, f.bottom, f.bullish):
            s = self.he_m1[i]
            if bull:
                fill.append(first_cross(self.l, s, b if full else t, False))
            else:
                fill.append(first_cross(self.h, s, t if full else b, True))
        self.fH_fill = np.array(fill, dtype=int)

    def _session_ranges(self, m1):
        cfg = self.cfg
        a, b = (_hm(x) for x in cfg.session_range_times[cfg.session_range])
        ny = pd.DatetimeIndex(m1.index).tz_convert(cfg.timezone)
        mod = (ny.hour * 60 + ny.minute).to_numpy()
        d = ny.tz_localize(None).normalize().to_numpy().astype("datetime64[D]").astype(np.int64)
        key = np.full(len(mod), -1, dtype=np.int64)
        if b <= a:                       # wraps midnight: [a, 24:00) belongs to the next day, [00:00, b) to the same day
            m = mod >= a
            key[m] = d[m] + 1
            m = mod < b
            key[m] = d[m]
        else:
            m = (mod >= a) & (mod < b)
            key[m] = d[m] + (1 if a >= 12 * 60 else 0)
        ok = key >= 0
        g = pd.DataFrame({"k": key[ok], "h": self.h[ok], "l": self.l[ok], "i": np.nonzero(ok)[0]}).groupby("k")
        rng = pd.DataFrame({"hi": g["h"].max(), "lo": g["l"].min(), "i0": g["i"].min(), "i1": g["i"].max(), "n": g["h"].size()})
        rng = rng[rng["n"] >= cfg.session_min_bars]
        ny5 = pd.DatetimeIndex(self.m5.index).tz_convert(cfg.timezone)
        self.mod5 = (ny5.hour * 60 + ny5.minute).to_numpy()
        self.day5 = ny5.tz_localize(None).normalize().to_numpy().astype("datetime64[D]").astype(np.int64)
        n5 = len(self.s5)
        self.sr_hi = np.full(n5, np.nan); self.sr_lo = np.full(n5, np.nan)
        self.sr_s5 = np.full(n5, -1); self.sr_e5 = np.full(n5, -1)
        pos = rng.reindex(self.day5)
        have = pos["hi"].notna().to_numpy()
        if have.any():
            i0 = pos["i0"].to_numpy()[have].astype(int); i1 = pos["i1"].to_numpy()[have].astype(int)
            end_ns = self.end[i1]
            valid = end_ns <= self.s5[have]            # range must be complete before the 5m bar starts
            idx = np.nonzero(have)[0][valid]
            self.sr_hi[idx] = pos["hi"].to_numpy()[have][valid]
            self.sr_lo[idx] = pos["lo"].to_numpy()[have][valid]
            self.sr_s5[idx] = np.searchsorted(self.s5, self.start[i0[valid]], "right") - 1
            self.sr_e5[idx] = np.searchsorted(self.s5, end_ns[valid], "left")

    # ------------------------------------------------------------------ 1H context
    def h1_last(self, now_ns: int) -> int:
        return int(np.searchsorted(self.he, now_ns, "right")) - 1

    def dealing_mid(self, J: int) -> Optional[float]:
        if J < 0:
            return None
        ih = np.searchsorted(self.shH.confirm, J, "right") - 1
        il = np.searchsorted(self.slH.confirm, J, "right") - 1
        if ih < 0 or il < 0:
            return None
        return 0.5 * (self.shH.price[ih] + self.slH.price[il])

    def draw_above(self, J: int, t: int, price: float):
        """Nearest unfilled 1H FVG / untouched 1H swing high above `price`, within
        draw_max_atr_mult x ATR14(1H). Returns (level, kind) or (None, reason)."""
        cfg = self.cfg
        if J < 0 or np.isnan(self.atr1[J]):
            return None, "no_1h_atr"
        lim = cfg.draw_max_atr_mult * self.atr1[J]
        lo_bar = J - cfg.h1_lookback_bars
        best, kind = None, None
        if cfg.draw_use_swings and len(self.shH):
            m = (self.shH.confirm <= J) & (self.shH.pivot >= lo_bar) & (self.shH.price > price) & (self.shH_touch > t)
            if m.any():
                v = self.shH.price[m].min()
                best, kind = v, "1h_swing_high"
        if cfg.draw_use_fvg and len(self.fH):
            f = self.fH
            m = (f.idx <= J) & (f.idx >= lo_bar) & (f.bottom > price) & (self.fH_fill > t)
            if m.any():
                lv = {"proximal": f.bottom, "ce": 0.5 * (f.top + f.bottom), "distal": f.top}[cfg.draw_fvg_level][m]
                v = lv.min()
                if best is None or v < best:
                    best, kind = v, "1h_fvg"
        if best is None:
            return None, "no_draw"
        if best - price > lim:
            return None, "draw_too_far"
        return float(best), kind

    def discount_fvgs(self, J: int, t: int, mid: float):
        """Bullish unfilled 1H FVGs entirely below the dealing-range midpoint."""
        f = self.fH
        m = f.bullish & (f.idx <= J) & (f.idx >= J - self.cfg.h1_lookback_bars) & (self.fH_fill > t) & (f.top < mid)
        return f.top[m], f.bottom[m]


@dataclass
class SideState:
    phase: str = "search"      # search | curve | reclaim
    cons: Optional[dict] = None
    bo: int = -1
    sweep: Optional[dict] = None
    cand: Optional[dict] = None   # MSS candidate after a reclaimed sweep


class Side:
    def __init__(self, name: str, P: Prepared, cfg: Config, root: str, log: list):
        self.name, self.P, self.cfg, self.root = name, P, cfg, root
        self.st = SideState()
        self.tick = cfg.tick(root)
        self.log = log  # rejected setups (diagnostics)
        self.funnel = dict(consolidations=0, breakouts=0, curve_valid_bars=0, sweeps=0, reclaims=0, orders=0)
        self.cur_day, self.dead, self.ran_counted = None, False, False
        self.sgn = 1 if name == "long" else -1
        self.bias_arr = None   # v3: per-1m-bar HTF bias (+1/-1/0) in ORIGINAL price space
        self.bias_lvl = None

    def reset(self):
        self.st = SideState()

    # ------------------------------------------------------------------ 5m state machine
    def on_5m(self, j: int):
        if self.cfg.cons_mode == "session":
            return self.on_5m_session(j)
        P, cfg, st = self.P, self.cfg, self.st
        N = cfg.cons_min_bars
        if st.phase == "search":
            pre = cfg.cons_atr_ref == "pre"
            a = P.atr5[j - N] if pre and j - N >= 0 else (np.nan if pre else P.atr5[j])
            if j >= N - 1 and not np.isnan(a):
                hi = P.h5[j - N + 1:j + 1].max()
                lo = P.l5[j - N + 1:j + 1].min()
                if hi - lo <= cfg.cons_max_range_atr_mult * a:
                    c = st.cons
                    if c is not None and j - N + 1 <= c["end"] + 1:
                        uh, ul = max(hi, c["hi"]), min(lo, c["lo"])
                        au = P.atr5[c["start"] - 1] if pre and c["start"] >= 1 else a
                        if uh - ul <= cfg.cons_max_range_atr_mult * au:
                            st.cons = dict(start=c["start"], end=j, hi=uh, lo=ul)
                            return
                    st.cons = dict(start=j - N + 1, end=j, hi=hi, lo=lo)
                    self.funnel["consolidations"] += 1
                    return
            c = st.cons
            if c is not None:
                if j - c["end"] > cfg.cons_breakout_max_bars:
                    st.cons = None
                elif P.c5[j] < c["lo"]:
                    st.phase, st.bo = "curve", j
                    self.funnel["breakouts"] += 1
            return
        c = st.cons
        if P.c5[j] > c["hi"] or j - st.bo > cfg.curve_max_bars:
            self.reset()
            return
        if st.phase == "reclaim":
            sw = st.sweep
            sw["low"] = min(sw["low"], P.l5[j])
            if P.c5[j] > sw["level"]:
                self._reclaimed(j)
                st.phase = "curve"
            elif j >= sw["j"] + cfg.sweep_reclaim_bars - 1:
                st.phase, st.sweep = "curve", None
            return
        # phase == curve: count descending swing lows after the consolidation
        sl = P.sl5
        a_ = int(np.searchsorted(sl.pivot, c["end"], "right"))
        b_ = int(np.searchsorted(sl.confirm, j - 1, "right"))
        prices = sl.price[a_:b_]
        cnt, last = 0, np.inf
        for p in prices:
            if p < last:
                cnt += 1
                last = p
        if cnt < cfg.curve_min_swings:
            return
        self.funnel["curve_valid_bars"] += 1
        level, typ = None, None
        if cfg.sweep_use_swing:
            kk = int(np.searchsorted(sl.confirm, j - 1, "right")) - 1
            if kk >= 0:
                piv, lv = sl.pivot[kk], sl.price[kk]
                untouched = piv + 1 >= j or P.l5[piv + 1:j].min() > lv
                if untouched and P.l5[j] < lv:
                    level, typ = lv, "5m_swing_low"
        if level is None and cfg.sweep_use_h1_fvg and j >= 1:
            t0 = P.s5_m1[j] - 1
            J = P.h1_last(P.s5[j])
            mid = P.dealing_mid(J)
            if mid is not None and t0 >= 0:
                tops, bots = P.discount_fvgs(J, t0, mid)
                ok = (P.l5[j] <= tops) & (P.c5[j - 1] > tops)
                if ok.any():
                    level, typ = float(tops[ok].max()), "1h_discount_fvg"
        if level is None:
            return
        st.sweep = dict(level=level, type=typ, j=j, low=P.l5[j])
        self.funnel["sweeps"] += 1
        if P.c5[j] > level:
            self._reclaimed(j)
        else:
            st.phase = "reclaim"

    def on_5m_session(self, j: int):
        """v2: the session range is the consolidation; sweeps only inside the model window."""
        P, cfg = self.P, self.cfg
        if P.day5[j] != self.cur_day:
            self.reset()
            self.cur_day, self.dead, self.ran_counted = P.day5[j], False, False
            self._day_counted = False
        if not (_hm(cfg.session_model_start) <= P.mod5[j] < _hm(cfg.entry_end)) or np.isnan(P.sr_lo[j]) or self.dead:
            return
        st = self.st
        hi, lo, e = P.sr_hi[j], P.sr_lo[j], int(P.sr_e5[j])
        if not self._day_counted:
            self.funnel["consolidations"] += 1
            self._day_counted = True
        st.cons = dict(start=int(P.sr_s5[j]), end=e - 1, hi=hi, lo=lo)
        if st.bo < 0:
            st.bo = j
        if cfg.session_invalidate_on_opposite_close and P.c5[j] > hi:
            self.reset(); self.dead = True
            return
        if st.phase == "reclaim":
            sw = st.sweep
            sw["low"] = min(sw["low"], P.l5[j])
            if P.c5[j] > sw["level"]:
                self._reclaimed(j)
                st.phase = "curve"
            elif j >= sw["j"] + cfg.sweep_reclaim_bars - 1:
                st.phase, st.sweep = "curve", None
            return
        prior_min = P.l5[e:j].min() if j > e else np.inf
        ran = prior_min < lo or P.l5[j] < lo
        if ran and not self.ran_counted:
            self.funnel["breakouts"] += 1
            self.ran_counted = True
        sl = P.sl5
        a_ = int(np.searchsorted(sl.pivot, e - 1, "right"))
        b_ = int(np.searchsorted(sl.confirm, j - 1, "right"))
        cnt, last = 0, np.inf
        for p in sl.price[a_:b_]:
            if p < last:
                cnt += 1
                last = p
        curve_ok = cnt >= cfg.curve_min_swings or (cfg.session_curve_by_range_run and ran)
        level, typ = None, None
        if cfg.session_sweep_range_extreme and prior_min > lo and P.l5[j] < lo:
            level, typ = lo, "session_range_low"
        if level is None and not curve_ok:
            return
        if curve_ok:
            self.funnel["curve_valid_bars"] += 1
        if level is None and cfg.sweep_use_swing:
            kk = int(np.searchsorted(sl.confirm, j - 1, "right")) - 1
            if kk >= 0:
                piv, lv = sl.pivot[kk], sl.price[kk]
                untouched = piv + 1 >= j or P.l5[piv + 1:j].min() > lv
                if untouched and P.l5[j] < lv:
                    level, typ = lv, "5m_swing_low"
        if level is None and cfg.sweep_use_h1_fvg:
            t0 = P.s5_m1[j] - 1
            J = P.h1_last(P.s5[j])
            mid = P.dealing_mid(J)
            if mid is not None and t0 >= 0:
                tops, bots = P.discount_fvgs(J, t0, mid)
                ok = (P.l5[j] <= tops) & (P.c5[j - 1] > tops)
                if ok.any():
                    level, typ = float(tops[ok].max()), "1h_discount_fvg"
        if level is None:
            return
        st.sweep = dict(level=level, type=typ, j=j, low=P.l5[j])
        self.funnel["sweeps"] += 1
        if P.c5[j] > level:
            self._reclaimed(j)
        else:
            st.phase = "reclaim"

    def _reclaimed(self, j: int):
        P, st = self.P, self.st
        sw = st.sweep
        self.funnel["reclaims"] += 1
        a, b = P.s5_m1[sw["j"]], P.e5_m1[j]
        seg = P.l[a:b]
        si = a + int(np.argmin(seg))
        st.cand = dict(cons=dict(st.cons), bo=st.bo, sweep=dict(sw), reclaim_j=j, sweep_idx=si,
                       sweep_low=float(P.l[si]), reclaim_t=P.feed5[j], lh=None, mss=None, scanned=si)
        st.sweep = None

    # ------------------------------------------------------------------ 1m logic
    def on_1m(self, t: int, can_place: bool) -> Optional[dict]:
        P, cfg, st = self.P, self.cfg, self.st
        cd = st.cand
        if cd is None or t < cd["reclaim_t"]:
            return None
        if cfg.entry_model != "1m_fvg":
            return self._on_1m_v5(t, can_place)
        si = cd["sweep_idx"]
        if cd["lh"] is None:
            sh = P.sh1
            kk = int(np.searchsorted(sh.pivot, min(si, t - cfg.swing_strength + 1), "left")) - 1
            if kk < 0:
                return self._drop("no_1m_swing_high")
            if cfg.mss_require_lower_high and (kk == 0 or sh.price[kk - 1] <= sh.price[kk]):
                return self._drop("last_1m_high_not_lower_high")
            cd["lh"], cd["lh_idx"] = float(sh.price[kk]), int(sh.pivot[kk])
        # scan newly closed bars
        for b in range(cd["scanned"] + 1, t + 1):
            if P.l[b] < cd["sweep_low"]:
                return self._drop("new_low_before_entry")
            if cd["mss"] is None and P.c[b] > cd["lh"]:
                cd["mss"] = b
        cd["scanned"] = t
        if cd["mss"] is None:
            if t - si > cfg.mss_timeout_bars:
                return self._drop("mss_timeout")
            return None
        ms = cd["mss"]
        if t < ms + cfg.fvg_after_mss_bars and t < P.n - 1:
            return None
        # pick the 1m bullish FVG of the displacement leg
        f_lo, f_hi = si + 2, ms + cfg.fvg_after_mss_bars
        m = (P.bf_idx >= f_lo) & (P.bf_idx <= min(f_hi, t)) & (P.bf_bot > cd["sweep_low"])
        ks = np.nonzero(m)[0]
        chosen = None
        for kk in ks[::-1]:
            i3, top = P.bf_idx[kk], P.bf_top[kk]
            if i3 < t and P.l[i3 + 1:t + 1].min() <= top - cfg.fill_through_ticks * self.tick:
                continue  # already traded through before we could have placed the order
            chosen = kk
            break
        if chosen is None:
            return self._drop("no_1m_fvg")
        entry = float(P.bf_top[chosen])
        stop = cd["sweep_low"] - cfg.stop_offset_ticks * self.tick
        zone = dict(lh=cd["lh"], lh_idx=cd["lh_idx"], mss=ms, fvg_idx=int(P.bf_idx[chosen]),
                    fvg_top=float(P.bf_top[chosen]), fvg_bot=float(P.bf_bot[chosen]), entry_zone="1m_fvg")
        return self._finalize(t, can_place, cd, entry, stop, zone)

    def _finalize(self, t: int, can_place: bool, cd: dict, entry: float, stop: float, zone: dict,
                  cancel_bars: Optional[int] = None):
        """Common order checks (window, price, bias, discount, draw) and target construction."""
        P, cfg = self.P, self.cfg
        si = cd["sweep_idx"]
        if not can_place:
            return self._drop("blocked_or_outside_window", keep_state=True)
        if P.c[t] <= entry:
            return self._drop("price_not_above_entry")
        risk = entry - stop
        if risk <= 0:
            return self._drop("nonpositive_risk")
        htf_lvl = None
        if self.bias_arr is not None:
            b = self.bias_arr[t]
            if b == 0:
                return self._drop("htf_no_bias")
            if b != self.sgn:
                return self._drop("htf_bias_mismatch")
            htf_lvl = self.bias_lvl[t]
        now = int(P.end[t])
        J = P.h1_last(now)
        mid = P.dealing_mid(J)
        if cfg.require_discount:
            if mid is None:
                return self._drop("no_1h_dealing_range")
            if not entry < mid:
                return self._drop("not_in_discount")
        draw, dkind = P.draw_above(J, t, entry)
        if draw is None:
            return self._drop(dkind)
        tp1 = entry + cfg.tp1_r * risk
        tp1_src = f"{cfg.tp1_r:g}R"
        if cfg.tp1_use_5m_swing and len(P.sh5):
            s = P.sh5
            mm = (P.sh5_known_ns <= now) & (s.price > entry) & (P.sh5_touch > t)
            if mm.any():
                v = float(s.price[mm].min())
                if v < tp1:
                    tp1, tp1_src = v, "5m_swing_high"
        final_at_tp1 = draw <= tp1
        if final_at_tp1:
            tp1, tp1_src = draw, "1h_draw(<=tp1)"
        order = dict(side=self.name, placed=t, entry=entry, stop=stop, risk=risk, tp1=tp1, tp1_src=tp1_src,
                     draw=draw, draw_kind=dkind, final_at_tp1=final_at_tp1, mid=mid,
                     cons_start=cd["cons"]["start"], cons_end=cd["cons"]["end"], cons_hi=cd["cons"]["hi"],
                     cons_lo=cd["cons"]["lo"], breakout=cd["bo"], sweep_j=cd["sweep"]["j"], reclaim_j=cd["reclaim_j"],
                     sweep_level=cd["sweep"]["level"], sweep_type=cd["sweep"]["type"], sweep_idx=si,
                     sweep_low=cd["sweep_low"], htf_bias=cfg.htf_bias, htf_level=htf_lvl, **zone)
        if cancel_bars is not None:
            order["cancel_bars"] = int(cancel_bars)
        self.reset()
        self.funnel["orders"] += 1
        return order

    # ------------------------------------------------------------------ v5 entry models
    def _k5_closed(self, t: int) -> int:
        return int(np.searchsorted(self.P.feed5, t, "right")) - 1

    def _ob(self, cd):
        """Last down-close 5m candle at/before the 5m bar containing the sweep extreme (within ob_lookback_bars)."""
        P, cfg = self.P, self.cfg
        je = cd["j_ext"]
        for k in range(je, max(-1, je - cfg.ob_lookback_bars - 1), -1):
            if P.c5[k] < P.o5[k]:
                return k
        return None

    def _first_fvg5(self, cd, k_max: int):
        """First bullish 5m FVG whose first candle is at/after the sweep-extreme bar, bottom above the sweep low,
        third candle closed (index <= k_max)."""
        P = self.P
        f = P.fvg5b
        m = (f[0] - 2 >= cd["j_ext"]) & (f[0] <= k_max) & (f[2] > cd["sweep_low"])
        ks = np.nonzero(m)[0]
        return None if not len(ks) else int(ks[0])

    def _zone_entry(self, top, bot):
        return float(top) if self.cfg.entry_level == "proximal" else 0.5 * (float(top) + float(bot))

    def _on_1m_v5(self, t: int, can_place: bool):
        P, cfg, st = self.P, self.cfg, self.st
        cd = st.cand
        si = cd["sweep_idx"]
        tick = self.tick
        if "j_ext" not in cd:
            cd["j_ext"] = int(np.searchsorted(P.s5, P.start[si], "right")) - 1
            cd["s0"] = int(P.s5_m1[cd["sweep"]["j"]])
        for b in range(cd["scanned"] + 1, t + 1):
            if P.l[b] < cd["sweep_low"]:
                return self._drop("new_low_before_entry")
        cd["scanned"] = t
        stop = cd["sweep_low"] - cfg.stop_offset_ticks * tick
        K = self._k5_closed(t)
        em = cfg.entry_model
        c5bars = cfg.entry_cancel_5m_bars * 5
        if em == "5m_fvg":
            if K - cd["reclaim_j"] > cfg.fvg5_search_bars:
                return self._drop("no_5m_fvg")
            kk = self._first_fvg5(cd, K)
            if kk is None:
                return None
            i3, top, bot = (P.fvg5b[0][kk], P.fvg5b[1][kk], P.fvg5b[2][kk])
            entry = self._zone_entry(top, bot)
            zone = dict(lh=cd["sweep"]["level"], lh_idx=si, mss=int(P.feed5[cd["reclaim_j"]]), fvg_idx=int(P.feed5[i3]),
                        fvg_top=float(top), fvg_bot=float(bot), entry_zone="5m_fvg")
            return self._finalize(t, can_place, cd, entry, stop, zone, c5bars)
        if em == "5m_ob":
            ms = self._mss_v1(t, cd)
            if isinstance(ms, str):
                return self._drop(ms)
            if ms is None:
                return None
            ob = self._ob(cd)
            if ob is None:
                return self._drop("no_ob")
            top, bot = P.o5[ob], P.c5[ob]
            entry = float(top) if cfg.entry_level == "proximal" else 0.5 * (float(top) + float(bot))
            if cfg.ob_stop == "ob":
                stop = float(P.l5[ob]) - cfg.stop_offset_ticks * tick
            zone = dict(lh=cd["lh"], lh_idx=cd["lh_idx"], mss=ms, fvg_idx=int(P.feed5[ob]), fvg_top=float(top),
                        fvg_bot=float(P.l5[ob]), entry_zone="5m_ob")
            return self._finalize(t, can_place, cd, entry, stop, zone, c5bars)
        if em == "1m_fvg_loose":
            if cd.get("mss") is None:
                sh = P.sh1
                x = P.h if cfg.mss_loose_break == "wick" else P.c
                for b in range(cd.get("mss_scanned", si) + 1, t + 1):
                    m = (sh.pivot >= cd["s0"]) & (sh.confirm < b)
                    lv = [P.h[si]] + list(sh.price[m])
                    lvl = min(lv)
                    if x[b] > lvl:
                        cd["mss"], cd["lh"] = b, float(lvl)
                        cd["lh_idx"] = si if lvl == P.h[si] else int(sh.pivot[m][np.argmin(sh.price[m])])
                        break
                cd["mss_scanned"] = t
                if cd.get("mss") is None:
                    if t - si > cfg.mss_timeout_bars:
                        return self._drop("mss_timeout")
                    return None
            ms = cd["mss"]
            if t < ms + cfg.fvg_after_mss_bars and t < P.n - 1:
                return None
            m = (P.bf_idx >= si + 2) & (P.bf_idx <= min(ms + cfg.fvg_after_mss_bars, t)) & (P.bf_bot > cd["sweep_low"])
            chosen = None
            for kk in np.nonzero(m)[0][::-1]:
                i3, top = P.bf_idx[kk], P.bf_top[kk]
                if i3 < t and P.l[i3 + 1:t + 1].min() <= top - cfg.fill_through_ticks * tick:
                    continue
                chosen = kk
                break
            if chosen is None:
                return self._drop("no_1m_fvg")
            zone = dict(lh=cd["lh"], lh_idx=cd["lh_idx"], mss=ms, fvg_idx=int(P.bf_idx[chosen]),
                        fvg_top=float(P.bf_top[chosen]), fvg_bot=float(P.bf_bot[chosen]), entry_zone="1m_fvg")
            return self._finalize(t, can_place, cd, float(P.bf_top[chosen]), stop, zone)
        if em == "5m_mss":
            if cd.get("mss5") is None:
                sh = P.sh5
                kk = int(np.searchsorted(sh.pivot, cd["j_ext"], "left")) - 1
                if kk < 0:
                    return self._drop("no_5m_swing_high")
                lvl, piv, conf = float(sh.price[kk]), int(sh.pivot[kk]), int(sh.confirm[kk])
                for k in range(max(cd.get("mss5_scanned", cd["j_ext"]) + 1, conf + 1), K + 1):
                    if P.c5[k] > lvl:
                        cd["mss5"] = k
                        break
                cd["mss5_scanned"] = K
                cd["lh"], cd["lh_idx"] = lvl, int(P.s5_m1[piv])
                if cd.get("mss5") is None:
                    if K - cd["reclaim_j"] > cfg.mss5_timeout_bars:
                        return self._drop("mss5_timeout")
                    return None
            k = cd["mss5"]
            ms = int(P.feed5[k])
            if cfg.mss5_entry_zone == "fvg":
                if K < k + 1 and t < P.n - 1:
                    return None                       # allow the FVG to complete one 5m bar after the break
                kk = self._first_fvg5(cd, min(K, k + 1))
                if kk is None:
                    return self._drop("no_5m_fvg")
                i3, top, bot = (P.fvg5b[0][kk], P.fvg5b[1][kk], P.fvg5b[2][kk])
                if P.feed5[i3] < t and P.l[P.feed5[i3] + 1:t + 1].min() <= top - cfg.fill_through_ticks * tick:
                    return self._drop("fvg_already_traded")
                zone = dict(lh=cd["lh"], lh_idx=cd["lh_idx"], mss=ms, fvg_idx=int(P.feed5[i3]), fvg_top=float(top),
                            fvg_bot=float(bot), entry_zone="5m_fvg")
                return self._finalize(t, can_place, cd, float(top), stop, zone, c5bars)
            ob = self._ob(cd)
            if ob is None:
                return self._drop("no_ob")
            zone = dict(lh=cd["lh"], lh_idx=cd["lh_idx"], mss=ms, fvg_idx=int(P.feed5[ob]), fvg_top=float(P.o5[ob]),
                        fvg_bot=float(P.l5[ob]), entry_zone="5m_ob")
            return self._finalize(t, can_place, cd, float(P.o5[ob]), stop, zone, c5bars)
        raise ValueError(f"unknown entry_model {em}")

    def _mss_v1(self, t: int, cd: dict):
        """v1 1m MSS (last lower high, per mss_require_lower_high). Returns MSS bar index, None (pending) or a drop reason."""
        P, cfg = self.P, self.cfg
        si = cd["sweep_idx"]
        if cd.get("lh") is None:
            sh = P.sh1
            kk = int(np.searchsorted(sh.pivot, min(si, t - cfg.swing_strength + 1), "left")) - 1
            if kk < 0:
                return "no_1m_swing_high"
            if cfg.mss_require_lower_high and (kk == 0 or sh.price[kk - 1] <= sh.price[kk]):
                return "last_1m_high_not_lower_high"
            cd["lh"], cd["lh_idx"] = float(sh.price[kk]), int(sh.pivot[kk])
        if cd.get("mss") is None:
            for b in range(cd.get("mss_scanned", si) + 1, t + 1):
                if P.c[b] > cd["lh"]:
                    cd["mss"] = b
                    break
            cd["mss_scanned"] = t
            if cd.get("mss") is None:
                return "mss_timeout" if t - si > cfg.mss_timeout_bars else None
        return cd["mss"]

    def _drop(self, reason: str, keep_state: bool = False):
        cd = self.st.cand
        self.log.append(dict(side=self.name, t=cd.get("scanned"), sweep_idx=cd["sweep_idx"], reason=reason))
        self.st.cand = None
        return None


def run_backtest(m1: pd.DataFrame, cfg: Config, root: str, symbol: str = None):
    """Returns (trades DataFrame, orders DataFrame incl. cancelled, rejections DataFrame)."""
    symbol = symbol or root
    rejections: list = []
    sides = []
    if "long" in cfg.directions:
        sides.append(Side("long", Prepared(m1, cfg, root), cfg, root, rejections))
    if "short" in cfg.directions:
        sides.append(Side("short", Prepared(mirror(m1), cfg, root), cfg, root, rejections))
    P0 = sides[0].P
    n = P0.n
    idx_ny = pd.DatetimeIndex(m1.index).tz_convert(cfg.timezone)
    bias_tab = None
    if cfg.htf_bias != "none":
        from .htf import bias_table
        bias_tab = bias_table(m1, cfg)
        dts = pd.Series(idx_ny.date)
        barr = dts.map(bias_tab[cfg.htf_bias].to_dict()).fillna(0).astype(int).to_numpy()
        lcol = next((cfg.htf_bias + sfx for sfx in ("_lvl", "_mid") if cfg.htf_bias + sfx in bias_tab), None)
        larr = dts.map(bias_tab[lcol].to_dict()).to_numpy(dtype=float) if lcol else np.full(n, np.nan)
        if cfg.htf_bias in ("midnight_open", "midnight_daily_draw"):
            # v4: evaluated at order placement: price (1m close of the placement bar) vs the 00:00 NY open
            mo = dts.map(bias_tab["midnight_open_lvl"].to_dict()).to_numpy(dtype=float)
            px_ = m1["close"].to_numpy(float)
            mb = np.where(np.isnan(mo), 0, np.sign(mo - px_)).astype(int)
            if cfg.htf_bias == "midnight_daily_draw":
                dd = dts.map(bias_tab["daily_draw"].to_dict()).fillna(0).astype(int).to_numpy()
                mb = np.where(mb == dd, mb, 0)
                larr = dts.map(bias_tab["daily_draw_lvl"].to_dict()).to_numpy(dtype=float)
            else:
                larr = mo
            barr = mb
        for S in sides:
            S.bias_arr, S.bias_lvl = barr, larr
    mod = (idx_ny.hour * 60 + idx_ny.minute).to_numpy()
    day = idx_ny.normalize().asi8
    es, ee, ft = _hm(cfg.entry_start), _hm(cfg.entry_end), _hm(cfg.flat_time)
    place_lo = es - cfg.entry_cancel_bars
    tick = cfg.tick(root)
    thru = cfg.fill_through_ticks * tick
    slip = cfg.stop_slippage_ticks * tick
    ptr5 = [0 for _ in sides]
    order = None  # pending
    pos = None    # open position
    done: List[dict] = []

    def close_pos(pos, t_exit, price, reason):
        rem = pos["remaining"]
        pos["legs"].append((t_exit, price, rem, reason))
        pos["remaining"] = 0.0
        pos["exit_t"], pos["exit_reason"] = t_exit, reason
        done.append(pos)

    for t in range(n):
        # ---------------- 1. manage order / position with bar t (in the side's mirrored space)
        if pos is not None:
            S = pos["S"]
            P = S.P
            if (mod[t] >= ft or day[t] != day[pos["fill_t"]]) and t > pos["fill_t"]:
                close_pos(pos, t - 1, P.c[t - 1], "session_end")
                pos = None
            else:
                if P.l[t] <= pos["stop_cur"]:
                    close_pos(pos, t, pos["stop_cur"] - slip, "stop" if not pos["tp1_done"] else "stop_after_tp1")
                    pos = None
                elif t > pos["fill_t"]:
                    if not pos["tp1_done"] and P.h[t] >= pos["tp1"] + thru:
                        if pos["final_at_tp1"]:
                            close_pos(pos, t, pos["tp1"], "draw")
                            pos = None
                        else:
                            fr = cfg.tp1_fraction
                            pos["legs"].append((t, pos["tp1"], fr, "tp1"))
                            pos["remaining"] -= fr
                            pos["tp1_done"], pos["tp1_t"] = True, t
                            if cfg.move_stop_to_be_after_tp1:
                                pos["stop_cur"] = pos["entry"]
                    if pos is not None and pos["tp1_done"] and P.h[t] >= pos["draw"] + thru:
                        close_pos(pos, t, pos["draw"], "draw")
                        pos = None
        elif order is not None:
            S = order["S"]
            P = S.P
            in_win = es <= mod[t] < ee and day[t] == day[order["placed"]]
            if mod[t] >= ee or day[t] != day[order["placed"]]:
                order.update(status="cancelled_time", end_t=t)
                done.append(order); order = None
            elif in_win and P.l[t] <= order["entry"] - thru:
                pos = order
                pos.update(status="filled", fill_t=t, remaining=1.0, legs=[], tp1_done=False,
                           stop_cur=order["stop"], tp1_t=None)
                order = None
                if P.l[t] <= pos["stop_cur"]:
                    close_pos(pos, t, pos["stop_cur"] - slip, "stop_on_fill_bar")
                    pos = None
            elif t - order["placed"] >= order.get("cancel_bars", cfg.entry_cancel_bars):
                order.update(status="cancelled_unfilled", end_t=t)
                done.append(order); order = None
        # ---------------- 2. feed closed 5m bars
        for si_, S in enumerate(sides):
            P = S.P
            while ptr5[si_] < len(P.feed5) and P.feed5[ptr5[si_]] <= t:
                S.on_5m(ptr5[si_])
                ptr5[si_] += 1
        # ---------------- 3. 1m logic / order placement
        can_place = (order is None and pos is None) or not cfg.one_position_at_a_time
        can_place = can_place and place_lo <= (mod[t] + 1) < ee
        for S in sides:
            o = S.on_1m(t, can_place and order is None and pos is None)
            if o is not None:
                o["S"] = S
                o["status"] = "pending"
                order = o
                can_place = False
    if pos is not None:
        close_pos(pos, n - 1, pos["S"].P.c[n - 1], "end_of_data")
    if order is not None:
        order.update(status="cancelled_end_of_data", end_t=n - 1)
        done.append(order)
    tr, od, rj = _to_frames(done, rejections, m1, cfg, root, symbol)
    od.attrs["funnel"] = {S.name: dict(S.funnel) for S in sides}
    od.attrs["bias_table"] = bias_tab
    return tr, od, rj


def _to_frames(done, rejections, m1, cfg, root, symbol):
    idx = pd.DatetimeIndex(m1.index)
    ny = idx.tz_convert("America/New_York")
    jnb = idx.tz_convert("Africa/Johannesburg")
    buckets = [_hm(b) for b in cfg.session_buckets]
    rows = []
    for d in done:
        S = d["S"]
        sgn = 1.0 if S.name == "long" else -1.0
        P = S.P
        m5i = P.m5.index

        def px(v):
            return None if v is None else sgn * v

        def t5(j):
            return pd.Timestamp(m5i[j]).tz_convert("America/New_York")

        def lab(x):
            if sgn > 0 or x is None:
                return x
            return x.replace("high", "LOW").replace("low", "high").replace("LOW", "low").replace("discount", "premium")

        r = dict(symbol=symbol, direction=S.name, status=d["status"],
                 order_time_ny=ny[d["placed"]] + pd.Timedelta(minutes=1),   # placed at the close of bar `placed`
                 order_time_jnb=jnb[d["placed"]] + pd.Timedelta(minutes=1),
                 entry=px(d["entry"]), stop=px(d["stop"]), risk_pts=d["risk"], tp1=px(d["tp1"]), tp1_source=lab(d["tp1_src"]),
                 draw=px(d["draw"]), draw_kind=lab(d["draw_kind"]), h1_mid=px(d["mid"]),
                 cons_start_ny=t5(d["cons_start"]), cons_end_ny=t5(d["cons_end"]) + pd.Timedelta(minutes=5),
                 cons_high=px(d["cons_lo"] if sgn < 0 else d["cons_hi"]), cons_low=px(d["cons_hi"] if sgn < 0 else d["cons_lo"]),
                 breakout_ny=t5(d["breakout"]), sweep_bar_ny=t5(d["sweep_j"]), reclaim_bar_ny=t5(d["reclaim_j"]),
                 sweep_type=lab(d["sweep_type"]), sweep_level=px(d["sweep_level"]), sweep_extreme=px(d["sweep_low"]),
                 sweep_extreme_ny=ny[d["sweep_idx"]], mss_level=px(d["lh"]), mss_level_pivot_ny=ny[d["lh_idx"]],
                 mss_bar_ny=ny[d["mss"]], fvg_bar3_ny=ny[d["fvg_idx"]],
                 fvg_top=px(d["fvg_bot"] if sgn < 0 else d["fvg_top"]), fvg_bottom=px(d["fvg_top"] if sgn < 0 else d["fvg_bot"]),
                 htf_bias=d.get("htf_bias"), htf_level=d.get("htf_level"),
                 entry_model=cfg.entry_model, entry_zone=d.get("entry_zone", "1m_fvg"),
                 _placed=d["placed"], _sweep_idx=d["sweep_idx"], _mss=d["mss"], _fvg=d["fvg_idx"], _lh=d["lh_idx"])
        if d["status"] == "filled":
            ft_ = d["fill_t"]
            cost = cfg.cost_points_round_trip
            cost = float(cost.get(root, 0.0)) if isinstance(cost, dict) else float(cost)
            pnl = sum(fr * (p - d["entry"]) for _, p, fr, _ in d["legs"]) - cost
            R = pnl / d["risk"]
            m = ny[ft_].hour * 60 + ny[ft_].minute
            bk = next((f"{cfg.session_buckets[i]}-{cfg.session_buckets[i+1]}" for i in range(len(buckets) - 1)
                       if buckets[i] <= m < buckets[i + 1]), "other")
            tp1_leg = [x for x in d["legs"] if x[3] == "tp1"]
            r.update(entry_time_ny=ny[ft_], entry_time_jnb=jnb[ft_],
                     exit_time_ny=ny[d["exit_t"]], exit_time_jnb=jnb[d["exit_t"]],
                     tp1_hit=bool(tp1_leg), tp1_time_ny=ny[tp1_leg[0][0]] if tp1_leg else None,
                     exit_reason=d["exit_reason"],
                     avg_exit=px(sum(fr * p for _, p, fr, _ in d["legs"])),
                     pnl_points=pnl, r_multiple=R, weekday=ny[ft_].day_name(), session_bucket=bk, date_ny=ny[ft_].date(),
                     _fill=ft_, _exit=d["exit_t"])
        rows.append(r)
    orders = pd.DataFrame(rows)
    if len(orders):
        orders = orders.sort_values("order_time_ny").reset_index(drop=True)
    trades = orders[orders["status"] == "filled"].reset_index(drop=True) if len(orders) else orders
    rej = pd.DataFrame(rejections)
    return trades, orders, rej
