# Model U v1 base forward test = H013 (paper, HYPOTHETICAL; shadow R-unit log only, no orders)
Pre-registration: GdotAiM/hermes `research/protocols/preregs/H013_FORWARD_PREREG_2026-10-04.json` (board lock
`research/summaries/2026-10-04_H013_BOARD_LOCK.md`). Patched 2026-10-04 to match the prereg exactly; pre-patch copies are in
`_pre_h013_backup_2026-10-04/`.

- **Rules:** frozen v1 engine, sha256-verified on every run (`research/model-u-longrun/scripts/v1/u_engine.py`, `run_u_lib.py`,
  `scripts/longrun.py`, `data/costs.json`; a mismatch aborts). Invocation `best_trade(ctx, "11:00", False, False, True)`,
  **FILL_THRU = 1 tick**, costs 0.8 (US100) / 0.5 (US500) pt per side on entry and every exit leg (SLIP = cost/0.25).
  Fills 09:00-11:00 NY, time exit 11:30 NY, 50-50 exit is primary. Re-entry (`v1_reentry`) is not part of H013.
- **Data: TradingView CAPITALCOM:US100** (decision series) and **CAPITALCOM:US500** (disclosure series, never counted), 1m,
  public websocket (`tv_feed.py`). **No fallback feed** (no PEPPERSTONE/OANDA/Yahoo); a failed fetch or missing minutes are logged
  as gaps, never substituted. Not Dukascopy. All rule times America/New_York.
- **Filters:** prereg holiday list (`h013_harness.py`), min-bar rule >= 285 of 300 1m bars in 07:00-11:59 NY.
- **Provenance:** every run saves the raw 1m bars it consumed to `raw/forward/<inst>_<date>.csv` (never overwritten; a different
  re-fetch gets a timestamped sibling) and logs feed, fetch time, raw file and sha256, harness digest, and whether the harness
  hashes are registered in the prereg on `origin/main` (and when they landed).
- **Logs (append-only):** `h013_forward_log.csv` (one row per instrument per run, `counted` + `not_counted_reasons`);
  `h013_alerts.jsonl` (live FILL alerts). The legacy `forward_log.csv` / `alert_state.json` stop at 2026-10-02 for counting
  purposes and never count.

## Scripts
| Script | When (SAST, EDT until Fri 30 Oct 2026; +1 h from Mon 2 Nov 2026) | What |
|---|---|---|
| `h013_live_watch.py` | start 14:55 (08:55 NY), runs to 17:31 (11:31 NY) | polls CAPITALCOM every minute, appends first-fill alerts + raw snapshot to `h013_alerts.jsonl` |
| `tv_final.py today` | 18:05 (12:05 NY), same NY day | FINAL row per instrument; `live_alerted` = FILL alert logged before the 50-50 exit |
| `backfill_tv.py DATE` | any time (TV keeps ~5 sessions of 1m) | BACKFILL rows, raw bars saved, never counted |
| `tv_final.py DATE --dry` / `tv_final.py DATE US100=a.csv US500=b.csv` | any time | preview / replay from saved raw bars, writes nothing |
| `live_check.py` | optional, user-facing | status + charts; CAPITALCOM only, FILL_THRU=1; not used for counting |

Counted row (US100 only) = FINAL run on the session's NY date, calendar ok, >= 285 bars, raw bars saved, live-alerted fill,
session on/after 2026-10-05 and after the harness hashes landed on `origin/main` (before 07:00 NY), first FINAL row per session.
Tests: `.venv/bin/python -m pytest -q tests_h013`. `forward_v1.py` is the original Dukascopy-datafeed tool (unchanged, not part
of the H013 harness).
