"""Model U — user's hand-traded 07-09 rules, coded mechanically in RANGE FRACTIONS (frac 0 = range low, 1 = range high).
Real Yahoo 1m NQ=F / ES=F only. Hypothetical backtest marks, not trades.
All shorts are computed by running the long code on the negated price series (exact mirror)."""
import numpy as np, pandas as pd

TICK = 0.25
SLIP = 1                 # ticks of adverse slippage on entry AND on every exit [user assumption]
STOP_BUF = 2             # ticks beyond the swept extreme / 50% [user rule]
DISP_K, MED_N = 1.4, 20  # displacement: candle BODY >= 1.4 x median body of prior 20 1m bars [user rule]
REL_TOL_FRAC = 0.05      # relative-equal highs/lows: fractal pivots within 5% of range (min 2 ticks) [our choice]
LEG_MIN_FRAC = 0.5       # re-anchor leg must be >= 0.5 x range height [our choice]
TIME_EXIT = "11:30"
FILL_THRU = 0            # longrun robustness option: limit fills only if price trades THROUGH by this many ticks (0 = v1/v2 rule: touch)

def load(k):
    df = pd.read_csv(f"data/{k}_1m_0910_0925.csv", index_col=0)
    df.index = pd.to_datetime(df.index, utc=True).tz_convert("America/New_York")
    return df[["Open", "High", "Low", "Close"]].astype(float)

def neg(g):
    return pd.DataFrame({"Open": -g.Open, "High": -g.Low, "Low": -g.High, "Close": -g.Close}, index=g.index)

def at(d, hm, tz): return pd.Timestamp(f"{d} {hm}").tz_localize(tz)
def rnd(x): return round(round(x / TICK) * TICK, 2)

def rel_equal_lows(pre, tol):
    """Relative equal lows inside the 07:00-09:00 range: two 3-bar pivot lows within tol.
    Returns (intact, swept_pre): pools still untaken at 09:00, and pools already run (undercut by >=1 tick) before 09:00."""
    lo = pre.Low.values
    piv = [i for i in range(1, len(lo) - 1) if lo[i] < lo[i - 1] and lo[i] <= lo[i + 1]]
    intact, swept = set(), set()
    for a in range(len(piv)):
        for b in range(a + 1, len(piv)):
            if abs(lo[piv[a]] - lo[piv[b]]) <= tol:
                lvl = min(lo[piv[a]], lo[piv[b]])
                later = lo[piv[b] + 1:]
                (swept if len(later) and later.min() <= lvl - TICK else intact).add(lvl)
    return sorted(intact), sorted(swept)

def fractal_highs(h): return [i for i in range(1, len(h) - 1) if h[i] > h[i - 1] and h[i] > h[i + 1]]

def disp_fvgs(g, i_from, i_to):
    """Bullish displacement FVGs: c2 is an up candle with body >= K x median body(prior 20) and c1.high < c3.low.
    c2 in [i_from, i_to), c3 < i_to. Returns list of (c1, c2, c3)."""
    O, H, L, C = (g[c].values for c in ("Open", "High", "Low", "Close"))
    body = np.abs(C - O); out = []
    for c2 in range(max(i_from, MED_N, 1), i_to - 1):
        c1, c3 = c2 - 1, c2 + 1
        if C[c2] > O[c2] and body[c2] >= DISP_K * np.median(body[c2 - MED_N:c2]) and H[c1] < L[c3]:
            out.append((c1, c2, c3))
    return out

def long_candidates(g, ctx, i900, i_end, reanchor=False, in_range=True):
    """Generate long setups in 'long space'. ctx: H, L, M, R, pools (range low + REL lows), pre07_lows (London/Asia lows)."""
    H, L, M, R = ctx["H"], ctx["L"], ctx["M"], ctx["R"]
    O, Hi, Lo, C = (g[c].values for c in ("Open", "High", "Low", "Close"))
    i700 = ctx["i700"]; cands = []
    for c1, c2, c3 in disp_fvgs(g, i900, i_end):
        fl, fh = Hi[c1], Lo[c3]; ce = rnd((fl + fh) / 2)
        low_since_900 = Lo[i900:c2 + 1].min()
        swept_pool = any(low_since_900 <= p - TICK for p in ctx["pools"])
        deep = low_since_900 <= ctx.get("deep", M)   # longs: traded <= 0.5; shorts: traded >= 0.75 (mirrored level passed in ctx)
        # --- reversal: sweep or deep zone first, entry in discount
        if (swept_pool or deep) and ce <= M and (ce >= L or not in_range):
            stop = rnd(min(low_since_900, L) - STOP_BUF * TICK)
            cands.append(dict(kind="reversal", trig_i=c3, c1=c1, c2=c2, c3=c3, fvg_lo=fl, fvg_hi=fh, entry=ce, stop=stop,
                              t1=H, t2=H + R, why=("swept pool" if swept_pool else ctx.get("deep_lab", "deep zone <=0.5")),
                              sweep_i=i900 + int(np.argmin(Lo[i900:c2 + 1])), sweep_px=low_since_900))
        # --- continuation: opposite side (sell-side) swept earlier after 07:00, displacement closes through range high
        early_low = Lo[i700:c2 + 1].min()
        ss_swept = (early_low <= min(ctx["pre07_lows"]) - TICK) or (low_since_900 <= L - TICK) or bool(ctx["swept_pre"]) or \
                   any(Lo[i900:c2 + 1].min() <= p - TICK for p in ctx["pools"] if p != L)
        if ss_swept and C[c2] > H and fh > H:
            entry = ce if ce >= H + TICK else rnd(H + TICK)
            stop = rnd(M - STOP_BUF * TICK)
            t1, t2 = H + R, H + 1.5 * R   # continuation: T1 = fib 2, T2 = fib 2.5 (our choice)
            if entry < t1 and entry <= H + 0.25 * R:   # "just beyond the extreme": entry within 0.25 range-heights (our choice)
                cands.append(dict(kind="continuation", trig_i=c3, c1=c1, c2=c2, c3=c3, fvg_lo=fl, fvg_hi=fh, entry=entry, stop=stop,
                                  t1=t1, t2=t2, why=ctx.get("opp_lab", "sell-side swept earlier"), sweep_i=i700 + int(np.argmin(Lo[i700:c2 + 1])),
                                  sweep_px=early_low))
    if reanchor:
        cands += reanchor_candidates(g, ctx, i900, i_end)
    return cands

def reanchor_candidates(g, ctx, i900, i_end):
    """Discretionary proxy: after 09:00 a sell-side pool is swept, then a displacement leg up breaks structure (close above the
    last fractal high before the leg low). Fib on the leg; entry at its 0.5 retrace; stop = leg low (1.0) - 2 ticks;
    T1 = leg high, T2 = leg high + 1 leg height."""
    Hi, Lo, C = g.High.values, g.Low.values, g.Close.values
    fh = fractal_highs(Hi); out = []; used = set()
    for c1, c2, c3 in disp_fvgs(g, i900, i_end):
        low_i = i900 + int(np.argmin(Lo[i900:c2 + 1])); leg_low = Lo[low_i]
        if not any(leg_low <= p - TICK for p in ctx["pools"]) or low_i in used: continue
        prior = [f for f in fh if f < low_i]
        if not prior: continue
        sw = Hi[prior[-1]]
        bos = [t for t in range(c2, min(i_end, len(g))) if C[t] > sw]
        if not bos: continue
        t0 = bos[0]; leg_high = Hi[low_i:t0 + 1].max()
        for t in range(t0 + 1, min(i_end, len(g))):
            if Hi[t] > leg_high: leg_high = Hi[t]; continue
            h = leg_high - leg_low
            if h < LEG_MIN_FRAC * ctx["R"]: continue
            lvl = rnd(leg_high - 0.5 * h)
            if Lo[t] <= lvl:
                used.add(low_i)
                out.append(dict(kind="re-anchor", trig_i=t - 1, fill_hint=t, c1=None, c2=c2, c3=None, fvg_lo=None, fvg_hi=None,
                                entry=lvl, stop=rnd(leg_low - STOP_BUF * TICK), t1=leg_high, t2=leg_high + h,
                                why=f"leg {h:.2f} pts BoS", sweep_i=low_i, sweep_px=leg_low, leg=(low_i, leg_low, leg_high)))
                break
    return out

def simulate(g, cand, i_fill_end, i_exit):
    """Fill limit on touch (then 1-tick slippage), cancel if T1 prints first. Returns fill info + 3 R variants."""
    Hi, Lo, C = g.High.values, g.Low.values, g.Close.values
    e, s, t1, t2 = cand["entry"], cand["stop"], cand["t1"], cand["t2"]
    risk = e - s
    if risk <= 0: return None
    fill = None
    start = cand.get("fill_hint", cand["trig_i"] + 1)
    for i in range(start, min(i_fill_end, len(g))):
        if i > start - 1 and Hi[i] >= t1 and not (Lo[i] <= e - FILL_THRU * TICK): return None   # target ran first -> cancelled
        if Lo[i] <= e - FILL_THRU * TICK: fill = i; break
    if fill is None: return None
    ef = e + SLIP * TICK
    R = lambda px: (px - ef) / risk
    stop_px, tgt = s - SLIP * TICK, None
    res = dict(fill_i=fill, entry_fill=ef)
    # walk forward; same-bar stop+target = loss; fill bar can stop but not target
    def run(target_list):
        """target_list: [(price, fraction)] in order; after first target stop moves to entry (BE). returns (R, exit_i, label)"""
        pos, got, cur_stop, lab = 1.0, 0.0, s, []
        if Lo[fill] <= s: return R(stop_px), fill, "LOSS (stop in fill bar)"
        for i in range(fill + 1, min(i_exit, len(g))):
            hit_stop = Lo[i] <= cur_stop
            hits = [(p, f) for p, f in target_list if Hi[i] >= p]
            if hit_stop:
                px = cur_stop - SLIP * TICK
                return got + pos * R(px), i, ("LOSS (stop)" if not lab else "+".join(lab) + " then BE")
            for p, f in list(target_list):
                if Hi[i] >= p:
                    got += f * R(p - SLIP * TICK); pos -= f; lab.append("T1" if p == t1 else "T2")
                    target_list = [x for x in target_list if x[0] != p]
                    cur_stop = e  # breakeven after first partial
            if pos <= 1e-9: return got, i, "WIN " + "+".join(lab)
        last = min(i_exit, len(g)) - 1
        px = C[last] - SLIP * TICK
        return got + pos * R(px), last, ("+".join(lab) + " then " if lab else "") + f"time exit {TIME_EXIT}"
    res["R_t1"], res["exit_t1_i"], res["out_t1"] = run([(t1, 1.0)])
    res["R_t2"], res["exit_t2_i"], res["out_t2"] = run([(t2, 1.0)])
    res["R_part"], res["exit_part_i"], res["out_part"] = run([(t1, 0.5), (t2, 0.5)])
    return res
