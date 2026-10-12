"""NOWICK-1 addendum 4: fixed 7-variant H-NW11 family (PREREG Addendum 4). EXPLORATORY, IN-SAMPLE, NOT EVIDENCE."""
import math, sys
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
sys.path.insert(0, "research/nowick")
import nowick as nw
from addendum2 import swings
from addendum3 import book, boot, COST, TFMIN, MIN
OUT = "research/nowick/"; V = ["V1_FVG_CE", "V2_partial_2R", "V3_far_stop_1.5R", "V4_killzone", "V5_prem_disc", "V6_fade", "V7_HTF_bias"]

def run(inst):
    bid, ask = nw.load(f"{inst}_1m_bid"), nw.load(f"{inst}_1m_ask"); ask = ask.reindex(bid.index).ffill()
    T1 = bid.index.values.astype("datetime64[ns]").astype(np.int64)
    O, H, L, C = (bid[x].values for x in ["Open", "High", "Low", "Close"])
    AO, AH, AL, AC = (ask[x].values for x in ["Open", "High", "Low", "Close"])
    tday = np.array((bid.index + nw.SHIFT).date)
    dend = pd.Series(np.arange(len(T1))).groupby(tday).transform("max").values
    dd = bid.groupby(tday).agg(h=("High", "max"), l=("Low", "min"), o=("Open", "first"), c=("Close", "last")).shift(1)  # previous day
    c = COST[inst]; mr = 4 * (c["spr"] + 2 * c["mkt"]); bs, bl = max(1.0, c["spr"] + c["stop"]), max(1.0, c["stop"])
    sl_lo, sl_hi = swings(L), swings(-H)

    def sim(short, m0, e, entry, stop, tgt):
        for m in range(m0, e + 1):
            if short:
                if AH[m] >= stop: return max(stop, AO[m]) + c["stop"], m, "stop"
                if AL[m] < tgt: return tgt + c["lim"], m, "target"
            else:
                if L[m] <= stop: return min(stop, O[m]) - c["stop"], m, "stop"
                if H[m] > tgt: return tgt - c["lim"], m, "target"
        x = max(e, m0 - 1); return ((AC[x] + c["mkt"]) if short else (C[x] - c["mkt"])), x, "time"

    def rec(var, tf, short, k, entry, ref, stop, ex, xt, why, R=None):
        risk = abs(ref - stop)
        if R is None: R = ((entry - ex) if short else (ex - entry)) / risk
        return dict(var=var, inst=inst, tf=tf, dir="short" if short else "long", entry_t=bid.index[k], exit_t=bid.index[xt],
                    day=tday[k], R=R, why=why)
    out_rows = []
    for tf in TFMIN:
        b = nw.bars(bid, ask, tf); out, _ = nw.features(b, tf)
        close_ns = (pd.to_datetime(out.t) + pd.Timedelta(minutes=TFMIN[tf])).values.astype("datetime64[ns]").astype(np.int64)
        for i in np.where((out.grp == "TOL").values)[0]:
            bull = out.dir.values[i] == "bull"; op = b.o.values[i]; far = b.h.values[i] if bull else b.l.values[i]
            a = np.searchsorted(T1, close_ns[i])
            if a >= len(T1): continue
            e = min(np.searchsorted(T1, close_ns[i] + 20 * TFMIN[tf] * MIN) - 1, dend[a])
            sw = sl_lo if bull else sl_hi; lb = close_ns[i] - 60 * MIN; sig = None
            for k in range(a, e + 1):
                if (H[k] > far) if bull else (L[k] < far): break
                if (L[k] <= op) if bull else (H[k] >= op): break
                q = np.searchsorted(sw, k - 3, "right") - 1
                if q < 0 or T1[sw[q]] < lb: continue
                s = sw[q]
                if (C[k] < L[s]) if bull else (C[k] > H[s]): sig = (k, s); break
            if sig is None: continue
            k, s = sig; short = bull; ck = C[k]
            entry = (C[k] - c["mkt"]) if short else (AC[k] + c["mkt"])
            stop = (H[s:k + 1].max() + bs) if short else (L[s:k + 1].min() - bl)
            if abs(stop - ck) < mr: stop = ck + mr if short else ck - mr
            risk = abs(stop - ck)
            base = sim(short, k + 1, e, entry, stop, op); baseR = rec("base", tf, short, k, entry, ck, stop, *base)
            # V1 FVG CE
            gs = [g for g in range(s + 1, k + 1) if g >= 2 and ((L[g - 2] > H[g]) if short else (H[g - 2] < L[g]))]
            if gs:
                g = gs[-1]; ce = (L[g - 2] + H[g]) / 2 if short else (H[g - 2] + L[g]) / 2
                st = stop if abs(stop - ce) >= mr else (ce + mr if short else ce - mr)
                for m in range(k + 1, e + 1):
                    if (H[m] > far) if short else (L[m] < far): break
                    if (L[m] <= op) if short else (H[m] >= op): break
                    if (H[m] >= ce) if short else (AL[m] <= ce):
                        en = ce - c["lim"] if short else ce + c["lim"]
                        # fill bar: stop check on the same bar (conservative), then subsequent bars
                        r = sim(short, m, e, en, st, op); out_rows.append(rec("V1_FVG_CE", tf, short, m, en, ce, st, *r)); break
            # V2 partial + 2R
            t2 = ck - 2 * risk if short else ck + 2 * risk
            t1 = op if (op > t2 if short else op < t2) else t2
            r1 = sim(short, k + 1, e, entry, stop, t1); r2 = sim(short, k + 1, e, entry, stop, t2)
            R1 = ((entry - r1[0]) if short else (r1[0] - entry)) / risk; R2 = ((entry - r2[0]) if short else (r2[0] - entry)) / risk
            out_rows.append(rec("V2_partial_2R", tf, short, k, entry, ck, stop, r2[0], max(r1[1], r2[1]), r2[2], R=(R1 + R2) / 2))
            # V3 far-extreme stop, 1.5R filter
            st = far + bs if short else far - bl
            if abs(st - ck) < mr: st = ck + mr if short else ck - mr
            if abs(ck - op) >= 1.5 * abs(st - ck):
                out_rows.append(rec("V3_far_stop_1.5R", tf, short, k, entry, ck, st, *sim(short, k + 1, e, entry, st, op)))
            # V4 killzone
            if nw.kz(bid.index[k]) in ("London", "NYAM"): out_rows.append(baseR | {"var": "V4_killzone"})
            # V5 / V7 previous day
            pdv = dd.loc[tday[k]]
            if np.isfinite(pdv.h):
                mid = (pdv.h + pdv.l) / 2
                if (ck > mid) if short else (ck < mid): out_rows.append(baseR | {"var": "V5_prem_disc"})
                if (pdv.c < pdv.o) if short else (pdv.c > pdv.o): out_rows.append(baseR | {"var": "V7_HTF_bias"})
            # V6 fade: far extreme taken before open/time stop
            for m in range(k + 1, e + 1):
                if (L[m] <= op) if short else (H[m] >= op): break
                if (H[m] > far) if short else (L[m] < far):
                    lng = short  # continuation of the candle direction
                    en = (AC[m] + c["mkt"]) if lng else (C[m] - c["mkt"]); cm = C[m]
                    st = (L[k:m + 1].min() - bl) if lng else (H[k:m + 1].max() + bs)
                    if abs(cm - st) < mr: st = cm - mr if lng else cm + mr
                    rk = abs(cm - st); tg = cm + 2 * rk if lng else cm - 2 * rk
                    if m < e: out_rows.append(rec("V6_fade", tf, not lng, m, en, cm, st, *sim(not lng, m + 1, e, en, st, tg)))
                    break
    return pd.DataFrame(out_rows)

def main():
    A = pd.concat([run(x) for x in ["US100", "US500"]], ignore_index=True); A.to_csv(OUT + "add4_signals.csv.gz", index=False)
    rows, curves = [], {}
    for v in V:
        S = A[A["var"] == v].drop(columns="var")
        rng = np.random.default_rng(20261012); days = S.day.unique(); g = S.groupby("day").R.agg(["sum", "count"]).reindex(days)
        W = rng.multinomial(len(days), np.ones(len(days)) / len(days), size=2000); bm = (W @ g["sum"].values) / (W @ g["count"].values)
        se = bm.std(ddof=1); m = S.R.mean()
        r = dict(variant=v, N=len(S), win=(S.R > 0).mean(), meanR=m, lo=np.quantile(bm, .025), hi=np.quantile(bm, .975),
                 p_one=max((bm <= 0).mean(), 1 / 2000), haircutR=m - 1.352 * se)
        for halt in (True, False):
            T, cv, h, mdd = book(S, halt); tag = "halted" if halt else "unhalted"
            r |= {f"N_{tag}": len(T), f"final_{tag}": cv["eq"].iloc[-1], f"maxDD_{tag}": mdd}
            if halt: r["halted_at"] = h
            else: curves[v] = cv
        for (a, t), G in S.groupby(["inst", "tf"]): r[f"R_{a}_{t}"] = G.R.mean()
        rows.append(r)
    R = pd.DataFrame(rows); R["p_holm"] = nw.holm(R.p_one.values)
    R["forward_worthy"] = (R.p_holm < 0.05) & (R.haircutR > 0) & (R.maxDD_unhalted < 0.20)
    R.to_csv(OUT + "add4_summary.csv", index=False)
    pd.set_option("display.width", 250); print(R.round(4).to_string())
    fig, ax = plt.subplots(figsize=(12, 6))
    for v, cv in curves.items(): ax.step(cv.t, cv["eq"], where="post", label=v, lw=1)
    ax.axhline(1e4, color="k", lw=.5); ax.legend(fontsize=8); ax.grid(alpha=.3); ax.set_ylabel("equity $ (unhalted)")
    ax.set_title("NOWICK Addendum 4: H-NW11 variants, unhalted $10k books. IN-SAMPLE burned window, EXPLORATORY, NOT EVIDENCE", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT + "add4_equity.png", dpi=110)

if __name__ == "__main__":
    main()
