"""R outcome of a ticket on 1m bars (hermes_interpretation exit; REPORT D17).

Entry = close of the 15m ticket bar. Stop = draft stop_reference. Target = 2R fixed.
Time exit = last 1m close before 16:00 NY. If a bar touches both stop and target, the stop
counts (conservative). Cost = ``2 * cost_per_side_pts`` in price, expressed in R.
"""

from __future__ import annotations

from datetime import datetime, time

from ftn.research.bars import Series

TARGET_R = 2.0


def simulate(s: Series, entry_time: datetime, entry: float, stop: float, side: str,
             cost_per_side: float, target_r: float = TARGET_R) -> dict:
    risk = (entry - stop) if side == "buy" else (stop - entry)
    if risk <= 0:
        return {"R": None, "exit": "invalid_stop"}
    tgt = entry + target_r * risk if side == "buy" else entry - target_r * risk
    end = datetime.combine(entry_time.date(), time(16, 0))
    r_gross, how, last = None, "time", entry
    for i in s.window(entry_time, end):
        hi, lo = s.h[i], s.l[i]
        hit_stop = lo <= stop if side == "buy" else hi >= stop
        hit_tgt = hi >= tgt if side == "buy" else lo <= tgt
        if hit_stop:
            r_gross, how = -1.0, "stop"
            break
        if hit_tgt:
            r_gross, how = target_r, "target"
            break
        last = s.c[i]
    if r_gross is None:
        r_gross = ((last - entry) if side == "buy" else (entry - last)) / risk
    cost_r = 2 * cost_per_side / risk
    return {"R": r_gross - cost_r, "R_gross": r_gross, "exit": how, "risk_pts": risk, "cost_R": cost_r}
