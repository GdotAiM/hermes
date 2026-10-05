"""Screening batch 3 (PROTOCOL.md v1 + PROTOCOL_BATCH3.md): simple rules E1..E5.
Subcommands: burned | s1 | s3 | report."""
from __future__ import annotations

import gzip
import json
import os
import sys
from multiprocessing import Pool
from datetime import date
from pathlib import Path

import numpy as np

from research.screening import core
from research.screening.batch1 import folds, power, n_for_power, _mean, v_mean_pos

OUT = Path(__file__).resolve().parent / "batch3"
ALPHA_SCREEN, N_NULL, SHRINK, ERA_MULT, ERA_SENS = 0.10, 50, 0.5, 1.5, 2.0
HOLDOUT_DAYS = {"US100": 1004, "US500": 1612}
S1_ALL = ("GER40", "US30", "XAUUSD")
FRICTION = {"US100": 1.55 + 0.5 + 0.5, "US500": 0.72 + 0.25 + 0.25, "GER40": 2.624 + 0.884 + 0.884,
            "US30": 2.17 + 1.775 + 1.775, "XAUUSD": 0.84 + 0.281 + 0.281}
NAMES = {"E1": "Asia/London range sweep reversal", "E2": "PDH/PDL sweep reversal", "E3": "PD range breakout continuation",
         "E4": "30m opening-range breakout", "E5": "30m opening-range fade"}
HOLDOUT = {k: ("US100", "US500") for k in NAMES}
RANGES = {"burned": (date(2025, 8, 25), date(2026, 9, 25)), "s1": (date(2023, 1, 1), date(2026, 9, 25))}


def run_cand(cid, sym, s, rng):
    from research.screening.batch3 import rules
    return rules.run_rule(cid, sym, s, FRICTION[sym], *RANGES[rng])


_H = {}


def _init_burned():
    from ftn.pipeline import invariance as inv
    from research.screening import nulls
    for s, h in inv.load_histories().items():
        _H[s] = (h.s, h.ask, nulls.minute_sigma(h.s))


def _burned_task(job):
    cid, sym = job
    return job, run_cand(cid, sym, _H[sym][0], "burned")


def run_burned(workers=6):
    jobs = [(c, s) for c in NAMES for s in ("US100", "US500")]
    res = {}
    with Pool(workers, initializer=_init_burned) as p:
        for (c, s), tr in p.imap_unordered(_burned_task, jobs):
            res[f"{c}|{s}|primary"] = tr
    OUT.mkdir(exist_ok=True)
    (OUT / "burned_trades.json").write_text(json.dumps(res))


def _s1_task(job):
    from ftn.research.bars import load_series
    cid, sym = job
    droot = Path(os.environ.get("SCREENING_DATA", "/workspace/screening-data"))
    s = load_series(droot / f"{sym}_1m_bid.csv.gz", sym)
    assert str(max(s.t))[:10] <= "2026-09-25" and str(min(s.t))[:10] >= "2022-12-31"
    return job, run_cand(cid, sym, s, "s1"), (str(s.t[0]), str(s.t[-1]))


def run_s1(workers=6):
    jobs = [(c, s) for c in NAMES for s in S1_ALL]
    res, cov = {}, {}
    with Pool(workers) as p:
        for (c, s), tr, span in p.imap_unordered(_s1_task, jobs):
            res[f"{c}|{s}"] = tr; cov[s] = span
            print("s1", c, s, len(tr), flush=True)
    (OUT / "s1_trades.json").write_text(json.dumps({"coverage": cov, "trades": res, "friction": FRICTION}))


def _null_task(job):
    from research.screening import nulls
    kind, sym, k = job
    bid, ask, sig = _H[sym]
    seed = core.SEED + k
    b, _ = nulls.shuffled_day(bid, ask, seed) if kind == "A" else nulls.random_walk(bid, ask, seed, sig)
    out = {}
    for cid in NAMES:
        out[cid] = run_cand(cid, sym, b, "burned")
    return kind, sym, k, out


def run_s3(workers=6):
    jobs = [(kind, sym, k) for kind in ("A", "B") for k in range(N_NULL) for sym in ("US100", "US500")]
    res = {}
    with Pool(workers, initializer=_init_burned) as p:
        for i, (kind, sym, k, out) in enumerate(p.imap_unordered(_null_task, jobs), 1):
            for cid, tr in out.items():
                res[f"{cid}|{kind}|{sym}|{k}"] = tr
            if i % 20 == 0:
                print(f"s3 {i}/{len(jobs)}", flush=True)
    with gzip.open(OUT / "s3_nulls.json.gz", "wt") as fh:
        json.dump(res, fh)


def report():
    from ftn.pipeline import invariance as inv
    from ftn.research.bars import trading_days
    H = inv.load_histories()
    bdays = {s: trading_days(h.s) for s, h in H.items()}
    fb = folds(sorted({d.isoformat() for v in bdays.values() for d in v}))
    B = json.loads((OUT / "burned_trades.json").read_text())
    S1 = json.loads((OUT / "s1_trades.json").read_text())
    with gzip.open(OUT / "s3_nulls.json.gz", "rt") as fh:
        NU = json.load(fh)
    res = {}
    for cid, name in NAMES.items():
        syms = HOLDOUT[cid]
        bt = [t for s in syms for t in B[f"{cid}|{s}|primary"]]
        for t in bt:
            fr = FRICTION[t["symbol"]]
            t["R_era"] = t["R"] - (ERA_MULT - 1) * fr / t["risk_pts"]
            t["R_era2"] = t["R"] - (ERA_SENS - 1) * fr / t["risk_pts"]
        bs = core.cluster_boot(bt)
        prim_all = {s: core.cluster_boot(B[f"{cid}|{s}|primary"]) for s in ("US100", "US500")}
        st = [t for s in S1_ALL for t in S1["trades"][f"{cid}|{s}"]]
        s1b = core.cluster_boot(st)
        per = {s: core.cluster_boot(S1["trades"][f"{cid}|{s}"]) for s in S1_ALL}
        elig = [s for s, v in per.items() if v["n"] >= 20]
        maj = sum(1 for s in elig if v_mean_pos(per[s])) * 2 > len(elig) if elig else False
        s2a = [[t["R"] for t in bt if a <= t["date"] <= b] for a, b in fb]
        s2a_pos = sum(1 for f in s2a if len(f) >= 10 and np.mean(f) > 0)
        yrs = ("2023", "2024", "2025", "2026")
        s2b = [[t["R"] for t in st if t["date"][:4] == y] for y in yrs]
        s2b_pos = sum(1 for f in s2b if len(f) >= 10 and np.mean(f) > 0)
        real = bs["mean"]; p3 = {}; nullm = {}
        for kind in ("A", "B"):
            ms, ns = [], []
            for k in range(N_NULL):
                tr = [t for s in syms for t in NU[f"{cid}|{kind}|{s}|{k}"]]
                ms.append(_mean([t["R"] for t in tr])); ns.append(len(tr))
            ge = sum(1 for m in ms if m is None or real is None or m >= real)
            p3[kind] = (1 + ge) / (N_NULL + 1)
            vals = [m for m in ms if m is not None]
            nullm[kind] = {"mean": _mean(vals), "p95": float(np.percentile(vals, 95)) if vals else None, "n_trades_mean": _mean(ns)}
        era = core.cluster_boot(bt, key="R_era"); era2 = core.cluster_boot(bt, key="R_era2")
        sd = float(np.std([t["R_era"] for t in bt])) if bt else 0.0
        deff = max(1.0, era["var"] / (sd ** 2 / len(bt))) if bt and sd > 0 else 1.0
        rate = {s: sum(1 for t in bt if t["symbol"] == s) / len(bdays[s]) for s in syms}
        n_hold = sum(rate[s] * HOLDOUT_DAYS[s] for s in syms)
        s1_mean = s1b["mean"] if s1b["n"] else 0.0
        mu_plan = SHRINK * min(era["mean"], s1_mean) if era["n"] else None
        res[cid] = dict(name=name, burned_set=list(syms), burned=bs, burned_by_symbol_primary=prim_all, s1=s1b, s1_per_instrument=per, s1_majority_positive=maj,
                        s2a_folds=[{"from": a, "to": b, "n": len(f), "mean": _mean(f)} for (a, b), f in zip(fb, s2a)],
                        s2b_folds=[{"year": y, "n": len(f), "mean": _mean(f)} for y, f in zip(yrs, s2b)],
                        s2a_pos=s2a_pos, s2b_pos=s2b_pos, s3_p=p3, s3_p_max=max(p3.values()), s3_null=nullm,
                        era=era, era2_mean=era2["mean"], sd_era=sd, deff=deff, rate=rate, n_hold=n_hold, mu_plan=mu_plan,
                        s1_mean_for_plan=s1_mean, power=power(mu_plan, sd, deff, n_hold),
                        power_ceiling=power(SHRINK * era["mean"], sd, deff, n_hold) if era["n"] else None,
                        power_unshrunk=power(era["mean"], sd, deff, n_hold) if era["n"] else None,
                        n_for_08_at_mu_plan=n_for_power(mu_plan, sd, deff))
    h1 = core.holm({k: v["s1"]["p_le0"] if v["s1"]["n"] else 1.0 for k, v in res.items()})
    h3 = core.holm({k: v["s3_p_max"] for k, v in res.items()})
    for k, v in res.items():
        v["s1_holm"], v["s3_holm"] = h1[k], h3[k]
        v["S1"] = "PASS" if v["s1"]["n"] >= 30 and h1[k] <= ALPHA_SCREEN and v["s1_majority_positive"] else "FAIL"
        v["S2"] = "PASS" if v["s2a_pos"] >= 3 and v["s2b_pos"] >= 3 else "FAIL"
        v["S3"] = "PASS" if h3[k] <= ALPHA_SCREEN and (v["burned"]["mean"] or 0) > 0 else "FAIL"
        v["power_ok"] = bool(v["power"] is not None and v["power"] >= 0.8)
        v["QUALIFIES"] = all(v[s] == "PASS" for s in ("S1", "S2", "S3")) and v["power_ok"]
    meta = {"protocol": "research/screening/PROTOCOL.md v1 + PROTOCOL_BATCH3.md", "s1_coverage": S1["coverage"],
            "friction": FRICTION, "burned_trading_days": {s: len(v) for s, v in bdays.items()},
            "s2a_fold_bounds": fb}
    (OUT / "results.json").write_text(json.dumps({"meta": meta, "candidates": res}, indent=1, default=str))
    return meta, res


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    if sys.argv[1] != "report":
        {"burned": run_burned, "s1": run_s1, "s3": run_s3}[sys.argv[1]]()


def write_md(meta, res):
    f = lambda x, d=3: "—" if x is None else (f"{x:+.{d}f}" if isinstance(x, float) else str(x))
    pw = lambda x: "—" if x is None else f"{x:.3f}"
    L = ["# Screening batch 3: simple session-level rules E1–E5", "",
         "> **Screening.** The protocol is `PROTOCOL.md` v1 + `PROTOCOL_BATCH3.md`, committed and pushed before any batch 3 data was read.",
         "> The burned US100/US500 window is *discovery* for these new rules; S1 (GER40, US30, XAUUSD 2023-01..2026-09-25) is the real out-of-sample test. The H017 holdout was not read.", "",
         "Costs: friction F as a round trip in points (US100 2.55, US500 1.22, GER40 4.392, US30 5.720, XAUUSD 1.402). Holm across the 5 rules at α_screen = 0.10 (S1, S3).", ""]
    for cid, v in res.items():
        b, s1 = v["burned"], v["s1"]
        L += [f"## {cid} {v['name']}", "",
              "| set | N | mean R | 95% CI | win | total R |", "|---|---:|---:|---|---:|---:|"]
        for lab, x in ((f"burned {'+'.join(v['burned_set'])} (primary cost)", b),
                       *((f"burned {s}", v["burned_by_symbol_primary"][s]) for s in ("US100", "US500")),
                       ("S1 pooled", s1), *((f"S1 {s}", x) for s, x in v["s1_per_instrument"].items())):
            L.append(f"| {lab} | {x['n']} | {f(x['mean'])} | [{f(x['lo'])}, {f(x['hi'])}] | "
                     f"{'—' if x['n'] == 0 else format(x['win'], '.2f')} | {'—' if x['n'] == 0 else format(x['total'], '+.1f')} |")
        L += ["", f"- **S1 {v['S1']}**: one-sided p = {s1['p_le0']:.4f}, Holm = {v['s1_holm']:.4f}; majority of instruments positive: {v['s1_majority_positive']}.",
              f"- **S2 {v['S2']}**: burned folds positive {v['s2a_pos']}/4 (" + ", ".join(f"n={x['n']} {f(x['mean'])}" for x in v["s2a_folds"])
              + f"); S1 year folds positive {v['s2b_pos']}/4 (" + ", ".join(f"{x['year']} n={x['n']} {f(x['mean'])}" for x in v["s2b_folds"]) + ").",
              f"- **S3 {v['S3']}**: shuffled-day p = {v['s3_p']['A']:.3f} (null mean {f(v['s3_null']['A']['mean'])}, ~{v['s3_null']['A']['n_trades_mean']:.0f} trades/rep); "
              f"random-walk p = {v['s3_p']['B']:.3f} (null mean {f(v['s3_null']['B']['mean'])}, ~{v['s3_null']['B']['n_trades_mean']:.0f} trades/rep); max {v['s3_p_max']:.3f}, Holm {v['s3_holm']:.3f}.",
              f"- **Holdout power** ({'+'.join(v['burned_set'])}): era mean {f(v['era']['mean'])} (×2.0: {f(v['era2_mean'])}); μ_plan {f(v['mu_plan'])}; σ {v['sd_era']:.3f}; deff {v['deff']:.2f}; "
              f"projected N {v['n_hold']:.0f}; **power {pw(v['power'])}**, ceiling {pw(v['power_ceiling'])}, unshrunk {pw(v['power_unshrunk'])}.",
              f"- **Gate: {'QUALIFIES' if v['QUALIFIES'] else 'does NOT qualify'}**.", ""]
    L += ["## Summary", "", "| candidate | burned N | burned mean R [CI] | S1 N | S1 mean R [CI] | S1 | S2 | S3 | holdout power | power ceiling | qualifies |",
          "|---|---:|---|---:|---|---|---|---|---:|---:|---|"]
    for cid, v in res.items():
        b, s1 = v["burned"], v["s1"]
        L.append(f"| {cid} {v['name']} | {b['n']} | {f(b['mean'])} [{f(b['lo'])}, {f(b['hi'])}] | {s1['n']} | {f(s1['mean'])} [{f(s1['lo'])}, {f(s1['hi'])}] | "
                 f"{v['S1']} | {v['S2']} | {v['S3']} | {pw(v['power'])} | {pw(v['power_ceiling'])} | {'yes' if v['QUALIFIES'] else 'no'} |")
    L += ["", "Power ceiling = gate power if S1 ≥ burned era mean (μ_plan = 0.5 × burned era mean). It is a derived bound, not a protocol change.", ""]
    L += READING
    (OUT / "REPORT.md").write_text("\n".join(L) + "\n")
    return L


READING = ["## Reading (screening caveats)", "",
           "- **No rule qualifies.** All five fail S1, S2 and S3, and the gate power is 0.025 for each, because the burned era-cost mean and the S1 mean are both ≤ 0 for every rule (so even the power ceiling is 0.025).",
           "- **S1 (the real out-of-sample test):** all five pooled S1 means are negative, and every CI excludes 0. Of the 15 rule × instrument cells, only E2 on US30 is positive (+0.058R, CI spans 0). No S1 calendar year is positive for any rule.",
           "- **Burned (discovery):** every pooled burned mean is ≤ 0. The best single-instrument cells (E2 US100 +0.089R, E5 US100 +0.031R) do not carry over to US500 or to S1.",
           "- **E1** (Asia/London sweep reversal) is the worst rule: −0.23R on burned and −0.32R on S1. Sweeps of the overnight range during NY AM did not reverse on average.",
           "- **E4/E5** are exact mirrors and fire on the same 492 burned / 2,540 S1 signals. Both lose by about the cost, i.e. the 30-minute opening-range break carries no directional edge either way at 2R / 0.25 ATR.",
           "- **S3:** the real burned means sit inside both null distributions (max p 0.43–0.96). The rules do no better than they do on shuffled-day or random-walk tape.",
           "- **Caveats:** results are at realistic cost F only (gross was not pre-registered and is not reported). One fixed parameter set was tested per rule, by design. The rules are discarded, not re-tuned.", ""]


if __name__ == "__main__" and sys.argv[1] == "report":
    write_md(*report())
