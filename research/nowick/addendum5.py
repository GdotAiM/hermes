"""NOWICK-1 addendum 5: FVG / iFVG entries toward the open, no MSS (PREREG Addendum 5). EXPLORATORY, IN-SAMPLE, NOT EVIDENCE."""
import sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "research/nowick")
import nowick as nw
from addendum3 import book, COST, TFMIN, MIN
OUT = "research/nowick/"; V = ["A_open", "B_open", "C_open", "A_2R", "B_2R", "C_2R"]

def run(inst):
    bid, ask = nw.load(f"{inst}_1m_bid"), nw.load(f"{inst}_1m_ask"); ask = ask.reindex(bid.index).ffill()
    T1 = bid.index.values.astype("datetime64[ns]").astype(np.int64)
    O, H, L, C = (bid[x].values for x in ["Open", "High", "Low", "Close"])
    AO, AH, AL, AC = (ask[x].values for x in ["Open", "High", "Low", "Close"])
    tday = np.array((bid.index + nw.SHIFT).date)
    dend = pd.Series(np.arange(len(T1))).groupby(tday).transform("max").values
    c = COST[inst]; mr = 4 * (c["spr"] + 2 * c["mkt"]); bs, bl = max(1.0, c["spr"] + c["stop"]), max(1.0, c["stop"])

    def sim(short, m0, e, stop, tgt):
        for m in range(m0, e + 1):
            if short:
                if AH[m] >= stop: return max(stop, AO[m]) + c["stop"], m, "stop"
                if AL[m] < tgt: return tgt + c["lim"], m, "target"
            else:
                if L[m] <= stop: return min(stop, O[m]) - c["stop"], m, "stop"
                if H[m] > tgt: return tgt - c["lim"], m, "target"
        x = max(e, m0 - 1); return ((AC[x] + c["mkt"]) if short else (C[x] - c["mkt"])), x, "time"
    rows = []
    for tf in TFMIN:
        b = nw.bars(bid, ask, tf); out, _ = nw.features(b, tf)
        close_ns = (pd.to_datetime(out.t) + pd.Timedelta(minutes=TFMIN[tf])).values.astype("datetime64[ns]").astype(np.int64)
        for i in np.where((out.grp == "TOL").values)[0]:
            short = out.dir.values[i] == "bull"; op = b.o.values[i]; far = b.h.values[i] if short else b.l.values[i]
            a = np.searchsorted(T1, close_ns[i])
            if a >= len(T1): continue
            e = min(np.searchsorted(T1, close_ns[i] + 20 * TFMIN[tf] * MIN) - 1, dend[a])
            seg = np.arange(a, e + 1)
            dead_m = ((L[seg] <= op) | (H[seg] > far)) if short else ((H[seg] >= op) | (L[seg] < far))
            d = a + int(np.argmax(dead_m)) if dead_m.any() else e + 1
            lim = min(d, e)  # entries must occur at bars < lim (time stop bar excluded)
            ents = {}
            # A
            for g in range(a + 2, lim):
                if (L[g - 2] > H[g]) if short else (H[g - 2] < L[g]):
                    ce = (L[g - 2] + H[g]) / 2 if short else (H[g - 2] + L[g]) / 2
                    st = H[g - 2] + bs if short else L[g - 2] - bl
                    for m in range(g + 1, lim):
                        if (H[m] >= ce) if short else (AL[m] <= ce):
                            ents["A"] = (m, ce - c["lim"] if short else ce + c["lim"], ce, st, m); break
                    break
            # B
            for g in range(a + 2, lim):
                if (H[g - 2] < L[g]) if short else (L[g - 2] > H[g]):
                    edge = H[g - 2] if short else L[g - 2]
                    for q in range(g + 1, lim):
                        if (C[q] < edge) if short else (C[q] > edge):
                            st = H[g - 2:q + 1].max() + bs if short else L[g - 2:q + 1].min() - bl
                            ents["B"] = (q, C[q] - c["mkt"] if short else AC[q] + c["mkt"], C[q], st, q + 1); break
                    break
            if ents: ents["C"] = min(ents.values(), key=lambda x: (x[0], 0 if x is ents.get("A") else 1))
            for k_, (m, en, ref, st, s0) in ents.items():
                if abs(ref - st) < mr: st = ref + mr if short else ref - mr
                risk = abs(ref - st)
                for tn, tg in [("open", op), ("2R", ref - 2 * risk if short else ref + 2 * risk)]:
                    ex, xt, why = sim(short, s0, e, st, tg)
                    R = ((en - ex) if short else (ex - en)) / risk
                    rows.append(dict(var=f"{k_}_{tn}", inst=inst, tf=tf, dir="short" if short else "long", entry_t=bid.index[m],
                                     exit_t=bid.index[max(xt, m)], day=tday[m], R=R, why=why, risk_pts=risk))
    return pd.DataFrame(rows)

def main():
    A = pd.concat([run(x) for x in ["US100", "US500"]], ignore_index=True); A.to_csv(OUT + "add5_signals.csv.gz", index=False)
    rows, curves = [], {}
    for v in V:
        S = A[A["var"] == v].drop(columns="var")
        rng = np.random.default_rng(20261012); days = S.day.unique(); g = S.groupby("day").R.agg(["sum", "count"]).reindex(days)
        W = rng.multinomial(len(days), np.ones(len(days)) / len(days), size=2000); bm = (W @ g["sum"].values) / (W @ g["count"].values)
        se = bm.std(ddof=1); m = S.R.mean()
        r = dict(variant=v, N=len(S), win=(S.R > 0).mean(), avg_win=S.R[S.R > 0].mean(), avg_loss=S.R[S.R <= 0].mean(), meanR=m,
                 lo=np.quantile(bm, .025), hi=np.quantile(bm, .975), p_one=max((bm <= 0).mean(), 1 / 2000), haircutR=m - 1.267 * se)
        for halt in (True, False):
            T, cv, h, mdd = book(S, halt); tag = "halted" if halt else "unhalted"
            r |= {f"N_{tag}": len(T), f"final_{tag}": cv["eq"].iloc[-1], f"maxDD_{tag}": mdd}
            if halt: r["halted_at"] = h
            else: curves[v] = cv
        for (a, t), G in S.groupby(["inst", "tf"]): r[f"R_{a}_{t}"] = G.R.mean()
        rows.append(r)
    R = pd.DataFrame(rows); R["p_holm"] = nw.holm(R.p_one.values)
    R["forward_worthy"] = (R.p_holm < 0.05) & (R.haircutR > 0) & (R.maxDD_unhalted < 0.20)
    R.to_csv(OUT + "add5_summary.csv", index=False)
    pd.set_option("display.width", 300); print(R.to_string(float_format=lambda x: f"{x:.4f}"))
    print(A.groupby(["var", "why"]).size().unstack())
    fig, ax = plt.subplots(figsize=(12, 6))
    for v, cv in curves.items(): ax.step(cv.t, cv["eq"], where="post", label=v, lw=1)
    ax.axhline(1e4, color="k", lw=.5); ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_ylabel("equity $ (unhalted)")
    ax.set_title("NOWICK Addendum 5: 1m FVG / iFVG entries toward the no-wick open, unhalted $10k books. IN-SAMPLE burned, EXPLORATORY, NOT EVIDENCE", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT + "add5_equity.png", dpi=110)

if __name__ == "__main__":
    main()
