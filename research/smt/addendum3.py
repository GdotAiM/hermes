"""SMT addendum 3: confluence filters F1-F4 (PREREG Addendum 3). EXPLORATORY, IN-SAMPLE, NOT EVIDENCE."""
import sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "research/smt")
import smt as S
OUT = "research/smt/"; MIN = S.MIN
VARS = {"base": [], "F1": ["F1"], "F2": ["F2"], "F3": ["F3"], "F4": ["F4"], "F1234": ["F1", "F2", "F3", "F4"], "F123": ["F1", "F2", "F3"]}

def f3_meta(M, m=5):
    """mirror of smt.detect pairing (SMT only) -> {(T0, v): f3}"""
    B, idx = S.build_tf(M, m); Tf = idx.values.astype("datetime64[ns]").astype(np.int64); n = len(idx); out = {}
    for v in (1, -1):
        lowV = {i: (B[i].l.values if v == 1 else -B[i].h.values) for i in S.INST}
        sw = {i: S.fractal(lowV[i]) for i in S.INST}; atr = {i: B[i].atr.values for i in S.INST}; used = set()
        for sA in sw["US100"]:
            k = np.searchsorted(sw["US500"], sA); cand = [x for x in sw["US500"][max(k - 2, 0):k + 2] if abs(x - sA) <= 2 and x not in used]
            if not cand: continue
            sB = min(cand, key=lambda x: abs(x - sA)); used.add(sB)
            Sx = {"US100": sA, "US500": sB}; Lv = {i: lowV[i][Sx[i]] for i in S.INST}; a0 = {i: atr[i][min(sA, sB)] for i in S.INST}
            tol = {i: 0.02 * a0[i] for i in S.INST}
            if not all(np.isfinite(tol[i]) for i in S.INST): continue
            c0 = max(sA, sB) + 3; tstar = None
            for t in range(c0, min(c0 + 48, n - 3)):
                if any(lowV[i][t] < Lv[i] - tol[i] for i in S.INST): tstar = t; break
            if tstar is None: continue
            br = {i: (lowV[i][tstar:tstar + 3] < Lv[i] - tol[i]).any() for i in S.INST}
            if br["US100"] == br["US500"]: continue
            lead = "US100" if br["US100"] else "US500"; hold = "US500" if lead == "US100" else "US100"
            ext = {i: lowV[i][tstar:tstar + 3].min() for i in S.INST}
            f3 = (ext[lead] <= Lv[lead] - 0.10 * a0[lead]) and (ext[hold] >= Lv[hold] + 0.05 * a0[hold])
            out[(pd.Timestamp(Tf[tstar + 2] + m * MIN), v)] = f3
    return out

def lon_daily(m1):
    b = m1.b; h = b.index.hour; w = b[(h >= 2) & (h < 5)]
    lr = w.groupby(w.index.date).agg(hi=("High", "max"), lo=("Low", "min")); lr = lr.hi - lr.lo
    return pd.DataFrame({"lr": lr, "med": lr.shift(1).rolling(20, min_periods=20).median(), "q67": lr.shift(1).rolling(20, min_periods=20).quantile(2 / 3)})

def main():
    M = {i: S.M1(i) for i in S.INST}
    E = S.detect(M, 5); E = E[E.kind == "SMT"].reset_index(drop=True); F3 = f3_meta(M)
    LON = {i: lon_daily(M[i]) for i in S.INST}
    DATR = {}
    for i in S.INST:
        g = M[i].b.groupby(M[i].tday).agg(h=("High", "max"), l=("Low", "min")); DATR[i] = (g.h - g.l).rolling(14).mean().shift(1)
    rows = []
    for r in E.itertuples():
        m1 = M[r.inst]; c = S.COST[r.inst]; mr = 4 * (c["spr"] + 2 * c["mkt"]); sd = r.v; V_ = S.LV(m1, sd)
        a, e = int(r.a), int(r.e); T0 = pd.Timestamp(r.T0); ka = a - 1
        if ka < 0 or m1.T[ka] < T0.value - 2 * MIN or e <= a: continue
        lt = T0.hour * 60 + T0.minute; d = T0.date(); lo_ = LON[r.inst]
        if not (570 <= lt < 690) or d not in lo_.index or not np.isfinite(lo_.med.get(d, np.nan)): continue
        base_ok = lo_.lr[d] >= lo_.med[d]; f1 = lo_.lr[d] >= lo_.q67[d]
        if not (base_ok or f1): continue
        f2 = lt < 660; f3 = F3.get((T0, r.v), False)
        i0 = np.searchsorted(m1.T, (T0 - pd.Timedelta(minutes=15)).value)
        buf = max(1.0, c["stop"]) if sd == 1 else max(1.0, c["spr"] + c["stop"])
        seg = V_.BL[i0:ka + 1]; jl = i0 + int(np.argmin(seg)); base_ext = min(r.L, seg.min())
        pv = m1.prev.loc[m1.tday[a]]; pdl = (pv.l if r.v == 1 else -pv.h); dat = DATR[r.inst].get(m1.tday[a], np.nan)
        f4 = bool(np.isfinite(pdl) and np.isfinite(dat) and abs(base_ext - pdl) <= 0.25 * dat)
        k_mss = None
        for k in range(a, e):
            if V_.BL[k] <= base_ext - buf: break
            q = np.searchsorted(V_.swh, k - 3, "right") - 1
            if q < 0 or m1.T[V_.swh[q]] < (T0 - pd.Timedelta(minutes=45)).value: continue
            s = V_.swh[q]
            if V_.BC[k] > V_.BH[s]: k_mss = k; jj = s + int(np.argmin(V_.BL[s:k + 1])); A1 = (V_.BL[jj], V_.BH[jj:k + 1].max()); break
        if k_mss is None: continue
        k = k_mss; ref = V_.BC[k]; fill = V_.EC[k] + c["mkt"]
        st = min(base_ext, V_.BL[i0:k + 1].min()) - buf
        if ref - st < mr: st = ref - mr
        risk = ref - st
        A2 = (base_ext, V_.BH[jl:ka + 1].max())
        for tag, (lo, hi), n, pre in [("A1_SD2.5", A1, 2.5, -np.inf), ("A2_SD2", A2, 2.0, V_.BH[a:k + 1].max())]:
            R = hi - lo; tg = hi + n * R
            if not R > 0 or tg <= ref or pre >= tg: continue
            ex = None
            for j in range(k + 1, e + 1):
                if V_.SL[j] <= st: ex, why = min(st, V_.SO[j]) - c["stop"], "stop"
                elif V_.TH[j] > tg: ex, why = tg - c["lim"], "target"
                if ex is not None: break
            if ex is None: j, why, ex = e, "time", V_.TC[e] - c["mkt"]
            rows.append(dict(exit=tag, inst=r.inst, day=r.day, entry_t=m1.idx[k], exit_t=m1.idx[max(j, k)], R=(ex - fill) / risk, why=why,
                             base=base_ok, F1=f1, F2=f2, F3=f3, F4=f4))
    TR = pd.DataFrame(rows); TR.to_csv(OUT + "addendum3_trades.csv", index=False)
    res, curves = [], {}
    for ex_tag in ["A1_SD2.5", "A2_SD2"]:
        for vn, fl in VARS.items():
            sel = TR[TR.exit == ex_tag]
            sel = sel[sel.F1] if "F1" in fl else sel[sel.base]
            for f in fl:
                if f != "F1": sel = sel[sel[f]]
            for scope in ["pooled"] + S.INST:
                X = sel if scope == "pooled" else sel[sel.inst == scope]
                if len(X) < 2: res.append(dict(exit=ex_tag, variant=vn, scope=scope, N=len(X))); continue
                lo_, hi_, se, p = S.boot(X)
                r = dict(exit=ex_tag, variant=vn, scope=scope, N=len(X), underpowered=len(X) < 100, win=(X.R > 0).mean(), avg_win=X.R[X.R > 0].mean(),
                         avg_loss=X.R[X.R <= 0].mean(), meanR=X.R.mean(), sd=X.R.std(), lo=lo_, hi=hi_, se=se, p_one=p, haircutR=X.R.mean() - 1.352 * se)
                if scope == "pooled":
                    for halt in (True, False):
                        n_, cv, h, mdd = S.book(X, halt); tag = "halted" if halt else "unhalted"
                        r |= {f"N_book_{tag}": n_, f"final_{tag}": cv["eq"].iloc[-1], f"maxDD_{tag}": mdd}
                        if halt: r["halted_at"] = h
                        elif ex_tag == "A1_SD2.5": curves[vn] = cv
                    # design effect
                    days = X.day.nunique(); se_iid = X.R.std() / np.sqrt(len(X)); r["DE"] = (se / se_iid) ** 2; r["trades_per_year"] = len(X) / (395 / 365.25)
                res.append(r)
    R = pd.DataFrame(res)
    for ex_tag in ["A1_SD2.5", "A2_SD2"]:
        m = (R.exit == ex_tag) & (R.scope == "pooled") & R.p_one.notna(); R.loc[m, "p_holm"] = S.holm(R.p_one[m].values)
        for vn in VARS:
            sub = R[(R.exit == ex_tag) & (R.variant == vn) & (R.scope != "pooled") & R.meanR.notna()]
            R.loc[(R.exit == ex_tag) & (R.variant == vn) & (R.scope == "pooled"), "same_sign"] = bool(len(sub) == 2 and np.sign(sub.meanR).nunique() == 1)
    m = R.scope == "pooled"
    R.loc[m, "forward_worthy"] = (R.p_holm[m] < .05) & (R.haircutR[m] > 0) & (R.same_sign[m] == True) & (R.maxDD_unhalted[m] < .2)
    R.to_csv(OUT + "addendum3_results.csv", index=False)
    pd.set_option("display.width", 400); print(R.to_string(float_format=lambda z: f"{z:.4f}"))
    P = R[(R.exit == "A1_SD2.5") & m & (R.N >= 100) & (R.same_sign == True)].sort_values("haircutR", ascending=False)
    if len(P):
        b = P.iloc[0]; delta = b.meanR / 2; n_iid = ((1.645 + 0.842) * b.sd / delta) ** 2; nreq = n_iid * b.DE
        print(f"\nCANDIDATE {b.variant}: meanR {b.meanR:.4f} sd {b.sd:.3f} DE {b.DE:.2f} delta {delta:.4f} N_req {nreq:.0f} rate/yr {b.trades_per_year:.0f} years {nreq / b.trades_per_year:.1f}")
    fig, ax = plt.subplots(figsize=(11, 5))
    for v, cv in curves.items(): ax.step(cv.t, cv["eq"], where="post", label=v, lw=1.4 if v == "base" else 1)
    ax.axhline(1e4, c="k", lw=.5); ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_ylabel("equity $ (unhalted)")
    ax.set_title("SMT Addendum 3: confluence filters on NY AM SMT + MSS, A1 -2.5 exit. IN-SAMPLE burned (~50 variants tried), NOT EVIDENCE", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT + "addendum3_equity.png", dpi=105)

if __name__ == "__main__":
    main()
