"""7PM range sweep (see PREREG.md). EXPLORATORY, IN-SAMPLE burned window, NOT EVIDENCE."""
import gzip, hashlib, io, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
DATA = "/workspace/ftn-demo-output/data"; OUT = "research/7pm/"
SHA = {"US100_1m_bid": "6afa3130", "US100_1m_ask": "fcc3c877", "US500_1m_bid": "9d68787c", "US500_1m_ask": "ff63783f"}
END = pd.Timestamp("2026-09-25 17:00"); START = pd.Timestamp("2025-08-24 18:00")
COST = {"US100": dict(spr=1.55, stop=0.50, mkt=0.50, lim=0.25), "US500": dict(spr=0.72, stop=0.25, mkt=0.25, lim=0.10)}
import os
RHR = int(os.environ.get("RANGE_HOUR", "19")); SUF = "" if RHR == 19 else "_6pm"
MIN = 60_000_000_000; NB = 2000; SEED = 20261012; V = ["a_opp", "a_mid", "b_opp", "b_mid", "c_opp", "c_mid"]

def load(f):
    raw = gzip.open(f"{DATA}/{f}.csv.gz").read(); assert hashlib.sha256(raw).hexdigest().startswith(SHA[f]), f
    df = pd.read_csv(io.BytesIO(raw)); t = pd.to_datetime(df.Datetime, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    df.index = t; df = df.drop(columns="Datetime"); df = df[(df.index >= START) & (df.index < END)]; assert df.index.max() < END
    return df

def swings_low(lo):
    m = np.zeros(len(lo), bool); m[2:-2] = (lo[2:-2] < lo[1:-3]) & (lo[2:-2] < lo[:-4]) & (lo[2:-2] < lo[3:-1]) & (lo[2:-2] < lo[4:])
    return np.where(m)[0]

def run(inst):
    bid, ask = load(f"{inst}_1m_bid"), load(f"{inst}_1m_ask"); ask = ask.reindex(bid.index).ffill()
    T = bid.index; Tn = T.values.astype("datetime64[ns]").astype(np.int64)
    O, H, L, C = (bid[x].values for x in ["Open", "High", "Low", "Close"]); AO, AH, AL, AC = (ask[x].values for x in ["Open", "High", "Low", "Close"])
    c = COST[inst]; mr = 4 * (c["spr"] + 2 * c["mkt"])
    swl, swh = swings_low(L), swings_low(-H)
    trades, desc = [], []
    for D in pd.date_range("2025-08-24", "2026-09-24"):
        if D.weekday() in (4, 5): continue
        t0 = D + pd.Timedelta(hours=RHR); i0, i1 = np.searchsorted(Tn, [t0.value, (t0 + pd.Timedelta(hours=1)).value])
        if i1 - i0 < 45: continue
        RH, RL = H[i0:i1].max(), L[i0:i1].min(); mid = (RH + RL) / 2
        e = np.searchsorted(Tn, (D + pd.Timedelta(hours=32)).value) - 1  # last bar < 08:00 D+1
        if e <= i1 or (T[e] - (D + pd.Timedelta(hours=32))) < pd.Timedelta(hours=-2): continue
        up = H[i1:e + 1] > RH; dn = L[i1:e + 1] < RL
        if not (up.any() or dn.any()): desc.append(dict(day=D.date(), swept=False)); continue
        ku = np.argmax(up) if up.any() else 10**9; kd = np.argmax(dn) if dn.any() else 10**9
        if ku == kd: desc.append(dict(day=D.date(), swept=True, amb=True)); continue
        short = ku < kd; s = i1 + min(ku, kd); sd = -1 if short else 1
        opp_lvl = RL if short else RH
        rest = (L[s:e + 1] <= opp_lvl) if short else (H[s:e + 1] >= opp_lvl)
        midr = (L[s:e + 1] <= mid) if short else (H[s:e + 1] >= mid)
        desc.append(dict(day=D.date(), swept=True, amb=False, side="high" if short else "low", opp=rest.any(),
                         mins=(Tn[s + np.argmax(rest)] - Tn[s]) / MIN if rest.any() else np.nan, mid=midr.any()))
        ent = {"b": s}
        for k in range(s, e):
            if (C[k] < RH) if short else (C[k] > RL): ent["a"] = k; break
        sw = swl if short else swh
        for k in range(s, e):
            q = np.searchsorted(sw, k - 3, "right") - 1
            if q < 0 or sw[q] < i0: continue
            lv = L[sw[q]] if short else H[sw[q]]
            if ((C[k] < lv) and (C[k] < RH)) if short else ((C[k] > lv) and (C[k] > RL)): ent["c"] = k; break
        for en, k in ent.items():
            if k >= e: continue
            ref = C[k]; fill = (C[k] - c["mkt"]) if short else (AC[k] + c["mkt"])
            stop = (H[s:k + 1].max() + max(1.0, c["spr"] + c["stop"])) if short else (L[s:k + 1].min() - max(1.0, c["stop"]))
            if abs(ref - stop) < mr: stop = ref + mr if short else ref - mr
            risk = abs(ref - stop)
            for tn, tg in [("opp", opp_lvl), ("mid", mid)]:
                if (ref <= tg) if short else (ref >= tg): continue
                if en != "b":
                    pre = (L[s:k] <= tg) if short else (H[s:k] >= tg)
                    if pre.any(): continue
                ex = None
                for m in range(k + 1, e + 1):
                    if short:
                        if AH[m] >= stop: ex, why = max(stop, AO[m]) + c["stop"], "stop"
                        elif AL[m] < tg: ex, why = tg + c["lim"], "target"
                    else:
                        if L[m] <= stop: ex, why = min(stop, O[m]) - c["stop"], "stop"
                        elif H[m] > tg: ex, why = tg - c["lim"], "target"
                    if ex is not None: break
                if ex is None: m, why = e, "time"; ex = (AC[e] + c["mkt"]) if short else (C[e] - c["mkt"])
                trades.append(dict(var=f"{en}_{tn}", inst=inst, day=D.date(), dir="short" if short else "long", entry_t=T[k], exit_t=T[m],
                                   R=sd * (ex - fill) / risk, why=why, risk_pts=risk, widened=abs(risk - mr) < 1e-9))
    nul = []
    for D in pd.date_range("2025-08-24", "2026-09-25"):
        for h in range(24):
            t0 = D + pd.Timedelta(hours=h); i0, i1 = np.searchsorted(Tn, [t0.value, (t0 + pd.Timedelta(hours=1)).value])
            if i1 - i0 < 45: continue
            e = np.searchsorted(Tn, (t0 + pd.Timedelta(hours=13)).value) - 1
            if e - i1 < 300 or (t0 + pd.Timedelta(hours=13)) > END: continue
            RH, RL = H[i0:i1].max(), L[i0:i1].min()
            up = H[i1:e + 1] > RH; dn = L[i1:e + 1] < RL
            if not (up.any() or dn.any()): nul.append(dict(day=D.date(), h=h, swept=0, opp=0)); continue
            ku = np.argmax(up) if up.any() else 10**9; kd = np.argmax(dn) if dn.any() else 10**9
            if ku == kd: continue
            s = i1 + min(ku, kd); rest = (L[s:e + 1] <= RL) if ku < kd else (H[s:e + 1] >= RH)
            nul.append(dict(day=D.date(), h=h, swept=1, opp=int(rest.any())))
    return pd.DataFrame(trades), pd.DataFrame(desc), pd.DataFrame(nul)

def book(S, halt=True, start=10_000.0):
    S = S.sort_values("entry_t").reset_index(drop=True)
    eq = start; peak = start; busy = {}; pend = []; n = 0; curve = [(S.entry_t.min(), start)]
    st = dict(day=None, dstart=start, dpnl=0.0, halted=None, maxdd=0.0)
    def settle(upto):
        nonlocal eq, peak
        pend.sort(key=lambda x: x[0])
        while pend and pend[0][0] <= upto:
            t, pnl, d = pend.pop(0); eq += pnl; peak = max(peak, eq); st["maxdd"] = max(st["maxdd"], 1 - eq / peak)
            if d == st["day"]: st["dpnl"] += pnl
            curve.append((t, eq))
            if halt and st["halted"] is None and eq <= 0.95 * peak: st["halted"] = t
    for r in S.itertuples():
        settle(r.entry_t)
        if st["halted"] is not None: break
        if r.day != st["day"]: st.update(day=r.day, dstart=eq, dpnl=0.0)
        if st["dpnl"] <= -0.02 * st["dstart"]: continue
        if busy.get(r.inst, pd.Timestamp.min) > r.entry_t: continue
        pnl = r.R * 0.005 * eq; busy[r.inst] = r.exit_t; pend.append((r.exit_t, pnl, r.day)); n += 1
    settle(pd.Timestamp.max)
    return n, pd.DataFrame(curve, columns=["t", "eq"]), st["halted"], st["maxdd"]

def boot(S):
    rng = np.random.default_rng(SEED); days = S.day.unique(); g = S.groupby("day").R.agg(["sum", "count"]).reindex(days)
    W = rng.multinomial(len(days), np.ones(len(days)) / len(days), size=NB); bm = (W @ g["sum"].values) / (W @ g["count"].values)
    return np.quantile(bm, .025), np.quantile(bm, .975), bm.std(ddof=1), max((bm <= 0).mean(), 1 / NB)

def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(o): run = max(run, (m - k) * ps[i]); adj[i] = min(1, run)
    return adj

def main():
    TR, DE, NU = [], [], []
    for inst in ["US100", "US500"]:
        t, d, n = run(inst); d["inst"] = inst; n["inst"] = inst; TR.append(t); DE.append(d); NU.append(n)
    TR, DE, NU = (pd.concat(x, ignore_index=True) for x in (TR, DE, NU))
    TR.to_csv(OUT + "trades" + SUF + ".csv", index=False)
    drows = []
    for inst, d in DE.groupby("inst"):
        s = d[d.swept & (d.amb != True)]
        drows.append(dict(inst=inst, nights=len(d), P_swept=d.swept.mean(), ambiguous=int((d.amb == True).sum()), N_first_sweep=len(s),
                          P_opp_after_sweep=s.opp.astype(float).mean(), P_mid_after_sweep=s.mid.astype(float).mean(),
                          median_min_to_opp=s.mins.median(), p75_min_to_opp=s.mins.quantile(.75), high_first=(s.side == "high").mean()))
    desc = pd.DataFrame(drows)
    nrows = []
    for inst, n in NU.groupby("inst"):
        sw = n[n.swept == 1]; per_h = sw.groupby("h").opp.mean(); n_h = n.groupby("h").swept.mean()
        days = pd.Index(sorted(sw.day.unique())); di = days.get_indexer(sw.day); D = len(days)
        a = (sw.h == RHR).values; v = sw.opp.values * 1.
        y1, n1 = np.bincount(di[a], v[a], D), np.bincount(di[a], minlength=D) * 1.; y2, n2 = np.bincount(di[~a], v[~a], D), np.bincount(di[~a], minlength=D) * 1.
        rng = np.random.default_rng(SEED); W = rng.multinomial(D, np.ones(D) / D, size=NB)
        bs = W @ y1 / (W @ n1) - W @ y2 / (W @ n2)
        nrows.append(dict(inst=inst, P_opp_rangehour=per_h[RHR], P_opp_other_hours=v[~a].mean(), diff=per_h[RHR] - v[~a].mean(), lo=np.quantile(bs, .025), hi=np.quantile(bs, .975),
                          rank_rangehour_of_24=int((per_h > per_h[RHR]).sum()) + 1, P_swept_rangehour=n_h[RHR], P_swept_other=n.swept[n.h != RHR].mean()))
        per_h.rename(f"P_opp_{inst}").to_csv(OUT + f"null_by_hour_{inst}.csv")
    nul = pd.DataFrame(nrows)
    res, curves = [], {}
    for v in V:
        for scope in ["pooled", "US100", "US500"]:
            S = TR[TR["var"] == v] if scope == "pooled" else TR[(TR["var"] == v) & (TR.inst == scope)]
            if len(S) < 2: continue
            lo, hi, se, p = boot(S)
            r = dict(variant=v, scope=scope, N=len(S), win=(S.R > 0).mean(), avg_win=S.R[S.R > 0].mean(), avg_loss=S.R[S.R <= 0].mean(),
                     meanR=S.R.mean(), lo=lo, hi=hi, p_one=p, haircutR=S.R.mean() - 1.267 * se, widened=S.widened.mean())
            if scope == "pooled":
                for halt in (True, False):
                    n_, cv, h, mdd = book(S, halt); tag = "halted" if halt else "unhalted"
                    r |= {f"N_{tag}": n_, f"final_{tag}": cv["eq"].iloc[-1], f"maxDD_{tag}": mdd}
                    if halt: r["halted_at"] = h
                    else: curves[v] = cv
            res.append(r)
    R = pd.DataFrame(res); m = R.scope == "pooled"; R.loc[m, "p_holm"] = holm(R.p_one[m].values)
    for v in V:
        sub = R[(R.variant == v) & (R.scope != "pooled")]
        R.loc[(R.variant == v) & m, "same_sign"] = bool(len(sub) == 2 and np.sign(sub.meanR).nunique() == 1)
    R.loc[m, "forward_worthy"] = (R.p_holm[m] < .05) & (R.haircutR[m] > 0) & (R.same_sign[m] == True) & (R.maxDD_unhalted[m] < .2)
    R.to_csv(OUT + "results" + SUF + ".csv", index=False); desc.to_csv(OUT + "descriptive" + SUF + ".csv", index=False); nul.to_csv(OUT + "null" + SUF + ".csv", index=False)
    pd.set_option("display.width", 320)
    for x in (desc, nul, R): print(x.to_string(float_format=lambda z: f"{z:.4f}")); print()
    print(TR.groupby(["var", "why"]).size().unstack())
    fig, ax = plt.subplots(1, 2, figsize=(15, 5.5))
    for v, cv in curves.items(): ax[0].step(cv.t, cv["eq"], where="post", label=v, lw=1)
    ax[0].axhline(1e4, c="k", lw=.5); ax[0].legend(fontsize=8); ax[0].grid(alpha=.3); ax[0].set_ylabel("equity $ (unhalted, 0.5% risk, US100+US500)")
    ax[0].set_title(f"{RHR}:00 range sweep variants, $10k unhalted books")
    for inst in ["US100", "US500"]:
        ph = pd.read_csv(OUT + f"null_by_hour_{inst}.csv", index_col=0).iloc[:, 0]; ax[1].plot(ph.index, ph.values, "o-", label=inst)
    ax[1].axvline(RHR, c="r", lw=.8); ax[1].set_xlabel("range start hour (NY)"); ax[1].set_ylabel("P(opposite side reached | first sweep, 12h)")
    ax[1].legend(); ax[1].grid(alpha=.3); ax[1].set_title("Null: same stat for the 1h range at every hour")
    fig.suptitle("IN-SAMPLE burned window 2025-08-25..2026-09-25, EXPLORATORY, NOT EVIDENCE", fontsize=9); fig.tight_layout(); fig.savefig(OUT + "equity" + SUF + ".png", dpi=105)

if __name__ == "__main__":
    main()
