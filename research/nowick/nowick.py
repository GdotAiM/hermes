"""NOWICK-1 descriptive study (see PREREG.md). In-sample burned exploration only."""
import gzip, hashlib, json, math, sys
from datetime import date
import numpy as np, pandas as pd

DATA = "/workspace/ftn-demo-output/data"
SHA = {"US100_1m_bid": "6afa3130", "US100_1m_ask": "fcc3c877", "US500_1m_bid": "9d68787c", "US500_1m_ask": "ff63783f"}
D0, D1 = date(2025, 8, 25), date(2026, 9, 25)
TFS = {"15m": 15, "1H": 60, "4H": 240, "D": 1380}
KMAX = {"15m": 200, "1H": 60, "4H": 20, "D": 20}
BAR_H = {"15m": [5, 20, 50], "1H": [5, 20, 50], "4H": [5, 20, 50], "D": [5, 20]}
NB, RNG = 2000, np.random.default_rng(20261012)
SHIFT = pd.Timedelta(hours=7)

def load(f):
    raw = gzip.open(f"{DATA}/{f}.csv.gz").read()
    assert hashlib.sha256(raw).hexdigest().startswith(SHA[f]), f
    df = pd.read_csv(pd.io.common.BytesIO(raw))
    t = pd.to_datetime(df.Datetime, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    df.index = t; df = df.drop(columns="Datetime")
    day = (df.index + SHIFT).date
    df = df[(day >= D0) & (day <= D1)]
    assert ((df.index + SHIFT).date <= D1).all()
    return df

def bars(bid, ask, tf):
    m = TFS[tf]
    sp = (ask.Close.reindex(bid.index) - bid.Close)
    s = bid.index + SHIFT
    if tf == "W": key = s.to_period("W-SUN").start_time
    elif tf == "D": key = s.floor("D")
    elif tf == "4H": key = s.floor("4h")
    else: key = s.floor(f"{m}min")
    g = bid.assign(sp=sp.values).groupby(key)
    b = pd.DataFrame({"o": g.Open.first(), "h": g.High.max(), "l": g.Low.min(), "c": g.Close.last(),
                      "n": g.Open.size(), "spread": g.sp.median()})
    b = b[b.n >= 0.5 * m].copy()
    b["t"] = b.index - SHIFT; b["day"] = b.index.date
    b = b.reset_index(drop=True)
    pc = b.c.shift(1)
    tr = np.maximum(b.h - b.l, np.maximum((b.h - pc).abs(), (b.l - pc).abs()))
    b["atr"] = tr.shift(1).rolling(14).mean()   # ATR of the 14 bars before the candle
    b["spread"] = b.spread.fillna(b.spread.median())
    return b

def first_hit(arr, i_cmp, ok, K):
    """for each i: smallest k in 1..K with ok(arr[i+k], i) ; inf if none"""
    n = len(arr); fh = np.full(n, np.inf)
    for k in range(K, 0, -1):
        idx = np.arange(n) + k; v = idx < n
        hit = np.zeros(n, bool); hit[v] = ok(arr[idx[v]], np.where(v)[0])
        fh[hit] = k
    return fh

def kz(t):
    h = t.hour + t.minute / 60
    if h >= 20: return "Asia"
    if 2 <= h < 5: return "London"
    if 7 <= h < 10: return "NYAM"
    if 13.5 <= h < 16: return "NYPM"
    return "other"

def features(b, tf):
    o, h, l, c, sp, atr = (b[x].values for x in ["o", "h", "l", "c", "spread", "atr"])
    rng = h - l; body = np.abs(c - o); K = KMAX[tf]; n = len(b)
    d = np.where(c > o, 1, np.where(c < o, -1, 0))
    wick = np.where(d == 1, o - l, h - o)
    base = (rng >= 0.5 * atr) & (body >= 0.3 * rng) & (d != 0) & np.isfinite(atr)
    grp = np.full(n, "", object)
    grp[base & (wick >= 0.10 * rng)] = "WICK"
    grp[base & (wick <= 0.02 * rng) & (wick <= sp)] = "TOL"
    exact = base & (wick == 0)
    lo_, hi_ = l, h
    rev = np.where(d == 1, first_hit(lo_, None, lambda a, i: a <= o[i], K), first_hit(hi_, None, lambda a, i: a >= o[i], K))
    rb = first_hit(lo_, None, lambda a, i: a <= o[i], K); rs = first_hit(hi_, None, lambda a, i: a >= o[i], K)
    rev = np.where(d == 1, rb, rs)
    sb = first_hit(lo_, None, lambda a, i: a <= o[i] - np.maximum(sp[i], 0.001), K)
    ss = first_hit(hi_, None, lambda a, i: a >= o[i] + np.maximum(sp[i], 0.001), K)
    swp = np.where(d == 1, sb, ss)
    xb = first_hit(hi_, None, lambda a, i: a > h[i], K); xs = first_hit(lo_, None, lambda a, i: a < l[i], K)
    opp = np.where(d == 1, xb, xs)
    out = pd.DataFrame({"t": b.t, "day": b.day, "dir": np.where(d == 1, "bull", "bear"), "grp": grp, "exact": exact,
                        "body_atr": body / atr, "rng_atr": rng / atr, "rev": rev, "swp": swp, "opp": opp,
                        "dist": np.where(d == 1, o - c, c - o) / atr})  # signed target in ATR (bull negative)
    # horizons
    hz = {}
    for H in BAR_H[tf]:
        valid = np.arange(n) + H < n
        hz[f"{H}b"] = (H, valid)
    if tf not in ("D", "W"):
        days = b.day.values; ud = np.unique(days); pos = {x: k for k, x in enumerate(ud)}
        last = pd.Series(np.arange(n)).groupby(days).max(); lastidx = last.reindex(ud).values
        dk = np.array([pos[x] for x in days])
        for name, off in [("sameday", 0), ("nextday", 1)]:
            tgt = dk + off; valid = tgt < len(ud)
            H = np.where(valid, lastidx[np.minimum(tgt, len(ud) - 1)] - np.arange(n), 0)
            valid &= H <= K
            hz[name] = (H, valid)
    out.attrs["hz"] = hz
    # paths for bootstrap null (b): normalized min-low / max-high relative to close
    return out, (l, h, c, atr)

def hits(out, col, H):
    return (out[col].values <= H)

def cell_stats(out, col, H, valid, dirn, extra=None):
    T = (out.grp == "TOL") & (out.dir == dirn) & valid
    C = (out.grp == "WICK") & (out.dir == dirn) & valid
    y = hits(out, col, H) if np.isscalar(H) else (out[col].values <= H)
    pool = out[(T | C)]
    qb = np.quantile(pool.body_atr, [.2, .4, .6, .8]); qr = np.quantile(pool.rng_atr, [.2, .4, .6, .8])
    bins = np.digitize(out.body_atr, qb) * 5 + np.digitize(out.rng_atr, qr)
    days = pd.Index(np.unique(out.day[T | C])); di = days.get_indexer(out.day)
    D, B = len(days), 25
    nt = np.zeros((D, B)); ht = np.zeros((D, B)); nc = np.zeros((D, B)); hc = np.zeros((D, B))
    for m, N_, Hh in [(T, nt, ht), (C, nc, hc)]:
        np.add.at(N_, (di[m], bins[m]), 1); np.add.at(Hh, (di[m], bins[m]), y[m])
    def est(w):
        Nt, Ht, Nc, Hc = (w @ x for x in (nt, ht, nc, hc))
        ok = Nc > 0
        pt = Ht[ok].sum() / Nt[ok].sum()
        base = (Nt[ok] / Nt[ok].sum() * Hc[ok] / Nc[ok]).sum()
        return pt, base, Ht.sum() / max(Nt.sum(), 1), Nt[~ok].sum()
    w1 = np.ones(D); pt, base, raw, dropped = est(w1)
    W = RNG.multinomial(D, np.ones(D) / D, size=NB).astype(float)
    diffs = np.array([np.subtract(*est(w)[:2]) for w in W])
    se = diffs.std(ddof=1); diff = pt - base
    p = math.erfc(abs(diff) / se / math.sqrt(2)) if se > 0 else 1.0
    return dict(N=int(T.sum()), Nc=int(C.sum()), rate=raw, rate_matched=pt, base=base, diff=diff,
                lo=np.quantile(diffs, .025), hi=np.quantile(diffs, .975), p=p, dropped=int(dropped)), T, y

def null_b(out, paths, T, H, dirn, draws=20):
    l, h, c, atr = paths; n = len(c); Hm = int(H)
    idx = np.arange(n); okj = np.where((idx + Hm < n) & np.isfinite(atr))[0]
    # normalized extremes over next H bars
    if dirn == "bull":
        ext = pd.Series(l[::-1]).rolling(Hm, min_periods=Hm).min().values[::-1]  # min l[j..j+H-1]
        m = np.full(n, np.nan); m[:-1] = (ext[1:] - c[:-1]) / atr[:-1]
    else:
        ext = pd.Series(h[::-1]).rolling(Hm, min_periods=Hm).max().values[::-1]
        m = np.full(n, np.nan); m[:-1] = (ext[1:] - c[:-1]) / atr[:-1]
    ti = np.where(T)[0]; js = RNG.choice(okj, size=(len(ti), draws))
    tgt = out.dist.values[ti][:, None]
    mm = m[js]
    return float(np.nanmean(mm <= tgt) if dirn == "bull" else np.nanmean(mm >= -tgt))

def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(o):
        run = max(run, (m - k) * ps[i]); adj[i] = min(1, run)
    return adj

def main():
    rows, kzrows, ordrows, exrows = [], [], [], []
    for inst in ["US100", "US500"]:
        bid, ask = load(f"{inst}_1m_bid"), load(f"{inst}_1m_ask")
        print(inst, bid.index.min(), bid.index.max(), file=sys.stderr)
        for tf in TFS:
            b = bars(bid, ask, tf); out, paths = features(b, tf)
            base_all = np.isfinite(out.body_atr) & (out.rng_atr >= 0.5) & (out.body_atr >= 0.3 * out.rng_atr)
            for dirn in ["bull", "bear"]:
                for hname, (H, valid) in out.attrs["hz"].items():
                    for col in ["rev", "swp"]:
                        st, T, y = cell_stats(out, col, H, valid, dirn)
                        st.update(inst=inst, tf=tf, dir=dirn, hz=hname, outcome=col)
                        # (b)
                        st["null_b"] = null_b(out, paths, T, H, dirn) if (col == "rev" and hname.endswith("b")) else np.nan
                        # (c) distance-conditioned over all filtered same-dir candles
                        A = base_all & (out.dir == dirn).values & valid
                        q = np.quantile(out.body_atr[A], np.linspace(.1, .9, 9))
                        bA = np.digitize(out.body_atr, q)
                        rate_bin = pd.Series(y[A]).groupby(bA[A]).mean()
                        st["null_c"] = float(rate_bin.reindex(bA[T]).mean())
                        # exact variant
                        E = out.exact.values & (out.dir == dirn).values & valid
                        st["N_exact"] = int(E.sum()); st["rate_exact"] = float(y[E].mean()) if E.any() else np.nan
                        fh = out[col].values[T]
                        st["med_bars"] = float(np.median(fh[fh <= KMAX[tf]])) if np.isfinite(fh).any() else np.nan
                        rows.append(st)
                        if col == "rev" and hname == ("20b" if tf != "D" else "5b") and tf in ("15m", "1H"):
                            C = (out.grp == "WICK").values & (out.dir == dirn).values & valid
                            k = out.t.map(kz).values
                            for z in ["Asia", "London", "NYAM", "NYPM", "other"]:
                                kzrows.append(dict(inst=inst, tf=tf, dir=dirn, kz=z, N=int((T & (k == z)).sum()),
                                                   rev=float(y[T & (k == z)].mean()), Nc=int((C & (k == z)).sum()),
                                                   rev_ctrl=float(y[C & (k == z)].mean())))
                # ordering at max horizon
                T = (out.grp == "TOL").values & (out.dir == dirn).values
                C = (out.grp == "WICK").values & (out.dir == dirn).values
                for g, M in [("TOL", T), ("WICK", C)]:
                    r, x = out.rev.values[M], out.opp.values[M]
                    ordrows.append(dict(inst=inst, tf=tf, dir=dirn, grp=g, N=int(M.sum()),
                                        open_first=float(np.mean(r < x)), opp_first=float(np.mean(x < r)),
                                        same_bar=float(np.mean((r == x) & np.isfinite(r))), neither=float(np.mean(~np.isfinite(r) & ~np.isfinite(x)))))
    R = pd.DataFrame(rows)
    for col in ["rev", "swp"]:
        m = R.outcome == col; R.loc[m, "p_holm"] = holm(R.p[m])
    R.to_csv("research/nowick/results_cells.csv", index=False)
    pd.DataFrame(kzrows).to_csv("research/nowick/results_killzones.csv", index=False)
    pd.DataFrame(ordrows).to_csv("research/nowick/results_ordering.csv", index=False)

if __name__ == "__main__":
    main()
