"""SMT divergence study (see PREREG.md). EXPLORATORY, IN-SAMPLE burned window, NOT EVIDENCE."""
import gzip, hashlib, io, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
DATA = "/workspace/ftn-demo-output/data"; OUT = "research/smt/"
SHA = {"US100_1m_bid": "6afa3130", "US100_1m_ask": "fcc3c877", "US500_1m_bid": "9d68787c", "US500_1m_ask": "ff63783f"}
END = pd.Timestamp("2026-09-25 16:15"); START = pd.Timestamp("2025-08-24 18:00")
COST = {"US100": dict(spr=1.55, stop=0.50, mkt=0.50, lim=0.25), "US500": dict(spr=0.72, stop=0.25, mkt=0.25, lim=0.10)}
MIN = 60_000_000_000; NB = 2000; SEED = 20261012; INST = ["US100", "US500"]; V = ["MSS_R1", "MSS_CE", "FVG_R1", "FVG_CE"]

def load(f):
    raw = gzip.open(f"{DATA}/{f}.csv.gz").read(); assert hashlib.sha256(raw).hexdigest().startswith(SHA[f]), f
    df = pd.read_csv(io.BytesIO(raw)); t = pd.to_datetime(df.Datetime, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    df.index = t; df = df.drop(columns="Datetime"); df = df[(df.index >= START) & (df.index < END)]; assert df.index.max() < END
    return df

def fractal(x):  # local minima, 2 each side
    m = np.zeros(len(x), bool); m[2:-2] = (x[2:-2] < x[1:-3]) & (x[2:-2] < x[:-4]) & (x[2:-2] < x[3:-1]) & (x[2:-2] < x[4:])
    return np.where(m)[0]

class M1:
    def __init__(s, inst):
        b, a = load(f"{inst}_1m_bid"), load(f"{inst}_1m_ask"); a = a.reindex(b.index).ffill()
        s.inst, s.idx = inst, b.index; s.T = b.index.values.astype("datetime64[ns]").astype(np.int64)
        s.O, s.H, s.L, s.C = (b[x].values for x in ["Open", "High", "Low", "Close"]); s.AO, s.AH, s.AL, s.AC = (a[x].values for x in ["Open", "High", "Low", "Close"])
        s.tday = np.array((b.index + pd.Timedelta(hours=6)).date)
        s.dend = pd.Series(np.arange(len(s.T))).groupby(s.tday).transform("max").values
        s.dstart = pd.Series(np.arange(len(s.T))).groupby(s.tday).transform("min").values
        dd = b.groupby(s.tday).agg(h=("High", "max"), l=("Low", "min")); s.prev = dd.shift(1)
        s.b = b
    def view(s, v):  # SMT view: v=1 lows-SMT as is; v=-1 negate (highs become lows)
        return (s.H, s.L) if v == 1 else (-s.L, -s.H)

def tfbars(m1, m):
    g = m1.b.groupby(m1.b.index.floor(f"{m}min"))
    B = pd.DataFrame({"o": g.Open.first(), "h": g.High.max(), "l": g.Low.min(), "c": g.Close.last(), "n": g.Open.size()})
    B = B[B.n >= m / 2]; pc = B.c.shift(1)
    tr = np.maximum(B.h - B.l, np.maximum((B.h - pc).abs(), (B.l - pc).abs())); B["atr"] = tr.shift(1).rolling(14).mean()
    return B

def build_tf(M, m):
    B = {i: tfbars(M[i], m) for i in INST}; idx = B[INST[0]].index.intersection(B[INST[1]].index)
    return {i: B[i].loc[idx] for i in INST}, idx

def measure(m1, v, L, T0, tfB, tfidx, tstar, m):
    """steps on one instrument in SMT view v. returns dict (view prices)."""
    Hv, Lv = m1.view(v); a = np.searchsorted(m1.T, T0)
    if a >= len(m1.T): return None
    e = min(np.searchsorted(m1.T, T0 + 8 * 60 * MIN) - 1, m1.dend[a])
    if e <= a: return None
    c0 = (m1.C[a - 1] if v == 1 else -m1.C[a - 1])
    hiV = tfB.h.values if v == 1 else -tfB.l.values
    sh = fractal(-hiV); sh = sh[(sh + 2 <= tstar + 2) & (sh >= tstar + 2 - 48)]
    lv = hiV[sh]; lv = lv[lv > c0]; internal = lv.min() if len(lv) else np.nan
    pv = m1.prev.loc[m1.tday[a]]; pdh = (pv.h if v == 1 else -pv.l) if np.isfinite(pv.h) else np.nan
    dsh = Hv[m1.dstart[a]:a].max() if a > m1.dstart[a] else np.nan
    ext = [x for x in (pdh, dsh) if np.isfinite(x) and x > c0]; external = min(ext) if ext else np.nan
    def first(cond_arr, j0):
        if j0 > e: return None
        w = cond_arr[j0:e + 1]; return j0 + int(np.argmax(w)) if w.any() else None
    r = dict(a=a, e=e, L=L, internal=internal, external=external, ki=None, ke=None, r1=None, r2=None)
    if np.isfinite(internal):
        r["ki"] = first(Hv > internal, a)
        if r["ki"] is not None:
            r["r1"] = first(Lv <= L, r["ki"] + 1); r["r2"] = first(Lv <= (L + internal) / 2, r["ki"] + 1)
    if np.isfinite(external): r["ke"] = first(Hv > external, a)
    return r

def detect(M, m):
    B, idx = build_tf(M, m); Tf = idx.values.astype("datetime64[ns]").astype(np.int64); n = len(idx)
    ev = []
    for v in (1, -1):
        lowV = {i: (B[i].l.values if v == 1 else -B[i].h.values) for i in INST}
        sw = {i: fractal(lowV[i]) for i in INST}; atr = {i: B[i].atr.values for i in INST}
        used = set()
        for sA in sw["US100"]:
            k = np.searchsorted(sw["US500"], sA); cand = [x for x in sw["US500"][max(k - 2, 0):k + 2] if abs(x - sA) <= 2 and x not in used]
            if not cand: continue
            sB = min(cand, key=lambda x: abs(x - sA)); used.add(sB)
            S = {"US100": sA, "US500": sB}; Lv = {i: lowV[i][S[i]] for i in INST}; tol = {i: 0.02 * atr[i][min(sA, sB)] for i in INST}
            if not all(np.isfinite(tol[i]) for i in INST): continue
            c0 = max(sA, sB) + 3; tstar = None
            for t in range(c0, min(c0 + 48, n - 3)):
                if any(lowV[i][t] < Lv[i] - tol[i] for i in INST): tstar = t; break
            if tstar is None: continue
            br = {i: (lowV[i][tstar:tstar + 3] < Lv[i] - tol[i]).any() for i in INST}
            kind = "SMT" if br["US100"] != br["US500"] else "BOTH"
            T0 = Tf[tstar + 2] + m * MIN
            for i in INST:
                r = measure(M[i], v, Lv[i], T0, B[i], idx, tstar, m)
                if r is None: continue
                ev.append(dict(tf=f"{m}m", kind=kind, v=v, inst=i, leader=[j for j in INST if br[j]][0] if kind == "SMT" else "both",
                               T0=pd.Timestamp(T0), day=M[i].tday[r["a"]], sA=idx[sA], **r))
        # null 2: every single-instrument swing break
        for i in INST:
            for s in sw[i]:
                L = lowV[i][s]; tl = 0.02 * atr[i][s]
                if not np.isfinite(tl): continue
                w = lowV[i][s + 3:min(s + 51, n - 3)] < L - tl
                if not w.any(): continue
                tstar = s + 3 + int(np.argmax(w)); T0 = Tf[tstar + 2] + m * MIN
                r = measure(M[i], v, L, T0, B[i], idx, tstar, m)
                if r is None: continue
                ev.append(dict(tf=f"{m}m", kind="RANDOM", v=v, inst=i, leader=i, T0=pd.Timestamp(T0), day=M[i].tday[r["a"]], sA=idx[s], **r))
    return pd.DataFrame(ev)

def bootdiff(E, g1, g2, col):
    days = pd.Index(sorted(E.day.unique())); di = days.get_indexer(E.day); D = len(days); y = E[col].values * 1.
    arr = [(np.bincount(di[g], y[g], D), np.bincount(di[g], minlength=D) * 1.) for g in (g1, g2)]
    rng = np.random.default_rng(SEED); W = rng.multinomial(D, np.ones(D) / D, size=NB)
    bs = W @ arr[0][0] / (W @ arr[0][1]) - W @ arr[1][0] / (W @ arr[1][1])
    return y[g1].mean() - y[g2].mean(), np.quantile(bs, .025), np.quantile(bs, .975)

# ---------------- trades ----------------
class LV:
    """long view for trade side sd (as NOWICK addendum 6)."""
    def __init__(s, m1, sd):
        if sd == 1: s.BH, s.BL, s.BC, s.EC, s.SL, s.SO, s.TH, s.TC, s.LF = m1.H, m1.L, m1.C, m1.AC, m1.L, m1.O, m1.H, m1.C, m1.AL
        else: s.BH, s.BL, s.BC, s.EC, s.SL, s.SO, s.TH, s.TC, s.LF = -m1.L, -m1.H, -m1.C, -m1.C, -m1.AH, -m1.AO, -m1.AL, -m1.AC, -m1.H
        s.swh = fractal(-s.BH)

def trades(E, M):
    out = []; views = {(i, sd): LV(M[i], sd) for i in INST for sd in (1, -1)}
    for r in E[(E.kind == "SMT") & (E.tf == "5m") & E.ki.notna()].itertuples():
        m1 = M[r.inst]; c = COST[r.inst]; mr = 4 * (c["spr"] + 2 * c["mkt"]); sd = -r.v; V_ = views[(r.inst, sd)]
        tk, e = int(r.ki), int(r.e); buf = max(1.0, c["stop"]) if sd == 1 else max(1.0, c["spr"] + c["stop"])
        for tn, tgt in [("R1", -r.L), ("CE", -(r.L + r.internal) / 2)]:
            hit = V_.BH[tk:e + 1] >= tgt; lim = tk + int(np.argmax(hit)) if hit.any() else e
            ents = {}
            for k in range(tk, lim):
                q = np.searchsorted(V_.swh, k - 3, "right") - 1
                if q < 0 or m1.T[V_.swh[q]] < m1.T[tk] - 30 * MIN: continue
                if V_.BC[k] > V_.BH[V_.swh[q]]: ents["MSS"] = (k, V_.EC[k] + c["mkt"], V_.BC[k], k + 1); break
            for g in range(tk + 2, lim):
                if V_.BH[g - 2] < V_.BL[g]:
                    ce = (V_.BH[g - 2] + V_.BL[g]) / 2
                    for mm in range(g + 1, lim):
                        if V_.LF[mm] <= ce: ents["FVG"] = (mm, ce + c["lim"], ce, mm); break
                    break
            for en, (k, fill, ref, x0) in ents.items():
                if ref >= tgt: continue
                st = V_.BL[tk:k + 1].min() - buf
                if ref - st < mr: st = ref - mr
                risk = ref - st; ex = None
                for j in range(x0, e + 1):
                    if V_.SL[j] <= st: ex, why = min(st, V_.SO[j]) - c["stop"], "stop"
                    elif V_.TH[j] > tgt: ex, why = tgt - c["lim"], "target"
                    if ex is not None: break
                if ex is None: j, why, ex = e, "time", V_.TC[e] - c["mkt"]
                out.append(dict(var=f"{en}_{tn}", inst=r.inst, day=r.day, side="long" if sd == 1 else "short", entry_t=m1.idx[k], exit_t=m1.idx[max(j, k)],
                                R=(ex - fill) / risk, why=why, widened=abs(risk - mr) < 1e-9))
    return pd.DataFrame(out)

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
    M = {i: M1(i) for i in INST}
    E = pd.concat([detect(M, 5), detect(M, 15)], ignore_index=True)
    for c in ["ki", "ke", "r1", "r2"]: E[f"has_{c}"] = E[c].notna()
    E["seq"] = E.has_ki & E.has_r1
    E["min_T0_ki"] = (E.ki - E.a); E["min_ki_r1"] = (E.r1 - E.ki)  # 1m bars ~ minutes
    E.to_csv(OUT + "events.csv.gz", index=False)
    rows = []
    for (tf, kind, inst), G in E.groupby(["tf", "kind", "inst"]):
        rows.append(dict(tf=tf, kind=kind, inst=inst, N=len(G), P_2i=G.has_ki.mean(), P_2e=G.has_ke.mean(), P_R1_given_2i=G[G.has_ki].has_r1.mean(),
                         P_R2_given_2i=G[G.has_ki].has_r2.mean(), P_seq=G.seq.mean(), med_min_T0_2i=G.min_T0_ki.median(), med_min_2i_R1=G.min_ki_r1.median(),
                         no_internal=G.internal.isna().mean()))
    D = pd.DataFrame(rows); D.to_csv(OUT + "descriptive.csv", index=False)
    eff = []
    for tf in ["5m", "15m"]:
        for scope in ["pooled"] + INST:
            X = E[(E.tf == tf) & ((E.inst == scope) if scope != "pooled" else True)].reset_index(drop=True)
            for null in ["BOTH", "RANDOM"]:
                for col in ["seq", "has_ki", "has_r1"]:
                    if col == "has_r1":
                        Y = X[X.has_ki].reset_index(drop=True); d, lo, hi = bootdiff(Y, (Y.kind == "SMT").values, (Y.kind == null).values, col)
                    else: d, lo, hi = bootdiff(X, (X.kind == "SMT").values, (X.kind == null).values, col)
                    eff.append(dict(tf=tf, scope=scope, vs=null, metric={"seq": "P(2i & R1)", "has_ki": "P(2i)", "has_r1": "P(R1|2i)"}[col], diff=d, lo=lo, hi=hi))
    EF = pd.DataFrame(eff); EF.to_csv(OUT + "effects.csv", index=False)
    TR = trades(E, M); TR.to_csv(OUT + "trades.csv", index=False)
    res, curves = [], {}
    for v in V:
        for scope in ["pooled"] + INST:
            S = TR[(TR["var"] == v) & ((TR.inst == scope) if scope != "pooled" else True)]
            if len(S) < 2: continue
            lo, hi, se, p = boot(S)
            r = dict(variant=v, scope=scope, N=len(S), win=(S.R > 0).mean(), avg_win=S.R[S.R > 0].mean(), avg_loss=S.R[S.R <= 0].mean(), meanR=S.R.mean(),
                     lo=lo, hi=hi, p_one=p, haircutR=S.R.mean() - 1.029 * se, widened=S.widened.mean())
            if scope == "pooled":
                for halt in (True, False):
                    n_, cv, h, mdd = book(S, halt); tag = "halted" if halt else "unhalted"
                    r |= {f"N_book_{tag}": n_, f"final_{tag}": cv["eq"].iloc[-1], f"maxDD_{tag}": mdd}
                    if halt: r["halted_at"] = h
                    else: curves[v] = cv
            res.append(r)
    R = pd.DataFrame(res); m = R.scope == "pooled"; R.loc[m, "p_holm"] = holm(R.p_one[m].values)
    for v in V:
        sub = R[(R.variant == v) & (R.scope != "pooled")]
        R.loc[(R.variant == v) & m, "same_sign"] = bool(len(sub) == 2 and np.sign(sub.meanR).nunique() == 1)
    R.loc[m, "forward_worthy"] = (R.p_holm[m] < .05) & (R.haircutR[m] > 0) & (R.same_sign[m] == True) & (R.maxDD_unhalted[m] < .2)
    R.to_csv(OUT + "results.csv", index=False)
    pd.set_option("display.width", 320)
    for x in (D, EF, R): print(x.to_string(float_format=lambda z: f"{z:.4f}")); print()
    print(TR.groupby(["var", "why"]).size().unstack())
    # plots
    fig, axs = plt.subplots(1, 2, figsize=(14, 5))
    for ax, tf in zip(axs, ["5m", "15m"]):
        X = D[D.tf == tf]; mets = ["P_2i", "P_2e", "P_R1_given_2i", "P_seq"]; w = 0.13; k = 0
        for kind in ["SMT", "BOTH", "RANDOM"]:
            for inst in INST:
                y = X[(X.kind == kind) & (X.inst == inst)][mets].values[0]; ax.bar(np.arange(4) + k * w, y, w, label=f"{kind} {inst}"); k += 1
        ax.set_xticks(np.arange(4) + 2.5 * w); ax.set_xticklabels(["P(2i internal)", "P(2e external)", "P(R1 | 2i)", "P(2i & R1)"]); ax.set_title(f"{tf} swings"); ax.set_ylim(0, 1); ax.grid(alpha=.3, axis="y")
    axs[0].legend(fontsize=7); fig.suptitle("SMT step rates vs nulls (US100/US500, burned window, descriptive, NOT evidence)", fontsize=9); fig.tight_layout(); fig.savefig(OUT + "smt_rates.png", dpi=105)
    fig, ax = plt.subplots(figsize=(11, 5))
    for v, cv in curves.items(): ax.step(cv.t, cv["eq"], where="post", label=v)
    ax.axhline(1e4, c="k", lw=.5); ax.legend(); ax.grid(alpha=.3); ax.set_ylabel("equity $ (unhalted)")
    ax.set_title("SMT trade variants, $10k unhalted books (5m SMT, US100+US500). IN-SAMPLE burned, EXPLORATORY, NOT EVIDENCE", fontsize=9); fig.tight_layout(); fig.savefig(OUT + "equity.png", dpi=105)
    X = E[(E.tf == "5m") & (E.kind == "SMT") & (E.inst == "US100") & E.seq].sort_values("T0").head(3)
    for n, r in enumerate(X.itertuples(), 1):
        t0 = pd.Timestamp(r.sA) - pd.Timedelta(minutes=60); t1 = M["US100"].idx[int(r.r1)] + pd.Timedelta(minutes=30)
        fig, axs = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
        for ax, i in zip(axs, INST):
            b = M[i].b[(M[i].b.index >= t0) & (M[i].b.index <= t1)]; ax.plot(b.index, b.Close, lw=.8, c="k")
            ax.fill_between(b.index, b.Low, b.High, color="grey", alpha=.3)
            Ei = E[(E.tf == "5m") & (E.kind == "SMT") & (E.inst == i) & (E.T0 == r.T0) & (E.v == r.v)]
            if len(Ei):
                q = Ei.iloc[0]; Lr = q.L * r.v; ax.axhline(Lr, c="b", ls="--", lw=1, label=f"SMT swing {'low' if r.v == 1 else 'high'}")
                if np.isfinite(q.internal): ax.axhline(q.internal * r.v, c="orange", ls=":", lw=1, label="internal liquidity")
            ax.axvline(r.T0, c="purple", lw=.8, label="SMT confirmed (T0)"); ax.axvline(M["US100"].idx[int(r.ki)], c="orange", lw=.8, label="internal taken (US100)")
            ax.axvline(M["US100"].idx[int(r.r1)], c="g", lw=.8, label="return to SMT level (US100)"); ax.set_title(i, fontsize=9); ax.grid(alpha=.2)
        axs[0].legend(fontsize=7); fig.suptitle(f"Example {n}: 5m {'bullish (lows)' if r.v == 1 else 'bearish (highs)'} SMT, leader {r.leader}, {pd.Timestamp(r.T0):%Y-%m-%d %H:%M} NY. In-sample burned, NOT evidence", fontsize=9)
        fig.tight_layout(); fig.savefig(OUT + f"example_{n}.png", dpi=100); plt.close(fig)

if __name__ == "__main__":
    main()
