"""NOWICK-1 addendum 1 (A timing, B premium/discount DiD, C clock/daily/weekly opens). See PREREG.md Addendum 1."""
import math, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "research/nowick")
import nowick as nw
nw.TFS["W"] = 1380 * 5; nw.KMAX["W"] = 4; nw.BAR_H["W"] = [1, 4]
TFMIN = {"15m": 15, "1H": 60, "4H": 240, "D": 1440, "W": 10080}
RNG = np.random.default_rng(20261012); NB = 2000
OUT = "research/nowick/"
KS = [1, 3, 5, 10, 20, 50]

def bins_for(out, pool):
    qb = np.quantile(out.body_atr[pool], [.2, .4, .6, .8]); qr = np.quantile(out.rng_atr[pool], [.2, .4, .6, .8])
    return np.digitize(out.body_atr, qb) * 5 + np.digitize(out.rng_atr, qr)

def ctrl_weights(T, C, bins):
    w = np.zeros(len(bins)); nt = np.bincount(bins[T], minlength=25); nc = np.bincount(bins[C], minlength=25)
    ok = nc > 0; w[C] = np.where(ok[bins[C]], nt[bins[C]] / np.maximum(nc[bins[C]], 1), 0)
    return w / w.sum()

def wq(x, w, q):  # weighted quantile with inf allowed
    o = np.argsort(x); x, w = x[o], w[o]; c = np.cumsum(w) / w.sum()
    return np.array([x[min(np.searchsorted(c, qq), len(x) - 1)] for qq in q])

def minute_scan(T1, L1, H1, close_ns, lvl, side, maxmin):
    res = np.full(len(lvl), np.inf)
    st = np.searchsorted(T1, close_ns); en = np.searchsorted(T1, close_ns + maxmin * 60_000_000_000)
    for k in range(len(lvl)):
        a, b = st[k], en[k]
        if a >= b: continue
        hit = (L1[a:b] <= lvl[k]) if side[k] == 1 else (H1[a:b] >= lvl[k])
        j = np.argmax(hit)
        if hit[j]: res[k] = (T1[a + j] - close_ns[k]) / 60e9 + 1
    return res

def fmt(v, scan):
    return f">{scan}" if not np.isfinite(v) else f"{v:g}"

def matched_boot(groups, y, bins, day, W_days, days_index):
    """groups: list of (T,C) masks. returns point & bootstrap arrays of matched diffs per group"""
    D = len(days_index); di = days_index.get_indexer(day)
    res = []
    for T, C in groups:
        arr = []
        for m in (T, C):
            N_ = np.zeros((D, 25)); H_ = np.zeros((D, 25)); ok = m & (di >= 0)
            np.add.at(N_, (di[ok], bins[ok]), 1); np.add.at(H_, (di[ok], bins[ok]), y[ok]); arr += [N_, H_]
        res.append(arr)
    def est(w):
        out = []
        for nt, ht, nc, hc in res:
            Nt, Ht, Nc, Hc = w @ nt, w @ ht, w @ nc, w @ hc; ok = (Nc > 0) & (Nt > 0)
            if Nt[ok].sum() == 0: out.append(np.nan); continue
            out.append(Ht[ok].sum() / Nt[ok].sum() - (Nt[ok] / Nt[ok].sum() * Hc[ok] / Nc[ok]).sum())
        return out
    pt = est(np.ones(D)); bs = np.array([est(w) for w in W_days])
    return pt, bs

def holm(ps): return nw.holm(np.nan_to_num(ps, nan=1.0))

def main():
    A_rows, surv, B_rows, C_rows, W_rows = [], {}, [], [], []
    for inst in ["US100", "US500"]:
        bid, ask = nw.load(f"{inst}_1m_bid"), nw.load(f"{inst}_1m_ask")
        T1 = bid.index.values.astype("datetime64[ns]").astype(np.int64); L1, H1, O1, C1 = (bid[x].values for x in ["Low", "High", "Open", "Close"])
        dB = nw.bars(bid, ask, "D")
        H20 = dB.h.shift(1).rolling(20).max(); L20 = dB.l.shift(1).rolling(20).min()
        dr = pd.DataFrame({"H20": H20.values, "L20": L20.values}, index=dB.day.values)
        b1h = nw.bars(bid, ask, "1H")
        for tf in ["15m", "1H", "4H", "D", "W"]:
            b = nw.bars(bid, ask, tf); out, paths = nw.features(b, tf); K = nw.KMAX[tf]
            close_ns = (pd.to_datetime(out.t) + pd.Timedelta(minutes=TFMIN[tf])).values.astype("datetime64[ns]").astype(np.int64)
            o = b.o.values; sp = np.maximum(b.spread.values, 0.001)
            for dirn in ["bull", "bear"]:
                sgn = 1 if dirn == "bull" else -1
                T = (out.grp == "TOL").values & (out.dir == dirn).values
                C = (out.grp == "WICK").values & (out.dir == dirn).values
                pool = T | C
                if T.sum() == 0: continue
                bins = bins_for(out, pool); w = ctrl_weights(T, C, bins)
                if tf == "W":
                    for g, M in [("TOL", T), ("WICK", C)]:
                        W_rows.append(dict(inst=inst, dir=dirn, grp=g, N=int(M.sum()),
                                           rev_1w=float((out.rev.values[M] <= 1).mean()) if M.any() else np.nan,
                                           rev_4w=float((out.rev.values[M] <= 4).mean()) if M.any() else np.nan,
                                           swp_4w=float((out.swp.values[M] <= 4).mean()) if M.any() else np.nan))
                    continue
                side = np.full(len(o), sgn)
                lvl_r = o.copy(); lvl_s = o - sgn * sp
                maxmin = K * TFMIN[tf]
                idx = np.where(pool)[0]
                m_r = np.full(len(o), np.inf); m_s = np.full(len(o), np.inf)
                m_r[idx] = minute_scan(T1, L1, H1, close_ns[idx], lvl_r[idx], side[idx], maxmin)
                m_s[idx] = minute_scan(T1, L1, H1, close_ns[idx], lvl_s[idx], side[idx], maxmin)
                # censor: candles whose scan window runs past data end
                valid = close_ns + maxmin * 60e9 <= T1[-1]
                for g, M, ww in [("no-wick", T & valid, None), ("control(w)", C & valid, w)]:
                    wts = np.ones(M.sum()) if ww is None else ww[M]
                    row = dict(inst=inst, tf=tf, dir=dirn, grp=g, N=int(M.sum()))
                    for nm, arr in [("rev", out.rev.values), ("swp", out.swp.values)]:
                        q = wq(arr[M], wts, [.25, .5, .75, .9])
                        for qq, v in zip([25, 50, 75, 90], q): row[f"{nm}_p{qq}_bars"] = fmt(v, K)
                        for k in KS: row[f"{nm}_<= {k}b"] = float(np.average(arr[M] <= k, weights=wts))
                        row[f"{nm}_never"] = float(np.average(~np.isfinite(arr[M]), weights=wts))
                    for nm, arr in [("rev", m_r), ("swp", m_s)]:
                        q = wq(arr[M], wts, [.25, .5, .75, .9])
                        for qq, v in zip([25, 50, 75, 90], q): row[f"{nm}_p{qq}_min1m"] = fmt(round(v), maxmin) if np.isfinite(v) else f">{maxmin}"
                    A_rows.append(row)
                    if tf in ("15m", "1H"): surv[(inst, tf, dirn, g)] = (m_r[M], wts, maxmin)
                # ---- B: premium / discount
                if tf in ("15m", "1H", "4H"):
                    rngD = dr.reindex(out.day.values); pos20 = ((o - rngD.L20.values) / (rngD.H20.values - rngD.L20.values))
                    hh = b.groupby("day").h.cummax().groupby(b.day).shift(1).values
                    ll = b.groupby("day").l.cummin().groupby(b.day).shift(1).values
                    first_t = b.groupby("day").t.transform("min").values
                    el = (pd.to_datetime(out.t).values - first_t) / np.timedelta64(1, "m")
                    posd = np.where((el >= 60) & (hh - ll > 0), (o - ll) / (hh - ll), np.nan)
                    for rdef, pos in [("20sess", pos20), ("curday", posd)]:
                        A = (pos < 0.5) if dirn == "bull" else (pos > 0.5)
                        Bz = (pos > 0.5) if dirn == "bull" else (pos < 0.5)
                        ote = ((pos >= 0.21) & (pos <= 0.38)) if dirn == "bull" else ((pos >= 0.62) & (pos <= 0.79))
                        for zA_name, zA in ([("aligned", A), ("OTE", ote)] if rdef == "20sess" else [("aligned", A)]):
                            fam = "primary" if (rdef == "20sess" and zA_name == "aligned") else f"{rdef}_{zA_name}"
                            for hname in ["20b", "sameday"]:
                                H, hv = out.attrs["hz"][hname]
                                for col in ["rev", "swp"]:
                                    y = out[col].values <= H
                                    m = np.isfinite(pos) & hv
                                    TA, CA, TB, CB = T & zA & m, C & zA & m, T & Bz & m, C & Bz & m
                                    days_index = pd.Index(np.unique(out.day.values[TA | CA | TB | CB]))
                                    Wd = RNG.multinomial(len(days_index), np.ones(len(days_index)) / len(days_index), size=NB).astype(float)
                                    pt, bs = matched_boot([(TA, CA), (TB, CB)], y, bins, out.day.values, Wd, days_index)
                                    did = pt[0] - pt[1]; bd = bs[:, 0] - bs[:, 1]; bd = bd[np.isfinite(bd)]
                                    se = bd.std(ddof=1) if len(bd) > 10 else np.nan
                                    p = math.erfc(abs(did) / se / math.sqrt(2)) if se and np.isfinite(se) and se > 0 else np.nan
                                    B_rows.append(dict(family=fam, inst=inst, tf=tf, dir=dirn, hz=hname, outcome=col,
                                                       N_A=int(TA.sum()), N_B=int(TB.sum()), Nc_A=int(CA.sum()), Nc_B=int(CB.sum()),
                                                       rate_A=float(y[TA].mean()) if TA.any() else np.nan, rate_B=float(y[TB].mean()) if TB.any() else np.nan,
                                                       diff_A=pt[0], diff_B=pt[1], DiD=did,
                                                       lo=np.quantile(bd, .025) if len(bd) else np.nan, hi=np.quantile(bd, .975) if len(bd) else np.nan, p=p))
                # ---- C(i): daily cells
                if tf == "D":
                    for g, M in [("TOL", T), ("WICK", C)]:
                        for H in [1, 5, 20]:
                            v = M & (np.arange(len(o)) + H < len(o))
                            C_rows.append(dict(kind="daily_nowick", inst=inst, dir=dirn, grp=g, horizon=f"{H}d", N=int(v.sum()),
                                               revisit=float((out.rev.values[v] <= H).mean()) if v.any() else np.nan,
                                               sweep=float((out.swp.values[v] <= H).mean()) if v.any() else np.nan))
        # ---- C(iii): clock-time 60-min candles
        Ts = pd.DatetimeIndex(bid.index); minute_of_day = Ts.hour * 60 + Ts.minute
        cand = [m for m in list(range(18 * 60, 24 * 60)) + list(range(0, 9 * 60 + 45)) if m not in (0, 570)]
        base_times = sorted(RNG.choice(cand, 60, replace=False).tolist())
        atr1h = pd.Series(b1h.atr.values, index=pd.to_datetime(b1h.t)).sort_index()
        sp1 = (ask.Close.reindex(bid.index) - bid.Close).values
        tday = (Ts + nw.SHIFT).date
        for mt in [0, 570] + base_times:
            st_idx = np.where(minute_of_day == mt)[0]
            rows = []
            for a in st_idx:
                t0 = T1[a]; e = np.searchsorted(T1, t0 + 60 * 60e9)
                if e - a < 30 or tday[e - 1] != tday[a]: continue
                op, hi, lo, cl = O1[a], H1[a:e].max(), L1[a:e].min(), C1[e - 1]
                if cl == op: continue
                sgn = 1 if cl > op else -1; s = max(np.nanmedian(sp1[a:e]), 0.001)
                close_ns = t0 + 60 * 60e9
                r = minute_scan(T1, L1, H1, np.array([close_ns]), np.array([op]), np.array([sgn]), 360)[0]
                sw = minute_scan(T1, L1, H1, np.array([close_ns]), np.array([op - sgn * s]), np.array([sgn]), 360)[0]
                at = atr1h.asof(pd.Timestamp(t0)); rng = hi - lo; wick = (op - lo) if sgn == 1 else (hi - op)
                nwk = bool(np.isfinite(at) and rng >= 0.5 * at and abs(cl - op) >= 0.3 * rng and wick <= 0.02 * rng and wick <= s)
                rows.append((r, sw, nwk))
            if not rows: continue
            r, sw, nwk = map(np.array, zip(*rows))
            for sub, M in [("all", np.ones(len(r), bool)), ("nowick", nwk.astype(bool))]:
                C_rows.append(dict(kind="clock", inst=inst, clock=f"{mt // 60:02d}:{mt % 60:02d}", is_base=mt not in (0, 570), sub=sub, N=int(M.sum()),
                                   revisit=float(np.isfinite(r[M]).mean()) if M.any() else np.nan,
                                   sweep=float(np.isfinite(sw[M]).mean()) if M.any() else np.nan,
                                   med_min=float(np.median(r[M][np.isfinite(r[M])])) if np.isfinite(r[M]).any() else np.nan))
    A = pd.DataFrame(A_rows); A.to_csv(OUT + "add1_timing.csv", index=False)
    B = pd.DataFrame(B_rows)
    for fam in B.family.unique():
        m = B.family == fam; B.loc[m, "p_holm"] = holm(B.p[m].values)
    B.to_csv(OUT + "add1_pd_did.csv", index=False)
    Cdf = pd.DataFrame(C_rows); Cdf.to_csv(OUT + "add1_opens.csv", index=False)
    pd.DataFrame(W_rows).to_csv(OUT + "add1_weekly.csv", index=False)
    for tf in ["15m", "1H"]:
        fig, axs = plt.subplots(2, 2, figsize=(11, 8), sharey=True)
        for ax, (inst, dirn) in zip(axs.flat, [(i, d) for i in ["US100", "US500"] for d in ["bull", "bear"]]):
            for g, ls in [("no-wick", "-"), ("control(w)", "--")]:
                if (inst, tf, dirn, g) not in surv: continue
                x, wts, mm = surv[(inst, tf, dirn, g)]; grid = np.linspace(0, mm, 400)
                S = [np.average(x > gg, weights=wts) for gg in grid]
                ax.plot(grid, S, ls, label=f"{g} (N={len(x)})")
            ax.set_title(f"{inst} {tf} {dirn}"); ax.set_xlabel("minutes after candle close (1m res.)"); ax.set_ylabel("P(open not yet revisited)")
            ax.set_xscale("symlog", linthresh=15); ax.grid(alpha=.3); ax.legend()
        fig.suptitle(f"NOWICK-1 survival to open revisit, {tf} (in-sample burned 2025-08-25..2026-09-25)"); fig.tight_layout()
        fig.savefig(OUT + f"survival_{tf}.png", dpi=110); plt.close(fig)

if __name__ == "__main__":
    main()
