"""SMT addendum 2: ICT intraday SD projections (PREREG Addendum 2; anchors are OUR assumption). EXPLORATORY, IN-SAMPLE, NOT EVIDENCE."""
import sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "research/smt")
import smt as S
from addendum1 import london
OUT = "research/smt/"; MIN = S.MIN; NS = [2.0, 2.5]
V = [f"{a}_{t}" for a in ["A1", "A2"] for t in ["SD1", "SD2", "SD2.5", "P1_2.5"]]

def lvl_stats(V_, j0, e, level, R):
    """reach / reverse|reach / turn|reach on long-view arrays from bar j0+1..e"""
    w = V_.BH[j0 + 1:e + 1] >= level
    if not w.any(): return 0, np.nan, np.nan
    t = j0 + 1 + int(np.argmax(w)); dn = V_.BL[t:e + 1] <= level - 0.5 * R; up = V_.BH[t:e + 1] >= level + 0.5 * R
    idn = int(np.argmax(dn)) if dn.any() else 10**9; iup = int(np.argmax(up)) if up.any() else 10**9
    return 1, float(idn < iup), float(V_.BH[t:e + 1].max() <= level + 0.25 * R)

def main():
    M = {i: S.M1(i) for i in S.INST}; rng = np.random.default_rng(S.SEED)
    E = S.detect(M, 5); E = E[E.kind == "SMT"].reset_index(drop=True)
    LON = {i: london(M[i]) for i in S.INST}
    hours = {i: pd.Series(np.arange(len(M[i].T))).groupby(M[i].idx.hour).apply(np.array).to_dict() for i in S.INST}
    desc, trades = [], []
    for r in E.itertuples():
        m1 = M[r.inst]; c = S.COST[r.inst]; mr = 4 * (c["spr"] + 2 * c["mkt"]); sd = r.v; V_ = S.LV(m1, sd)
        a, e = int(r.a), int(r.e); T0 = pd.Timestamp(r.T0); ka = a - 1
        if ka < 0 or m1.T[ka] < T0.value - 2 * MIN or e <= a: continue
        i0 = np.searchsorted(m1.T, (T0 - pd.Timedelta(minutes=15)).value)
        buf = max(1.0, c["stop"]) if sd == 1 else max(1.0, c["spr"] + c["stop"])
        seg = V_.BL[i0:ka + 1]; jl = i0 + int(np.argmin(seg)); base_ext = min(r.L, seg.min())
        anchors = {"A2": (ka, base_ext, V_.BH[jl:ka + 1].max())}
        k_mss = None
        for k in range(a, e):
            if V_.BL[k] <= base_ext - buf: break
            q = np.searchsorted(V_.swh, k - 3, "right") - 1
            if q < 0 or m1.T[V_.swh[q]] < (T0 - pd.Timedelta(minutes=45)).value: continue
            s = V_.swh[q]
            if V_.BC[k] > V_.BH[s]:
                k_mss = k; jj = s + int(np.argmin(V_.BL[s:k + 1])); anchors["A1"] = (k, V_.BL[jj], V_.BH[jj:k + 1].max()); break
        for an, (j0, lo, hi) in anchors.items():
            R = hi - lo
            if not R > 0 or j0 >= e: continue
            H = e - j0
            for n in NS:
                lv = hi + n * R; dist = lv - V_.BC[j0]
                rec = dict(inst=r.inst, day=r.day, anchor=an, n=n, R=R)
                rch, rv, tn = lvl_stats(V_, j0, e, lv, R); desc.append(rec | dict(kind="SD", reach=rch, rev=rv, turn=tn))
                ms = []
                while len(ms) < 10:
                    x = rng.uniform(1.5, 3.0)
                    if min(abs(x - 2), abs(x - 2.5)) >= 0.1: ms.append(x)
                for x in ms:
                    rch, rv, tn = lvl_stats(V_, j0, e, hi + x * R, R); desc.append(rec | dict(kind="C1", reach=rch, rev=rv, turn=tn))
                pool = hours[r.inst][m1.idx[j0].hour]
                for _ in range(20):
                    j2 = int(rng.choice(pool))
                    if m1.tday[j2] != m1.tday[j0] and j2 + H <= m1.dend[j2]: break
                else: continue
                rch, rv, tn = lvl_stats(V_, j2, j2 + H, V_.BC[j2] + dist, R); desc.append(rec | dict(kind="C2", reach=rch, rev=rv, turn=tn))
        # check 2: filtered MSS trades
        lt = T0.hour * 60 + T0.minute; d = T0.date(); lo_ = LON[r.inst]
        F = (570 <= lt < 690) and d in lo_.index and np.isfinite(lo_.med.get(d, np.nan)) and lo_.lr[d] >= lo_.med[d]
        if not F or k_mss is None: continue
        k = k_mss; ref = V_.BC[k]; fill = V_.EC[k] + c["mkt"]
        st = min(base_ext, V_.BL[i0:k + 1].min()) - buf
        if ref - st < mr: st = ref - mr
        risk = ref - st
        def sim(tg):
            ex = None
            for j in range(k + 1, e + 1):
                if V_.SL[j] <= st: ex, why = min(st, V_.SO[j]) - c["stop"], "stop"
                elif V_.TH[j] > tg: ex, why = tg - c["lim"], "target"
                if ex is not None: break
            if ex is None: j, why, ex = e, "time", V_.TC[e] - c["mkt"]
            return (ex - fill) / risk, j, why
        for an, (j0, lo, hi) in anchors.items():
            R = hi - lo
            if not R > 0: continue
            L = {n: hi + n * R for n in (1, 2, 2.5)}
            pre = V_.BH[a:k + 1].max() if an == "A2" else -np.inf
            base = dict(inst=r.inst, day=r.day, side="long" if sd == 1 else "short", entry_t=m1.idx[k], widened=abs(risk - mr) < 1e-9)
            for n, tn in [(1, "SD1"), (2, "SD2"), (2.5, "SD2.5")]:
                if L[n] <= ref or pre >= L[n]: continue
                R_, j, why = sim(L[n]); trades.append(base | dict(var=f"{an}_{tn}", R=R_, exit_t=m1.idx[max(j, k)], why=why))
            if L[1] > ref and pre < L[1]:
                r1, j1, w1 = sim(L[1]); r2, j2, w2 = sim(L[2.5])
                trades.append(base | dict(var=f"{an}_P1_2.5", R=(r1 + r2) / 2, exit_t=m1.idx[max(j1, j2, k)], why=w2))
    D = pd.DataFrame(desc); D.to_csv(OUT + "addendum2_levels.csv.gz", index=False)
    drow = []
    for (an, n), G in D.groupby(["anchor", "n"]):
        for scope in ["pooled"] + S.INST:
            X = G if scope == "pooled" else G[G.inst == scope]
            row = dict(anchor=an, n=n, scope=scope, N_events=int((X.kind == "SD").sum()))
            for k_ in ["SD", "C1", "C2"]: row[f"reach_{k_}"] = X[X.kind == k_].reach.mean()
            Y = X[X.reach == 1].reset_index(drop=True)
            for met in ["rev", "turn"]:
                for k_ in ["SD", "C1", "C2"]: row[f"{met}_{k_}"] = Y[Y.kind == k_][met].mean()
                for ctl in ["C1", "C2"]:
                    dd, lo, hi = S.bootdiff(Y, (Y.kind == "SD").values, (Y.kind == ctl).values, met)
                    row[f"d_{met}_vs_{ctl}"], row[f"lo_{met}_{ctl}"], row[f"hi_{met}_{ctl}"] = dd, lo, hi
            drow.append(row)
    DS = pd.DataFrame(drow); DS.to_csv(OUT + "addendum2_descriptive.csv", index=False)
    TR = pd.DataFrame(trades); TR.to_csv(OUT + "addendum2_trades.csv", index=False)
    res, curves = [], {}
    for v in V:
        for scope in ["pooled"] + S.INST:
            X = TR[(TR["var"] == v) & ((TR.inst == scope) if scope != "pooled" else True)]
            if len(X) < 2: continue
            lo_, hi_, se, p = S.boot(X)
            r = dict(variant=v, scope=scope, N=len(X), win=(X.R > 0).mean(), avg_win=X.R[X.R > 0].mean(), avg_loss=X.R[X.R <= 0].mean(), meanR=X.R.mean(),
                     lo=lo_, hi=hi_, p_one=p, haircutR=X.R.mean() - 1.424 * se, widened=X.widened.mean())
            if scope == "pooled":
                for halt in (True, False):
                    n_, cv, h, mdd = S.book(X, halt); tag = "halted" if halt else "unhalted"
                    r |= {f"N_book_{tag}": n_, f"final_{tag}": cv["eq"].iloc[-1], f"maxDD_{tag}": mdd}
                    if halt: r["halted_at"] = h
                    else: curves[v] = cv
            res.append(r)
    R = pd.DataFrame(res); m = R.scope == "pooled"; R.loc[m, "p_holm"] = S.holm(R.p_one[m].values)
    for v in V:
        sub = R[(R.variant == v) & (R.scope != "pooled")]
        R.loc[(R.variant == v) & m, "same_sign"] = bool(len(sub) == 2 and np.sign(sub.meanR).nunique() == 1)
    R.loc[m, "forward_worthy"] = (R.p_holm[m] < .05) & (R.haircutR[m] > 0) & (R.same_sign[m] == True) & (R.maxDD_unhalted[m] < .2)
    R.to_csv(OUT + "addendum2_results.csv", index=False)
    pd.set_option("display.width", 400)
    print(DS.to_string(float_format=lambda z: f"{z:.3f}")); print(); print(R.to_string(float_format=lambda z: f"{z:.4f}"))
    print(TR.groupby(["var", "why"]).size().unstack())
    fig, ax = plt.subplots(figsize=(11, 5))
    for v, cv in curves.items(): ax.step(cv.t, cv["eq"], where="post", label=v)
    ax.axhline(1e4, c="k", lw=.5); ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_ylabel("equity $ (unhalted)")
    ax.set_title("SMT Addendum 2: filtered MSS entry, ICT SD-projection exits (anchors assumed). IN-SAMPLE burned, NOT EVIDENCE", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT + "addendum2_equity.png", dpi=105)

if __name__ == "__main__":
    main()
