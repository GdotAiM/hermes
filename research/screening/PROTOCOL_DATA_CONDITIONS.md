# Screening protocol: Addendum on DATA's screening-feed conditions (DAX / Dow / XAUUSD)

**Added:** 2026-10-05 (SAST), on branch `research/screening-pipeline` (PR #8).
**Source (binding, owner DATA):** `/home/box/hermes-x/investigations/POST-WAVE1-LEADS/DATA_CONDITIONS_SCREENING_FEEDS_DAX_DOW_XAU_2026-10-05.md`, sha256 `758d6d5de2b3dd0682f3b96ce1c45f12921622021cb2e1b8060b8b6d38c8e628`.
**Scope.** This addendum changes no statistic, threshold or result of batches 1–3. It records DATA's conditions, states the status of the results already produced, and blocks further scoring on the screening tape until the remediation checklist (§4) is cleared. No data was downloaded, and no sealed holdout bar was opened, to write it.

## 1. DATA's conditions C1–C12 (quoted from DATA's §4 "Concise condition list"; attribution: DATA, 2026-10-05)

> 1. Instruments: datafeed **`DEUIDXEUR`**, **`USA30IDXUSD`**, **`XAUUSD`** (not dotted trading symbols); scale 1e3 provisional; probe before bulk.
> 2. Window **2023-01-01 → 2026-09-25** only; hard cap; **no reads ≥ 2026-10-05** (H016b).
> 3. **H017 seal:** no US100/US500 reads in certified ranges; no download of those INST before 2022-12-24; separate screening manifest.
> 4. **Do not contend** with the running `default` downloader on shared RAW/throttle; queue after FX or use an isolated raw root.
> 5. Always **BID+ASK**; never call BID "mid"; decompressed-content sha256 + screening manifest.
> 6. Bar OPEN timestamps; DAX needs Frankfurt TZ + calendar (else CFD-session only); Dow NYSE; gold daily break + weekend gaps; no forward fill.
> 7. Drop only zero-volume flat fillers; per-side finality; report one-sided minutes and crossed bars; hard-fail dup/out-of-order.
> 8. Verify price scale bands; report CFD roll jumps; do not flatten gold weekend gaps.
> 9. Measure spread p50/p90/p99 by hour; costs ≥ spread; correct-side fills; provisional slip DE40/US30 0.5/1.0 pt, XAU 0.05/0.10 until replaced.
> 10. Transfer results = **in-sample screening** with multiple-testing disclosure; not confirmatory; no certified-untouched claim.
> 11. QC gate (hashes, calendar label, one-sided/crossed, scale, spread draft) must PASS before PnL scoring.
> 12. Provenance language: Dukascopy BID/ASK only; stamp `data=dukascopy-screening-2023-20260925`.

C1–C12 in full, with sub-clauses, are in the source file (§1 there). The mapping is: list item *n* above = DATA condition C*n*. Where the full text is stricter than the summary, the full text governs.

### Downloader-isolation blocker (quoted: DATA C3 and Blocking item B1)

> **C3: Downloader isolation from the running `default` plan (BLOCKING if ignored).** Observed state at ~08:23 SAST 2026-10-05: pids 1874362 / 1874367 are running `dl_dukascopy.py --plan default --threads 2`. Shared `PACE` AIMD throttle; shared `RAW = raw/dukascopy/`. […] That is step 6 of `default_plan` (EURUSD / GBPUSD / XAUUSD BID+ASK, newest first). The US100/US500 2019–20 BID backfill is part of the same job queue.
> 1. Do not start a second `dl_dukascopy.py` against the same RAW + same process host while default is mid-FX. […]
> 2. Allowed patterns: (A) Queue after default FX […] or (B) Separate raw root + separate machine/container with its own throttle, never writing under `USATECHIDXUSD/` or `USA500IDXUSD/`.
>
> **B1:** Running `default` downloader (pids ~1874362/1874367) holds the shared RAW + global throttle and is mid-FX (incl. XAUUSD). Parallel screening pull is forbidden (C3). Clearance: wait for default FX DONE, **or** use a separate raw root on a separate host (C3-B).

At 08:3x SAST 2026-10-05, `ps` shows both pids still running (elapsed ≈ 9 h 53 m). Other open DATA blockers that apply here: B2 (no Xetra calendar), B3/B4 (scale and INST probe), B5 (provisional slip floors), B6 (H017 backfill in the default queue).

## 2. What batches 1–3 already ran on (statement of fact)

1. **Feed.** All S1 scoring in batches 1–3 used `/workspace/screening-data`:
   - Dukascopy public datafeed, 1m **BID and ASK** day files for INST **`DEUIDXEUR`** (GER40), **`USA30IDXUSD`** (US30) and **`XAUUSD`**.
   - UTC day files 2023-01-01..2026-09-25 (Saturdays skipped), 7,020 day files.
   - Built by `research/screening/dl.py`. Build report: 0 missing day files; empty weekday files GER40 6, US30 3, XAUUSD 4.
   - Last bar date 2026-09-25 for all three. No bar ≥ 2026-09-26 was downloaded, read or scored.
2. **Isolation from `default`.**
   - Raw root: `/workspace/screening-data/raw/<INST>/<SIDE>/<YYYYMMDD>.bi5`, separate from the `default` plan's `raw/dukascopy/` tree.
   - Its own downloader (`dl.py`, its own thread pool, no shared `PACE` throttle).
   - Its own manifest (`batch1/s1_data_manifest.json`).
   - It never wrote, read or enqueued `USATECHIDXUSD`/`USA500IDXUSD`; `dl.py` hard-refuses those INST, any date outside the window, and `/workspace/marketdata`.
   - **Correction (DATA addendum 2026-10-12 §2): concurrent, separate raw roots.** The earlier claim that the pull ran "before the default pids started" is **false**. The `default` pass started at 2026-10-04 11:55:27 SAST (`dl_dukascopy.log` line 594). Screening ran from about 14:39 to 15:13 SAST (pipeline-code commit 019f6d4 at 14:39:36, batch 1 results a2af9a7 at 15:13:28). So the screening pull ran **concurrently** with the default/backfill pids, on the same host and egress IP, adding throttle pressure. It used a separate raw root, log/state and manifest. The pull time comes from commit times, not file metadata: raw `.bi5`, `download.log` and `build_report.json` mtimes all read 2026-10-09 01:21–01:22 SAST (a copy/restore), and `download.log` has no timestamps.
   - Integrity is unaffected (DATA s2): 1,400 of 1,402 overlapping XAUUSD day files are byte-identical when decompressed. The 2 that differ (2024-12-11 BID/ASK) differ only in one volume value (a vendor revision); time and OHLC match.
3. **Sides used.**
   - Batch 1 (REV, via ftn) filled on BID and ASK.
   - Batches 2 (Model U, MMXM) and 3 (E1–E5) are BID-only rule engines. They charged a round-trip friction F (spread + 2 × slip) in points instead of side-correct ASK fills.
   - No series was labelled or used as "mid".
4. **US100/US500.** Only the burned tape `/workspace/ftn-demo-output/data/US{100,500}_1m_{bid,ask}.csv.gz` was used: 2025-08-24 18:00 NY .. 2026-09-25 16:14 NY, read via `ftn.pipeline.invariance.load_histories()`. That means:
   - no certified-range reads (US100 2019-01-01..2022-12-23; US500 before 2025-06-01 18:00 NY);
   - no H017 pool A;
   - no 2019–20 backfill;
   - no `untouched="certified"`;
   - no `prefer_reused`;
   - no bar ≥ 2026-09-26.

## 3. Status of batch 1–3 results

1. **In-sample screening only:** `design=in-sample-screening`, `data=dukascopy-screening-2023-20260925`. The screening-manifest content hash is **pending**. The existing manifest hashes the built `.csv.gz` files, not the decompressed bi5 content that C4.3 requires; see §4 item R1.
2. **No confirmatory claim, no holdout claim, and no certified-untouched claim** on DE40, US30 or XAUUSD. Nothing in batches 1–3 unlocks H017 bytes or changes the status of any rule.
3. **Conditions issued after the runs.** Batches 1–3 were scored on 2026-10-04, before these conditions existed and **without** the C11 QC gate PASS. Their S1 numbers therefore carry the flags `qc_gate=not_run`, `slip=provisional` and `session=cfd` (GER40 = `cfd_deu`, US30 = `cfd_usa30`, XAUUSD = `cfd_xau`; no Xetra claim was made). No candidate qualified in any batch, so no decision depends on these numbers.
4. **Multiple-testing disclosure (C10.2).** `n_instruments=3`. All cells were pre-declared in a protocol committed before the run. Holm was applied within each batch at α = 0.10 (S1, S3). No cell is reported as selected post hoc. Across the three batches: 3 batch families, 14 pre-declared candidates, 41 S1 instrument×candidate cells, with no correction across batches.

   | batch | family | k (n_specs_in_family) | S1 cells | note |
   |---|---|---:|---:|---|
   | 1 | REV (H016b rule) and filters | 3 | 8 | C3 was GER40+US30 only. C2 (Wednesday) was itself a post hoc pick from 18 burned looks, disclosed in batch 1. |
   | 2 | Model U v1 + MMXM v1–v5 | 6 | 18 | Frozen rules. Tick and cost ρ-scaling declared beforehand. |
   | 3 | simple session rules E1–E5 | 5 | 15 | New rules. Parameters fixed before any data read. |

5. **Cost-floor cross-check vs DATA C8 provisional floors** (information only; affects no verdict):
   - Batch 1/2/3 slips were US30 1.775 stop/market and 0.887 limit, and XAUUSD 0.281 and 0.141. Both are at or above DATA's floors.
   - GER40 used 0.884 stop/market and 0.442 limit, which is **below** DATA's DE40 floors of 1.0 / 0.5 points. GER40 costs in batches 1–3 were therefore lighter than DATA's provisional floor. Batches 1 and 3 GER40 means are all ≤ 0. **Batch 2 is not:** rescored at DATA's floor round trip of 4.624 pt (was 4.392), D3 MMXM v2 = **+0.125R** (95% CI −0.16 to +0.42, n=43) and D5 MMXM v4 = **+0.174R** (95% CI −0.12 to +0.47, n=40). These are `slip=provisional` first-order rescorings (trade set held fixed). Neither is significant, no verdict changes, and both need a full re-run before any promotion. (The earlier "all GER40 means ≤ 0" wording was wrong; DATA addendum 2026-10-12 §3.)
6. **Scale band note for DATA (C7.1 / §0).** The decoded BID close range by year is:

   | instrument | 2023 | 2024 | 2025 | 2026 (to 09-25) |
   |---|---|---|---|---|
   | GER40 | 13,850–17,000 | 16,347–20,522 | 18,875–24,770 | 21,865–26,618 |
   | US30 | 31,429–37,782 | 37,134–45,073 | 36,569–48,881 | 44,825–54,737 |
   | XAUUSD | 1,807–2,145 | 1,985–2,790 | 2,617–4,549 | 3,944–5,593 |

   **Amended bands (DATA addendum 2026-10-12 §1). These replace the §0 single bands.** VERIFIED as market trend, not decode error. The tape extremes match public references within 0.1%.
   - (a) Scale-error detectors (hard fail): consecutive-bar close ratio or tape-vs-reference ratio outside [1/1.5, 1.5]; any ratio within 5% of 10/100/1000 (or reciprocals); ASK/BID outside [1.0, 1.01]; decode scale fixed at 1e3 for DEUIDXEUR, USA30IDXUSD, XAUUSD.
   - (b) Per-year plausible ranges (warn/fail), to be revisited before any 2027 data:

     | Year | GER40 | US30 | XAU |
     |---|---|---|---|
     | 2023 | 12k–19k | 28k–42k | 1.6k–2.4k |
     | 2024 | 14k–23k | 32k–50k | 1.7k–3.1k |
     | 2025 | 16k–28k | 32k–55k | 2.2k–5.1k |
     | 2026 | 18.5k–30k | 38k–61k | 3.4k–6.3k |
   - (c) Each year's tape extremes must be within 1% of a cited public reference, recorded in the QC report.
   - **Band check: PASS** under (a)–(c) (DATA: "R7 band item: PASS").

## 4. Remediation checklist: required before ANY further scoring on `/workspace/screening-data`

Further scoring of any candidate on this tape is **blocked** until every item below is DONE and a `DATA_SCREENING_FEED_GATE_*.md` records PASS (C11). Status: **R7 CLOSED** (DATA addendum 2026-10-12, band check PASS). All other items remain **OPEN**. Progress on R1 is recorded in §6.

| # | Item (DATA ref) | Deliverable | Current state |
|---|---|---|---|
| R1 | Separate screening manifest with **decompressed-content sha256** (C2.5, C4.3, C4.4) | `data/screening_manifest_DAX_DOW_XAU_2023_20260925.json` (or under `/workspace/screening-data/`). One entry per day file: INST, SIDE, UTC date, bytes on disk, sha256 of the lzma-decompressed bi5 payload (zero-byte = documented 404/empty), rows after filler drop, first/last bar UTC, decode scale 1e3. Plus the manifest's own content hash, to stamp on result tables (C10.4). | Only `.csv.gz` sha256s exist (`batch1/s1_data_manifest.json`). |
| R2 | §0 probe / scale (B3, B4, C7.1) | A recorded single-day HTTP 200 + decode check per INST/SIDE (e.g. 2024-06-12). The existing raw file may serve as evidence if DATA accepts it; otherwise wait for a non-contending probe (R10). DATA amends the sanity bands (see §3.6). | The scale is consistent across 2023–26 (no 10× jumps), but no band PASS exists. |
| R3 | **CFD session labels, not Xetra** (C5.2–C5.4, B2) | Every bar and result carries `session=cfd_deu` / `cfd_usa30` / `cfd_xau`. DAX also exposes `ts_frankfurt`. DST-mismatch weeks are logged. Any Xetra-RTH claim waits for a DATA-filed Xetra calendar. | Bars carry a NY-offset timestamp only; there are no session labels. GER40 day eligibility used NYSE closures. |
| R4 | **QC gate report** (C11) | An automated `DATA_SCREENING_FEED_GATE_<date>.md` with PASS/FAIL for: probe, hashes (R1), calendar label (R3), filler / one-sided / crossed (R5), scale band (R2), spread table (R7). | None. |
| R5 | **One-sided / crossed counts, duplicates, finality** (C6.2–C6.6) | Per UTC day and side: BID-only and ASK-only minute counts; crossed minutes (`ask_x < bid_x` for o/h/l/c, tolerance 0); a hard fail on duplicate or out-of-order timestamps; per-side finality flags (`frozen_incomplete`, `feed_gap_{bid,ask}`). Days failing a check are excluded from primary scoring. | Filler drop already matches C6.1 (`v==0 & high==low`, per side). BID and ASK row totals are equal per instrument, but no matched-minute, crossed or duplicate check has been run. |
| R6 | **Roll tags** (C7.2, C7.3) | Day-over-day basis-jump report at equity-futures roll clusters for GER40 and US30, with roll-adjacent days tagged in the screening output (not "fixed"). Gold weekend and daily-break gap sizes reported, not filled. | None. |
| R7 — **CLOSED 2026-10-12** | **Spread by hour** (C8.1, C8.5) | ASK−BID on matched minutes: p50/p90/p99 by local hour of day, RTH vs off-hours, per year 2023–2026. Minutes with BID but no ASK are excluded from primary fills. | Batch 1 measured a single p90 spread (killzone) per instrument only. |
| R8 | **Cost floors** (C8.2–C8.4, B5) | Primary cost ≥ the measured spread for that minute, with side-correct fills (buys on ASK, sells on BID), plus DATA's provisional slip floors (DE40/US30 0.5 limit / 1.0 stop pt; XAU 0.05 / 0.10). Required sensitivity: p90 spread + 2 × provisional slip. Every result is stamped `slip=provisional` until DATA accepts the floors. The BID-only engines (batch 2/3 style) must be adapted to side-correct fills, or carry an explicit DATA waiver. | GER40 slips are below DATA's DE40 floor (§3.5). Batches 2/3 used a flat per-trade F. |
| R9 | **Provenance stamps** (C10.2, C10.4, C12) | Every result table carries `design=in-sample-screening`, `data=dukascopy-screening-2023-20260925`, the R1 manifest hash, `family`, `n_instruments=3`, `n_specs_in_family`, and the multiple-testing disclosure. Language: "Dukascopy BID/ASK" only. | Added to this addendum and as a banner on the batch 1–3 reports. The manifest hash is pending R1. |
| R10 | **Download discipline** (C1, C2, C3, B1, B6) | No new download while the `default` pids (~1874362/1874367) run. Any future pull either queues after default FX is DONE (C3-A), or uses an isolated raw root on a separate host/container with its own throttle (C3-B), and states which in the run log. Never enqueue, fetch, read or rehash `USATECHIDXUSD`/`USA500IDXUSD` before 2022-12-24, the H017 2019–20 backfill, the certified US100/US500 ranges, or any bar ≥ 2026-09-26 (and never ≥ 2026-10-05). | No download is planned. `dl.py` already refuses US INST, out-of-window dates and `/workspace/marketdata`. |

## 5. Rules that bind from this commit
1. **No further scoring** on `/workspace/screening-data` until R1–R9 are DONE and the C11 gate is PASS.
2. **No new download** while the default pids run. After that, use C3-A or C3-B only. `research/screening/dl.py` is not to be re-run for these INST until R10 is satisfied.
3. **Never touch** the H017 2019–20 backfill, the certified US100/US500 ranges, the H016b forward window (≥ 2026-10-05), or any bar after 2026-09-25 for screening.
4. Batches 1–3 stay as reported, labelled in-sample screening. Nothing is re-run or re-tuned as a consequence of this addendum.

## 6. Download provenance and raw manifest (DATA addendum 2026-10-12 §2 open items)
Read-only investigation. No download was run.

1. **Pull time.** This comes from commit times only (§1.2). File metadata can't show it, because all 7,020 raw mtimes are 2026-10-09 01 SAST (a restore).
2. **The 571 pre-existing ("skip") files.** `download.log` is one pass of `dl.py download` (7,020 jobs, newest day first, ordered day → INST → side). Skips were 195 of the first 200 jobs, 392 of the first 400, and 571 of the first 600, then stayed at 571. So the skipped files are about the newest 571 jobs (UTC days around 2026-06-02..2026-09-25, all three INST, both sides). They were not copied from `marketdata`: they include DEUIDXEUR/USA30IDXUSD, which that tree doesn't hold, and `dl.py` only writes under `$SCREENING_DATA/raw`. The pattern fits an **earlier, interrupted run of the same `dl.py`** into the same root, with a log that was overwritten. No log, transcript or mtime for that earlier run survives, so this is inferred, not proven. Their content is now hashed in the manifest below.
3. **The 63 failed jobs.** `dl.py` returns `fail` after 6 tries with backoff and writes no file. The log only has cumulative counters, so the individual jobs can't be named. Fail increments by 200-job window, as UTC day ranges: 2026-03-16..04-23 (1), 2026-02-05..03-16 (16), 2025-12-28..2026-02-04 (5), 2025-11-19..12-28 (1), 2025-05-08..06-16 (3), 2025-02-20..03-31 (4), 2025-01-12..02-19 (2), 2024-08-09..09-17 (1), 2023-11-12..12-20 (12), 2023-10-03..11-10 (10), 2023-02-12..03-22 (3), 2023-01-04..02-12 (4), 2023-01-01..01-04 (1); total 63. **Resolution:** all 7,020 raw files exist now, and none is zero-byte or missing (manifest). `build_report.json` shows 0 missing day files. So every failed job was filled by a later idempotent re-invocation of `dl.py download`, which skips existing files. That re-run's log was not kept, which matches the empty-marker-free tree (0 HTTP 404s in the logged pass). Per-job resolution can't be shown beyond this.
4. **Raw manifest (C4 / R1).** `research/screening/s1_raw_manifest.csv` was generated by `research/screening/raw_manifest.py` (read-only). It has one row per INST × side × UTC day (7,020 rows): raw bytes, raw sha256, lzma-decompressed bytes, **decompressed sha256** and record count. 0 missing, 0 zero-byte. Manifest file sha256 = `4deac902f639ada94b0248721581eb617b76c7e154ec752f8e0727dd0b30af48`. R1 stays OPEN until the remaining fields (rows after filler drop, first/last bar UTC) and the JSON form are added and DATA accepts it.
