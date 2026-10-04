# H016b data-handling appendix (2026-10-04)

**Applies to:** H016b (`research/protocols/preregs/H016b_FORWARD_PREREG_2026-10-04.json`, tag `prereg-H016b` → 74b13d3). **Paper research only.**

**Basis:**
- the H015b data appendix (`H015b_DATA_APPENDIX_2026-10-04.md` at `harness-H015b-v2` → 5ea3e89) and DATA_CERT_H015B_HARNESS_V2 (v1 blockers B1–B5 fixed);
- the H016b prereg (BID **and** ASK binding);
- DATA's H016b prereg review (`DATA_REVIEW_H016B_PREREG_2026-10-04.md`, K1–K12), CASSANDRA's H016b prereg check (C1–C3) and early-reads ruling, ORION's B1 ruling.

**Status:** committed with the H016b harness v1, before any forward bar is read. This file is part of the harness manifest (`harness_sha256`), so any change to it is a harness change.

This appendix only defines how data is handled. It changes none of the binding items of the prereg. A binding change is a new ID (H016c), not an edit of this file.

**Implementation:**
- `research/forward/H016b/duka.py`: feed and store, code-identical to the certified H015b v2 `duka.py` (only the docstring differs).
- `research/forward/H016b/h016b.py`: provenance store, sessions, ledger, report.
- `research/forward/H016b/one_sided.py`: DATA's one-sided-exit reference functions (v2), verbatim.
- The draft H016 harness (`research/forward/H016/`, never committed, never registered, never run on forward data) is superseded by this directory and was removed from the working tree.

## A1. Pull time and finality (unchanged logic; B1/B2)
- **Pull time.** A UTC day file is pulled no earlier than 01:00 UTC on the next UTC day. A session dated d (NY) uses UTC days d−1 and d, so it is first scored at or after **d+1 01:00 UTC (03:00 SAST)**.
- **Scheduled run.** `python research/forward/H016b/h016b.py final` at or after 01:00 UTC on each day after a trading day (suggested 01:07 UTC, Tue–Sat). Every run scores all pending dates, so a missed run is caught up by the next one.
- **FINAL day file (B1).** A day file is FINAL when it was pulled at or after 01:00 UTC next day **and** it is complete by content:
  - Mon–Fri: the last real bar is at or after 16:14 NY that date;
  - Sunday: the last real bar is at or after 23:50 UTC;
  - Saturday: always complete;
  - a listed holiday or early close may be short.

  A 404, empty or cut-off file is re-pulled on every run for up to 5 weekdays. After that it is frozen FINAL with `frozen_incomplete: true`, which is disclosed. Replaced bytes are kept in `superseded/`.
- **FINAL session (H016b).** All of the following must hold:
  - every **BID** day file (context + session) is FINAL;
  - **both** the BID and ASK day files for UTC days d−1 and d are FINAL;
  - **both** sides have bars to 16:14 NY on d (full datetime, B2).

  Finality is **per side** (DATA K1): each side's day file is final by its own content. If any file is not FINAL (e.g. ASK late, 404 or cut off while BID is fine), the session is `provisional` (no status, no decision) and is re-pulled on every run. If every file is final but a side is short of 16:14 NY, the status is `feed_gap_bid` or `feed_gap_ask` (the BID side is named first if both). A session still incomplete more than 5 trading days after d is frozen as `feed_gap_bid` / `feed_gap_ask`. Never a fallback, never an early decision. **ASK publication latency has never been measured** (the H015b store pulled BID only): it is measured from `pulls.jsonl` during the first weeks and reported by DATA.
- **Re-pulls** depend on completeness only, never on R. Every pull is logged in `pulls.jsonl`.

## A2. Feed (H016b: BID and ASK binding, no fallback)
- **One pipeline:** `duka.py`, using the Dukascopy datafeed `BID_candles_min_1.bi5` and `ASK_candles_min_1.bi5`.
- **Roles:**
  - BID drives the kernel (chart, levels, context of at least 22 sessions over 45 calendar days).
  - ASK drives the correct-side fills and `spread_measured` at the signal. ASK covers the session's UTC days d−1 and d.
- **Banned sources:** marketdata loader output (`marketdata.load()` fills ASK synthetically by default, `assume_missing_ask=True`), ftn's default old bar tape (`DEFAULT_BARS`), the reused parquet, HistData, CAPITALCOM, Yahoo, or any synthetic ASK (BID + assumed spread). The harness never switches feed. A feed change is a new ID.
- **Error handling:**
  - An ASK feed error (`FeedError`) keeps the session `provisional`.
  - An ASK schema error is `feed_suspended`, exactly as for BID.
- **Marketdata use:** only the `repull` certification command (mode `local`) reads marketdata's **native** Dukascopy bi5 bytes, and only for burned-window days ≤ 2026-09-25 (the getter refuses any later day). The forward path never imports `marketdata` (tested).

## A3. Filler bars (unchanged)
- The harness drops exactly `(volume == 0) & (high == low)`. It never synthesises, interpolates or forward-fills a bar.
- Dropped counts are logged per row for BID (`filler_dropped_session`) and ASK (`filler_dropped_session_ask`).
- A duplicate or out-of-order raw timestamp, or a record that does not decode as `>5if`, is a schema failure: `feed_suspended`.

## A4. Statuses, context, min-bar and exit-bar rules (B3/B4/B5; H016b both sides)
**Statuses:** `trade`, `no_trade`, `provisional`, `feed_gap_bid`, `feed_gap_ask`, `feed_gap_entry`, `no_r_ticket`, `holiday`, `short_session`, `context_gap`, `feed_suspended`, `not_trading_day`, `calendar_identity_fail`. Only `trade` rows can be counted. A date past the last covered calendar year is held `provisional` with error `calendar_not_covered` (never terminal; DATA K3).

**Context (B3/B4).**
- The context calendar is the full NYSE calendar: the prereg list, the pre-window holidays from 2025-09-01 (including Labor Day 2026-09-07), and 2028, 2029, 2030.
- **Context needs BID only** (DATA K4): ASK is fetched only for the session's UTC days d−1 and d, so a missing or frozen ASK on an earlier day can never cause `context_gap` (tested).
- Expected trading days that are absent from `trading_days(BID)` are skipped exactly as `History` skips them, and are disclosed per row (`context_missing_days`, `context_frozen_incomplete`; the latter is tagged `SIDE:day`).
- `context_gap` fires only when fewer than 22 prior sessions exist.

**Trading-day filter.** A weekday needs at least 300 BID 1m bars in 09:30–15:59 NY.

**Killzone min-bar filter (H016b).** At least 171 of 180 1m bars on **BID** (`kz_bars`) **and** on **ASK** (`kz_bars_ask`). Failing it gives `short_session`, not counted.

**Exit-bar rule (B5, binding, H016b both sides).**
- At least one bar in [15:45, 16:00) NY on date d, on **BID** (`exit_bar_1545_ok`) **and** **ASK** (`exit_bar_1545_ok_ask`).
- It is checked for **every** session, trade or no_trade. Failing it gives `short_session`.
- A gap of more than 5 minutes between entry and 16:00 on BID **or** ASK is the non-binding `gap_flag`.

**ASK-gap minutes.**
- BID minutes in [entry, 16:00) with no ASK print are skipped by `simulate_both`; they are never filled.
- They are logged per trade (`ask_gap_minutes`) and totalled in the report. They are descriptive only.

**Risk blocks.** A ticket blocked by the pinned risk gate (`stop_below_min_risk`, the 4× friction minimum stop) is a `no_trade` row with `block_reason`. It is counted in `report.risk_blocks` and never counted as a trade.

**Feed outage.**
- A schema failure suspends counting.
- So does a run of more than 10 consecutive expected trading days whose rows are all `feed_gap_bid` / `feed_gap_ask`.
- Resuming needs DATA's `FEED_RESUMED.json`.

## A5. Raw storage and hashes
- **Storage:** `$HERMES_FWD_DATA/H016b/raw/<inst>/<BID|ASK>/<YYYY-MM-DD>.{bi5,csv,json}` plus the provenance record `prov/<inst>/<SIDE>/<day>.json` written by this harness at download time (A13). The default root is `/home/box/hermes-x/forward/H016b`.
- **Row hashes.** Each row carries:
  - `session_raw_sha256`: the sha256 of the ordered [day, side, bi5_sha256, csv_sha256] list for BID d−1, d and ASK d−1, d;
  - `context_manifest_sha256`: the same over all BID context and session files plus the ASK session files;
  - `manifest_file`: the stored list itself.
- **Recompute.** `h016b.py verify` recomputes every final row from the stored manifest, on both sides, and must reproduce the ticket and the sealed R exactly. It never downloads.

## A6. Bar labels and timezone (unchanged)
- Bars are labelled by their open time.
- Times are converted from UTC to America/New_York with zoneinfo, and the offset is written on every row.
- All rule times are NY wall clock. The report splits London results by DST-mismatch week.

## A7. Costs (prereg `costs`)
- **Binding:** `ftn.research.outcomes.simulate_both(slip_mult=1.0)` with DATA's slippage floors per side from the pinned `ftn.os.instruments`:
  - US100: stop/market 0.50, limit 0.25;
  - US500: 0.25 / 0.10.
- **Co-reports:**
  - `simulate_both(slip_mult=2.0)`, stored as `R_slip2x`;
  - flat cost of 0.8 / 0.5 pt per side via `simulate`, stored as `R_flatcost`.

## A8. ASK side (H016b)
- ASK is **binding** for fills (A7) and for the stop buffer, through `spread_measured` at the signal.
- The H015b-style "ASK spot-check" is not needed, because every short stop-out is already resolved on ASK.

## A9. Spread and crossed-bar monitor (unchanged)
- `report` always gives `data_monitor_monthly`, sealed or not:
  - the median killzone ASK−BID close per instrument-month over every scored session;
  - a flag when that median is above 1.1 pt (US100) or 0.5 pt (US500);
  - the crossed-bar count.
- It also gives `spread_measured_at_signal` (median and p90 per instrument).
- DATA reviews these monthly.

## A10. Holidays
- **Counting list:** the prereg's list (2026-11-26 … 2027-12-24 plus early closes).
- **Pre-window context list:** as in the H015b v2 appendix, B4.
- **2028** (as in the H015b appendix, A10, from DATA):
  - full closures: 2028-01-17, 02-21, 04-14, 05-29, 06-19, 07-04, 09-04, 11-23, 12-25;
  - early closes: 07-03, 11-24.
- **2029** (from `pandas_market_calendars` NYSE; **DATA to verify at certification**):
  - full closures: 2029-01-01, 01-15, 02-19, 03-30, 05-28, 06-19, 07-04, 09-03, 11-22, 12-25;
  - early closes: 2029-07-03, 11-23, 12-24.
- **2030** (PROJECTED): full closures 2030-01-01, 01-21, 02-18, 04-19, 05-27, 06-19, 07-04, 09-02, 11-28, 12-25; early closes 07-03, 11-29, 12-24.
- **Source** (DATA `NYSE_HOLIDAYS_2028_2030.{csv,md}`): 2028 is OFFICIAL (NYSE published); 2029–2030 are PROJECTED from NYSE Rule 7.2 (pandas_market_calendars 5.4.0, exchange_calendars 4.13.2 and a rule-set implementation agree). DATA re-verifies each year against the NYSE publication before its first session; a discrepancy is resolved in favour of the NYSE publication (prereg `holiday_source`); a correction is a harness change (new digest, re-certification). Ad-hoc closures are added by appendix entry when they occur.
- Dates after 2030-12-31 are held **provisional** (`calendar_not_covered`), never written as terminal rows.

## A11. Feed outage policy (unchanged)
On an outage or schema change, counting is suspended and the feed is never switched. Resuming needs DATA's sign-off (`FEED_RESUMED.json`).

## A12. Sealing, clearance, state
- **Sealed outcomes.** R, fills, exits and the co-report R are written only to `sealed/outcomes.csv`. `final` never prints them.
- **Clearance.** `report` shows R only when `DATA_CERTIFIED.json` and `CASSANDRA_CLEARED.json` exist in the data dir, each with the key `harness_sha256` equal to the registered H016b digest.
- **Kill log.** The first crossing of −40R writes `sealed/KILL_LOG.json` once (row keys to the crossing, cumulative R, time, digest); never overwritten.
- **Futility set.** The first time counted N reaches 200, the 200 row keys are written once to `sealed/FUTILITY_SET.json`. Futility is evaluated on that set only, and any later reshuffle is reported. This file is in `sealed/` because it carries an R-derived bound.
- **State files:**
  - `STATE.json`: public, no R. It holds the last run, status counts, counted N and pending dates.
  - `sealed/STATE.json`: holds cumulative R, the kill walk and futility.
  - Both are rewritten by every `final`.
- **Run lock.** `final` takes an exclusive lock (`.final.lock`) and refuses to run concurrently.
- **No verdict below 100.** Below N = 100 counted trades there is no verdict or edge wording.
- **Feed disclosure.** Every report states the feed is Dukascopy BID+ASK.
- **Running book.** The running paper book (0.5% / 2% / 5%, `next_calendar_month`) is replayed over the binding tickets as a **co-report only**, pooled and per instrument.
- **H015b overlap.** Not computed: the H015b data directory is quarantined (CASSANDRA C2) and never read; H015b is WITHDRAWN-PRE-DATA with 0 rows.
- **DATA condition 4 (from the H015b v2 cert)** is carried over: a non-binding headline that excludes rows with a non-empty `context_missing_days` or `context_frozen_incomplete`.

## A13. Own downloads only; quarantine (CASSANDRA C2, DATA B1)
- `OwnStore` (in `h016b.py`) wraps the certified `duka.Store`: every pull writes `prov/<inst>/<SIDE>/<day>.json` = {harness, harness_sha256, pulled_at_utc, bi5_sha256, csv_sha256, url}. Every file used must carry a matching record and verify byte-for-byte; otherwise `ForeignFile` is raised and the file is never used. `final` refuses to run if any raw file under the data root lacks provenance.
- The harness refuses a data root inside `/home/box/hermes-x/forward/H015b` or `/workspace/marketdata`, and never builds a path to the H015b directory.
- Files downloaded before the registration commit by other processes (marketdata downloader, H015b runner, DATA's H015b dry run) are listed in the registration note and never read by this harness; it downloads its own copies after registration.
- Days 2026-09-26 … 2026-10-03 are `pre_registration_touched`: context only, never counted, never evidence, never backfilled (rows carry `context_pre_registration_touched`).

## A14. First eligible session (CASSANDRA C1)
A session counts only if its killzone starts after the later of the `prereg-H016b` tag push (2026-10-04 09:48:19 UTC) and the first H016b harness registration commit on origin (`timing_reasons`, tested). Earlier sessions are context only and are never backfilled.

## A15. Entry minute and no_r (DATA K6)
- A tradeable ticket needs BID and ASK bars at exactly t−1m (`entry_bar_bid`, `entry_bar_ask`), else `feed_gap_entry`. The kernel's first selection is the ticket (`session_ticket_log` breaks at the first selection), so a `feed_gap_entry` session never falls through to a later 15m signal (tested on burned 2026-03-23 US100 ny_am).
- A tradeable ticket with binding R = None is `no_r_ticket` (reason logged).
- The pinned foil may draw stale entries (`close_at`); the stale-draw count per replicate is reported (`foil.stale_entry_draws_per_replicate`). The foil method is unchanged.

## A16. One-sided minutes after entry (DATA K7; CASSANDRA/ORION binding fragility leg)
- The pinned `simulate_both` skips BID minutes without an ASK bar (including the BID-side stop check for longs) and ignores ASK-only minutes; both favour a pass.
- Every trade carries (sealed) `one_sided_exit_minutes`, `bid_only_minutes`, `ask_only_minutes` from entry to the pinned exit, and the conservative re-resolution `R_conservative` / `exit_conservative` (`stop_one_sided`, `stop_proxy`) from DATA's `conservative()` v2 (registered verbatim, `one_sided.py`), with `proxy_events`. The p95 proxy-spread floor uses the ASK files this harness has stored for the prior 31 UTC days (20 prior sessions when available, else DATA's documented `p95_session` fallback).
- The report shows `mean_R_conservative_one_sided_exit` next to the headline mean, and `conservative_one_sided_exit` is a fill-fragility leg: a verdict flip under it makes a pass `fill-fragile`, which blocks SURVIVES.
- Burned check (harness): 0 of 258 trades flagged, conservative R = pinned R on all 258, pooled mean +0.1003 (DATA's reference result).

## A17. Fill-fragility set (CASSANDRA C3)
21 legs, each re-run over the counted trades with n, pooled / per-instrument mean, exit flips, the six pass criteria (foil criterion = perturbed pooled mean vs the binding foil distribution), kill and futility:
- `trigger_{stop|target|both}_{+|-}{0.1|1tick}` (12): only trigger levels move, "+" = away from the entry (wider stop / farther target), "−" = towards it; planned risk (R denominator), the registered 2R target (when only the stop moves), the entry fill and slippage are held; a triggered exit fills at the shifted level as `simulate_both` fills. `sim_trigger` at zero shift equals the pinned `simulate_both` on all 258 burned trades (tested).
- `recompute_stop_{+|-}{0.1|1tick}` (4): CASSANDRA's probe variant; the stop itself moves (wider/tighter) and the pinned `simulate_both` recomputes risk and the 2R target.
- `ask_{+|-}0.1` (2): all ASK O/H/L/C shifted.
- `min_risk_{+|-}0.25` (2): re-gating; counted trades with |entry−stop| < min_risk+0.25 drop out, and min_risk-blocked tickets that met every other counting rule (`regate_candidate`) with |entry−stop| ≥ min_risk−0.25 come in (the risk gate sees a flat book, so the min-stop check is the only book-independent block). The count of tickets within ±0.25 of min_risk is reported.
- `conservative_one_sided_exit` (1): A16.
If any leg changes any criterion, the kill or the futility outcome, a pass is `PASSES (unadjusted, fill-fragile)`.

## A18. Burned inputs and hashes (DATA K10, K11)
- Burned reproduction uses the canonical export `/workspace/ftn-demo-output/data/US{100,500}_1m_{bid,ask}.csv.gz` and checks its **decompressed** content sha256 (US100 ask fcc3c877…, bid 6afa3130…; US500 ask ff63783f…, bid 9d68787c…) before use; the gzip-byte hashes in the prereg depend on the gzip header timestamp.
- Disclosure (K11): the EURUSD 61.5-pip median daily range behind the index scale factors rests on 185 days (2025-08-25 → ~2026-05-08) because the HistData-banned span is excluded; the rule constants are unaffected.
- `repull` (CASSANDRA F8): ≥ 20 burned session days re-pulled through `OwnStore` (network by default, refusing any day after 2026-09-25), reproducing the burned trades of those days, with per-day BID/ASK minute alignment, crossed bars, input hashes and bi5 equality with marketdata's native files. Evidence: `research/evidence/quant/H016b_REPULL_BURNED_2026-10-04.json`.

## A19. Imports
Only pinned ftn modules of this checkout may be imported (`unpinned_ftn_modules()`, checked per row → `unpinned_import`, and by test); `ftn.__main__`, adapters, journal, workflow and `marketdata` are never imported.
