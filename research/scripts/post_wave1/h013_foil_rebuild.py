"""H013 random-entry foil rebuild (CASSANDRA Attack 1, 2026-10-04). EXPLORATORY re-score of the burned OOS year, run once.
Foil logic = ict-blueprint/research/model-u-longrun/scripts/analyze.py rand_R (lines 26-62) with ONLY the entry window changed:
  F0 replicate original: random minute 09:30-10:59, path 09:30-11:29   (must reproduce random_benchmark.csv 98.7)
  F1 PRIMARY (fill-window matched): random minute 09:00-10:59 (the v1 fill window), path to 11:29 close (11:30 time exit)
  F2 time-matched: model fill minute + U{-5..+5}, clipped to 09:00-10:59
  F3 direction-only: model fill minute exactly, random side
Every foil: random side, market entry at bar open, same day / risk_pts / T1,T2 R-multiples as the model trade,
same cost per side (0.8 US100), BE after first partial, time exit 11:29 close. 1000 runs, seed 7.
Trade sets: trades.csv (FILL_THRU=0, as reported) and data/trades_cost1x_thru1.csv (FILL_THRU=1, CASSANDRA frozen rule)."""
import json, sys, numpy as np, pandas as pd
LR = "/workspace/ict-blueprint/research/model-u-longrun"
COST = json.load(open(f"{LR}/data/costs.json"))
DATA = {nm: pd.read_parquet(f"{LR}/data/{nm}_1m.parquet") for nm in ("US100",)}
_c = {}
def arrays(nm, d, start):
    k = (nm, d, start)
    if k not in _c:
        g = DATA[nm].loc[f"{d} {start}":f"{d} 11:29"]
        _c[k] = (g.Open.values, g.High.values, g.Low.values, g.Close.values, g.index)
    return _c[k]
def sim(o, h, l, c, k, side, risk, d1, d2, cost):
    if side: o, h, l, c = -o, -l, -h, -c
    e = o[k]; s = e - risk; t1 = e + d1; t2 = e + d2; ef = e + cost
    R = lambda px: (px - ef) / risk
    pos, got, stop, done = 1.0, 0.0, s, False
    tg = [(t1, .5), (t2, .5)]
    if l[k] <= s: return R(s - cost)
    for i in range(k + 1, len(o)):
        if l[i] <= stop: got += pos * R(stop - cost); pos = 0; done = True; break
        for p, f in list(tg):
            if h[i] >= p: got += f * R(p - cost); pos -= f; tg = [x for x in tg if x[0] != p]; stop = e
        if pos <= 1e-9: done = True; break
    if not done and pos > 0: got += pos * R(c[-1] - cost)
    return got
def foil(rows, nm, mode, runs=1000, seed=7):
    rng = np.random.default_rng(seed); out = []
    start = "09:30" if mode == "F0" else "09:00"
    for _ in range(runs):
        acc = 0.0
        for d, risk, a1, a2, et in rows:
            O, H, L, C, idx = arrays(nm, d, start)
            n_entry = int(np.searchsorted(idx.values, pd.Timestamp(f"{d} 11:00", tz=idx.tz).to_datetime64()))
            fill_k = int(np.searchsorted(idx.values, pd.Timestamp(f"{d} {et}", tz=idx.tz).to_datetime64()))
            if mode in ("F0", "F1"):
                k = rng.integers(0, max(n_entry, 1)); side = rng.integers(0, 2)
            elif mode == "F2":
                k = int(np.clip(fill_k + rng.integers(-5, 6), 0, n_entry - 1)); side = rng.integers(0, 2)
            else:
                k = min(fill_k, n_entry - 1); side = rng.integers(0, 2)
            acc += sim(O.copy(), H.copy(), L.copy(), C.copy(), k, side, risk, a1 * risk, a2 * risk, COST[nm])
        out.append(acc / len(rows))
    return np.array(out)
if __name__ == "__main__":
    res = []
    for label, f in (("FILL_THRU=0 (reported)", f"{LR}/trades.csv"), ("FILL_THRU=1 (CASSANDRA freeze)", f"{LR}/data/trades_cost1x_thru1.csv")):
        T = pd.read_csv(f)
        x = T[(T.model == "v1 base") & (T.inst == "US100") & (T.status == "trade") & (T["sample"] == "OOS")].sort_values("date")
        rows = x[["date", "risk_pts", "t1_R_planned", "t2_R_planned", "entry_time_ny"]].values
        me = x.R_5050.mean()
        for mode in ("F0", "F1", "F2", "F3"):
            d = foil(rows, "US100", mode)
            res.append(dict(trade_set=label, foil=mode, n=len(x), model_exp=round(me, 4), foil_mean=round(d.mean(), 4),
                            foil_p95=round(np.percentile(d, 95), 4), percentile=(d < me).mean() * 100))
            print(res[-1], flush=True)
    pd.DataFrame(res).to_csv(sys.argv[1] if len(sys.argv) > 1 else "h013_foil_rebuild_results.csv", index=False)
