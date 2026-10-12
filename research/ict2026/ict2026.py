"""ICT-2026 descriptive study (see PREREG.md). EXPLORATORY, IN-SAMPLE burned window, NOT EVIDENCE."""
import gzip, hashlib, io, math, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
DATA = "/workspace/ftn-demo-output/data"; OUT = "research/ict2026/"
SHA = {"US100": "6afa3130", "US500": "9d68787c"}
END = pd.Timestamp("2026-09-25 17:00"); START = pd.Timestamp("2025-08-24 18:00")
NB = 2000; SEED = 20261012
CAL = pd.read_csv("ftn/src/ftn/research/data/us_macro_events.csv", comment="#")
NEWS830 = set(pd.to_datetime(CAL[CAL.time_ny == "08:30"].date).dt.date)

def load(inst):
    raw = gzip.open(f"{DATA}/{inst}_1m_bid.csv.gz").read(); assert hashlib.sha256(raw).hexdigest().startswith(SHA[inst])
    df = pd.read_csv(io.BytesIO(raw)); t = pd.to_datetime(df.Datetime, utc=True).dt.tz_convert("America/New_York").dt.tz_localize(None)
    df.index = t; df = df.drop(columns="Datetime"); df = df[(df.index >= START) & (df.index < END)]
    assert df.index.max() < END
    df["date"] = df.index.date; df["hm"] = df.index.hour * 60 + df.index.minute
    return df

def win(g, a, b):  # minutes [a, b)
    return g[(g.hm >= a) & (g.hm < b)]

def boot(D, y1, n1, y2=None, n2=None):
    """D days; per-day sums. returns est, lo, hi, p (two-sided) of ratio1 - ratio2 (or ratio1 if y2 None)"""
    rng = np.random.default_rng(SEED); W = rng.multinomial(D, np.ones(D) / D, size=NB).astype(float)
    f = lambda w: (w @ y1) / (w @ n1) - ((w @ y2) / (w @ n2) if y2 is not None else 0)
    est = f(np.ones(D)); bs = np.array([f(w) for w in W]) if False else ((W @ y1) / (W @ n1) - ((W @ y2) / (W @ n2) if y2 is not None else 0))
    bs = bs[np.isfinite(bs)]
    return est, np.quantile(bs, .025), np.quantile(bs, .975), min(1, 2 * min((bs <= 0).mean(), (bs >= 0).mean()) + 1 / NB)

def h(p1, p2): return 2 * math.asin(math.sqrt(p1)) - 2 * math.asin(math.sqrt(p2))

def first_touch(g, lvl):
    m = (g.Low.values <= lvl) & (g.High.values >= lvl)
    return int(np.argmax(m)) if m.any() else None

def days_table(df):
    rows = []; G = dict(tuple(df.groupby("date")))
    dates = sorted(d for d in G if pd.Timestamp(d).weekday() < 5)
    prev_rth = None
    for d in dates:
        g = G[d]; rth = win(g, 570, 960); pm = win(g, 420, 540)
        if len(rth) < 300 or len(pm) < 100: continue
        news = d in NEWS830; pmw = win(g, 420, 510) if news else pm
        am = win(g, 570, 690); dr = lambda w: abs(w.Close.iloc[-1] - w.Open.iloc[0]) / (w.High.max() - w.Low.min())
        er = lambda w: abs(w.Close.iloc[-1] - w.Open.iloc[0]) / np.abs(np.diff(np.r_[w.Open.iloc[0], w.Close.values])).sum()
        r = dict(date=d, news=news, pm_dr=dr(pmw), pm_er=er(pmw), am_rng=am.High.max() - am.Low.min(), am_dr=dr(am), am_er=er(am),
                 o930=rth.Open.iloc[0], pmH=pm.High.max(), pmL=pm.Low.min())
        c1614 = win(g, 974, 975); r["c1614"] = c1614.Close.iloc[0] if len(c1614) else np.nan
        mo = win(g, 0, 1); r["mo"] = mo.Open.iloc[0] if len(mo) else np.nan
        r["prev_c1614"] = prev_rth
        prev_rth = r["c1614"]
        # sessions: Asia = previous calendar day 20:00-24:00
        pdte = (pd.Timestamp(d) - pd.Timedelta(days=1)).date()
        asia = win(G[pdte], 1200, 1440) if pdte in G else g.iloc[:0]
        if pd.Timestamp(d).weekday() == 0:
            sun = (pd.Timestamp(d) - pd.Timedelta(days=1)).date(); asia = win(G[sun], 1200, 1440) if sun in G else g.iloc[:0]
        lon = win(g, 120, 300)
        r["asia_rng"] = asia.High.max() - asia.Low.min() if len(asia) >= 120 else np.nan
        r["lon_rng"] = lon.High.max() - lon.Low.min() if len(lon) >= 90 else np.nan
        r["ny_rng"] = r["am_rng"]
        r["gg"] = g
        rows.append(r)
    T = pd.DataFrame(rows)
    T["atr_am"] = T.am_rng.shift(1).rolling(20).mean()
    for s in ["asia", "lon", "ny"]:
        T[f"{s}_ratio"] = T[f"{s}_rng"] / T[f"{s}_rng"].shift(1).rolling(20, min_periods=15).median()
    return T

def s1(T):
    X = T.dropna(subset=["atr_am"]).copy(); X["y"] = X.am_rng / X.atr_am
    R_, Tr = (X.pm_dr <= 0.3).values.astype(float), (X.pm_dr >= 0.6).values.astype(float)
    out = {}
    for col in ["y", "am_dr", "am_er"]:
        v = X[col].values; out[col] = boot(len(X), v * R_, R_, v * Tr, Tr)
    rho = pd.Series(X.pm_dr.values).rank().corr(pd.Series(X.y.values).rank())
    std = out["y"][0] / X.y.std()
    return out, dict(N_range=int(R_.sum()), N_trend=int(Tr.sum()), N=len(X), rho=rho, std=std,
                     m_range=X.y[R_ == 1].mean(), m_trend=X.y[Tr == 1].mean()), X

def touch_after(g, lvl, a, b):
    w = win(g, a, b); k = first_touch(w, lvl); return (k is not None), (k if k is not None else np.nan)

def s2(T):
    X = T.dropna(subset=["atr_am", "prev_c1614"]).copy(); rows = []
    for r in X.itertuples():
        gap = r.o930 - r.prev_c1614
        if abs(gap) < 0.05 * r.atr_am: continue
        ce = (r.o930 + r.prev_c1614) / 2; mir = r.o930 + gap / 2
        t1, m1 = touch_after(r.gg, ce, 570, 690); t2, _ = touch_after(r.gg, mir, 570, 690)
        t3, _ = touch_after(r.gg, ce, 570, 960); t4, _ = touch_after(r.gg, mir, 570, 960); f5, _ = touch_after(r.gg, r.prev_c1614, 570, 960)
        rows.append(dict(date=r.date, ce=t1, mir=t2, ce16=t3, mir16=t4, fill16=f5, mins=m1, gap_atr=abs(gap) / r.atr_am))
    Y = pd.DataFrame(rows); one = np.ones(len(Y))
    return boot(len(Y), Y.ce.values * 1., one, Y.mir.values * 1., one), boot(len(Y), Y.ce16.values * 1., one, Y.mir16.values * 1., one), Y

def s3(T):
    X = T.dropna(subset=["atr_am", "mo"]).copy(); rows = []
    for r in X.itertuples():
        d = r.o930 - r.mo
        if abs(d) < 0.05 * r.atr_am: continue
        mir = r.o930 + d
        a, _ = touch_after(r.gg, r.mo, 570, 690); b, _ = touch_after(r.gg, mir, 570, 690)
        a16, _ = touch_after(r.gg, r.mo, 570, 960); b16, _ = touch_after(r.gg, mir, 570, 960)
        rows.append(dict(date=r.date, mo=a, mir=b, mo16=a16, mir16=b16, d_atr=abs(d) / r.atr_am))
    Y = pd.DataFrame(rows); one = np.ones(len(Y))
    return boot(len(Y), Y.mo.values * 1., one, Y.mir.values * 1., one), boot(len(Y), Y.mo16.values * 1., one, Y.mir16.values * 1., one), Y

def s4(T):
    P = []
    for i, r in enumerate(T.itertuples()):
        P.append(("Asia>London", i, r.asia_ratio, r.lon_ratio)); P.append(("London>NY", i, r.lon_ratio, r.ny_ratio))
        if i + 1 < len(T) and (pd.Timestamp(T.date.iloc[i + 1]) - pd.Timestamp(r.date)).days <= 3:
            P.append(("NY>Asia", i, r.ny_ratio, T.asia_ratio.iloc[i + 1]))
    Y = pd.DataFrame(P, columns=["pair", "day", "prev", "nxt"]).dropna()
    Y = Y[(Y.prev != 1) & (Y.nxt != 1)]
    D = len(T); res = {}
    for name, Z in [("pooled", Y)] + list(Y.groupby("pair")):
        c = (Z.prev < 1).values; e = (Z.nxt > 1).values * 1.
        f = lambda m: np.bincount(Z.day.values[m], minlength=D).astype(float)
        fy = lambda m: np.bincount(Z.day.values[m], weights=e[m], minlength=D)
        res[name] = boot(D, fy(c), f(c), fy(~c), f(~c)) + (Z.prev.rank().corr(Z.nxt.rank()), int(c.sum()), int((~c).sum()))
    return res, Y

def s5(T):
    rng = np.random.default_rng(SEED); rows = []
    ict = [0.375, 0.5, 0.625]
    for r in T.itertuples():
        R = r.pmH - r.pmL
        if not R > 0: continue
        g = win(r.gg, 540, 720)
        if len(g) < 60: continue
        c900 = g.Open.iloc[0]
        fr = []
        while len(fr) < 20:
            x = rng.uniform(.05, .95)
            if min(abs(x - f) for f in ict) >= .03: fr.append(x)
        for kind, fs in [("ict", ict), ("rand", fr)]:
            for f in fs:
                lvl = r.pmL + f * R
                if abs(c900 - lvl) < .05 * R: continue
                k = first_touch(g, lvl)
                if k is None: continue
                up = c900 < lvl  # approach from below
                hi, lo = g.High.values[k:], g.Low.values[k:]
                back = (lo <= lvl - .15 * R) if up else (hi >= lvl + .15 * R)
                beyond = (hi >= lvl + .15 * R) if up else (lo <= lvl - .15 * R)
                ib = int(np.argmax(back)) if back.any() else 10**9; iy = int(np.argmax(beyond)) if beyond.any() else 10**9
                rows.append(dict(date=r.date, kind=kind, f=f, respect=ib < iy))
    Y = pd.DataFrame(rows); days = pd.Index(sorted(Y.date.unique())); di = days.get_indexer(Y.date); D = len(days)
    a = (Y.kind == "ict").values; b = ~a; v = Y.respect.values * 1.
    return boot(D, np.bincount(di[a], v[a], D), np.bincount(di[a], minlength=D) * 1., np.bincount(di[b], v[b], D), np.bincount(di[b], minlength=D) * 1.), Y

def holm(ps):
    ps = np.asarray(ps); o = np.argsort(ps); m = len(ps); adj = np.empty(m); run = 0
    for k, i in enumerate(o): run = max(run, (m - k) * ps[i]); adj[i] = min(1, run)
    return adj

def main():
    rows, extra = [], []
    figs = {k: plt.subplots(1, 2, figsize=(12, 4.5)) for k in ["s1", "s2", "s3", "s4", "s5"]}
    for j, inst in enumerate(["US100", "US500"]):
        T = days_table(load(inst)); print(inst, "days", len(T), T.date.min(), T.date.max(), "news830", int(T.news.sum()), file=sys.stderr)
        o, m, X = s1(T)
        rows.append(dict(study="S1 PM regime->AM range", inst=inst, effect=o["y"][0], lo=o["y"][1], hi=o["y"][2], p=o["y"][3], std=m["std"],
                         note=f"AMrange/ATR range-days {m['m_range']:.3f} (N {m['N_range']}) vs trend-days {m['m_trend']:.3f} (N {m['N_trend']}); rho {m['rho']:.3f}; dAM_DR {o['am_dr'][0]:+.3f} [{o['am_dr'][1]:+.3f},{o['am_dr'][2]:+.3f}]; dAM_ER {o['am_er'][0]:+.3f} [{o['am_er'][1]:+.3f},{o['am_er'][2]:+.3f}]"))
        ax = figs["s1"][1][j]; ax.scatter(X.pm_dr, X.am_rng / X.atr_am, s=6, alpha=.5); ax.axvline(.3, c="g"); ax.axvline(.6, c="r")
        ax.set_xlabel("PM 07-09 directional ratio"); ax.set_ylabel("AM 09:30-11:30 range / ATR20"); ax.set_title(f"{inst}: rho {m['rho']:.2f}")
        a, b16, Y = s2(T); p1, p2 = Y.ce.mean(), Y.mir.mean()
        rows.append(dict(study="S2 ORG CE touch by 11:30 vs mirror", inst=inst, effect=a[0], lo=a[1], hi=a[2], p=a[3], std=h(p1, p2),
                         note=f"N {len(Y)}; CE {p1:.3f} vs mirror {p2:.3f}; by16 diff {b16[0]:+.3f} [{b16[1]:+.3f},{b16[2]:+.3f}]; full fill by 16 {Y.fill16.mean():.3f}; median min to CE {Y.mins.median():.0f}"))
        ax = figs["s2"][1][j]; ax.hist(Y.mins.dropna(), bins=40); ax.set_title(f"{inst}: minutes 09:30 -> CE touch (CE {p1:.2f} vs mirror {p2:.2f} by 11:30)"); ax.set_xlabel("min")
        a, b16, Y = s3(T); p1, p2 = Y.mo.mean(), Y.mir.mean()
        Y["terc"] = pd.qcut(Y.d_atr, 3, labels=["near", "mid", "far"]); tt = Y.groupby("terc", observed=True)[["mo", "mir"]].mean()
        rows.append(dict(study="S3 midnight open touch 09:30-11:30 vs mirror", inst=inst, effect=a[0], lo=a[1], hi=a[2], p=a[3], std=h(p1, p2),
                         note=f"N {len(Y)}; MO {p1:.3f} vs mirror {p2:.3f}; by16 diff {b16[0]:+.3f} [{b16[1]:+.3f},{b16[2]:+.3f}]; tercile MO/mirror " + "; ".join(f"{i} {r.mo:.2f}/{r.mir:.2f}" for i, r in tt.iterrows())))
        ax = figs["s3"][1][j]; tt.plot.bar(ax=ax); ax.set_title(f"{inst}: touch 09:30-11:30 by distance tercile"); ax.set_ylim(0, 1)
        res, Y = s4(T); pr = res["pooled"]
        rows.append(dict(study="S4 session alternation (P expand|cons - P expand|exp)", inst=inst, effect=pr[0], lo=pr[1], hi=pr[2], p=pr[3], std=np.nan,
                         note="; ".join(f"{k}: {v[0]:+.3f} [{v[1]:+.3f},{v[2]:+.3f}] rho {v[4]:+.2f} (Ncons {v[5]}, Nexp {v[6]})" for k, v in res.items())))
        ax = figs["s4"][1][j]; ks = list(res); ax.errorbar(range(len(ks)), [res[k][0] for k in ks], yerr=[[res[k][0] - res[k][1] for k in ks], [res[k][2] - res[k][0] for k in ks]], fmt="o")
        ax.axhline(0, c="k"); ax.set_xticks(range(len(ks))); ax.set_xticklabels(ks); ax.set_title(f"{inst}: P(next expands|prev cons) - P(..|prev exp)")
        a, Y = s5(T); p1, p2 = Y[Y.kind == "ict"].respect.mean(), Y[Y.kind == "rand"].respect.mean()
        byf = Y[Y.kind == "ict"].groupby("f").respect.agg(["mean", "size"])
        rows.append(dict(study="S5 PM-range .375/.5/.625 respect vs random fractions", inst=inst, effect=a[0], lo=a[1], hi=a[2], p=a[3], std=h(p1, p2),
                         note=f"ICT {p1:.3f} (N {int((Y.kind=='ict').sum())}) vs random {p2:.3f} (N {int((Y.kind=='rand').sum())}); " + "; ".join(f"f{f}: {r['mean']:.3f} (N {int(r['size'])})" for f, r in byf.iterrows())))
        ax = figs["s5"][1][j]; R = Y[Y.kind == "rand"].copy(); R["bin"] = (R.f * 10).round() / 10
        ax.plot(R.groupby("bin").respect.mean(), "o-", label="random fractions (binned)"); ax.plot(byf["mean"], "rs", ms=9, label="ICT .375/.5/.625")
        ax.set_xlabel("fraction of PM 07-09 range"); ax.set_ylabel("respect rate"); ax.legend(fontsize=8); ax.set_title(inst)
    Rr = pd.DataFrame(rows); Rr["p_holm"] = holm(Rr.p.values)
    Rr.to_csv(OUT + "results.csv", index=False); pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 400)
    print(Rr.to_string(float_format=lambda x: f"{x:.4f}"))
    for k, (fig, _) in figs.items():
        fig.suptitle(f"ICT-2026 {k.upper()} (burned window 2025-08-25..2026-09-25, descriptive, NOT evidence)", fontsize=9); fig.tight_layout(); fig.savefig(OUT + f"{k}.png", dpi=105)

if __name__ == "__main__":
    main()
