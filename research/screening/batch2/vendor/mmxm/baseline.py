"""Random-entry baseline: same days, sides, risk (points) and R-multiple targets as a set of real trades,
but the entry is a market order at the open of a uniformly random 1m bar inside the entry window.
Exit rules mirror the engine: stop checked first (also on the entry bar), TP1 fraction at tp1_R (target limits need a
`fill_through_ticks` trade-through; targets never on the entry bar), runner at draw_R, flat at the close of the last bar
before flat_time, same round-trip cost. Used to ask whether an entry model's timing beats chance."""
from __future__ import annotations

import numpy as np
import pandas as pd


def _hm(s):
    h, m = s.split(":")
    return int(h) * 60 + int(m)


def outcome_table(m1: pd.DataFrame, trades: pd.DataFrame, cfg, root: str):
    """For every trade: array of R outcomes for every possible random entry bar in the window."""
    ny = pd.DatetimeIndex(m1.index).tz_convert("America/New_York")
    mod = ny.hour * 60 + ny.minute
    dates = ny.date
    es, ft = _hm(cfg.entry_start), _hm(cfg.flat_time)
    if cfg.move_stop_to_be_after_tp1 or cfg.stop_slippage_ticks:
        raise NotImplementedError("baseline assumes no BE move and no stop slippage (the v1 defaults)")
    tick = cfg.tick(root)
    thru = cfg.fill_through_ticks * tick
    cost = cfg.cost_points_round_trip
    cost = float(cost.get(root, 0.0)) if isinstance(cost, dict) else float(cost)
    o, h, l, c = (m1[k].to_numpy(float) for k in ("open", "high", "low", "close"))
    out = []
    for _, t in trades.iterrows():
        d = pd.Timestamp(t["entry_time_ny"]).date()
        sel = np.nonzero((dates == d) & (mod >= es) & (mod < ft))[0]
        if len(sel) < 2:
            out.append(np.array([float(t["r_multiple"])]))
            continue
        sg = 1.0 if t["direction"] == "long" else -1.0
        risk = float(t["risk_pts"])
        tp1R = sg * (float(t["tp1"]) - float(t["entry"])) / risk
        drR = sg * (float(t["draw"]) - float(t["entry"])) / risk
        final = str(t["tp1_source"]).startswith("1h_draw")
        # work in "long space": favourable = sg*price
        H = sg * h[sel] if sg > 0 else -l[sel]
        L = sg * l[sel] if sg > 0 else -h[sel]
        C = sg * c[sel]
        O = sg * o[sel]
        W = len(sel)
        res = np.empty(W - 1)
        for e in range(W - 1):
            E = O[e]
            stop, tp1, dr = E - risk, E + tp1R * risk, E + drR * risk
            sh = np.nonzero(L[e:] <= stop)[0]
            s = e + sh[0] if len(sh) else W
            ah = np.nonzero(H[e + 1:] >= tp1 + thru)[0]
            a = e + 1 + ah[0] if len(ah) else W
            if final or a >= W or s <= a:
                if s <= a and s < W:
                    r = -1.0
                elif a < W:
                    r = tp1R
                else:
                    r = (C[-1] - E) / risk
            else:
                fr = cfg.tp1_fraction
                dh = np.nonzero(H[a:] >= dr + thru)[0]
                dd = a + dh[0] if len(dh) else W
                s2 = s  # first stop after a (s > a here)
                if dd < s2 and dd < W:
                    run = drR
                elif s2 < W:
                    run = -1.0
                else:
                    run = (C[-1] - E) / risk
                r = fr * tp1R + (1 - fr) * run
            res[e] = r - cost / risk
        out.append(res)
    return out


def permute(tables, n_perm: int, rng: np.random.Generator):
    """Total R for n_perm random draws (one random entry per trade)."""
    tot = np.zeros(n_perm)
    for arr in tables:
        tot += arr[rng.integers(0, len(arr), n_perm)]
    return tot
