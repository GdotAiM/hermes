"""NOWICK-1 addendum 3: H-NW11 illustrative equity curve (PREREG Addendum 3). EXPLORATORY, IN-SAMPLE, NOT EVIDENCE."""
import sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "research/nowick")
import nowick as nw
from addendum2 import swings
OUT = "research/nowick/"; MIN = 60_000_000_000
TFMIN = {"15m": 15, "1H": 60}
COST = {"US100": dict(spr=1.55, stop=0.50, mkt=0.50, lim=0.25), "US500": dict(spr=0.72, stop=0.25, mkt=0.25, lim=0.10)}

def signals(inst):
    bid, ask = nw.load(f"{inst}_1m_bid"), nw.load(f"{inst}_1m_ask")
    ask = ask.reindex(bid.index).ffill()
    T1 = bid.index.values.astype("datetime64[ns]").astype(np.int64)
    O, H, L, C = (bid[x].values for x in ["Open", "High", "Low", "Close"])
    AO, AH, AL, AC = (ask[x].values for x in ["Open", "High", "Low", "Close"])
    tday = np.array((bid.index + nw.SHIFT).date)
    dend = pd.Series(np.arange(len(T1))).groupby(tday).transform("max").values
    c = COST[inst]; minrisk = 4 * (c["spr"] + 2 * c["mkt"])
    sl_lo = swings(L); sl_hi = swings(-H)  # swing lows (bull view) / swing highs (bear view)
    trades = []
    for tf in TFMIN:
        b = nw.bars(bid, ask, tf); out, _ = nw.features(b, tf)
        close_ns = (pd.to_datetime(out.t) + pd.Timedelta(minutes=TFMIN[tf])).values.astype("datetime64[ns]").astype(np.int64)
        for i in np.where((out.grp == "TOL").values)[0]:
            bull = out.dir.values[i] == "bull"; op = b.o.values[i]; far = b.h.values[i] if bull else b.l.values[i]
            a = np.searchsorted(T1, close_ns[i])
            if a >= len(T1): continue
            e = min(np.searchsorted(T1, close_ns[i] + 20 * TFMIN[tf] * MIN) - 1, dend[a])  # last bar of time stop window
            sw = sl_lo if bull else sl_hi; lb = close_ns[i] - 60 * MIN; k_sig = None
            for k in range(a, e + 1):
                if (H[k] > far) if bull else (L[k] < far): break
                if (L[k] <= op) if bull else (H[k] >= op): break
                q = np.searchsorted(sw, k - 3, "right") - 1  # confirmed: s+2 <= k-1
                if q < 0 or T1[sw[q]] < lb: continue
                s = sw[q]
                if (C[k] < L[s]) if bull else (C[k] > H[s]): k_sig = (k, s); break
            if k_sig is None: continue
            k, s = k_sig
            if bull:  # short
                stop = H[s:k + 1].max() + max(1.0, c["spr"] + c["stop"]); entry = C[k] - c["mkt"]
                if stop - C[k] < minrisk: stop = C[k] + minrisk
                risk = stop - C[k]
            else:
                stop = L[s:k + 1].min() - max(1.0, c["stop"]); entry = AC[k] + c["mkt"]
                if C[k] - stop < minrisk: stop = C[k] - minrisk
                risk = C[k] - stop
            ex, xt, why = None, None, "time"
            for m in range(k + 1, e + 1):
                if bull:
                    if AH[m] >= stop: ex, why = max(stop, AO[m]) + c["stop"], "stop"
                    elif AL[m] < op: ex, why = op + c["lim"], "target"
                else:
                    if L[m] <= stop: ex, why = min(stop, O[m]) - c["stop"], "stop"
                    elif H[m] > op: ex, why = op - c["lim"], "target"
                if ex is not None: xt = m; break
            if ex is None:
                xt = max(e, k); ex = (AC[xt] + c["mkt"]) if bull else (C[xt] - c["mkt"])
            R = ((entry - ex) if bull else (ex - entry)) / risk
            trades.append(dict(inst=inst, tf=tf, dir="short" if bull else "long", candle_t=out.t.values[i],
                               entry_t=bid.index[k], exit_t=bid.index[xt], day=tday[k], entry=entry, stop=stop, target=op,
                               risk_pts=risk, widened=bool(abs(risk - minrisk) < 1e-9), exit=ex, why=why, R=R))
    return pd.DataFrame(trades)

def book(S, halt=True, start=10_000.0):
    S = S.sort_values(["entry_t", "tf"]).reset_index(drop=True)
    eq = start; peak = start; busy = {}; pend = []; taken = []; curve = [(S.entry_t.min(), start)]
    day = None; dstart = start; dpnl = 0; halted_at = None; maxdd = 0
    def settle(upto):
        nonlocal eq, peak, dpnl, maxdd, halted_at
        pend.sort(key=lambda x: x[0])
        while pend and pend[0][0] <= upto:
            t, pnl, d = pend.pop(0); eq += pnl; peak = max(peak, eq); maxdd = max(maxdd, 1 - eq / peak)
            if d == day: dpnl += pnl
            curve.append((t, eq))
            if halt and halted_at is None and eq <= peak * 0.95: halted_at = t
    for r in S.itertuples():
        settle(r.entry_t)
        if halted_at is not None: break
        if r.day != day: day, dstart, dpnl = r.day, eq, 0
        if dpnl <= -0.02 * dstart: continue
        if busy.get(r.inst, pd.Timestamp.min) > r.entry_t: continue
        risk = 0.005 * eq; pnl = r.R * risk
        busy[r.inst] = r.exit_t; pend.append((r.exit_t, pnl, r.day)); taken.append(r._asdict() | {"pnl": pnl})
    settle(pd.Timestamp.max)
    return pd.DataFrame(taken), pd.DataFrame(curve, columns=["t", "eq"]), halted_at, maxdd

def boot(T):
    rng = np.random.default_rng(20261012); days = T.day.unique(); g = T.groupby("day").R.agg(["sum", "count"]).reindex(days)
    W = rng.multinomial(len(days), np.ones(len(days)) / len(days), size=2000)
    m = (W @ g["sum"].values) / (W @ g["count"].values)
    return np.quantile(m, [.025, .975])

def summ(T, label):
    lo, hi = boot(T) if len(T) > 1 else (np.nan, np.nan)
    return dict(set=label, N=len(T), win=(T.R > 0).mean(), meanR=T.R.mean(), lo=lo, hi=hi, sumR=T.R.sum(),
                pnl=T.pnl.sum() if "pnl" in T else np.nan)

def main():
    S = pd.concat([signals(x) for x in ["US100", "US500"]], ignore_index=True)
    S.to_csv(OUT + "add3_signals.csv", index=False)
    res = {}
    for halt in (True, False):
        T, cv, h, dd = book(S, halt); res[halt] = (T, cv, h, dd)
        T.to_csv(OUT + f"add3_trades_{'halted' if halt else 'unhalted'}.csv", index=False)
    rows = []
    for name, T in [("all_signals(no book)", S), ("book_halted", res[True][0]), ("book_unhalted", res[False][0])]:
        rows.append(summ(T, name))
        for (a, b_), G in T.groupby(["inst", "tf"]): rows.append(summ(G, f"{name} | {a} {b_}"))
        for a, G in T.groupby("inst"): rows.append(summ(G, f"{name} | {a}"))
        for a, G in T.groupby("tf"): rows.append(summ(G, f"{name} | {a}"))
    R = pd.DataFrame(rows); R.to_csv(OUT + "add3_summary.csv", index=False)
    pd.set_option("display.width", 200); print(R.round(3).to_string())
    for halt in (True, False):
        T, cv, h, dd = res[halt]
        print(f"halt={halt} final={cv["eq"].iloc[-1]:.2f} ret={cv["eq"].iloc[-1]/1e4-1:.2%} N={len(T)} maxDD={dd:.2%} halted_at={h}")
    print("exit reasons", S.why.value_counts().to_dict(), "widened", S.widened.mean())
    fig, ax = plt.subplots(figsize=(11, 5))
    for halt, ls in [(False, "-"), (True, "--")]:
        cv = res[halt][1]; ax.step(cv.t, cv["eq"], where="post", ls=ls, label=("halted at 5% DD" if halt else "unhalted"))
    if res[True][2] is not None: ax.axvline(res[True][2], color="r", lw=.8, label=f"5% DD halt {res[True][2]:%Y-%m-%d}")
    ax.axhline(1e4, color="k", lw=.5); ax.legend(); ax.grid(alpha=.3); ax.set_ylabel("equity $")
    ax.set_title("H-NW11 illustrative equity, US100+US500, 15m+1H, 0.5% risk. IN-SAMPLE burned window, EXPLORATORY, NOT EVIDENCE", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT + "hnw11_equity.png", dpi=110)

if __name__ == "__main__":
    main()
