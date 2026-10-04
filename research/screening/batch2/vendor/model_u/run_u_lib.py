# v1 rule functions copied verbatim from research/model-u/scripts/run_u.py (main loop removed)
import sys, pathlib, pandas as pd, numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
from u_engine import *

DAYS = [d.strftime("%Y-%m-%d") for d in pd.bdate_range("2026-09-14", "2026-09-25")]
USER = {  # user's hand-marked US100 CFD trades (approx); R as stated by the user
    "2026-09-21": ("long", "reversal (sweep below range low, reclaim 09:30)", 3.3),
    "2026-09-22": ("long", "reversal (50%/FVG after 09:30 displacement)", 4.0),
    "2026-09-23": ("short", "reversal (0.875 premium FVG after equal-highs run)", 8.5),
    "2026-09-24": ("long", "continuation (breakout above range high)", 2.1),
    "2026-09-25": ("short", "re-anchor (0.5-0.625 of new down leg)", 3.7),
}
VARIANTS = {  # name: (window end, use bias, re-anchor)
    "U base (09-11)": ("11:00", False, False),
    "U 09-10": ("10:00", False, False),
    "U +bias": ("11:00", True, False),
    "U +re-anchor": ("11:00", False, True),
    "U literal (no in-range cap)": ("11:00", False, False),
}

def ctx_for(df, d, k):
    tz = df.index.tz
    g = df[(df.index >= at(d, "07:00", tz)) & (df.index < at(d, "12:00", tz))]
    pre = g[g.index < at(d, "09:00", tz)]
    H, L = pre.High.max(), pre.Low.min(); R = H - L; M = (H + L) / 2
    tol = max(2 * TICK, REL_TOL_FRAC * R)
    prev = (pd.Timestamp(d) - pd.tseries.offsets.BDay(1)).date()
    ps = df[(df.index >= at((pd.Timestamp(prev) - pd.tseries.offsets.BDay(1)).date(), "18:00", tz)) & (df.index < at(prev, "17:00", tz))]
    bias = ("long" if ps.Close.iloc[-1] > (ps.High.max() + ps.Low.min()) / 2 else "short") if len(ps) else "n/a"  # longrun: guard empty session (bias unused in base models)
    lon = df[(df.index >= at(d, "02:00", tz)) & (df.index < at(d, "05:00", tz))]
    asia = df[(df.index >= at(prev, "19:00", tz)) & (df.index < at(d, "00:00", tz))]
    idx = lambda hm: int(np.searchsorted(g.index.values, at(d, hm, tz).to_datetime64()))
    return dict(g=g, H=H, L=L, M=M, R=R, bias=bias, n_missing=300 - len(g),
                rel_lows=[p for p in rel_equal_lows(pre, tol)[0] if p <= M],
                rel_highs=[-p for p in rel_equal_lows(neg(pre), tol)[0] if -p >= M],
                swept_pre_lows=[p for p in rel_equal_lows(pre, tol)[1] if p <= L + 0.25 * R],   # only lows in the bottom quarter count
                swept_pre_highs=[-p for p in rel_equal_lows(neg(pre), tol)[1] if -p >= H - 0.25 * R],
                lon=(lon.Low.min(), lon.High.max()), asia=(asia.Low.min(), asia.High.max()),
                i700=0, i900=idx("09:00"), i1000=idx("10:00"), i1100=idx("11:00"), i1130=idx("11:30"))

def side_ctx(c, side):
    if side == "long":
        return dict(H=c["H"], L=c["L"], M=c["M"], R=c["R"], i700=0, pools=[c["L"]] + c["rel_lows"], pre07_lows=[c["lon"][0], c["asia"][0]],
                    swept_pre=c["swept_pre_lows"], deep=c["M"])
    return dict(H=-c["L"], L=-c["H"], M=-c["M"], R=c["R"], i700=0, pools=[-c["H"]] + [-p for p in c["rel_highs"]],
                pre07_lows=[-c["lon"][1], -c["asia"][1]], swept_pre=[-p for p in c["swept_pre_highs"]],
                deep=-c["H"] + 0.25 * c["R"], deep_lab="deep zone >=0.75", opp_lab="buy-side swept earlier")

def best_trade(c, wend, use_bias, reanchor, in_range=True):
    g = c["g"]; i_end = c["i1000"] if wend == "10:00" else c["i1100"]
    found = []
    for side in ("long", "short"):
        if use_bias and side != c["bias"]: continue
        gg = g if side == "long" else neg(g); sc = side_ctx(c, side)
        for cand in long_candidates(gg, sc, c["i900"], i_end, reanchor=reanchor, in_range=in_range):
            res = simulate(gg, cand, i_end, c["i1130"])
            if res: found.append((res["fill_i"], cand["trig_i"], side, cand, res))
    if not found: return None
    found.sort(key=lambda x: (x[0], x[1]))
    fill_i, _, side, cand, res = found[0]
    sgn = 1 if side == "long" else -1
    px = lambda v: None if v is None else sgn * v
    return dict(side=side, cand=cand, res=res, entry=px(cand["entry"]), stop=px(cand["stop"]), t1=px(cand["t1"]), t2=px(cand["t2"]),
                fvg=(None if cand["fvg_lo"] is None else tuple(sorted((px(cand["fvg_lo"]), px(cand["fvg_hi"]))))),
                sweep_px=px(cand["sweep_px"]), leg=(None if "leg" not in cand else (cand["leg"][0], px(cand["leg"][1]), px(cand["leg"][2]))))

