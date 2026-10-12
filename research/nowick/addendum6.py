"""NOWICK-1 addendum 6: deliberate US100 fit, single US500 test (PREREG Addendum 6). EXPLORATORY, IN-SAMPLE, NOT EVIDENCE.
usage: addendum6.py fit   -> US100 only, writes add6_fit_grid.csv.gz + add6_frozen.json
       addendum6.py test  -> US500 only, requires add6_frozen.json committed & clean"""
import itertools, json, math, subprocess, sys
import numpy as np, pandas as pd
sys.path.insert(0, "research/nowick")
import nowick as nw
from addendum2 import swings
from addendum3 import book, COST, TFMIN, MIN
OUT = "research/nowick/"
DIRS, ENTRIES, STOPS, TGTS, TSTOPS = ["toward", "cont"], ["immediate", "MSS", "FVG_CE", "iFVG"], ["swing", "fvg", "far", "atr1"], ["open", "1.5R", "2R", "3R", "opp"], [10, 20]
KZ, PD_, BIAS, TFF = ["all", "LonNYAM"], ["off", "on"], ["off", "on"], ["both", "15m", "1H"]
N_CONFIGS = len(DIRS) * len(ENTRIES) * len(STOPS) * len(TGTS) * len(TSTOPS) * len(KZ) * len(PD_) * len(BIAS) * len(TFF)

class View:
    """long-trade view: for sd=-1 (short) prices are negated and BID/ASK roles swapped so all logic is 'long'."""
    def __init__(v, bid, ask, sd):
        O, H, L, C = (bid[x].values for x in ["Open", "High", "Low", "Close"]); AO, AH, AL, AC = (ask[x].values for x in ["Open", "High", "Low", "Close"])
        if sd == 1: v.BH, v.BL, v.BC, v.EC, v.SL, v.SO, v.TH, v.TC, v.LF = H, L, C, AC, L, O, H, C, AL
        else: v.BH, v.BL, v.BC, v.EC, v.SL, v.SO, v.TH, v.TC, v.LF = -L, -H, -C, -C, -AH, -AO, -AL, -AC, -H
        v.swh = swings(-v.BH)  # swing highs in view
        v.sd = sd

def prep(inst):
    bid, ask = nw.load(f"{inst}_1m_bid"), nw.load(f"{inst}_1m_ask"); ask = ask.reindex(bid.index).ffill()
    T1 = bid.index.values.astype("datetime64[ns]").astype(np.int64)
    tday = np.array((bid.index + nw.SHIFT).date)
    dend = pd.Series(np.arange(len(T1))).groupby(tday).transform("max").values
    pdd = bid.groupby(tday).agg(h=("High", "max"), l=("Low", "min"), o=("Open", "first"), c=("Close", "last")).shift(1)
    views = {1: View(bid, ask, 1), -1: View(bid, ask, -1)}
    kzs = np.array([nw.kz(t) for t in bid.index])
    ev = []
    for tf in TFMIN:
        b = nw.bars(bid, ask, tf); out, _ = nw.features(b, tf)
        close_ns = (pd.to_datetime(out.t) + pd.Timedelta(minutes=TFMIN[tf])).values.astype("datetime64[ns]").astype(np.int64)
        for i in np.where((out.grp == "TOL").values)[0]:
            a = np.searchsorted(T1, close_ns[i])
            if a >= len(T1): continue
            es = {n: min(np.searchsorted(T1, close_ns[i] + n * TFMIN[tf] * MIN) - 1, dend[a]) for n in TSTOPS}
            if es[20] <= a: continue
            ev.append(dict(tf=tf, bull=out.dir.values[i] == "bull", op=b.o.values[i], far=b.h.values[i] if out.dir.values[i] == "bull" else b.l.values[i],
                           atr=b.atr.values[i], a=a, close_ns=close_ns[i], e=es))
    return dict(inst=inst, bid=bid, T1=T1, tday=tday, pdd=pdd, views=views, kzs=kzs, ev=ev, c=COST[inst])

def gen_trades(P, d, entry):
    """all trades for direction d and entry type, across stops/targets/tstops; returns DataFrame with config columns + filter flags"""
    c = P["c"]; mr = 4 * (c["spr"] + 2 * c["mkt"]); T1, tday = P["T1"], P["tday"]; rows = []
    for E in P["ev"]:
        sd = (-1 if E["bull"] else 1) if d == "toward" else (1 if E["bull"] else -1)
        V = P["views"][sd]; op, far = sd * E["op"], sd * E["far"]; a, e20 = E["a"], E["e"][20]
        buf = max(1.0, c["stop"]) if sd == 1 else max(1.0, c["spr"] + c["stop"])
        seg = slice(a, e20 + 1)
        kill = (V.BH[seg] >= op) | (V.BL[seg] < far) if d == "toward" else (V.BL[seg] <= op)
        kb = a + int(np.argmax(kill)) if kill.any() else e20 + 1
        lim = min(kb, e20)
        ent = None  # (k entry bar, fill, ref, setup_start, fvg_stop, s0 first exit-check bar)
        if entry == "immediate":
            if a < lim: ent = (a, V.EC[a] + c["mkt"], V.BC[a], a, None, a + 1)
        elif entry == "MSS":
            lb = E["close_ns"] - 60 * MIN
            for k in range(a, lim):
                q = np.searchsorted(V.swh, k - 3, "right") - 1
                if q < 0 or T1[V.swh[q]] < lb: continue
                s = V.swh[q]
                if V.BC[k] > V.BH[s]: ent = (k, V.EC[k] + c["mkt"], V.BC[k], s, None, k + 1); break
        elif entry == "FVG_CE":
            for g in range(a + 2, lim):
                if V.BH[g - 2] < V.BL[g]:
                    ce = (V.BH[g - 2] + V.BL[g]) / 2
                    for m in range(g + 1, lim):
                        if V.LF[m] <= ce: ent = (m, ce + c["lim"], ce, g - 2, V.BL[g - 2], m); break
                    break
        else:  # iFVG
            for g in range(a + 2, lim):
                if V.BL[g - 2] > V.BH[g]:
                    for q in range(g + 1, lim):
                        if V.BC[q] > V.BL[g - 2]: ent = (q, V.EC[q] + c["mkt"], V.BC[q], g - 2, V.BL[g - 2:q + 1].min(), q + 1); break
                    break
        if ent is None: continue
        k, fill, ref, s0_, fstop, x0 = ent
        pv = P["pdd"].loc[tday[k]]; ok_pd = ok_bias = False; opp = np.nan
        if np.isfinite(pv.h):
            mid = sd * (pv.h + pv.l) / 2; ok_pd = V.BC[k] < mid; ok_bias = sd * (pv.c - pv.o) > 0
            opp = pv.h if sd == 1 else -pv.l
        flags = dict(tf=E["tf"], kz_ok=P["kzs"][k] in ("London", "NYAM"), pd_ok=ok_pd, bias_ok=ok_bias,
                     inst=P["inst"], entry_t=P["bid"].index[k], day=tday[k])
        swing = V.BL[s0_:k + 1].min()
        stops = {"swing": swing - buf, "fvg": (fstop if fstop is not None else swing) - buf,
                 "far": (far if d == "toward" else op) - buf, "atr1": ref - E["atr"] if np.isfinite(E["atr"]) else np.nan}
        for ts in TSTOPS:
            e = E["e"][ts]
            if k >= e: continue
            for sn, st in stops.items():
                if not np.isfinite(st): continue
                if ref - st < mr: st = ref - mr
                risk = ref - st
                sl = V.SL[x0:e + 1] <= st; si = x0 + int(np.argmax(sl)) if sl.any() else None
                for tn in TGTS:
                    if tn == "open": tg = op if d == "toward" else np.nan
                    elif tn == "opp": tg = opp
                    else: tg = ref + float(tn[:-1]) * risk
                    if not np.isfinite(tg) or tg <= ref: continue
                    th = V.TH[x0:e + 1] > tg; ti = x0 + int(np.argmax(th)) if th.any() else None
                    if si is not None and (ti is None or si <= ti): ex, xt, why = min(st, V.SO[si]) - c["stop"], si, "stop"
                    elif ti is not None: ex, xt, why = tg - c["lim"], ti, "target"
                    else: ex, xt, why = V.TC[e] - c["mkt"], e, "time"
                    rows.append(dict(flags, dir=d, entry=entry, stop=sn, target=tn, tstop=ts, R=(ex - fill) / risk,
                                     exit_t=P["bid"].index[max(xt, k)], why=why))
    return pd.DataFrame(rows)

def select(T, cfg):
    m = (T.dir == cfg["dir"]) & (T.entry == cfg["entry"]) & (T.stop == cfg["stop"]) & (T.target == cfg["target"]) & (T.tstop == cfg["tstop"])
    if cfg["kz"] == "LonNYAM": m &= T.kz_ok
    if cfg["pd"] == "on": m &= T.pd_ok
    if cfg["bias"] == "on": m &= T.bias_ok
    if cfg["tf"] != "both": m &= T.tf == cfg["tf"]
    return T[m]

def stats(S, seed=20261012):
    if len(S) < 2: return dict(N=len(S))
    rng = np.random.default_rng(seed); days = S.day.unique(); g = S.groupby("day").R.agg(["sum", "count"]).reindex(days)
    W = rng.multinomial(len(days), np.ones(len(days)) / len(days), size=2000); bm = (W @ g["sum"].values) / (W @ g["count"].values)
    return dict(N=len(S), win=(S.R > 0).mean(), meanR=S.R.mean(), lo=np.quantile(bm, .025), hi=np.quantile(bm, .975),
                se=bm.std(ddof=1), p_one=max((bm <= 0).mean(), 1 / 2000))

def allT(P):
    return pd.concat([gen_trades(P, d, en) for d in DIRS for en in ENTRIES], ignore_index=True)

def fit():
    P = prep("US100"); T = allT(P); print("US100 trade rows", len(T), file=sys.stderr)
    base = T.groupby(["dir", "entry", "stop", "target", "tstop"])
    rows = []
    for key, G in base:
        for kz, pd_, bi, tf in itertools.product(KZ, PD_, BIAS, TFF):
            cfg = dict(zip(["dir", "entry", "stop", "target", "tstop"], key)) | dict(kz=kz, pd=pd_, bias=bi, tf=tf)
            S = select(G, cfg); rows.append(cfg | dict(N=len(S), meanR=S.R.mean() if len(S) else np.nan, win=(S.R > 0).mean() if len(S) else np.nan))
    Gd = pd.DataFrame(rows); Gd.to_csv(OUT + "add6_fit_grid.csv.gz", index=False)
    elig = Gd[Gd.N >= 150].sort_values("meanR", ascending=False)
    top = elig.head(5).to_dict("records")
    hk = math.sqrt(2 * math.log(N_CONFIGS)); frozen = []
    for r in top:
        cfg = {k: (int(r[k]) if k == "tstop" else r[k]) for k in ["dir", "entry", "stop", "target", "tstop", "kz", "pd", "bias", "tf"]}
        st = stats(select(T, cfg)); frozen.append(dict(config=cfg, fit_US100={k: float(v) for k, v in st.items()} | dict(haircutR=float(st["meanR"] - hk * st["se"]))))
    meta = dict(n_configs_grid=N_CONFIGS, n_configs_with_trades=int((Gd.N > 0).sum()), n_eligible_ge150=int(len(elig)),
                haircut_multiplier=hk, share_eligible_meanR_gt0=float((elig.meanR > 0).mean()), best_is_rank1=True, top5=frozen)
    json.dump(meta, open(OUT + "add6_frozen.json", "w"), indent=1, default=str); print(json.dumps(meta, indent=1, default=str))

def test():
    f = "research/nowick/add6_frozen.json"
    assert subprocess.run(["git", "log", "-1", "--format=%H", "--", f], capture_output=True, text=True).stdout.strip(), "frozen file not committed"
    assert not subprocess.run(["git", "status", "--porcelain", f], capture_output=True, text=True).stdout.strip(), "frozen file modified"
    meta = json.load(open(f))
    import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
    res, curves = [], {}
    TT = {}
    for inst in ["US100", "US500"]:
        P = prep(inst); TT[inst] = {}
        for r in meta["top5"]:
            cfg = r["config"]; key = (cfg["dir"], cfg["entry"])
            if key not in TT[inst]: TT[inst][key] = gen_trades(P, *key)
    for n, r in enumerate(meta["top5"], 1):
        cfg = r["config"]
        for inst in ["US100", "US500"]:
            S = select(TT[inst][(cfg["dir"], cfg["entry"])], cfg); st = stats(S)
            row = dict(rank=n, inst=inst, role="fit" if inst == "US100" else "TEST", **cfg, **st)
            for halt in (True, False):
                B, cv, h, mdd = book(S, halt); tag = "halted" if halt else "unhalted"
                row |= {f"final_{tag}": cv["eq"].iloc[-1], f"maxDD_{tag}": mdd}
                if halt: row["halted_at"] = h
                else: curves[(n, inst)] = cv
            for t, G in S.groupby("tf"): row[f"R_{t}"] = G.R.mean(); row[f"N_{t}"] = len(G)
            res.append(row)
    R = pd.DataFrame(res); R.to_csv(OUT + "add6_results.csv", index=False)
    pd.set_option("display.width", 320); print(R.to_string(float_format=lambda x: f"{x:.4f}"))
    fig, axs = plt.subplots(1, 2, figsize=(15, 5.5), sharey=True)
    for (n, inst), cv in curves.items():
        ax = axs[0 if inst == "US100" else 1]; ax.step(cv.t, cv["eq"], where="post", lw=1.6 if n == 1 else .9, label=f"#{n}")
    for ax, t in zip(axs, ["FIT: US100 (grid-optimized, in-sample)", "TEST: US500 (same window, run once)"]):
        ax.axhline(1e4, color="k", lw=.5); ax.set_title(t, fontsize=10); ax.grid(alpha=.3); ax.legend(fontsize=8)
    axs[0].set_ylabel("equity $ (unhalted, 0.5% risk)")
    fig.suptitle("NOWICK Addendum 6: fit vs test, top-5 configs. Burned window, EXPLORATORY, NOT EVIDENCE; US100/US500 highly correlated", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT + "add6_equity.png", dpi=110)

if __name__ == "__main__":
    {"fit": fit, "test": test}[sys.argv[1]]()
