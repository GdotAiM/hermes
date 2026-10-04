"""``ftn score`` — EXPLORATORY scorer for FTN month-layer hypotheses.

Pipeline: 1m bars → bar-derived DayContext → unchanged Month 9 kernel → per-session ticket
log → research-draft gate chain (allowlist empty, I0 contract gate) → R outcome (2R / stop / 16:00) → conditional
comparisons per hypothesis (bootstrap CI + permutation p + Holm) + a random-entry foil.

Nothing here trades, routes, or writes to MINT. Every output is marked EXPLORATORY and
pending CASSANDRA / DATA review. The tape has already been used by H013 / H014 (burned).
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
from copy import deepcopy
from datetime import date, datetime, time, timedelta
from pathlib import Path
from statistics import mean

from ftn.config_load import load_config, repo_root
from ftn.research import stats
from ftn.research.bars import load_series, trading_days
from ftn.research.daycontext import History
from ftn.research.features import compute
from ftn.research.hypotheses import HYPOTHESES
from ftn.research.kernel_log import KILLZONES, session_ticket_log, tradeable
from ftn.research.outcomes import TARGET_R, simulate

DEFAULT_BARS = {
    "US100": "/workspace/ict-blueprint/research/model-u-longrun/data/US100_1m.csv.gz",
    "US500": "/workspace/ict-blueprint/research/model-u-longrun/data/US500_1m.csv.gz",
}
TAPE = {"US100": "DUKASCOPY-CFD-USATECHIDXUSD-BID1M", "US500": "DUKASCOPY-CFD-USA500IDXUSD-BID1M"}
COST_PER_SIDE = {"US100": 0.8, "US500": 0.5}   # ict-blueprint model-u-longrun/data/costs.json
MIN_GROUP_N = 10
N_FOIL = 2000
BANNER = "EXPLORATORY — pending CASSANDRA + DATA review. Not a board result. No SURVIVES language."


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def foil(hist: History, trades: list[dict], cost: float, n: int = N_FOIL, seed: int = stats.SEED) -> list[float]:
    """Random-entry foil: same day + killzone, random minute, random side, same risk_pts."""
    rng = random.Random(seed)
    s = hist.s
    means = []
    for _ in range(n):
        rs = []
        for tr in trades:
            d = date.fromisoformat(tr["date"])
            a, b = KILLZONES[tr["session"]]
            mins = rng.randrange(int((datetime.combine(d, b) - datetime.combine(d, a)).total_seconds() // 60))
            et = datetime.combine(d, a) + timedelta(minutes=mins + 1)
            px = s.close_at(et)
            side = rng.choice(("buy", "sell"))
            risk = tr["risk_pts"]
            stop = px - risk if side == "buy" else px + risk
            r = simulate(s, et, px, stop, side, cost)["R"]
            if r is not None:
                rs.append(r)
        means.append(mean(rs) if rs else 0.0)
    return means


def run_series(sym: str, path: str, cfg: dict, other: History | None = None, legacy_side: bool = False,
               hist: History | None = None, log: list | None = None):
    if hist is None:
        s = load_series(path, sym)
        hist = History(s, trading_days(s))
    s = hist.s
    log = log if log is not None else session_ticket_log(hist, cfg)
    trades = []
    for row in log:
        if not tradeable(row, legacy_side):
            continue
        out = simulate(s, datetime.fromisoformat(row["entry_time"]), float(row["entry"]),
                       float(row["stop"]), row["side"], COST_PER_SIDE[sym])
        if out["R"] is None:
            continue
        row = dict(row, **out)
        row["features"] = compute(row, hist, other)
        trades.append(row)
    return hist, log, trades


def summarize(trades: list[dict]) -> dict:
    rs = [t["R"] for t in trades]
    if not rs:
        return {"n": 0}
    lo, hi = stats.boot_ci(rs)
    p25 = sorted(t["risk_pts"] for t in trades)[len(trades) // 4]
    big = [t["R"] for t in trades if t["risk_pts"] >= p25]
    top = sorted(rs, reverse=True)
    k = max(1, len(rs) // 100)
    return {"n": len(rs), "mean_R": mean(rs), "ci95": (lo, hi), "win_rate": stats.metric(rs, "win_rate"),
            "longs": len([t for t in trades if t["side"] == "buy"]),
            "shorts": len([t for t in trades if t["side"] == "sell"]),
            "mean_ex_top1pct": mean(top[k:]) if len(top) > k else None,
            "mean_ex_small_stop": mean(big) if big else None,
            "exits": {e: sum(1 for t in trades if t["exit"] == e) for e in ("stop", "target", "time")}}


def evaluate_hypotheses(trades: list[dict]) -> list[dict]:
    res = []
    for h in HYPOTHESES:
        a = [t["R"] for t in trades if t["features"].get(h.conditioning_variable) is True]
        b = [t["R"] for t in trades if t["features"].get(h.conditioning_variable) is False]
        r = {"id": h.id, "month": h.source_month, "var": h.conditioning_variable, "metric": h.metric,
             "direction": h.expected_direction, "n_true": len(a), "n_false": len(b)}
        if len(a) < MIN_GROUP_N or len(b) < MIN_GROUP_N:
            r["status"] = f"not_evaluable_n<{MIN_GROUP_N}"
        else:
            r.update(stats.diff_test(a, b, h.metric, h.expected_direction))
            r["metric_true"] = stats.metric(a, h.metric)
            r["metric_false"] = stats.metric(b, h.metric)
            r["status"] = "evaluated"
        res.append(r)
    adj = stats.holm({r["id"]: r["p_one_sided"] for r in res if r["status"] == "evaluated"})
    for r in res:
        if r["id"] in adj:
            r["p_holm"] = adj[r["id"]]
    return res


def write_ticket_csv(path: Path, log: list[dict]) -> None:
    cols = ["date", "symbol", "session", "ticket", "module", "reason", "entry_time", "direction", "entry", "stop",
            "blocked_by", "raid_level", "iof_state", "iof_confidence", "origin_pd_array", "R", "R_gross",
            "exit", "risk_pts", "cost_R", "fingerprint", "gates", "features"]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for row in log:
            r = dict(row)
            r["gates"] = "|".join(row.get("gates") or [])
            r["features"] = json.dumps(row.get("features")) if row.get("features") else ""
            w.writerow(r)


def hypotheses_doc(asof: str) -> dict:
    files = ["src/ftn/research/hypotheses.py", "src/ftn/research/features.py", "src/ftn/research/daycontext.py",
             "src/ftn/research/kernel_log.py", "src/ftn/research/outcomes.py", "src/ftn/research/stats.py",
             "src/ftn/research/score.py"]
    root = repo_root()
    return {
        "id": f"FTN-HFAMILY-{asof}",
        "title": "FTN month-layer hypotheses scored on Month 9 kernel tickets",
        "status_at_registration": "EXPLORATORY — NOT REGISTERED. Hypotheses and first scores were produced in the same change; pending CASSANDRA + DATA",
        "registered_by": "FTN research bridge (agent-generated; not ORION)",
        "registered_at": f"{asof} (SAST); git commit is the timestamp of record",
        "rule_object_root": "ftn/ (this monorepo)",
        "rule_object_sha256": {f: _sha(root / f) for f in files if (root / f).is_file()},
        "ticket_authority": "Month 9 kernel only (ftn.os.candidates.evaluate_candidates); context months never issue tickets",
        "decision_series": "US100 (DUKASCOPY-CFD-USATECHIDXUSD-BID1M), kernel tickets passing every research-draft gate except the empty allowlist and the I0 contract gate",
        "disclosure_series": "US500 (DUKASCOPY-CFD-USA500IDXUSD-BID1M) reported separately, never pooled; interpretation-trigger variant reported separately",
        "tape_status": "BURNED — same Dukascopy tape and calendar as H013/H014 OOS/IS; exploratory only",
        "exit_rule": f"hermes_interpretation: stop = draft stop_reference, target = {TARGET_R}R, time exit 16:00 NY, stop-first on ambiguous bars",
        "costs_pts_per_side": COST_PER_SIDE,
        "statistics": {"bootstrap": f"percentile, {stats.N_BOOT} resamples, seed {stats.SEED}",
                       "p_value": "one-sided permutation in the expected direction, same resamples/seed",
                       "multiple_testing": "Holm across every evaluated hypothesis in the family",
                       "min_group_n": MIN_GROUP_N,
                       "foil": f"random-entry F1-style: same day + killzone, random minute, random side, same risk_pts/target/costs/exit; {N_FOIL} replicates"},
        "hypotheses": [h.to_dict() for h in HYPOTHESES],
        "never": ["assert results in this file", "SURVIVES language", "orders, broker calls or allowlist edits"],
    }


def _brief(v: dict) -> dict:
    s = v.get("summary") or {}
    return {"tickets": v.get("tickets"), "tradeable_n": s.get("n", 0), "mean_R": s.get("mean_R"),
            "ci95": s.get("ci95"), "foil_pct": v.get("foil_pct"), "side_conflicts": v.get("side_conflicts"),
            "hypotheses": {h["id"]: {k: h.get(k) for k in ("status", "n_true", "n_false", "diff", "ci95",
                                                         "p_one_sided", "p_holm")}
                           for h in v.get("hypotheses") or []}}


def _fmt(x, nd=3):
    return "—" if x is None else f"{x:+.{nd}f}"


def _before_after(results: dict) -> list[str]:
    b = results.get("_before")
    if not b:
        return []
    L = ["", "## BEFORE vs AFTER (REV direction from the raid; D18 gate kept as safety net)", "",
         f"Before = `{b['source']}` (REV side from the daytrade IOF, D18 blocking incoherent ones).", "",
         "| Series | Tickets before → after | Tradeable N before → after | Mean R before → after (95% CI) | Foil pct before → after | D18 blocks before → after |",
         "|---|---|---|---|---|---|"]
    for key in ("US100_base", "US500_base", "US100_interp"):
        a, o = _brief(results[key]) if key in results else None, b.get(key)
        if not a or not o:
            continue
        ci = lambda x: f"[{_fmt((x or (None, None))[0])}, {_fmt((x or (None, None))[1])}]"
        L.append(f"| {key} | {o['tickets']} → {a['tickets']} | {o['tradeable_n']} → {a['tradeable_n']} | "
                 f"{_fmt(o['mean_R'])} {ci(o['ci95'])} → {_fmt(a['mean_R'])} {ci(a['ci95'])} | "
                 f"{o['foil_pct']:.1f} → {a['foil_pct']:.1f} | {o['side_conflicts']} → {a['side_conflicts']} |")
    L += ["", "| Series | Hypothesis | before: status / Δ / p Holm | after: status / Δ (95% CI) / p Holm | Changed? |",
          "|---|---|---|---|---|"]
    for key in ("US100_base", "US500_base"):
        if key not in results or key not in b:
            continue
        ah, bh = _brief(results[key])["hypotheses"], b[key]["hypotheses"]
        for hid in sorted(set(ah) | set(bh)):
            x, y = bh.get(hid) or {}, ah.get(hid) or {}
            def cell(h, with_ci=False):
                if not h:
                    return "not run"
                if h.get("status") != "evaluated":
                    return f"{h.get('status')} ({h.get('n_true')}/{h.get('n_false')})"
                c = f" [{h['ci95'][0]:+.3f}, {h['ci95'][1]:+.3f}]" if with_ci else ""
                return f"evaluated ({h['n_true']}/{h['n_false']}) / {h['diff']:+.3f}{c} / {h['p_holm']:.3f}"
            sig = lambda h: bool(h) and h.get("status") == "evaluated" and h["p_holm"] < 0.05
            ev = lambda h: bool(h) and h.get("status") == "evaluated"
            changed = ("Holm verdict" if sig(x) != sig(y) else "evaluability" if ev(x) != ev(y) else
                       "sign of Δ" if ev(x) and ev(y) and (x["diff"] > 0) != (y["diff"] > 0) else "—")
            L.append(f"| {key} | {hid} | {cell(x)} | {cell(y, True)} | {changed} |")
    return L


def render_summary(asof: str, results: dict, tag: str = "") -> str:
    base = results["US100_base"]
    s = base["summary"]
    L = [f"# INTELLIGENCE SUMMARY — FTN Month 9 kernel × month-layer hypotheses (EXPLORATORY)",
         f"**Date:** {asof}  ",
         "**Owner:** FTN research bridge (agent-generated) · CASSANDRA **not yet reviewed** · DATA **not yet reviewed**  ",
         f"**Tape:** historical = `{TAPE['US100']}` (decision) · `{TAPE['US500']}` (disclosure, never pooled) · "
         f"{base['days'][0]}→{base['days'][1]} · **burned** (same tape/calendar as H013/H014) · not CME futures",
         "", f"> **{BANNER}** Paper-only research. No trades, broker calls or allowlist changes are authorized by this file. "
         "The MINT allowlist stays empty.", "",
         "## WHAT DID WE THINK?",
         "The FTN context months (M1–M8, M10–M12, Model 13) each make lecture-derived claims about when a setup works. "
         f"They were turned into {len(HYPOTHESES)} typed hypotheses "
         "(`research/protocols/preregs/FTN_HYPOTHESES_EXPLORATORY_" + asof + ".json`) and scored only on tickets issued by the "
         "unchanged Month 9 kernel. The conditioning formulas are `hermes_interpretation`.", "",
         "## WHAT DID WE OBSERVE?",
         "| Layer | Result |", "|-------|--------|",
         f"| Kernel sessions scanned (US100) | {base['sessions']} (London + NY AM) · tickets {base['tickets']} · "
         f"gate-chain tradeable (all gates but allowlist + I0 contract) {s.get('n', 0)} · blocked by direction-vs-raid (D18) {base['side_conflicts']} · "
         f"sessions where REV was refused because both/neither extremes were raided {base.get('rev_direction_undetermined_sessions', 0)} · "
         f"blocked by risk {base['risk_blocked']} |",
         f"| Kernel module mix | {base['modules']} |",
         f"| US100 base expectancy (2R/stop/16:00, after costs) | **{_fmt(s.get('mean_R'))}R** · N={s.get('n')} · bootstrap 95% CI "
         f"[{_fmt(s.get('ci95', (None, None))[0])}, {_fmt(s.get('ci95', (None, None))[1])}] · win rate {s.get('win_rate', 0):.1%} |",
         f"| Fragility | ex-top-1% {_fmt(s.get('mean_ex_top1pct'))} · ex-small-stop (<p25) {_fmt(s.get('mean_ex_small_stop'))} · "
         f"longs {s.get('longs')} / shorts {s.get('shorts')} · exits {s.get('exits')} |",
         f"| Random-entry foil (US100) | kernel mean at the **{base['foil_pct']:.1f}th pct** of {N_FOIL} foil means "
         f"(foil median {_fmt(base['foil_median'])}) |"]
    for key, label in (("US100_base_legacy_side", "US100 kernel side as-is (pre-D18; admits REV buys after high raids / sells after low raids)"),
                       ("US500_base", "US500 disclosure (same rules, never pooled)"),
                       ("US500_base_legacy_side", "US500 kernel side as-is (pre-D18)"),
                       ("US100_interp", "US100 with interpretation triggers ON (CONSO/BB/PIP20; disclosure)")):
        r = results.get(key)
        if not r:
            continue
        ss = r["summary"]
        ci = ss.get("ci95") or (None, None)
        L.append(f"| {label} | {_fmt(ss.get('mean_R'))}R · N={ss.get('n', 0)} · CI [{_fmt(ci[0])}, {_fmt(ci[1])}] · "
                 f"win {ss.get('win_rate', 0):.1%} · modules {r['modules']} · foil pct {r.get('foil_pct', float('nan')):.1f} |")
    for key, title in (("US100_base", "US100 decision series (gate chain incl. D18)"),
                       ("US100_base_legacy_side", "US100 kernel side as-is (pre-D18 disclosure)"),
                       ("US500_base", "US500 disclosure series (separate family, never pooled)")):
        if key not in results:
            continue
        L += ["", f"### Hypotheses — {title}; Holm across the evaluated family", "",
              "| ID | Month | Variable | Metric | N true / false | true vs false | Δ (95% CI) | p one-sided | p Holm | Read |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in results[key]["hypotheses"]:
            if r["status"] != "evaluated":
                L.append(f"| {r['id']} | {r['month']} | `{r['var']}` | {r['metric']} | {r['n_true']} / {r['n_false']} | — | — | — | — | {r['status']} |")
                continue
            read = "consistent with claim (exploratory)" if r["p_holm"] < 0.05 else "no evidence after Holm"
            L.append(f"| {r['id']} | {r['month']} | `{r['var']}` | {r['metric']} | {r['n_true']} / {r['n_false']} | "
                     f"{r['metric_true']:+.3f} vs {r['metric_false']:+.3f} | {r['diff']:+.3f} "
                     f"[{r['ci95'][0]:+.3f}, {r['ci95'][1]:+.3f}] | {r['p_one_sided']:.3f} | {r['p_holm']:.3f} | {read} |")
    L += ["", "## WHAT CHANGED?",
          ("- REV direction now comes from the raid (user decision on D18): low raided → bullish, high raided → bearish, "
           "both or neither → undetermined, no ticket. The D18 direction-vs-raid gate stays as a safety net "
           f"(US100 blocks: {base['side_conflicts']}). See BEFORE vs AFTER below.") if tag else
          (f"- The REV side check (D18) is new in this change. Of {base['tickets']} US100 kernel tickets, "
           f"{base['side_conflicts']} had a daytrade-IOF side that *agreed* with the raid (e.g. a buy after a PDH raid). "
           "That is a continuation, not a reversal, and the gate chain now blocks it."),
          "- Hypotheses and scores were produced in the same change, so this is **not** a pre-registration. "
          "Any claim worth keeping needs a fresh prereg on untouched or forward data.",
          *_before_after(results),
          "", "## WHAT SURVIVED?", "- Nothing is claimed to survive. This file asserts no result beyond the numbers above.",
          "", "## WHAT FAILED?",
          "- Read the table: any row whose CI includes 0 or whose Holm p ≥ 0.05 shows no evidence for its claim.",
          "", "## CAVEATS (binding on any citation)",
          "- Burned tape (H013/H014 used the same Dukascopy BID series and calendar).",
          "- Every bar formula is `hermes_interpretation`: IOF = candle colour, daily FVGs from session OHLC, CBDR scaled "
          "relative to its own median, OSOK = Mon–Wed opposite-side raid, SMT = US500 not taking its own extreme.",
          "- Exit = fixed 2R / stop / 16:00 (interpretation; MONTH9 docs give no REV exit). Stop = raided extreme (D12).",
          "- The REV origin rule is permissive (D7): almost any daily FVG below/above price satisfies `htf_pd`.",
          "- Feature groups overlap, so the hypotheses are not independent. Holm is conservative under dependence.",
          "- **This tape cannot confirm anything.** It was already used for H013/H014 and for the first FTN score; every "
          "re-score on it (including this one) is exploratory.",
          "", "## NEXT", "- CASSANDRA red-team, then DATA gate. If a row is worth testing, write a fresh prereg (new ID) "
          "before looking at untouched data: sessions after 2026-09-25 (forward), or a separate pull/feed that H013/H014 "
          "never touched (e.g. the `/workspace/marketdata` pull once DATA certifies it, or CME futures).",
          "", f"Reproduce: `cd ftn && PYTHONPATH=src python3 -m ftn score --asof {asof}` (bars default to "
          "`/workspace/ict-blueprint/research/model-u-longrun/data/US{100,500}_1m.csv.gz`; override `--bars-us100/--bars-us500`)."]
    return "\n".join(L) + "\n"


def score(asof: str | None = None, bars_us100: str | None = None, bars_us500: str | None = None,
          research_dir: str | Path | None = None, write: bool = True, with_interp: bool = True,
          tag: str = "", before: str | Path | None = None, with_legacy: bool = False) -> dict:
    """``before``: a previous FTN_M9_SCORE_*.json to compare against (before/after table).
    ``with_legacy``: also run the pre-D18 "kernel side as-is" disclosure streams."""
    asof = asof or date.today().isoformat()
    cfg = load_config()
    cfg_base = deepcopy(cfg)
    cfg_base["interpretation_triggers"] = {"conso": False, "bb": False, "pip20": False}
    p100, p500 = bars_us100 or DEFAULT_BARS["US100"], bars_us500 or DEFAULT_BARS["US500"]
    other = None
    results: dict = {}
    if Path(p500).is_file():
        s5 = load_series(p500, "US500")
        other = History(s5, trading_days(s5))
    runs = [("US100_base", "US100", p100, cfg_base, other, False)]
    if with_legacy:
        runs.append(("US100_base_legacy_side", "US100", p100, cfg_base, other, True))
    if other is not None:
        runs.append(("US500_base", "US500", p500, cfg_base, None, False))
        if with_legacy:
            runs.append(("US500_base_legacy_side", "US500", p500, cfg_base, None, True))
    if with_interp:
        cfg_i = deepcopy(cfg)
        cfg_i["interpretation_triggers"] = {"conso": True, "bb": True, "pip20": True}
        runs.append(("US100_interp", "US100", p100, cfg_i, other, False))
    logs: dict = {}
    trades_by: dict = {}
    cache: dict = {}
    for key, sym, path, c, oth, legacy in runs:
        ck = (sym, json.dumps(c["interpretation_triggers"], sort_keys=True))
        if ck in cache:
            hist0, log0 = cache[ck]
            hist, log, trades = run_series(sym, path, c, oth, legacy, hist=hist0, log=log0)
        else:
            hist, log, trades = run_series(sym, path, c, oth, legacy)
            cache[ck] = (hist, log)
            logs[f"{sym}_{'interp' if any(c['interpretation_triggers'].values()) else 'base'}"] = log
        trades_by[key] = trades
        fm = foil(hist, trades, COST_PER_SIDE[sym]) if trades else []
        real = mean(t["R"] for t in trades) if trades else 0.0
        mods: dict = {}
        for r in log:
            if r["ticket"]:
                mods[r["module"]] = mods.get(r["module"], 0) + 1
        results[key] = {
            "symbol": sym, "days": (hist.days[0].isoformat(), hist.days[-1].isoformat()),
            "sessions": len(log), "tickets": sum(1 for r in log if r["ticket"]),
            "risk_blocked": sum(1 for r in log if r["ticket"] and (r.get("blocked_by") or "").startswith("risk")),
            "modules": mods, "summary": summarize(trades),
            "foil_pct": 100.0 * sum(1 for m in fm if m < real) / len(fm) if fm else float("nan"),
            "foil_median": sorted(fm)[len(fm) // 2] if fm else None,
            "hypotheses": evaluate_hypotheses(trades) if "_base" in key else [],
            "side_conflicts": sum(1 for r in log if "direction:FAIL:rev_direction_conflicts_with_raid" in (r.get("gates") or [])),
            "rev_direction_undetermined_sessions": sum(1 for r in log if r.get("rev_direction_undetermined_seen")),
        }
    if before:
        results["_before"] = {"source": str(before), **{k: _brief(v) for k, v in
                              json.loads(Path(before).read_text()).items() if not k.startswith("_")}}
    if write:
        rd = Path(research_dir) if research_dir else repo_root().parent / "research"
        (rd / "protocols/preregs").mkdir(parents=True, exist_ok=True)
        if not tag:  # the hypothesis family itself does not change with a re-score
            (rd / "protocols/preregs" / f"FTN_HYPOTHESES_EXPLORATORY_{asof}.json").write_text(
                json.dumps(hypotheses_doc(asof), indent=2) + "\n")
        for key, log in logs.items():
            write_ticket_csv(rd / "evidence/quant" / f"FTN_M9_TICKETS_{key}_{asof}{tag}.csv", log)
        for key, tr in trades_by.items():
            write_ticket_csv(rd / "evidence/quant" / f"FTN_M9_TRADES_{key}_{asof}{tag}.csv", tr)
        (rd / "evidence/quant" / f"FTN_M9_SCORE_{asof}{tag}.json").write_text(json.dumps(results, indent=2, default=str) + "\n")
        (rd / "summaries").mkdir(parents=True, exist_ok=True)
        (rd / "summaries" / f"{asof}_FTN_M9_EXPLORATORY_SCORE{tag.upper()}.md").write_text(render_summary(asof, results, tag))
    return results
