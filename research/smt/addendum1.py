"""SMT addendum 1: first leg toward opposite liquidity + London-vol filter (PREREG Addendum 1). EXPLORATORY, IN-SAMPLE, NOT EVIDENCE."""
import sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "research/smt")
import smt as S
OUT = "research/smt/"; MIN = S.MIN
V = ["F_SMT_int", "F_SMT_ext", "F_MSS_int", "F_MSS_ext", "U_SMT_int", "F_SMT_scaled"]

def london(m1):
    b = m1.b; h = b.index.hour; w = b[(h >= 2) & (h < 5)]
    lr = w.groupby(w.index.date).agg(hi=("High", "max"), lo=("Low", "min")); lr = (lr.hi - lr.lo)
    return pd.DataFrame({"lr": lr, "med": lr.shift(1).rolling(20, min_periods=20).median()})

def main():
    M = {i: S.M1(i) for i in S.INST}
    E = S.detect(M, 5); E = E[E.kind == "SMT"].reset_index(drop=True)
    LON = {i: london(M[i]) for i in S.INST}
    rows = []
    for r in E.itertuples():
        m1 = M[r.inst]; c = S.COST[r.inst]; mr = 4 * (c["spr"] + 2 * c["mkt"]); sd = r.v; V_ = S.LV(m1, sd)
        a, e = int(r.a), int(r.e); T0 = pd.Timestamp(r.T0); ka = a - 1
        if ka < 0 or m1.T[ka] < T0.value - 2 * MIN or e <= a: continue
        i0 = np.searchsorted(m1.T, (T0 - pd.Timedelta(minutes=15)).value)
        buf = max(1.0, c["stop"]) if sd == 1 else max(1.0, c["spr"] + c["stop"])
        lt = T0.hour * 60 + T0.minute; d = T0.date(); lo = LON[r.inst]
        F = (570 <= lt < 690) and d in lo.index and np.isfinite(lo.med.get(d, np.nan)) and lo.lr[d] >= lo.med[d]
        LR = lo.lr.get(d, np.nan)
        base_ext = min(r.L, V_.BL[i0:ka + 1].min())
        def sim(k, fill, ref, st, tg, x0):
            ex = None
            for j in range(x0, e + 1):
                if V_.SL[j] <= st: ex, why = min(st, V_.SO[j]) - c["stop"], "stop"
                elif V_.TH[j] > tg: ex, why = tg - c["lim"], "target"
                if ex is not None: break
            if ex is None: j, why, ex = e, "time", V_.TC[e] - c["mkt"]
            return dict(inst=r.inst, day=r.day, side="long" if sd == 1 else "short", entry_t=m1.idx[k], exit_t=m1.idx[max(j, k)],
                        R=(ex - fill) / (ref - st), why=why, widened=abs((ref - st) - mr) < 1e-9, filt=F, T0=T0)
        # SMT-close entry
        k = ka; ref = V_.BC[k]; fill = V_.EC[k] + c["mkt"]
        st0 = base_ext - buf
        if ref - st0 < mr: st0 = ref - mr
        for tn, tg in [("int", r.internal), ("ext", r.external)]:
            if np.isfinite(tg) and tg > ref:
                t = sim(k, fill, ref, st0, tg, k + 1)
                if F: rows.append(t | {"var": f"F_SMT_{tn}"})
                if tn == "int": rows.append(t | {"var": "U_SMT_int"})
        if F and np.isfinite(LR):
            sdist = max(0.25 * LR, mr); rows.append(sim(k, fill, ref, ref - sdist, ref + 2 * sdist, k + 1) | {"var": "F_SMT_scaled"})
        # MSS entry
        if F:
            for tn, tg in [("int", r.internal), ("ext", r.external)]:
                if not np.isfinite(tg): continue
                stl = base_ext - buf
                for k in range(a, e):
                    if V_.BL[k] <= stl or V_.BH[k] >= tg: break
                    q = np.searchsorted(V_.swh, k - 3, "right") - 1
                    if q < 0 or m1.T[V_.swh[q]] < (T0 - pd.Timedelta(minutes=45)).value: continue
                    if V_.BC[k] > V_.BH[V_.swh[q]]:
                        ref = V_.BC[k]
                        if tg <= ref: break
                        st = min(base_ext, V_.BL[i0:k + 1].min()) - buf
                        if ref - st < mr: st = ref - mr
                        rows.append(sim(k, V_.EC[k] + c["mkt"], ref, st, tg, k + 1) | {"var": f"F_MSS_{tn}"}); break
    TR = pd.DataFrame(rows); TR.to_csv(OUT + "addendum1_trades.csv", index=False)
    res, curves = [], {}
    for v in V:
        for scope in ["pooled"] + S.INST:
            X = TR[(TR["var"] == v) & ((TR.inst == scope) if scope != "pooled" else True)]
            if len(X) < 2: continue
            lo_, hi_, se, p = S.boot(X)
            r = dict(variant=v, scope=scope, N=len(X), win=(X.R > 0).mean(), avg_win=X.R[X.R > 0].mean(), avg_loss=X.R[X.R <= 0].mean(), meanR=X.R.mean(),
                     lo=lo_, hi=hi_, p_one=p, haircutR=X.R.mean() - 1.267 * se, widened=X.widened.mean())
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
    R.to_csv(OUT + "addendum1_results.csv", index=False)
    pd.set_option("display.width", 320); print(R.to_string(float_format=lambda z: f"{z:.4f}"))
    print(TR.groupby(["var", "why"]).size().unstack())
    fig, ax = plt.subplots(figsize=(11, 5))
    for v, cv in curves.items(): ax.step(cv.t, cv["eq"], where="post", label=v)
    ax.axhline(1e4, c="k", lw=.5); ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_ylabel("equity $ (unhalted)")
    ax.set_title("SMT Addendum 1: first leg to opposite liquidity, London-vol filter. IN-SAMPLE burned, EXPLORATORY, NOT EVIDENCE", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT + "addendum1_equity.png", dpi=105)

if __name__ == "__main__":
    main()
