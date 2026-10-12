"""All tunable thresholds live here (one dataclass, loadable from / dumpable to YAML)."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict, fields
from typing import Dict, List, Optional, Union

import yaml


@dataclass
class Config:
    # ---- timeframes ------------------------------------------------------
    tf_model: str = "5min"          # model timeframe (consolidation / curve / sweep)
    tf_bias: str = "1h"             # bias / draw timeframe
    # ---- swings ------------------------------------------------------------
    swing_strength: int = 2         # bars on each side; swing confirmed `swing_strength` bars after pivot
    # min distance from last opposite swing, applied on 1m and 5m only
    swing_filter_mode: str = "points"   # "points" | "atr"
    min_swing_dist_points: Dict[str, float] = field(default_factory=lambda: {"NQ": 3.0, "ES": 1.0})
    min_swing_dist_atr_mult: float = 0.5   # used when swing_filter_mode == "atr" (x ATR14 of that timeframe)
    # ---- instrument -------------------------------------------------------
    tick_size: Dict[str, float] = field(default_factory=lambda: {"NQ": 0.25, "ES": 0.25})
    # ---- ATR ---------------------------------------------------------------
    atr_period: int = 14
    atr_method: str = "wilder"      # "wilder" | "sma"
    # ---- 1H bias / draw --------------------------------------------------
    draw_max_atr_mult: float = 1.5  # draw must lie within this x 1H ATR14 of the entry price
    draw_use_fvg: bool = True
    draw_use_swings: bool = True
    draw_fvg_level: str = "proximal"   # "proximal" | "ce" | "distal" edge of 1H FVG used as draw price
    fvg_filled_mode: str = "full"      # "full": FVG filled once price trades across whole gap; "touch": once price enters it
    h1_lookback_bars: int = 500        # only 1H swings/FVGs from the last N closed 1H bars are considered
    require_discount: bool = True      # buys only below 1H dealing-range midpoint (sells above)
    # ---- 5m original consolidation -----------------------------------------
    cons_mode: str = "bars"            # "bars" = v1 (N-bar range <= k x ATR) | "session" = v2 (a session's high/low range)
    # v2 session-range options (used when cons_mode == "session"); times America/New_York
    session_range: str = "overnight"   # "overnight" | "asia" | "custom"
    session_range_times: Dict[str, List[str]] = field(default_factory=lambda: {
        "overnight": ["18:00", "09:30"],   # prior evening 18:00 -> 09:30
        "asia": ["20:00", "00:00"]})       # prior evening 20:00 -> midnight
    session_min_bars: int = 30         # range needs at least this many 1m bars (holidays / thin data)
    session_model_start: str = "09:30" # sweeps (5m bar start) only in [session_model_start, entry_end)
    session_curve_by_range_run: bool = True   # curve satisfied once price has traded through the range low (buys)/high (sells)
    session_sweep_range_extreme: bool = True  # trading through the untouched range low (buys) itself counts as a sweep
    session_invalidate_on_opposite_close: bool = True  # a 5m close beyond the range high kills that day's buy model (mirror for sells)
    cons_min_bars: int = 12
    cons_max_range_atr_mult: float = 1.0
    cons_atr_ref: str = "end"          # "end": ATR14 at the consolidation's last bar; "pre": ATR14 of the bar before it starts
    cons_breakout_max_bars: int = 6    # breakout close must come within N 5m bars after consolidation's last qualifying bar
    # ---- v3 daily/weekly bias filter (applied at order placement; decided once per day at session_model_start)
    htf_bias: str = "none"             # none | daily_draw | weekly_draw | daily_weekly | daily_pd | prev_day_candle
    htf_day_boundary: str = "18:00"    # daily bars = futures trading day [D-1 18:00, D 18:00); weekly bars open Sunday 18:00
    htf_use_prior_bar_hl: bool = True  # prior day's (week's) high/low are draw candidates (if untouched since that bar closed)
    htf_draw_one_sided_ok: bool = True # if only one side has a draw, that side is the bias
    htf_lookback_days: int = 120       # daily swings/FVGs from the last N closed daily bars
    htf_lookback_weeks: int = 104
    # v4 methods: midnight_open | midnight_daily_draw | ipda20_draw | ipda40_draw | ipda60_draw | ipda20_pd | ipda20_40_draw |
    #             weekly_profile | wp_early_extreme | wp_tuesday | wp_wed_reversal | wp_thu_reversal
    wp_cons_atr_mult: float = 1.5      # consolidation-Thursday-reversal: Mon-Wed range <= this x daily ATR14
    # ---- 5m curve ----------------------------------------------------------
    curve_min_swings: int = 2          # >= N successive (lower lows for buy model) 5m swings after the breakout
    curve_max_bars: int = 144          # setup expires N 5m bars after the breakout (12h)
    # ---- sweep ---------------------------------------------------------------
    sweep_reclaim_bars: int = 3        # 5m close back through the level within N bars (sweep bar counts as bar 1)
    sweep_use_swing: bool = True
    sweep_use_h1_fvg: bool = True      # sweep into a 1H discount (buy) / premium (sell) FVG also counts
    # ---- 1m MSS ----------------------------------------------------------------
    mss_timeout_bars: int = 60         # MSS must happen within N 1m bars after the sweep extreme
    mss_require_lower_high: bool = True  # the broken 1m swing high must be lower than the swing high before it
    fvg_after_mss_bars: int = 1        # the 1m FVG's 3rd candle may close up to N bars after the MSS candle
    # ---- v5 entry models (default "1m_fvg" = v1-v4 behaviour) --------------------------
    entry_model: str = "1m_fvg"        # 1m_fvg | 5m_fvg | 5m_ob | 1m_fvg_loose | 5m_mss
    entry_level: str = "proximal"      # 5m FVG: proximal edge | "ce" (50%); 5m OB: proximal = OB open | "ce" = mean threshold (50% of body)
    entry_cancel_5m_bars: int = 12     # 5m-based entries: cancel after N 5m bars (= 5N 1m bars)
    fvg5_search_bars: int = 12         # 5m_fvg: the FVG must complete within N 5m bars after the close-back bar
    ob_lookback_bars: int = 5          # OB = last down-close 5m candle at/before the sweep-extreme bar, searching back N bars
    ob_stop: str = "sweep"             # 5m_ob stop: "sweep" (sweep extreme - 1 tick) | "ob" (OB low - 1 tick)
    mss_loose_break: str = "body"      # 1m_fvg_loose: "body" (close) or "wick" (high) through the level
    mss5_timeout_bars: int = 12        # 5m_mss: break must happen within N 5m bars after the close-back bar
    mss5_entry_zone: str = "fvg"       # 5m_mss entry: "fvg" (first 5m FVG of the leg, proximal) | "ob" (OB open)
    # ---- entry / exits -------------------------------------------------------
    entry_cancel_bars: int = 15        # limit order cancelled if not filled within N 1m bars
    fill_through_ticks: int = 1        # limit fill requires trading through by N ticks (entries AND targets)
    stop_offset_ticks: int = 1         # stop N ticks beyond the sweep extreme
    stop_slippage_ticks: int = 0
    tp1_r: float = 2.0
    tp1_fraction: float = 0.5
    tp1_use_5m_swing: bool = True      # TP1 = nearer of tp1_r*R and the first 5m swing high above entry
    move_stop_to_be_after_tp1: bool = False
    # spread/commission in price points per full round trip (converted to R); a float, or a dict by root {"NQ": 0.8, "ES": 0.5}
    cost_points_round_trip: Union[float, Dict[str, float]] = 0.0
    # ---- time filter (America/New_York) -------------------------------------
    timezone: str = "America/New_York"
    entry_start: str = "09:30"
    entry_end: str = "11:00"
    flat_time: str = "11:00"           # any open trade is closed at the end of the session window
    session_buckets: List[str] = field(default_factory=lambda: ["09:30", "10:00", "10:30", "11:00"])
    # ---- misc ---------------------------------------------------------------
    one_position_at_a_time: bool = True
    directions: List[str] = field(default_factory=lambda: ["long", "short"])

    # helpers
    def min_dist(self, root: str) -> float:
        return float(self.min_swing_dist_points[root])

    def tick(self, root: str) -> float:
        return float(self.tick_size[root])

    def to_yaml(self, path: str) -> None:
        with open(path, "w") as f:
            yaml.safe_dump(asdict(self), f, sort_keys=False)

    @classmethod
    def from_yaml(cls, path: Optional[str]) -> "Config":
        if not path:
            return cls()
        with open(path) as f:
            d = yaml.safe_load(f) or {}
        known = {f.name for f in fields(cls)}
        bad = set(d) - known
        if bad:
            raise ValueError(f"unknown config keys: {sorted(bad)}")
        return cls(**d)

    def override(self, **kw) -> "Config":
        d = asdict(self)
        d.update(kw)
        return Config(**d)
