"""Per-instrument units, frictions and thresholds (post-H015b fixes; docs/INSTRUMENT_UNITS.md).

Everything here is ``hermes_interpretation`` unless a value is quoted from a source.

* ``pip``: the instrument's quoting unit. FX 0.0001 (JPY 0.01, XAU 0.1); US100 / US500 CFDs = 1.0 index point.
  Month-8 "pips" are measured in this unit (before this fix they were hard-coded ``x 10000``, so a 99-pt US100 CBDR
  read as 990,010 "pips" and every index day was CBDR "wide").
* CBDR / Asian thresholds: ICT's FX numbers (CBDR ideal < 40 pips, wide >= 50; Asian range > 40 pips = poor
  consolidation). For indices they are scaled by ONE rule, not swept: multiply by the ratio of the instrument's median
  daily range to EURUSD's median daily range, both measured on the burned window 2025-08-25 -> 2026-09-25
  (Dukascopy/HistData BID via /workspace/marketdata): EURUSD 61.5 pips, US100 414.7 pt (x6.74), US500 74.9 pt (x1.22).
* Frictions (DATA ruling 3, /workspace/marketdata README): assumed spread = DATA's 2026 off-RTH p90 schedule
  (US100 1.55 pt, US500 0.72 pt; the killzones are mostly before 09:30, so the conservative off-RTH value is used);
  slippage floors per side: US100 0.50 stop/market, 0.25 limit; US500 0.25 / 0.10.
* ``min_risk``: minimum REV stop distance enforced by the risk gate = MIN_RISK_FRICTION_MULT x round-trip friction
  (assumed spread + 2 x stop/market slippage), i.e. friction is at most 25% of 1R. US100 4 x 2.55 = 10.2 pt,
  US500 4 x 1.22 = 4.88 pt. FX: none (fixtures stay as reconstructed).
* REV stop buffer (``rev_stop_buffer``): shorts are stopped on the ASK, so the buffer beyond the raid high must cover
  spread + stop slippage: max(1 pip, spread + slip_stop), spread = max(measured spread at the signal if supplied,
  assumed spread). Longs are stopped on the BID (the chart the raid low was printed on): max(1 pip, slip_stop).
  FX and unknown symbols keep the FTN-D22 1-pip buffer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

FX_CBDR_IDEAL_LT = 40.0      # ict_source (Month 8)
FX_CBDR_WIDE_GE = 50.0       # ict_source (Month 8)
FX_ASIAN_POOR_GT = 40.0      # ict_source (Month 8)
EURUSD_MEDIAN_DAILY_RANGE_PIPS = 61.5   # burned window, measured
MIN_RISK_FRICTION_MULT = 4.0  # friction <= 25% of 1R (hermes_interpretation)


@dataclass(frozen=True)
class Instrument:
    symbol: str
    pip: float
    asset: str                      # fx | index | metal
    range_scale: float = 1.0        # median daily range / EURUSD median daily range (in pips)
    spread_assumed: Optional[float] = None    # price units
    slip_stop: float = 0.0          # price units, per side
    slip_market: float = 0.0
    slip_limit: float = 0.0

    @property
    def cbdr_ideal_lt(self) -> float:
        return round(FX_CBDR_IDEAL_LT * self.range_scale, 1)

    @property
    def cbdr_wide_ge(self) -> float:
        return round(FX_CBDR_WIDE_GE * self.range_scale, 1)

    @property
    def asian_poor_gt(self) -> float:
        return round(FX_ASIAN_POOR_GT * self.range_scale, 1)

    @property
    def threshold_origin(self) -> str:
        return "ict_source" if self.asset == "fx" else "hermes_interpretation"

    @property
    def min_risk(self) -> Optional[float]:
        if self.spread_assumed is None:
            return None
        return round(MIN_RISK_FRICTION_MULT * (self.spread_assumed + 2 * max(self.slip_stop, self.slip_market)), 4)


INSTRUMENTS = {
    "US100": Instrument("US100", 1.0, "index", round(414.7 / EURUSD_MEDIAN_DAILY_RANGE_PIPS, 3), 1.55, 0.50, 0.50, 0.25),
    "US500": Instrument("US500", 1.0, "index", round(74.9 / EURUSD_MEDIAN_DAILY_RANGE_PIPS, 3), 0.72, 0.25, 0.25, 0.10),
}
ALIASES = {"NAS100": "US100", "USTEC": "US100", "USATECHIDXUSD": "US100", "NQ": "US100",
           "SPX500": "US500", "USA500IDXUSD": "US500", "ES": "US500"}


def spec(symbol: str | None, pip: float | None = None) -> Instrument:
    s = (symbol or "").upper()
    s = ALIASES.get(s, s)
    if s in INSTRUMENTS:
        return INSTRUMENTS[s]
    if pip is None:
        pip = 0.01 if "JPY" in s else 0.1 if "XAU" in s else 0.0001
    return Instrument(s, float(pip), "metal" if "XAU" in s else "fx")


def to_pips(distance: float, symbol: str | None, pip: float | None = None) -> float:
    return round(float(distance) / spec(symbol, pip).pip, 1)


def rev_stop_buffer(symbol: str | None, side: str, pip: float, spread_measured: float | None = None) -> tuple[float, str]:
    """(buffer in price, label). See module docstring."""
    ins = spec(symbol, pip)
    one = 1.0 * float(pip)
    if ins.spread_assumed is None:
        return one, "1pip"
    if side == "sell":
        spread = max(float(spread_measured or 0.0), ins.spread_assumed)
        return max(one, spread + ins.slip_stop), "spread_plus_slip_ask_side"
    return max(one, ins.slip_stop), "slip_bid_side"
