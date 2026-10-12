# Screening pipeline protocol v1 (written and committed BEFORE any screening run)

Status: **registered before batch 1**. No new instrument data had been downloaded, and no screening statistic had been computed, when this file was committed.
Author: ntloso ngubeni (via Grok Bot). Date: 2026-10-04 SAST. Paper research only; no orders, no broker, not MINT.

## 0. Purpose and sealing

The purpose is to rank candidate hypotheses by their chance of passing a holdout **before any holdout is spent**. A screening result is never evidence for a hypothesis. It only decides whether a hypothesis *earns* a holdout test, which still has to be pre-registered separately (H017+).

**Sealed. Never opened, decoded, hashed or listed by this pipeline:**
- US100 2019-01-01 .. 2022-12-23
- US500 before 2025-06-01
- every file under `/workspace/marketdata` that covers those ranges
- the 2019-2020 BID backfill

The pipeline does not read anything under `/workspace/marketdata`. It does not touch the frozen H015/H016b worktrees or tags, or `/home/box/hermes-x/forward/H016b`. It never reads a bar file dated 2026-10-05 or later; screening data ends 2026-09-25. The H016b forward results are read only via S4, and only once allowed (see S4).

## 1. Data

| Use | Instrument | Window | Source |
|---|---|---|---|
| burned (S2, S3, power) | US100, US500 | 2025-08-25 .. 2026-09-25 | the canonical burned BID+ASK tape `/workspace/ftn-demo-output/data/US{100,500}_1m_{bid,ask}.csv.gz` (sha256-pinned in `ftn.pipeline.invariance.DATA_SHA256`); the H016b registration trades |
| S1 transfer (new) | GER40 (`DEUIDXEUR`), US30 (`USA30IDXUSD`), XAUUSD (`XAUUSD`) | UTC days 2023-01-01 .. 2026-09-25 | fresh Dukascopy public datafeed 1m `BID_candles_min_1.bi5` and `ASK_candles_min_1.bi5` (pattern of `scripts/dl_dukascopy.py` / `research/forward/H016b/duka.py`), converted to America/New_York wall clock |

- REV was never tuned on GER40, US30 or XAUUSD. The XAUUSD fixtures in `ftn/fixtures` are Month-6 lesson reconstructions, not REV scoring.
- The first ~22 sessions of the S1 window are kernel context only.
- If an instrument has fewer than 200 trading days under the unchanged trading-day filter (at least 300 1m bars in 09:30-15:59 NY), it is reported as *not applicable* and dropped from S1. This rule is declared here, before any data is seen.

## 2. The rule under test (REV, unchanged)

- The Month 9 kernel exactly as on `main` @ `0df97e3`: `ftn.pipeline.invariance.base_cfg()` (interpretation triggers off), `History(..., calendar=True)`, `session_ticket_log` with a flat book, killzones London 02:00-05:00 and NY AM 07:00-10:00 NY.
- Correct-side BID/ASK fills via `simulate_both` with the instrument's slippage floors, 2R target, time exit before 16:00 NY.
- No kernel, model, risk or scoring file is edited; every H016b pin test must stay green. Non-US instruments get `other=None`, which affects features only.
- **Instrument scaling rules for new instruments.** These are the only permitted differences. They are declared before results and computed mechanically by `research/screening/instruments.py`, which registers specs at runtime without editing `ftn/os/instruments.py`. All scaling measurements use the window 2025-08-25 .. 2026-09-25 of the instrument's own new data, the same window as the pinned US100/US500 values.

| Field | Rule |
|---|---|
| `pip` | GER40 1.0 and US30 1.0 (index point); XAUUSD 0.1 (existing ftn convention for XAU) |
| `asset` | index / index / metal |
| `range_scale` | median of the daily (18:00 NY → 17:00 NY session) BID high−low, in pips, divided by 61.5 (the pinned EURUSD median) |
| `spread_assumed` | p90 of (ASK close − BID close) over 1m bars present on both sides inside the two killzones. This mirrors the "conservative off-RTH p90" used for US100/US500 |
| `slip_stop = slip_market` | max(0.335 × `spread_assumed`, `price_bp` × median BID close). 0.335 is the mean of the pinned US100 (0.50/1.55) and US500 (0.25/0.72) slip/spread ratios. `price_bp` is the pinned US500 `slip_stop` (0.25) divided by the US500 median BID close on the burned tape |
| `slip_limit` | 0.5 × `slip_stop` |
| `min_risk` | unchanged formula: 4 × (`spread_assumed` + 2 × slip) |

All values are rounded to 3 decimals. The computed specs are written to the batch output before any outcome is simulated.

## 3. Stages and thresholds

The screening family is a **batch**. Within a batch, every p-valued stage is Holm-adjusted across the batch's candidates at **α_screen = 0.10**. Batch 1 has 3 candidates, so each stage has a Holm family of 3.

Cluster = (date, killzone) across instruments. Bootstrap = 10,000 cluster resamples with seed 20261004.

### S1: other-market transfer (new instruments)
- **Run:** the candidate on the S1 instruments over 2023-01-01 .. 2026-09-25.
- **Statistic:** pooled mean R.
- **p1:** one-sided cluster-bootstrap p for H0 mean R ≤ 0, i.e. the fraction of resampled means ≤ 0 (minimum 1/10,000).
- **PASS** if Holm(p1) ≤ 0.10 **and** the mean R is > 0 on a strict majority of the S1 instruments that have ≥ 20 trades.
- **Fewer than 30 pooled S1 trades** means FAIL (insufficient).

### S2: time-split stability (no parameters are fitted, so walk-forward = fixed-rule time splits)
- **S2a (burned):** split the candidate's burned-window trading days (US100/US500) into 4 contiguous folds of equal trading-day count. Mean R must be > 0 in ≥ 3 of 4 folds.
- **S2b (S1 data):** calendar-year folds 2023, 2024, 2025 and 2026 (to 09-25), S1 instruments pooled. Mean R must be > 0 in ≥ 3 of 4 folds.
- A fold with n < 10 counts as not positive.
- **PASS** if S2a and S2b both pass. S2 is rule-based, so there is no p-value and no Holm.

### S3: null tests (does the rule profit on noise?)
Run on the burned US100 + US500 tape. **50 replicates per null type**, seeds 20261004 + k. Each replicate re-runs the full unchanged REV pipeline on synthetic BID+ASK bars, and the candidate's filter is applied to the null tickets.
- **Null A (shuffled-day block bootstrap):**
  - Randomly permute each instrument's sessions (18:00 prev → 17:00 NY), keeping each session's intraday BID and ASK path intact.
  - Shift prices additively so each session opens at the previous slot's last BID close; ASK gets the same shift, so spreads are preserved.
  - Timestamps are mapped to the slot's date.
  - This keeps intraday volatility, spreads and bar gaps, and destroys real multi-day structure (PDH/PDL vs HTF arrays).
- **Null B (matched-volatility random walk):**
  - Same timestamps as the real BID bars.
  - Close-to-close change ~ N(0, σ_m), where σ_m is the real standard deviation of 1m BID close changes for that minute-of-day (NY), measured on the burned tape.
  - open = previous close; high = max(o, c) + |N(0, σ_m/2)|; low = min(o, c) − |N(0, σ_m/2)|.
  - ASK = BID + the real (ASK−BID) close spread of that timestamp, only where a real ASK bar exists.
- **p3** for a null type = (1 + #{replicates with null mean R ≥ real mean R}) / 51. A replicate with no candidate trades counts as ≥ real. The candidate's p3 is the **max over the two null types**.
- **PASS** if Holm(p3) ≤ 0.10 **and** the real mean R is > 0.

### S4: H016b live paper results (interface only in v1)
- `research/screening/s4_h016b.py` is a read-only stub.
- It may only ever read **sealed outputs** of the registered H016b harness, and only when that harness's `DATA_CERTIFIED.json` and `CASSANDRA_CLEARED.json` both exist with the harness digest `8a752e769e045b063df9a7b5ef9942f71aa4399bae53bfd9c6637a668c7819a5`.
- Until then it returns `SEALED` without touching the filesystem path. Batch 1 does not call it with any real path.
- S4 is not part of the batch 1 gate.

### Gate: does a candidate earn a holdout?
A candidate **qualifies** only if S1, S2 and S3 all PASS **and** its projected realistic holdout power is ≥ 0.80. Power is computed as follows.

- **Holdout (planning assumption; nothing is opened):** US100 2019-01-02 .. 2022-12-23 = **1,004** trading days. US500 2019-01-02 .. 2025-05-30 = **1,612** trading days (the US500 start date is to be confirmed by DATA). C3 uses US500 only.
- **Trade rate:** the candidate's burned trades per burned trading day, per instrument (trading days from the unchanged filter on the burned tape). N_hold = Σ rate × holdout days.
- **Era costs** (assumption, unverified because the holdout is sealed): all frictions (spread + market slip + stop slip) are ×1.5 vs the pinned 2026 values. For each burned trade, R_era = R − 0.5 × (spread_assumed + slip_market + slip_stop) / risk_pts. A ×2.0 sensitivity is reported but is not gating.
- **Planning effect:** μ_plan = 0.5 × min(mean R_era on burned, mean R on S1). The factor 0.5 is a shrinkage for selection and winner's curse. If S1 has no trades, the S1 term is treated as 0.
- **σ** = SD of burned R_era. **deff** = (cluster-bootstrap variance of the burned mean) / (σ² / n_burned), floored at 1.
- **Power** = Φ(μ_plan / (σ √(deff / N_hold)) − 1.96), i.e. one-sided α = 0.025. If μ_plan ≤ 0, power is reported as ≤ 0.025.
- Also reported, not gating: the power at the unshrunk μ, and the N needed for 0.8.

## 4. Batch 1 candidates (declared now)

| ID | Candidate | Burned set (S2, S3, power) | S1 set |
|---|---|---|---|
| C1 | REV baseline (H016b rule, all tickets) | US100 + US500, all burned trades | GER40 + US30 + XAUUSD |
| C2 | REV Wednesday-only (NY date weekday = Wed; from `/workspace/ftn-context-breakdown`, best of 18 burned looks, so already selection-inflated) | Wednesday trades of US100 + US500 | Wednesday trades on GER40 + US30 + XAUUSD |
| C3 | REV US500-only | US500 burned trades | the "new indices" analogue: GER40 + US30 (no gold) |

## 5. Reporting and deviations
- For each candidate the report gives N, mean R, cluster CI, win rate and per-stage verdicts (with raw and Holm p), plus the projected holdout power and the gate verdict.
- Any change to this protocol after batch 1 results are seen is listed as a dated deviation, and batch 1 is reported as run.
- If a download is incomplete, S1 runs on whatever is complete. Missing day files are counted and reported, and S1 is marked provisional.
