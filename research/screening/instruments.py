"""Protocol section 2: mechanical, cost-pinned scaling rules for NEW S1 instruments (declared before results).

Specs are registered at runtime into ``ftn.os.instruments.INSTRUMENTS`` (no pinned file is edited). Every value is
measured on the instrument's own new data in 2025-08-25 .. 2026-09-25 (same window as the pinned US100/US500 values);
no outcome is simulated before the specs are fixed and written out.
"""
from __future__ import annotations

from datetime import date, datetime, time, timedelta
from statistics import median

PIP = {"GER40": 1.0, "US30": 1.0, "XAUUSD": 0.1}
ASSET = {"GER40": "index", "US30": "index", "XAUUSD": "metal"}
SCALE_WINDOW = (date(2025, 8, 25), date(2026, 9, 25))
SLIP_SPREAD_RATIO = round(((0.50 / 1.55) + (0.25 / 0.72)) / 2, 3)   # 0.335 (pinned US100 / US500 ratios)
KZ = ((time(2, 0), time(5, 0)), (time(7, 0), time(10, 0)))


def _p90(xs):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(0.9 * (len(xs) - 1) + 0.5))] if xs else None


def us500_price_bp(us500_bid) -> float:
    """Pinned US500 slip_stop (0.25) / median US500 BID close on the burned tape."""
    from ftn.os.instruments import INSTRUMENTS
    return INSTRUMENTS["US500"].slip_stop / median(us500_bid.c)


def measure(sym: str, bid, ask, price_bp: float) -> dict:
    from ftn.os.instruments import EURUSD_MEDIAN_DAILY_RANGE_PIPS
    from ftn.research.bars import session_bounds, trading_days
    a, b = SCALE_WINDOW
    days = [d for d in trading_days(bid) if a <= d <= b]
    rng = []
    for d in days:
        hl = bid.hl(*session_bounds(d))
        if hl:
            rng.append((hl[0] - hl[1]) / PIP[sym])
    spreads, closes = [], []
    for d in days:
        for k0, k1 in KZ:
            for i in bid.window(datetime.combine(d, k0), datetime.combine(d, k1)):
                j = ask.idx(bid.t[i])
                if j < len(ask.t) and ask.t[j] == bid.t[i]:
                    spreads.append(ask.c[j] - bid.c[i])
        closes.extend(bid.c[i] for i in bid.window(*session_bounds(d)))
    spread = round(_p90(spreads), 3)
    slip = round(max(SLIP_SPREAD_RATIO * spread, price_bp * median(closes)), 3)
    return {"symbol": sym, "pip": PIP[sym], "asset": ASSET[sym],
            "range_scale": round(median(rng) / EURUSD_MEDIAN_DAILY_RANGE_PIPS, 3), "median_daily_range_pips": round(median(rng), 1),
            "spread_assumed": spread, "slip_stop": slip, "slip_market": slip, "slip_limit": round(0.5 * slip, 3),
            "median_close": round(median(closes), 3), "n_scale_days": len(days), "n_spread_bars": len(spreads),
            "rule": "protocol v1 section 2"}


def register(spec: dict):
    from ftn.os.instruments import INSTRUMENTS, Instrument
    ins = Instrument(spec["symbol"], spec["pip"], spec["asset"], spec["range_scale"], spec["spread_assumed"],
                     spec["slip_stop"], spec["slip_market"], spec["slip_limit"])
    INSTRUMENTS[spec["symbol"]] = ins
    return ins
