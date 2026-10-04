# Forward harnesses for H013 (Model U v1 US100) and H014 (MMXM v5 A US100 + US500)
HYPOTHETICAL paper research: shadow R-unit logs only. No orders, broker calls, or MERCURY.

The harnesses run on the box at their **deployed roots** (`/workspace/ict-blueprint/forward-test`, `/workspace/mmxm/forward`),
because those folders hold the hash-pinned engines (not git repos). This folder keeps byte-identical copies. Hashes:
`HARNESS_SHA256.json`, recorded in each prereg's `harness_sha256.files`; check the deployment with
`sha256sum -c research/forward_harness/SHA256SUMS_deployed.txt`.

**Registration = landing on `origin/main`.** Each run does `git fetch origin main`, compares its own gate-file hashes with the
prereg on `origin/main`, and records the first-parent commit time at which they landed. A session counts only if they landed
before the session start: H013 07:00 NY; H014 18:00 NY the prior calendar day (the overnight range start). Until then, rows are
logged with `harness_registered_on_main=False` and never count. For a Monday 5 Oct 2026 start of both, merge by **Sun 4 Oct
23:59 SAST** (Sun 18:00 NY). A merge before Mon 12:59 SAST (07:00 NY) starts H013 on Monday, and H014 starts on Tuesday.

## Per-NY-session commands
Times are SAST while New York is on EDT (through Fri 30 Oct 2026). From Mon 2 Nov 2026 every time moves **+1 h** (EST); from
Mon 15 Mar 2027 it moves back. A routine can avoid the DST shift by pinning its cron to New York time (`CRON_TZ=America/New_York`).

| SAST (EDT) | NY | Command | Purpose |
|---|---|---|---|
| 14:55 Mon-Fri | 08:55 | `/workspace/ict-blueprint/forward-test/run_h013_h014_session.sh watch` | start the H013 live-alert watcher; it polls every minute until 11:31 NY (single instance via flock) |
| 15:25 and 16:25 Mon-Fri (watchdog) | 09:25 / 10:25 | same `watch` command | restarts the watcher if the box was relaunched; it prints "already running" otherwise |
| 18:05 Mon-Fri | 12:05 | `/workspace/ict-blueprint/forward-test/run_h013_h014_session.sh final` | H014 final (`h014_forward.py today`, needs >= 11:00 NY), then H013 final (`tv_final.py today`, needs >= 12:00 NY) |
| any time after a failed final, same NY day (before 06:00 SAST next day) | — | `... run_h013_h014_session.sh final` | a same-day re-run is still FINAL (only the first FINAL row per session stands) |
| missed day (TradingView keeps ~5 sessions of 1m) | — | `cd /workspace/ict-blueprint/forward-test && .venv/bin/python backfill_tv.py DATE` · `cd /workspace/mmxm/forward && ../.venv/bin/python h014_forward.py DATE --backfill` | H013 backfills never count; H014 backfills count but are reported with and without |

Holidays and weekends need no special handling: the scripts log them as excluded, and the watcher exits.
Tests: `cd /workspace/ict-blueprint/forward-test && .venv/bin/python -m pytest -q tests_h013` (21) ·
`cd /workspace/mmxm/forward && ../.venv/bin/python -m pytest -q tests` (63).

## Open issues for ORION / CASSANDRA / DATA (the harness logs the data either way; nothing is ruled here)
1. **Live-alert rule excludes very fast exits (H013).** The prereg counts a trade only if its fill alert precedes the 50-50 exit.
   A 1m bar is known only after it closes, so a trade stopped *in its fill bar* (or within about 1-2 min) can never be
   live-alerted, even with the watcher polling every minute. Those are all losers, so applying the rule literally biases counted
   R upward. The watcher and log record `fill_alert_sast`, `live_alerted`, the fill time and the exit time for every trade, so
   any ruling (for example "count every trade on sessions where the watcher ran live") can be applied before the first R read.
2. **H014 1H-context warm-up is mixed-feed until the CAPITALCOM archive is long enough.** CAPITALCOM 1m history on the public
   socket reaches back only about 5 sessions. The harness keeps every fetch (first archive: 27 Sep 18:00 -> 2 Oct 16:59 NY), and
   older context comes from the pinned Dukascopy BID parquet (to 25 Sep). 500 1H bars of pure CAPITALCOM is reached around late
   Oct 2026; the 60-day window is pure CAPITALCOM from about late Nov 2026. `warmup_dukascopy_bars` is logged on every row.
   The session's own bars (18:00 prior day -> 16:59) are always CAPITALCOM.
3. **H014 "spread-side fill model" = DATA's fill-realism proxy, using Dukascopy spreads** (US100 1.117 / US500 0.51). It is a
   co-report only; the binding R is the frozen 1-tick / 0.8-0.5 RT model. It should be re-parameterised once DATA measures
   the CAPITALCOM spread (prereg pre-read requirement).
4. Holiday list: ORION-compiled; DATA verification is still open (spot-checked against NYSE rules for 2026-27, no discrepancy found).
