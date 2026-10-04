# Forward harnesses — H013 (Model U v1 US100) and H014 (MMXM v5 A US100 + US500)

HYPOTHETICAL paper research: shadow R-unit logs only. **No orders, no broker calls, no MERCURY.**

The harnesses run from this repo, and the frozen rule files are byte-identical copies (`PROVENANCE.md`).
- **Feed:** TradingView `CAPITALCOM:US100` / `CAPITALCOM:US500` 1m bars over the public websocket (`common/tv_feed.py`, anonymous `unauthorized_user_token`). No account, no login, no credentials. There is **no fallback feed**: a failed fetch is logged as `feed_gap`.
- **Data and logs:** written to `$HERMES_FWD_DATA` (default `/home/box/hermes-x/forward/{H013,H014}`), outside git:
  - raw bars: `raw/<inst>/*.csv`;
  - live alerts: `alerts.jsonl`;
  - session rows: `log.csv`.
- **Runtime:** `/home/box/hermes-x/forward/.venv` (from `requirements.txt`).

## Registration (prereg `harness_sha256`)
- **What registers:** the gate files (`common/*.py`, `H013/{__init__,h013}.py`, `H014/{__init__,h014}.py`) are hashed into each prereg's `harness_sha256.files`, with `repo_root = GdotAiM/hermes`.
- **When it counts:** at run time the harness finds the **first first-parent commit on `origin/main`** that carried that manifest, and uses that commit's time as the registration time.
  - A session counts only if registration precedes its start: H013 at 07:00 NY; H014 at the first overnight bar, 18:00 NY on the prior calendar day.
  - Any later change to a gate file gives `harness_hash_mismatch`, so nothing counts after the change (a new ID is needed).

## Commands (run from the repo root)
```
P=/home/box/hermes-x/forward/.venv/bin/python
$P research/forward/H013/h013.py watch     # live poller 09:00-11:31 NY (single instance; re-run = no-op)
$P research/forward/H014/h014.py final     # after 12:00 NY
$P research/forward/H013/h013.py final     # after 12:00 NY
$P research/forward/H013/h013.py report ; $P research/forward/H014/h014.py report
$P research/forward/H013/h013.py backfill YYYY-MM-DD   # never counted
$P research/forward/H014/h014.py backfill YYYY-MM-DD   # counted if post-registration, flagged BACKFILLED
$P research/forward/H014/h014.py seed      # store the ~5 sessions TradingView currently serves as 1H context
$P -m pytest -q research/forward/tests     # reproduction + counting + kill tests (needs the Dukascopy history on the box)
```

## Counting rules implemented
- **H013:** a row counts only if all of the following hold:
  - it is US100, from a `FINAL` run, with status `trade`;
  - the prereg calendar is `ok` and the 07:00–11:59 window has ≥ 285/300 bars;
  - the session is complete (11:59 bar present) and the rule pins match;
  - the harness is registered before 07:00 NY;
  - a live `FILL` alert with the same trade key exists, with alert time before the 50-50 exit bar closes.
  US500 rows are disclosure only. `BACKFILL` rows never count.
- **H014:** a session counts per symbol if the calendar is `ok` and it has ≥ 86/90 bars in 09:30–10:59 and ≥ 791/930 in the 18:00→09:30 overnight range. It must also be complete (11:00 bar present), with pins matching and registration before the first overnight bar.
  - Backfills of post-registration sessions count and are flagged.
  - The latest run per session/symbol is authoritative.
  - Pooled cumulative R ≤ −5 → `FAILS (kill)`.
  - US100 and US500 are reported separately; pooled is secondary.

## Open issues (logged, not ruled here)
1. **Fast exits can't be live-alerted (H013)** (first raised on branch `forward/h013-h014-scripts`). A 1m bar is known only after it closes. So a trade stopped in its fill bar, or within about 1–2 minutes, can never have an alert before its exit. Those trades are losers, so the literal rule biases counted R upward. Every row logs fill time, exit time and alert time, so CASSANDRA can rule before the first R read.
2. **H014 1H context is CAPITALCOM-only and starts short.** TradingView serves about 5 sessions of 1m bars, and the harness archives every fetch.
   - Sensitivity on Dukascopy history: with 7 days of context, 46/48 frozen trades are reproduced; with 21 days, 48/48, with identical R.
   - So sessions in roughly the first 3 weeks after seeding may miss a trade. Rows log `h1_context_bars` and `context_short`.
   - I chose not to splice Dukascopy history in, because the forward feed must be CAPITALCOM only. DATA/CASSANDRA may rule otherwise.
3. **CAPITALCOM spread and bid/mid side are unmeasured** (DATA fix 3). The cost co-reports use Dukascopy spreads: H013 `R_5050_cost{1p5x,2x,3x}`; H014 `r_cost2x` and `r_data_measured_cost` (1.617 / 1.01 RT). DATA's fill-realism proxy needs an engine re-run, which can be done from the saved raw bars.
4. **CAPITALCOM trades until 16:59 NY** (halt 17:00–18:00, like futures), whereas Dukascopy halts at 16:14. This affects the H014 1H bars around the halt (DATA fix 9).
