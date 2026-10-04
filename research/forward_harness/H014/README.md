# H014 forward harness: MMXM v5 A_overnight_5mFVG_ce_c12_none (paper, HYPOTHETICAL; shadow R-unit log only)
Pre-registration: GdotAiM/hermes `research/protocols/preregs/H014_FORWARD_PREREG_2026-10-04.json`; board lock
`research/summaries/2026-10-04_H014_BOARD_LOCK.md`.

- Frozen rule: `configs/v5_A_overnight_5mFVG_ce_c12_none.yaml` + `mmxm/{engine,data,config,baseline}.py`, sha256-verified each run
  (mismatch aborts). Engine run unchanged (`run_backtest`), US100 -> NQ root, US500 -> ES root.
- Primary (binding) R: 1-tick fill-through, RT 0.8 / 0.5 pts, no stop slippage, touch-both = stop.
- Co-reports (never binding): spread-side fill proxy (DATA: spread + 1 tick through on limit entries/targets, stops slip 1 spread,
  RT 0.5; US100 6/4 ticks, US500 3/2 ticks), DATA measured cost (1.617 / 1.01 RT), 2x cost, random-entry baseline
  (`mmxm/baseline.py`, per-trade outcome arrays in `baseline/`), exit reason.
- Feed: TradingView CAPITALCOM:US100 / US500 only, no fallback. Filters: prereg holidays; >= 86/90 bars 09:30-10:59 and
  >= 791/930 bars 18:00 (prior day) -> 09:30.
- 1H-context warm-up (DATA open item): every saved CAPITALCOM fetch (`/workspace/ict-blueprint/forward-test/raw/forward/archive`
  plus earlier `raw/forward/<inst>_<date>.csv`) first; bars older than the first CAPITALCOM bar in the 60-day window come from the
  pinned Dukascopy BID parquet. `warmup_dukascopy_bars` is logged; the session's own bars must be 100% CAPITALCOM to count.
- Raw bars consumed (with `src` column) -> `raw/forward/<inst>_<date>.csv` (never overwritten), sha256 in the row.
- Append-only `h014_forward_log.csv`: US100 and US500 rows separately; `cum_R_*_counted`; binding kill at pooled cumulative
  counted R <= -5 (`kill_triggered`; later rows are never counted).

Run: `cd /workspace/mmxm/forward && ../.venv/bin/python h014_forward.py today` after 11:00 NY (17:05 SAST until Fri 30 Oct
2026, 18:05 SAST from Mon 2 Nov). Backfill: `h014_forward.py DATE --backfill` (note BACKFILLED; counts, reported with/without).
Preview: `--dry`; replay: `h014_forward.py DATE US100=a.csv US500=b.csv`. Tests: `../.venv/bin/python -m pytest -q tests`.
