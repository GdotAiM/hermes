"""Batch 1 (protocol v1 section 4): C1 REV baseline, C2 REV Wednesday-only, C3 REV US500-only.

  python -m research.screening.batch1 s3       # nulls on the burned tape (cached: batch1/s3_nulls.json)
  python -m research.screening.batch1 s1       # specs + REV on the new instruments (needs dl build; batch1/s1_*.json)
  python -m research.screening.batch1 report   # S1-S3 verdicts, holdout power, gate -> batch1/results.json, REPORT.md
"""
from __future__ import annotations

import json
import math
import sys
from datetime import date
from multiprocessing import Pool
from pathlib import Path

import numpy as np

from research.screening import core

OUT = Path(__file__).resolve().parent / "batch1"
ALPHA_SCREEN = 0.10
N_NULL = 50
HOLDOUT_DAYS = {"US100": 1004, "US500": 1612}
ERA_MULT, ERA_SENS = 1.5, 2.0
SHRINK = 0.5
S1_ALL = ("GER40", "US30", "XAUUSD")
CANDIDATES = {
    "C1": {"name": "REV baseline", "burned": lambda t: True, "s1_syms": S1_ALL, "s1": lambda t: True,
           "holdout": ("US100", "US500")},
    "C2": {"name": "REV Wednesday-only", "burned": lambda t: t["weekday"] == 2, "s1_syms": S1_ALL,
           "s1": lambda t: t["weekday"] == 2, "holdout": ("US100", "US500")},
    "C3": {"name": "REV US500-only", "burned": lambda t: t["symbol"] == "US500", "s1_syms": ("GER40", "US30"),
           "s1": lambda t: True, "holdout": ("US500",)},
}


# ---------------------------------------------------------------- S3 nulls
_H = {}


def _init():
    from ftn.pipeline import invariance as inv
    from research.screening import nulls
    H = inv.load_histories()
    for s, h in H.items():
        _H[s] = (h.s, h.ask, nulls.minute_sigma(h.s))


def _null_task(job):
    from research.screening import nulls
    kind, sym, k = job
    bid, ask, sig = _H[sym]
    seed = core.SEED + k
    b, a = nulls.shuffled_day(bid, ask, seed) if kind == "A" else nulls.random_walk(bid, ask, seed, sig)
    tr, nd = core.run_rev(sym, b, a)
    return kind, sym, k, tr


def run_s3(workers=5):
    jobs = [(kind, sym, k) for kind in ("A", "B") for k in range(N_NULL) for sym in ("US100", "US500")]
    res = {}
    with Pool(workers, initializer=_init) as p:
        for i, (kind, sym, k, tr) in enumerate(p.imap_unordered(_null_task, jobs), 1):
            res[f"{kind}|{sym}|{k}"] = tr
            if i % 20 == 0:
                print(f"s3 {i}/{len(jobs)}", flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "s3_nulls.json").write_text(json.dumps(res))


# ---------------------------------------------------------------- S1 new instruments
def run_s1():
    import os
    from ftn.pipeline import invariance as inv
    from ftn.research.bars import load_series
    from research.screening import instruments as ins
    droot = Path(os.environ.get("SCREENING_DATA", "/workspace/screening-data"))
    us500 = inv.load_histories()["US500"].s
    bp = ins.us500_price_bp(us500)
    specs, trades, cov = {}, {}, {}
    for sym in S1_ALL:
        pb, pa = droot / f"{sym}_1m_bid.csv.gz", droot / f"{sym}_1m_ask.csv.gz"
        if not (pb.is_file() and pa.is_file()):
            cov[sym] = {"status": "no_data"}; continue
        bid, ask = load_series(pb, sym), load_series(pa, sym)
        assert max(bid.t).date() <= date(2026, 9, 25) and min(bid.t).date() >= date(2022, 12, 31)
        sp = ins.measure(sym, bid, ask, bp)
        specs[sym] = sp
        (OUT / "s1_specs.json").write_text(json.dumps(specs, indent=1))   # specs fixed BEFORE outcomes
        ins.register(sp)
        tr, nd = core.run_rev(sym, bid, ask)
        trades[sym] = tr
        cov[sym] = {"first_bar": str(bid.t[0]), "last_bar": str(bid.t[-1]), "trading_days": nd,
                    "status": "ok" if nd >= 200 else "not_applicable_lt_200_days"}
        print(sym, cov[sym], flush=True)
    OUT.mkdir(exist_ok=True)
    (OUT / "s1_trades.json").write_text(json.dumps({"coverage": cov, "trades": trades, "us500_price_bp": bp}))


# ---------------------------------------------------------------- report
def _mean(xs):
    return float(np.mean(xs)) if xs else None


def folds(days, k=4):
    days = sorted(days); n = len(days)
    return [(days[i * n // k], days[(i + 1) * n // k - 1]) for i in range(k)]


def power(mu, sd, deff, n):
    if mu is None or n <= 0 or sd <= 0 or mu <= 0:
        return 0.025 if mu is not None and mu <= 0 else None
    z = mu / (sd * math.sqrt(deff / n)) - 1.959964
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def n_for_power(mu, sd, deff, target=0.8):
    if mu is None or mu <= 0:
        return None
    return math.ceil(((1.959964 + 0.841621) * sd / mu) ** 2 * deff)


def report():
    from ftn.os.instruments import spec
    from ftn.pipeline import invariance as inv
    from ftn.research.bars import trading_days
    H = inv.load_histories()
    bdays = {s: trading_days(h.s) for s, h in H.items()}
    union_days = sorted({d.isoformat() for v in bdays.values() for d in v})
    fb = folds(union_days)
    burned = core.burned_trades()
    for t in burned:
        ins = spec(t["symbol"]); fr = ins.spread_assumed + ins.slip_market + ins.slip_stop
        t["R_era"] = t["R"] - (ERA_MULT - 1) * fr / t["risk_pts"]
        t["R_era2"] = t["R"] - (ERA_SENS - 1) * fr / t["risk_pts"]
    s1 = json.loads((OUT / "s1_trades.json").read_text()) if (OUT / "s1_trades.json").is_file() else {"coverage": {}, "trades": {}}
    s1_ok = {s for s, c in s1["coverage"].items() if c.get("status") == "ok"}
    nulls = json.loads((OUT / "s3_nulls.json").read_text())
    dlrep = {}
    try:
        dlrep = json.loads(Path("/workspace/screening-data/build_report.json").read_text())
    except OSError:
        pass
    res = {}
    for cid, c in CANDIDATES.items():
        bt = [t for t in burned if c["burned"](t)]
        bs = core.cluster_boot(bt)
        # S1
        st = [t for s in c["s1_syms"] if s in s1_ok for t in s1["trades"][s] if c["s1"](t)]
        s1b = core.cluster_boot(st)
        per = {s: core.cluster_boot([t for t in s1["trades"].get(s, []) if c["s1"](t)]) for s in c["s1_syms"] if s in s1_ok}
        elig = [s for s, v in per.items() if v["n"] >= 20]
        maj = sum(1 for s in elig if v_mean_pos(per[s])) * 2 > len(elig) if elig else False
        # S2
        s2a = [[t["R"] for t in bt if a <= t["date"] <= b] for a, b in fb]
        s2a_pos = sum(1 for f in s2a if len(f) >= 10 and np.mean(f) > 0)
        yrs = ("2023", "2024", "2025", "2026")
        s2b = [[t["R"] for t in st if t["date"][:4] == y] for y in yrs]
        s2b_pos = sum(1 for f in s2b if len(f) >= 10 and np.mean(f) > 0)
        # S3
        real = bs["mean"]; p3 = {}; nullm = {}
        for kind in ("A", "B"):
            ms = []
            for k in range(N_NULL):
                tr = [t for s in ("US100", "US500") for t in nulls[f"{kind}|{s}|{k}"] if c["burned"](t)]
                ms.append(_mean([t["R"] for t in tr]))
            ge = sum(1 for m in ms if m is None or m >= real)
            p3[kind] = (1 + ge) / (N_NULL + 1)
            vals = [m for m in ms if m is not None]
            nullm[kind] = {"mean": _mean(vals), "p95": float(np.percentile(vals, 95)) if vals else None,
                           "n_trades_mean": _mean([sum(1 for s in ("US100", "US500") for t in nulls[f"{kind}|{s}|{k}"] if c["burned"](t)) for k in range(N_NULL)])}
        # power
        era = core.cluster_boot(bt, key="R_era")
        era2 = core.cluster_boot(bt, key="R_era2")
        sd = float(np.std([t["R_era"] for t in bt]))
        deff = max(1.0, era["var"] / (sd ** 2 / len(bt)))
        rate = {s: sum(1 for t in bt if t["symbol"] == s) / len(bdays[s]) for s in c["holdout"]}
        n_hold = sum(rate[s] * HOLDOUT_DAYS[s] for s in c["holdout"])
        s1_mean = s1b["mean"] if s1b["n"] else 0.0
        mu_plan = SHRINK * min(era["mean"], s1_mean)
        res[cid] = dict(name=c["name"], burned=bs, burned_eligible254=None, s1=s1b, s1_per_instrument=per,
                        s1_majority_positive=maj, s1_instruments=[s for s in c["s1_syms"] if s in s1_ok],
                        s2a_folds=[{"from": a, "to": b, "n": len(f), "mean": _mean(f)} for (a, b), f in zip(fb, s2a)],
                        s2b_folds=[{"year": y, "n": len(f), "mean": _mean(f)} for y, f in zip(yrs, s2b)],
                        s2a_pos=s2a_pos, s2b_pos=s2b_pos, s3_p=p3, s3_p_max=max(p3.values()), s3_null=nullm,
                        era=era, era2_mean=era2["mean"], sd_era=sd, deff=deff, rate=rate, n_hold=n_hold,
                        mu_plan=mu_plan, s1_mean_for_plan=s1_mean,
                        power=power(mu_plan, sd, deff, n_hold),
                        power_unshrunk=power(era["mean"], sd, deff, n_hold),
                        n_for_08_at_mu_plan=n_for_power(mu_plan, sd, deff))
    h1 = core.holm({k: v["s1"]["p_le0"] if v["s1"]["n"] else 1.0 for k, v in res.items()})
    h3 = core.holm({k: v["s3_p_max"] for k, v in res.items()})
    for k, v in res.items():
        v["s1_holm"], v["s3_holm"] = h1[k], h3[k]
        v["S1"] = "PASS" if v["s1"]["n"] >= 30 and h1[k] <= ALPHA_SCREEN and v["s1_majority_positive"] else "FAIL"
        v["S2"] = "PASS" if v["s2a_pos"] >= 3 and v["s2b_pos"] >= 3 else "FAIL"
        v["S3"] = "PASS" if h3[k] <= ALPHA_SCREEN and v["burned"]["mean"] > 0 else "FAIL"
        v["power_ok"] = bool(v["power"] is not None and v["power"] >= 0.8)
        v["QUALIFIES"] = all(v[s] == "PASS" for s in ("S1", "S2", "S3")) and v["power_ok"]
    meta = {"protocol": "research/screening/PROTOCOL.md v1", "s1_coverage": s1["coverage"], "download_build": dlrep,
            "s1_specs": json.loads((OUT / "s1_specs.json").read_text()) if (OUT / "s1_specs.json").is_file() else {},
            "burned_trading_days": {s: len(v) for s, v in bdays.items()}, "s2a_fold_bounds": fb}
    (OUT / "results.json").write_text(json.dumps({"meta": meta, "candidates": res}, indent=1, default=str))
    return meta, res


def v_mean_pos(v):
    return v["mean"] is not None and v["mean"] > 0


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    {"s3": run_s3, "s1": run_s1, "report": lambda: write_md(*report())}[sys.argv[1]]()


def write_md(meta, res):
    f = lambda x, d=3: "—" if x is None else (f"{x:+.{d}f}" if isinstance(x, float) else str(x))
    L = ["# Screening batch 1: C1 REV baseline, C2 Wednesday-only, C3 US500-only", "",
         "> **Screening, not evidence.** Protocol `research/screening/PROTOCOL.md` v1 was committed (`d42f966`) before any run.",
         "> The burned window is burned, and C2 was chosen by looking at it. A PASS here would only *earn* a holdout; the holdout "
         "(US100 2019-01-01..2022-12-23, US500 before 2025-06-01) stays SEALED and was not opened, decoded or hashed.", ""]
    cov = meta["s1_coverage"]
    L += ["## Data", "",
          f"- Burned: US100/US500 canonical BID+ASK tape 2025-08-25..2026-09-25 (trading days {meta['burned_trading_days']}), 258 registered trades.",
          "- S1: fresh Dukascopy BID+ASK 1m, UTC days 2023-01-01..2026-09-25:"]
    for s, c in cov.items():
        L.append(f"  - {s}: {c}")
    L += ["", "S1 instrument specs (protocol §2 rules, measured on 2025-08-25..2026-09-25 of the new data; fixed before outcomes):", "",
          "| instrument | pip | range_scale | spread_assumed | slip stop/market | slip limit | min_risk |", "|---|---:|---:|---:|---:|---:|---:|"]
    for s, sp in meta["s1_specs"].items():
        mr = 4 * (sp["spread_assumed"] + 2 * sp["slip_stop"])
        L.append(f"| {s} | {sp['pip']} | {sp['range_scale']} | {sp['spread_assumed']} | {sp['slip_stop']} | {sp['slip_limit']} | {mr:.3f} |")
    for cid, v in res.items():
        b, s1 = v["burned"], v["s1"]
        L += ["", f"## {cid}: {v['name']}", "",
              "| set | N | mean R | 95% CI (cluster) | win | total R |", "|---|---:|---:|---|---:|---:|",
              f"| burned US100/US500 | {b['n']} | {f(b['mean'])} | [{f(b['lo'])}, {f(b['hi'])}] | {b['win']:.1%} | {b['total']:+.1f} |"]
        if s1["n"]:
            L.append(f"| S1 pooled ({', '.join(v['s1_instruments'])}) | {s1['n']} | {f(s1['mean'])} | [{f(s1['lo'])}, {f(s1['hi'])}] | {s1['win']:.1%} | {s1['total']:+.1f} |")
        for s, p in v["s1_per_instrument"].items():
            if p["n"]:
                L.append(f"| S1 {s} | {p['n']} | {f(p['mean'])} | [{f(p['lo'])}, {f(p['hi'])}] | {p['win']:.1%} | {p['total']:+.1f} |")
        L += ["", f"- **S1 {v['S1']}**: one-sided p = {s1['p_le0']:.4f}, Holm = {v['s1_holm']:.4f} (needs ≤ 0.10, ≥ 30 trades, and a majority of instruments positive: {v['s1_majority_positive']}).",
              f"- **S2 {v['S2']}**: burned folds positive {v['s2a_pos']}/4 "
              + ", ".join(f"{x['from']}..{x['to']} n={x['n']} {f(x['mean'])}" for x in v["s2a_folds"])
              + f"; S1 year folds positive {v['s2b_pos']}/4 " + ", ".join(f"{x['year']} n={x['n']} {f(x['mean'])}" for x in v["s2b_folds"]) + ".",
              f"- **S3 {v['S3']}**: shuffled-day p = {v['s3_p']['A']:.3f} (null mean {f(v['s3_null']['A']['mean'])}, p95 {f(v['s3_null']['A']['p95'])}, "
              f"~{v['s3_null']['A']['n_trades_mean']:.0f} trades/rep); random-walk p = {v['s3_p']['B']:.3f} (null mean {f(v['s3_null']['B']['mean'])}, "
              f"p95 {f(v['s3_null']['B']['p95'])}, ~{v['s3_null']['B']['n_trades_mean']:.0f} trades/rep); max = {v['s3_p_max']:.3f}, Holm = {v['s3_holm']:.3f}.",
              f"- **Holdout power**: era-cost (×1.5) burned mean {f(v['era']['mean'])} (×2.0: {f(v['era2_mean'])}); μ_plan = 0.5 × min({f(v['era']['mean'])}, S1 {f(v['s1_mean_for_plan'])}) = {f(v['mu_plan'])}; "
              f"σ {v['sd_era']:.3f}, deff {v['deff']:.2f}; projected holdout N = {v['n_hold']:.0f} ({', '.join(f'{k} {r:.3f}/day' for k, r in v['rate'].items())}); "
              f"**power = {v['power']:.3f}** (unshrunk {f(v['power_unshrunk'])}; N for 0.8 at μ_plan: {v['n_for_08_at_mu_plan'] or 'n/a, μ_plan ≤ 0'}).",
              f"- **Gate: {'QUALIFIES' if v['QUALIFIES'] else 'does NOT qualify'}**."]
    L += ["", "## Summary", "", "| candidate | burned N | burned mean R [CI] | S1 N | S1 mean R [CI] | S1 | S2 | S3 | holdout power | qualifies |",
          "|---|---:|---|---:|---|---|---|---|---:|---|"]
    for cid, v in res.items():
        b, s1 = v["burned"], v["s1"]
        L.append(f"| {cid} {v['name']} | {b['n']} | {f(b['mean'])} [{f(b['lo'])}, {f(b['hi'])}] | {s1['n']} | "
                 f"{f(s1['mean'])} [{f(s1['lo'])}, {f(s1['hi'])}] | {v['S1']} | {v['S2']} | {v['S3']} | {v['power']:.3f} | {'yes' if v['QUALIFIES'] else 'no'} |")
    L += ["", "Holm per stage across the 3 candidates of this batch at α_screen = 0.10 (S1 and S3). S2 is rule-based.", ""]
    (OUT / "REPORT.md").write_text("\n".join(L) + "\n")
