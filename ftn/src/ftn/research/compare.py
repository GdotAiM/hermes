"""EXPLORATORY three-way comparison of FTN score runs (reads existing outputs only; no scoring).

Kept outside the pinned scoring harness (FTN-D22 prereg pins score.py etc. unchanged).
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path


def _blocked(csv_path: Path) -> Counter:
    c: Counter = Counter()
    if not csv_path.is_file():
        return c
    for r in csv.DictReader(csv_path.open()):
        if r.get("ticket") == "True":
            c[r.get("blocked_by") or "none"] += 1
    return c


def _fmt(x):
    return "—" if x is None else f"{x:+.3f}"


def _ci(s):
    ci = s.get("ci95") or (None, None)
    return f"[{_fmt(ci[0])}, {_fmt(ci[1])}]"


def _hcell(h):
    if not h:
        return "not run"
    if h.get("status") != "evaluated":
        return f"n/e ({h['n_true']}/{h['n_false']})"
    return f"{h['diff']:+.3f} [{h['ci95'][0]:+.3f}, {h['ci95'][1]:+.3f}] · Holm {h['p_holm']:.3f}"


def render(runs: list[tuple[str, Path, dict[str, Path]]], asof: str) -> str:
    """runs: [(label, score_json, {series: tickets_csv})]."""
    data = [(lab, json.loads(p.read_text()), tk, p) for lab, p, tk in runs]
    L = [f"# INTELLIGENCE SUMMARY — FTN REV: stop beyond the raid (FTN-D22), three-way comparison (EXPLORATORY)",
         f"**Date:** {asof}  ",
         "**Prereg:** `research/protocols/preregs/FTN_D22_REV_STOP_BEYOND_RAID_PREREG_2026-10-04.json` "
         "(committed before the code change and before scoring) · CASSANDRA **not yet reviewed** · DATA **not yet reviewed**  ",
         "**Tape:** Dukascopy CFD BID 1m, 2025-08-25 → 2026-09-25, **burned** (H013/H014 + two prior FTN scores) · not CME futures", "",
         "> **EXPLORATORY — pending CASSANDRA + DATA review. Not a board result. No SURVIVES language.** "
         "Paper-only research; no trades, broker calls or allowlist changes are authorized by this file. "
         "**This tape cannot confirm anything.** Confirmation needs untouched data: forward sessions after 2026-09-25, "
         "or the `/workspace/marketdata` Dukascopy pull once DATA certifies it.", "",
         "Same rules in every column except the REV change named in the header: entry = 15m ticket close, 2R / stop / 16:00 NY, "
         "costs 0.8 / 0.5 pt per side (US100 / US500), bootstrap 10k seed 20261004, 2,000-replicate random-entry foil, "
         "Holm across FTN-H001..H013 per instrument (min group n 10).", "",
         "Sources: " + " · ".join(f"{lab} = `{p.as_posix()}`" for lab, _, _, p in data), ""]
    for series in ("US100_base", "US500_base"):
        L += [f"## {series.split('_')[0]}", "", "| | " + " | ".join(lab for lab, *_ in data) + " |",
              "|---|" + "---|" * len(data)]
        rows = {"Kernel tickets": [], "Tradeable trades": [], "Mean R after costs [95% CI]": [], "Win rate": [],
                "Foil percentile": [], "Blocked (by first failing gate)": []}
        for lab, d, tk, _ in data:
            r = d[series]
            s = r["summary"]
            rows["Kernel tickets"].append(str(r["tickets"]))
            rows["Tradeable trades"].append(str(s.get("n", 0)))
            rows["Mean R after costs [95% CI]"].append(f"{_fmt(s.get('mean_R'))} {_ci(s)}")
            rows["Win rate"].append(f"{s.get('win_rate', 0):.1%}")
            rows["Foil percentile"].append(f"{r['foil_pct']:.1f}")
            b = _blocked(tk.get(series, Path("/nonexistent")))
            rows["Blocked (by first failing gate)"].append(
                " · ".join(f"{k} {v}" for k, v in b.most_common() if not k.startswith("allowlist")) or "none")
        for k, v in rows.items():
            L.append(f"| {k} | " + " | ".join(v) + " |")
        L += ["", f"### Holm table — {series.split('_')[0]} (Δ = mean R true − false, 95% CI)", "",
              "| Hypothesis | " + " | ".join(lab for lab, *_ in data) + " |", "|---|" + "---|" * len(data)]
        ids = sorted({h["id"] for _, d, *_ in data for h in d[series].get("hypotheses", [])})
        for hid in ids:
            cells = []
            for _, d, *_ in data:
                h = next((x for x in d[series].get("hypotheses", []) if x["id"] == hid), None)
                cells.append(_hcell(h))
            L.append(f"| {hid} | " + " | ".join(cells) + " |")
        L.append("")
    return "\n".join(L) + "\n"
