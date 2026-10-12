"""NOWICK-1 addendum 2: lower-timeframe path features into the revisit (see PREREG.md Addendum 2). Exploration only."""
import math, sys
from collections import Counter
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
sys.path.insert(0, "research/nowick")
import nowick as nw
from addendum1 import bins_for, ctrl_weights, TFMIN
nw.TFS["5m"] = 5
RNG = np.random.default_rng(20261012); NB = 2000; OUT = "research/nowick/"
MIN = 60_000_000_000
FEATS = ["OPP", "MSS1", "MSS5", "DISP", "FVG1", "FVG5", "SWP5", "SESS", "DRIFT"]

def swings(lo):
    n = len(lo); m = np.zeros(n, bool)
    m[2:-2] = (lo[2:-2] < lo[1:-3]) & (lo[2:-2] < lo[:-4]) & (lo[2:-2] < lo[3:-1]) & (lo[2:-2] < lo[4:])
    return np.where(m)[0]

class Side:
    """price arrays oriented so the open lies BELOW (bull view); bear = negated & swapped."""
    def __init__(s, O, H, L, C, o5, h5, l5, c5, atr5, sgn):
        if sgn == 1: s.O, s.H, s.L, s.C, s.o5, s.h5, s.l5, s.c5 = O, H, L, C, o5, h5, l5, c5
        else: s.O, s.H, s.L, s.C, s.o5, s.h5, s.l5, s.c5 = -O, -L, -H, -C, -o5, -l5, -h5, -c5
        s.atr5 = atr5
        s.sl1 = swings(s.L); s.sl5 = swings(s.l5); s.sh5 = swings(-s.h5)
        i = np.arange(2, len(s.H)); s.fvg1 = i[s.H[i] < s.L[i - 2]]
        k = np.arange(2, len(s.h5)); s.fvg5 = k[s.h5[k] < s.l5[k - 2]]
        s.disp = np.where((s.o5 - s.c5 >= 1.5 * atr5) & np.isfinite(atr5))[0]

def first_in(arr, lo, hi):  # first element of sorted arr in [lo, hi)
    k = np.searchsorted(arr, lo)
    return arr[k] if k < len(arr) and arr[k] < hi else None

def features(S, T1, T5s, a, j, close_ns, c_hi, sess_hi, i5_close):
    """bull-oriented features in 1m window [a, j). returns dict feat->first time (ns) or None, plus extras"""
    f = {k: None for k in FEATS}; ex = {"CE1": None, "OB": None, "turn": None}
    if j <= a:
        f["DRIFT"] = close_ns; return f, ex
    seg = S.H[a:j]; turn = a + int(np.argmax(seg)); ex["turn"] = T1[turn]
    if seg.max() > c_hi: f["OPP"] = T1[a + int(np.argmax(seg > c_hi))]
    if sess_hi is not None and S.H[a:turn + 1].max() > sess_hi: f["SESS"] = T1[a + int(np.argmax(S.H[a:turn + 1] > sess_hi))]
    # MSS1
    k = np.searchsorted(S.sl1, turn - 2, "right") - 1
    if k >= 0 and T1[S.sl1[k]] >= close_ns - 60 * MIN:
        lvl = S.L[S.sl1[k]]; br = np.where(S.C[turn + 1:j] < lvl)[0]
        if len(br): f["MSS1"] = T1[turn + 1 + br[0]]
    # 5m indices: bars fully inside window
    t_end = T1[j] if j < len(T1) else T1[-1]
    b0 = np.searchsorted(T5s, close_ns); b1 = np.searchsorted(T5s, t_end - 5 * MIN, "right")  # bars b0..b1-1 end <= t_end
    turn5 = np.searchsorted(T5s, T1[turn], "right") - 1
    k = np.searchsorted(S.sl5, turn5 - 2, "right") - 1
    if k >= 0 and T5s[S.sl5[k]] >= close_ns - 60 * MIN and turn5 + 1 < b1:
        lvl = S.l5[S.sl5[k]]; br = np.where(S.c5[turn5 + 1:b1] < lvl)[0]
        if len(br): f["MSS5"] = T5s[turn5 + 1 + br[0]] + 5 * MIN
    d = first_in(S.disp, b0, b1)
    if d is not None:
        f["DISP"] = T5s[d] + 5 * MIN
        ob = [q for q in range(d - 1, max(d - 13, -1), -1) if S.c5[q] > S.o5[q]]
        if ob:
            q = ob[0]; mid = (S.o5[q] + S.c5[q]) / 2; a2 = np.searchsorted(T1, T5s[d] + 5 * MIN)
            ex["OB"] = bool(a2 < j and S.H[a2:j].max() >= mid)
    g = first_in(S.fvg1, a + 2, j)
    if g is not None:
        f["FVG1"] = T1[g]; ce = (S.L[g - 2] + S.H[g]) / 2
        ex["CE1"] = bool(g + 1 < j and S.H[g + 1:j].max() >= ce)
    g5 = first_in(S.fvg5, b0 + 2, b1)
    if g5 is not None: f["FVG5"] = T5s[g5] + 5 * MIN
    sh = S.sh5[(S.sh5 >= i5_close - 24) & (S.sh5 + 2 < i5_close)]
    if len(sh) and S.H[a:turn + 1].max() > S.h5[sh].min(): f["SWP5"] = T1[a + int(np.argmax(S.H[a:turn + 1] > S.h5[sh].min()))]
    if all(f[x] is None for x in FEATS[:-1]): f["DRIFT"] = close_ns
    return f, ex

def seq_of(f):
    tok = []
    for name, keys in [("SWEEP", ["OPP", "SWP5", "SESS"]), ("MSS", ["MSS1", "MSS5"]), ("DISP", ["DISP"]), ("FVG", ["FVG1", "FVG5"])]:
        ts = [f[k] for k in keys if f[k] is not None]
        if ts: tok.append((min(ts), name))
    tok.sort(key=lambda x: x[0])
    return " > ".join([t for _, t in tok] + ["REV"]) if tok else "DRIFT > REV"

def boot_diff(df, g1, g2, feat):
    days = pd.Index(np.unique(df.day[g1 | g2])); di = days.get_indexer(df.day)
    D = len(days); arr = []
    for g in (g1, g2):
        w = df.w.values * g; arr.append((np.bincount(di[g], (w * df[feat].values)[g], D), np.bincount(di[g], w[g], D)))
    est = lambda W: (W @ arr[0][0]) / (W @ arr[0][1]) - (W @ arr[1][0]) / (W @ arr[1][1])
    pt = est(np.ones(D)); Wb = RNG.multinomial(D, np.ones(D) / D, size=NB).astype(float)
    bs = Wb @ arr[0][0] / (Wb @ arr[0][1]) - Wb @ arr[1][0] / (Wb @ arr[1][1]); bs = bs[np.isfinite(bs)]
    se = bs.std(ddof=1)
    return pt, np.quantile(bs, .025), np.quantile(bs, .975), (math.erfc(abs(pt) / se / math.sqrt(2)) if se > 0 else 1.0)

def main():
    rows = []
    for inst in ["US100", "US500"]:
        bid, ask = nw.load(f"{inst}_1m_bid"), nw.load(f"{inst}_1m_ask")
        T1 = bid.index.values.astype("datetime64[ns]").astype(np.int64)
        O, H, L, C = (bid[x].values for x in ["Open", "High", "Low", "Close"])
        b5 = nw.bars(bid, ask, "5m"); T5s = pd.to_datetime(b5.t).values.astype("datetime64[ns]").astype(np.int64)
        tday = np.array((bid.index + nw.SHIFT).date); dstart = pd.Series(np.arange(len(T1))).groupby(tday).transform("min").values
        sides = {s: Side(O, H, L, C, b5.o.values, b5.h.values, b5.l.values, b5.c.values, b5.atr.values, s) for s in (1, -1)}
        for tf in ["15m", "1H"]:
            b = nw.bars(bid, ask, tf); out, _ = nw.features(b, tf); K = nw.KMAX[tf]; maxmin = K * TFMIN[tf]
            close_ns = (pd.to_datetime(out.t) + pd.Timedelta(minutes=TFMIN[tf])).values.astype("datetime64[ns]").astype(np.int64)
            for dirn, sgn in [("bull", 1), ("bear", -1)]:
                S = sides[sgn]
                T = (out.grp == "TOL").values & (out.dir == dirn).values; Cm = (out.grp == "WICK").values & (out.dir == dirn).values
                valid = close_ns + maxmin * MIN <= T1[-1]; T &= valid; Cm &= valid
                bins = bins_for(out, T | Cm)
                ev = []
                for i in np.where(T | Cm)[0]:
                    a = np.searchsorted(T1, close_ns[i]); e = np.searchsorted(T1, close_ns[i] + maxmin * MIN)
                    lvl = sgn * b.o.values[i]
                    hit = np.where(S.L[a:e] <= lvl)[0]
                    j = a + hit[0] if len(hit) else None
                    ev.append((i, a, j))
                revmin = [(T1[j] - close_ns[i]) / MIN + 1 for i, a, j in ev if j is not None and T[i]]
                M = np.median(revmin) if revmin else 60
                recs = []
                for i, a, j in ev:
                    if j is None and not T[i]: continue
                    jj = j if j is not None else np.searchsorted(T1, close_ns[i] + M * MIN)
                    c_hi = sgn * (b.h.values[i] if sgn == 1 else b.l.values[i])
                    ds = dstart[min(a, len(T1) - 1)]; sess = S.H[ds:a].max() if a > ds else None
                    i5c = np.searchsorted(T5s, close_ns[i])
                    f, ex = features(S, T1, T5s, a, jj, close_ns[i], c_hi, sess, i5c)
                    rec = dict(inst=inst, tf=tf, dir=dirn, grp="TOL" if T[i] else "WICK", rev=j is not None, day=out.day.values[i],
                               bin=bins[i], t=out.t.values[i], close_ns=close_ns[i], a=a, j=jj, win_min=(T1[min(jj, len(T1)-1)] - close_ns[i]) / MIN,
                               seq=seq_of(f), CE1=ex["CE1"], OB=ex["OB"],
                               kz_turn=nw.kz(pd.Timestamp(ex["turn"])) if ex["turn"] else None,
                               kz_rev=nw.kz(pd.Timestamp(T1[jj])) if j is not None else None, open=b.o.values[i], hi=b.h.values[i], lo=b.l.values[i])
                    for k in FEATS: rec[k] = f[k] is not None; rec["t_" + k] = f[k]
                    recs.append(rec)
                R = pd.DataFrame(recs)
                # weights: controls (revisited) reweighted to TOL revisited bins
                R["w"] = 1.0
                tr, cr = (R.grp == "TOL") & R.rev, (R.grp == "WICK") & R.rev
                if tr.any() and cr.any():
                    nt = np.bincount(R.bin[tr], minlength=25); nc = np.bincount(R.bin[cr], minlength=25)
                    R.loc[cr, "w"] = (nt[R.bin[cr]] / np.maximum(nc[R.bin[cr]], 1)) * (nc[R.bin[cr]] > 0)
                rows.append(R)
            print(inst, tf, file=sys.stderr)
    E = pd.concat(rows, ignore_index=True)
    E.drop(columns=[c for c in E.columns if c.startswith("t_")]).to_csv(OUT + "add2_events.csv.gz", index=False)
    res = []
    for tf in ["15m", "1H"]:
        X = E[E.tf == tf].reset_index(drop=True)
        tr = ((X.grp == "TOL") & X.rev).values; cr = ((X.grp == "WICK") & X.rev).values; tn = ((X.grp == "TOL") & ~X.rev).values
        for f in FEATS:
            for cmp_, g2 in [("a: TOL-rev vs WICK-rev(matched)", cr), ("b: TOL-rev vs TOL-not-rev", tn)]:
                pt, lo, hi, p = boot_diff(X, tr, g2, f)
                res.append(dict(tf=tf, feature=f, comparison=cmp_, N1=int(tr.sum()), N2=int(g2.sum()),
                                f1=float(np.average(X[f][tr], weights=X.w[tr])), f2=float(np.average(X[f][g2], weights=X.w[g2])),
                                diff=pt, lo=lo, hi=hi, p=p))
    Rs = pd.DataFrame(res)
    for c in Rs.comparison.unique():
        m = Rs.comparison == c; Rs.loc[m, "p_holm"] = nw.holm(Rs.p[m].values)
    Rs.to_csv(OUT + "add2_features.csv", index=False)
    # stratified by window tertile (comparison a)
    st = []
    for tf in ["15m", "1H"]:
        X = E[(E.tf == tf) & E.rev]; q = np.quantile(X.win_min[X.grp == "TOL"], [1/3, 2/3])
        X = X.assign(tert=np.digitize(X.win_min, q))
        for (t, g), Y in X.groupby(["tert", "grp"]):
            st.append(dict(tf=tf, tertile=int(t), grp=g, N=len(Y), **{f: float(np.average(Y[f], weights=Y.w)) for f in FEATS}))
    pd.DataFrame(st).to_csv(OUT + "add2_features_by_window.csv", index=False)
    # descriptive extras
    ext = []
    for (tf, g, rv), Y in E.groupby(["tf", "grp", "rev"]):
        F = Y[Y.FVG1]; D = Y[Y.DISP]
        ext.append(dict(tf=tf, grp=g, revisited=rv, N=len(Y), CE1_given_FVG1=F.CE1.astype(float).mean() if len(F) else np.nan,
                        OB_retest_given_DISP=D.OB.dropna().astype(float).mean() if len(D) else np.nan,
                        med_window_min=Y.win_min.median()))
    pd.DataFrame(ext).to_csv(OUT + "add2_extras.csv", index=False)
    kzt = E[(E.grp == "TOL") & E.rev].groupby(["tf", "kz_turn"]).size().rename("N_turn").to_frame().join(
        E[(E.grp == "TOL") & E.rev].groupby(["tf", "kz_rev"]).size().rename("N_rev").rename_axis(["tf", "kz_turn"]), how="outer")
    kzt.to_csv(OUT + "add2_killzones.csv")
    sq = []
    for tf in ["15m", "1H"]:
        for g in ["TOL", "WICK"]:
            Y = E[(E.tf == tf) & (E.grp == g) & E.rev]; cnt = Counter(Y.seq)
            for s, n in cnt.most_common(10): sq.append(dict(tf=tf, grp=g, seq=s, n=n, share=n / len(Y)))
    SQ = pd.DataFrame(sq); SQ.to_csv(OUT + "add2_sequences.csv", index=False)
    # charts: first 3 15m TOL revisits by date with modal non-drift sequence, window 30-180 min
    modal = SQ[(SQ.tf == "15m") & (SQ.grp == "TOL") & (SQ.seq != "DRIFT > REV")].iloc[0].seq
    Y = E[(E.tf == "15m") & (E.grp == "TOL") & E.rev & (E.seq == modal) & E.win_min.between(30, 180)].sort_values("t").head(3)
    paths = []
    for n, r in enumerate(Y.itertuples(), 1):
        bid = nw.load(f"{r.inst}_1m_bid")
        t0 = pd.Timestamp(r.t) - pd.Timedelta(minutes=30); t1 = pd.Timestamp(r.close_ns) + pd.Timedelta(minutes=r.win_min + 30)
        x = bid[(bid.index >= t0) & (bid.index <= t1)]
        fig, ax = plt.subplots(figsize=(12, 5))
        for k, (ts, q) in enumerate(x.iterrows()):
            col = "tab:green" if q.Close >= q.Open else "tab:red"
            ax.vlines(k, q.Low, q.High, color=col, lw=.6); ax.add_patch(Rectangle((k - .35, min(q.Open, q.Close)), .7, max(abs(q.Close - q.Open), 1e-3), color=col))
        idx = lambda ts: int(np.searchsorted(x.index.values, np.datetime64(pd.Timestamp(ts))))
        ax.axhline(r.open, color="k", ls="--", lw=1, label=f"no-wick {r.dir} 15m open {r.open:.2f}")
        ax.axhline(r.hi if r.dir == "bull" else r.lo, color="tab:blue", ls=":", lw=1, label="candle opposite extreme")
        ax.axvspan(idx(r.t), idx(r.close_ns) - .5, color="gold", alpha=.2, label="no-wick candle")
        rv = idx(r.close_ns) + r.j - r.a
        ax.axvline(rv, color="purple", lw=1, label="revisit")
        ax.set_title(f"{r.inst} {r.dir} 15m no-wick {pd.Timestamp(r.t):%Y-%m-%d %H:%M} NY | sequence: {r.seq} | features: " +
                     ",".join(f for f in FEATS if getattr(r, f)) + "  (in-sample burned)", fontsize=9)
        ax.set_xticks(range(0, len(x), 15)); ax.set_xticklabels([f"{t:%H:%M}" for t in x.index[::15]], fontsize=7)
        ax.legend(fontsize=7, loc="best"); ax.grid(alpha=.2); fig.tight_layout()
        p = OUT + f"example_{n}.png"; fig.savefig(p, dpi=110); plt.close(fig); paths.append(p)
    print("modal", modal, paths, file=sys.stderr)

if __name__ == "__main__":
    main()
