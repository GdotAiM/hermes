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
    r_gross, how, last, xt = None, "time", entry, entry_time
    for i in s.window(entry_time, end):
        xt = s.t[i]
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
    return {"R": r_gross - cost_r, "R_gross": r_gross, "exit": how, "risk_pts": risk, "cost_R": cost_r,
            "exit_time": xt.isoformat(), "cost_model": "flat"}


def simulate_both(bid: Series, ask: Series, entry_time: datetime, entry: float, stop: float, side: str,
                  slip: dict, slip_mult: float = 1.0, target_r: float = TARGET_R) -> dict:
    """Correct-side fills (DATA ruling 3; the post-H015b DEFAULT cost model). Buys fill on ASK, sells on BID, plus the
    per-side slippage floors ``slip = {"market", "stop", "limit"}`` (``ftn.os.instruments``).

    Levels are the kernel's BID-chart levels. Long: entry = ask close + slip_market; stop when BID low <= stop, fill
    min(stop, bid open) - slip_stop; target when BID high > target (limits trade through), fill target - slip_limit.
    Short: entry = bid close - slip_market; stop when ASK high >= stop, fill max(stop, ask open) + slip_stop; target
    when ASK low < target, fill target + slip_limit. Time exit = last 1m close before 16:00 NY on the exit side.
    Stop first on ambiguous bars. Minutes without an ASK print are skipped (no synthetic fills).
    R denominator = planned risk |signal entry - stop| (same as ``simulate``), so R is comparable across cost models."""
    sl = {k: float(v) * slip_mult for k, v in slip.items()}
    risk = (entry - stop) if side == "buy" else (stop - entry)
    if risk <= 0:
        return {"R": None, "exit": "invalid_stop"}
    tgt = entry + target_r * risk if side == "buy" else entry - target_r * risk
    ib, ia = bid.idx(entry_time) - 1, ask.idx(entry_time) - 1
    if ib < 0 or ia < 0:
        return {"R": None, "exit": "no_entry_bar"}
    fill_in = ask.c[ia] + sl["market"] if side == "buy" else bid.c[ib] - sl["market"]
    end = datetime.combine(entry_time.date(), time(16, 0))
    how, xp, xt, last = "time", None, None, None
    for i in bid.window(entry_time, end):
        j = ask.idx(bid.t[i])
        if j >= len(ask.t) or ask.t[j] != bid.t[i]:
            continue
        if side == "buy":
            if bid.l[i] <= stop:
                xp, how = min(stop, bid.o[i]) - sl["stop"], "stop"
            elif bid.h[i] > tgt:
                xp, how = tgt - sl["limit"], "target"
        else:
            if ask.h[j] >= stop:
                xp, how = max(stop, ask.o[j]) + sl["stop"], "stop"
            elif ask.l[j] < tgt:
                xp, how = tgt + sl["limit"], "target"
        if xp is not None:
            xt = bid.t[i]
            break
        last = (i, j)
    if xp is None:
        if last is None:
            return {"R": None, "exit": "no_bars"}
        i, j = last
        xp = (bid.c[i] - sl["market"]) if side == "buy" else (ask.c[j] + sl["market"])
        xt = bid.t[i]
    pnl = (xp - fill_in) if side == "buy" else (fill_in - xp)
    return {"R": pnl / risk, "exit": how, "risk_pts": risk, "fill_in": fill_in, "fill_out": xp,
            "exit_time": xt.isoformat(), "target": tgt, "cost_model": "correct_side"}
