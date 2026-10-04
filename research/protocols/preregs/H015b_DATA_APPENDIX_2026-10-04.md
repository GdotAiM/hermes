# H015b data-handling appendix (2026-10-04)

**Applies to:** H015b (`research/protocols/preregs/H015b_FORWARD_PREREG_2026-10-04.json`, tag `prereg-H015b` → 49be2d6). **Paper research only.**
**Source of every item:** DATA_REVIEW_H015_PREREG_2026-10-04 (PASS WITH CONDITIONS, C1–C13) and DATA's canonical-bid ruling of 2026-10-04.
**Status:** committed with the harness and before any R is read. **Harness v2** (2026-10-04, DATA_CERT_H015B_HARNESS B1–B5, ORION ruling: stays H015b): A1, A4, A9, A10 and A12 below were changed before any forward row was computed; see `H015b_HARNESS_REGISTRATION_V2_2026-10-04.json`. It is part of the harness manifest (`harness_sha256`), so any change to it is a harness change.

This appendix only defines how data is handled. It changes none of the binding items: hypothesis, pins, feed, window, cost, exit, filters, N, kill, futility or bound. If an item below ever needs a binding change, that change is H015c, not an edit of this file.

Implementation: `research/forward/H015/duka.py` (feed and store) and `research/forward/H015/h015.py` (sessions, ledger and report).

## A1. Pull time and finality (F7, F9, C7)
- **Pull time.** A UTC day file is pulled no earlier than 01:00 UTC on the next UTC day. The pull is not done after 16:15 NY. A session dated d (NY) uses UTC days d−1 and d, so it is first scored at or after **d+1 01:00 UTC (03:00 SAST)**.
- **Scheduled run.** `python research/forward/H015/h015.py final` at or after 01:00 UTC every day. It scores every pending session date d with now ≥ d+1 01:00 UTC.
- **When a day file is FINAL (v2, DATA cert B1).** A UTC day file is FINAL only when it was pulled at or after 01:00 UTC on the next UTC day **and** it is complete by content:
  - Mon–Fri: the last real bar is at or after **16:14 NY on that same date** (full datetime, B2);
  - Sunday: the last real bar is at or after 23:50 UTC (reopen 18:00 NY); Saturday: always complete;
  - a listed NYSE holiday / early close may be short (no retries).
  
  A 404, empty or cut-off file is **not** final. It is re-pulled on every run (reason `incomplete_repull`) for up to **5 weekdays** after its date, then frozen FINAL with `frozen_incomplete: true` (disclosed in every row that uses it). Replaced non-final bytes are kept under `superseded/`; nothing is deleted. v1 metas (no `finality_rule`) are re-checked.
- **When a session is FINAL.** All of the following must hold:
  - every BID day file it uses (context + session) is FINAL as defined above; any non-final file → `provisional`;
  - its bars run to the 16:14 NY halt **on date d** (full datetime `last >= d 16:14`, B2); if every file is final and the session still ends earlier → `feed_gap`;
  - its context is complete (A4);
  - the min-bar filters have been evaluated.
- **Provisional.** Until a session is FINAL it is `provisional`. No R is computed, stored or shown for it. It is retried on every daily run; a session still incomplete more than 5 trading days after d is frozen as `feed_gap`.
- **Re-pulls.** A re-pull is decided on completeness only, never on R. Every pull is logged with its reason in `pulls.jsonl`.
- **Immutability.** FINAL raw files (by the v2 definition) are immutable. The store never overwrites or re-downloads them.
- **Disclosure: one-day lag.** A session is scored the morning after it trades. The binding outcome is unaffected because the rule is causal on bars (H015 `data_source.why_not_capitalcom`).

## A2. Context feed (F3, C1, C9)
- The ≥22 context sessions are **Dukascopy datafeed BID** day files (`BID_candles_min_1.bi5`), exactly like the counted sessions. That includes context dated before 2026-10-05.
- The harness never reads `/workspace/marketdata` loader output. It never uses `prefer_reused`, the reused research parquet, HistData (banned for 2026-05-13..09-24 by DATA's ruling and not used anywhere), CAPITALCOM or Yahoo.
- There is one pipeline: `duka.py`. Every day file's meta records `source = dukascopy_datafeed` and its URL.
- The only use of marketdata in the harness is the C5 certification command, which compares against marketdata's **native** Dukascopy files (`data/dukascopy/...`, `raw/dukascopy/...`).

## A3. Filler bars (F6, C4)
- The harness drops exactly the vendor filler bars `(volume == 0) & (high == low)`.
- It never synthesises, interpolates or forward-fills a bar.
- The dropped count is stored per day file and per session row.
- A raw download with a duplicate or out-of-order timestamp, or a record that does not decode as 24-byte `>5if`, is a schema failure (`feed_suspended`). It is never re-sorted or repaired (DATA ruling).

## A4. Statuses, context and exit-bar definitions (F10, F15, C8, C9)
**Statuses:** `trade`, `no_trade`, `provisional`, `feed_gap`, `holiday`, `short_session`, `context_gap`, `feed_suspended`, `calendar_not_covered`, `not_trading_day`. Only `trade` rows can be counted.

**Context (v2, DATA cert B3/B4).** Every context file must be FINAL (else `provisional`). The context calendar is the full NYSE calendar: the prereg list, the 2028 list (A10) and the pre-window NYSE holidays 2025-09-01, 2025-11-27, 2025-11-28 (early), 2025-12-24 (early), 2025-12-25, 2026-01-01, 01-19, 02-16, 04-03, 05-25, 06-19, 07-03 and **2026-09-07 (Labor Day)**, so the first sessions 5–7 Oct 2026 are not blocked. Expected trading days absent from `trading_days` (e.g. a day frozen incomplete) are **skipped exactly as the build's `History` skips them** and disclosed per row (`context_missing_days`, `context_frozen_incomplete`). **`context_gap`** is terminal only when fewer than 22 prior sessions exist. One bad day therefore never blacks out the following ~22 sessions.

**Holidays and early closes.** These dates are dropped from counting. They are dropped from `History.days` exactly as in the build, i.e. only through `trading_days` (≥300 RTH bars). The list is a counting filter only.

**"1m bars to 16:00 exist" (v2, binding).** At least one bar in [15:45, 16:00) NY on date d. It is checked for **every** session of the day, trade or no_trade, so session validity never depends on the entry. Failing it makes the session `short_session` (not counted).

**Gap flag (non-binding co-report).** A gap longer than 5 minutes between the entry time and 16:00 is logged per trade row as `gap_flag`. The report shows the flagged count and their summed R next to the headline, plus a non-binding headline with flagged trades excluded.

**PRE-DATA CHANGE to the registered appendix (v1 at 0ff2163, lines 43–45; v1 `exit_bars_ok` applied both conditions).** Deleted binding line:
> - no gap longer than 5 minutes between the entry time and 16:00.

Reason: it is not in the prereg (`counting_rules.min_bar_filter` says only "the 1m bars to 16:00 NY exist for exit resolution") and not in the build; it conditions on post-entry bars; on the burned tape it drops 6 trades with known, decisive outcomes (US100 4/185, US500 2/167; DATA_CERT_H015B_HARNESS §4). CASSANDRA ACKs, DATA agrees, ORION: stays H015b. Zero forward rows had been computed when it was changed.

**Feed outage.**
- A schema change → `feed_suspended`.
- More than 10 consecutive expected trading days of `feed_gap` → counting is suspended (`feed_suspended`).
- The harness never switches feeds. A feed change is a new ID.

## A5. Raw storage and hashes (F11, C10)
- **Storage.** For each instrument, side and UTC day the store keeps:
  - the source `.bi5` file;
  - the normalised `.csv`;
  - a `.json` meta with the sha256 of each, pull time, finality, row count and filler count.
  
  Location: `$HERMES_FWD_DATA/H015b/raw/<inst>/<BID|ASK>/<YYYY-MM-DD>.*`.
- **Row hashes.** Each log row carries:
  - `session_raw_sha256`: sha256 of the ordered list of [day, side, bi5_sha256, csv_sha256] for the session's UTC days d−1 and d;
  - `context_manifest_sha256`: the same over all context + session BID day files;
  - `manifest_file`: the stored list itself.
- **Recompute.** Context is assembled from stored files only. `h015.py verify` recomputes every final row from its manifest and must reproduce the ticket and the sealed outcome exactly.

## A6. Bar labels and timezone (F12, F13, C2, C5)
- Bars are labelled by their **open** time: a bar covers [t, t+1m).
- Dukascopy UTC seconds are converted to America/New_York with `zoneinfo`, and the NY offset is written on every row.
- `ftn.research.bars.load_series` reads the wall clock as-is.
- All rule times are NY wall clock, including the London killzone in US/EU DST-mismatch weeks. The report splits London results by mismatch week.

## A7. Feed wording (F2)
This is fixed in the H015b prereg itself (`data_source.feed`). The build tape was the reused HistData-merged file, which diverges from 2026-05-29. The binding feed is canonical Dukascopy datafeed BID. The burned-tape reproduction (C11) is a code-identity test only.

## A8. ASK side (F4, C3, C13)
- **Binding R.** BID for every leg, plus the fixed cost, as pinned (`outcomes.simulate`).
- **Storage.** ASK day files are downloaded and stored for UTC days d−1 and d of every session.
- **Co-report (non-binding).** A correct-side re-simulation: a long buys at ASK and exits on BID; a short sells at BID and exits on ASK. It is run with stop slip of 0 / 0.25 / 1.0 pt.
- **Spot-check at N = 100 counted trades.** The report lists every short stop-out with its ASK re-simulation, for DATA to inspect. This is descriptive and never changes a binding R.
- **Crossed bars** (ASK < BID) are counted in the spread co-report.

## A9. Spread and crossed-bar monitor (F5, C3, C13; DATA cert condition a)
- Every `report` (sealed or not; no R involved) gives `data_monitor_monthly`: per instrument-month, the median (ASK close − BID close) over killzone minutes of **every scored session** (trade, no_trade, short_session) and the crossed-bar count (any of O/H/L/C with BID > ASK). DATA reviews it monthly.
- The month is flagged if the median exceeds **1.1 pt (US100)** or **0.5 pt (US500)**.
- The binding cost is unchanged.

## A10. 2028 holidays (F8)
Added to the counting calendar, from the NYSE rules as listed by DATA:
- **Full closures:** 2028-01-17, 02-21, 04-14, 05-29, 06-19, 07-04, 09-04, 11-23, 12-25.
- **Early closes:** **2028-07-03**, 2028-11-24.

Dates after 2028-12-31 are `calendar_not_covered` until the list is extended.

**Reminder (DATA cert condition b):** the 2029 NYSE list must be committed **before 2029-01-02**. `calendar_not_covered` is terminal, so a late extension loses sessions. (The test runs ~28 months.)

## A11. Feed outage policy (F15)
On an outage or schema change, counting is suspended and the feed is never switched. Resuming after a suspension needs DATA's sign-off in the ledger notes. Changing the feed needs a new ID.

## A12. Sealing and clearance (prereg `reviews_required_before_first_R`)
- **Sealed outcomes.** R, exit and cost are written only to `sealed/outcomes.csv`. `final` never prints them.
- **Clearance files.** `report` shows R and statistics only when both `DATA_CERTIFIED.json` and `CASSANDRA_CLEARED.json` exist in the data dir, each with `"harness_sha256"` equal to the registered harness digest.
- **Cert key (DATA cert condition c).** Both clearance files must carry the key **`harness_sha256`** (that is the key `h015.cleared()` reads) with the v2 digest. Files carrying the v1 digest do not unseal anything.
- **Futility set.** The first time counted N reaches 200, the 200 row keys are written once to `FUTILITY_SET.json`; futility is evaluated on exactly that set and any later reshuffle is reported (CASSANDRA condition 4).
- **Resume.** Resuming after a suspension needs `FEED_RESUMED.json` from DATA (condition d).
- **No verdict below 100.** Below N = 100 counted trades there is no verdict or edge wording.
- **Feed disclosure.** Every report states that the feed is Dukascopy BID, not the TradingView CAPITALCOM feed used by H013/H014.
