"""Shared screening helpers: run the UNCHANGED REV pipeline on a BID/ASK pair, cluster bootstrap, Holm."""
from __future__ import annotations

from datetime import date

import numpy as np

SEED, B = 20261004, 10000
BURNED = (date(2025, 8, 25), date(2026, 9, 25))


def run_rev(sym: str, bid, ask, other=None) -> tuple[list[dict], int]:
    """(trades, n_trading_days) for the H016b rule (triggers off, calendar on, flat book, correct-side fills)."""
    from ftn.pipeline.invariance import base_cfg
    from ftn.research.bars import trading_days
    from ftn.research.daycontext import History
    from ftn.research.score import run_series
    days = trading_days(bid)
    h = History(bid, days, ask=ask, calendar=True)
    _, _, trades = run_series(sym, bid.source, base_cfg(), other, False, hist=h, cost_model="correct_side")
    return [slim(t, sym) for t in trades], len(days)


def slim(t: dict, sym: str) -> dict:
    return {"symbol": sym, "date": t["date"], "session": t["session"], "R": float(t["R"]),
            "risk_pts": float(t["risk_pts"]), "weekday": date.fromisoformat(t["date"]).weekday()}


def burned_trades() -> list[dict]:
    """The 258 registered H016b-input burned trades (= F1 guard regeneration, byte-identical)."""
    import csv
    from ftn.pipeline.invariance import registration_csv
    out = []
    for sym in ("US100", "US500"):
        for r in csv.DictReader(open(registration_csv(sym))):
            out.append(slim(r, sym))
    return out


def _w(n_clusters: int, seed=SEED, b=B):
    rng = np.random.default_rng(seed)
    return rng.multinomial(n_clusters, np.full(n_clusters, 1 / n_clusters), size=b).astype(float)


def cluster_boot(trades: list[dict], key="R", seed=SEED, b=B) -> dict:
    """mean, 95% percentile CI, one-sided p(mean <= 0), bootstrap variance of the mean (cluster = date, session)."""
    if not trades:
        return {"n": 0, "mean": None, "lo": None, "hi": None, "p_le0": 1.0, "var": None, "clusters": 0}
    R = np.array([t[key] for t in trades])
    ks = sorted({(t["date"], t["session"]) for t in trades}); ix = {k: i for i, k in enumerate(ks)}
    cl = np.array([ix[(t["date"], t["session"])] for t in trades])
    W = _w(len(ks), seed, b)
    s = W @ np.bincount(cl, weights=R, minlength=len(ks)); n = W @ np.bincount(cl, minlength=len(ks)).astype(float)
    m = s[n > 0] / n[n > 0]
    return {"n": int(len(R)), "mean": float(R.mean()), "lo": float(np.percentile(m, 2.5)), "hi": float(np.percentile(m, 97.5)),
            "p_le0": float(max((m <= 0).mean(), 1 / b)), "var": float(m.var()), "clusters": len(ks),
            "win": float((R > 0).mean()), "total": float(R.sum()), "sd": float(R.std())}


def holm(ps: dict) -> dict:
    items = sorted(ps.items(), key=lambda kv: kv[1]); k = len(items); out, run = {}, 0.0
    for r, (name, p) in enumerate(items):
        run = max(run, min(1.0, (k - r) * p)); out[name] = run
    return out
