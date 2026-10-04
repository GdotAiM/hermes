# Screening protocol: Addendum for batch 2 (Model U v1 and MMXM v1–v5)

Committed and pushed on 2026-10-04 before any batch 2 S1, S2, S3 or power number was computed. The only runs before this commit were a smoke test of the vendored code: a burned-tape reproduction at **frozen** costs (Model U H013 OOS window; MMXM v5 A), done to time the code and confirm it matches the published numbers. All of those numbers were already published and burned. Everything in `PROTOCOL.md` v1 applies unchanged unless this addendum overrides it: stages S1, S2 and S3, the gate, cluster bootstrap B = 10,000 with seed 20261004, α_screen = 0.10, N_NULL = 50 per null type, era costs ×1.5, μ_plan = 0.5 × min(burned era mean, S1 mean), power one-sided α = 0.025, and holdout day counts US100 1,004 / US500 1,612.

H017 holdout: SEALED and untouched. Not read: US100 2019-01-01..2022-12-23, US500 before 2025-06-01, the 2019–20 backfill, `/workspace/marketdata`, the model-u-longrun `data/` folder, and any bar after 2026-09-25. The H013, H014, H015 and H016b frozen worktrees, tags, forward folders and pinned files are only read. The code was **copied** into `research/screening/batch2/vendor/` and `batch2/configs/`, and its hashes are verified at import time (`batch2/adapters.py: verify_pins`).

## A. Candidates (Holm family = these 6, for S1 and for S3)

These are pre-defined versions only. No new variants, and nothing is tuned after results.

| ID | Candidate | Source (frozen copy) | Rule invocation | Development / in-sample window (all inside the burned tape) | Holdout set (power) |
|---|---|---|---|---|---|
| D1 | **Model U v1** (H013, as frozen) | `research/forward/H013/frozen/research/model-u-longrun/scripts/v1/{u_engine,run_u_lib}.py` | `best_trade(ctx_for(df,d,sym), "11:00", False, False, True)`; FILL_THRU = 1 tick; R = `R_part` (the 50/50 partial, H013's primary) | US100 BID 2025-09-02..2026-09-25 (rule IS 2026-09-14..25, backward OOS 2025-09-02..2026-09-11); US500 disclosure only | US100 only (H013 decision series) |
| D2 | MMXM v1 default | `configs/v1_default.yaml` | `engine.run_backtest(m1, cfg, root, sym)` | CFD 2025-08-25..2026-09-25 (v1 was not selected; it is the base spec) | US100 + US500 |
| D3 | MMXM v2 selected | `configs/v2_overnight_LHon_from0930.yaml` (`output/v2/selection.json` "chosen"; IS 32 trades, −4.36R) | same | IS 2025-08-25..2026-05-24, OOS 2026-05-25..09-25 | US100 + US500 |
| D4 | MMXM v3 selected (NOT QUALIFIED in v3) | `configs/v3_asia_LHoff_daily_draw.yaml` (`selection_v3.json` "chosen") | same | same | US100 + US500 |
| D5 | MMXM v4 selected (NOT QUALIFIED in v4) | `configs/v4_overnight_LHon_midnight_open.yaml` (`selection_v4.json` "chosen") | same | same | US100 + US500 |
| D6 | **MMXM v5 A** (H014, as frozen) | `research/forward/H014/frozen/configs/v5_A_overnight_5mFVG_ce_c12_none.yaml` | same | same | US100 + US500 |

The 7 MMXM sensitivity configs and the non-selected v2–v5 variants are **not** version picks. They are excluded.

## B. Code hashes (sha256, verified at run time)

| file | sha256 |
|---|---|
| vendor/model_u/u_engine.py | 5e98e99e47133905c6662afcdea9d9df4ef74e7afefa49f17e7798925613fe4e |
| vendor/model_u/run_u_lib.py | 8d00223c1f326bd386c1f924f05dc92fd38a3674639b57cd96df12194cdddad2 |
| vendor/mmxm/__init__.py | 6899cc98e28059141b39ac009c61e496d2bd19da256a5ae6d3480337f7643913 |
| vendor/mmxm/baseline.py | 8298952b8dcd2903e1783bb70a97ed257c255d2b613609c5c0373f72778516ed |
| vendor/mmxm/config.py | 4614c85b38c52f60018bd1b174368b4be221c47d645960a0cb89e6de16988f65 |
| vendor/mmxm/data.py | fa2ebee1e25c87507f9faf26fed99f7c7a9edf7a234dcfda198ad163bd255fcd |
| vendor/mmxm/engine.py | 86e7180980517e20b03a9bf4668dea28329fa203151fe56fa872e02a51f6c67f |
| vendor/mmxm/indicators.py | 0cd95b1134e25f502d9e1699062cf01176c3b03df0f805787f6488d76e3b2ecf |
| vendor/mmxm/htf.py (from /workspace/mmxm; needed by v3) | a6eb7d5ac75e7ea1fa3213e031e61c564e57c59d49e48bcd5df4b35d2ea47397 |
| vendor/mmxm/htf_v4.py (from /workspace/mmxm; needed by v4) | 0bbfb6f2abe69ced47503c0e574488c6f22cf65f8f11c4ce11adfebf3c8cba23 |
| configs/v1_default.yaml | 7e886516566a99eefde24ead96e9f40c7fb74207c09299cd11de86ee8d9dda9b |
| configs/v2_overnight_LHon_from0930.yaml | 90691aaab076711906d783cc53f3d650752f58b8d63b1ea3d94568619ce1b64d |
| configs/v3_asia_LHoff_daily_draw.yaml | 9aea2b0158802f81656b99817abb60aeac6c98cbb6b0def70937aad9afaa6e9b |
| configs/v4_overnight_LHon_midnight_open.yaml | c466ec8ff668f209c3cb7809ae30ab351c6e6ba7bd5a2d87ad59cc21c58ca579 |
| configs/v5_A_overnight_5mFVG_ce_c12_none.yaml | 3414c77c4693a2ad0557a3f77513118ad292821e6d18f6713b901c7451b67968 |

The engine files are byte-identical to the H013/H014 frozen copies and to `/workspace/mmxm/mmxm/`. The v5 A yaml is byte-identical to the H014 frozen yaml.

## C. Per-instrument parameters and cost scaling (fixed now; batch 1 S1 specs `batch1/s1_specs.json` are reused unchanged)

**Price ratio.** ρ = median_close_inst / 25,618.827, where 25,618.827 is the US100 median BID close on the burned tape. Batch 1 S1 median closes: GER40 24,453.999, US30 49,075.999, XAUUSD 4,345.535.

| instrument | ρ | tick (both models) = 0.25ρ | MMXM min_swing_dist_points = 3.0ρ (NQ-anchored) | MMXM root key | friction F = spread + slip_market + slip_stop |
|---|---:|---:|---:|---|---:|
| US100 (burned) | 1 | 0.25 (frozen) | 3.0 (frozen) | NQ | 1.55 + 0.5 + 0.5 = **2.55** |
| US500 (burned) | — | 0.25 (frozen) | 1.0 (frozen) | ES | 0.72 + 0.25 + 0.25 = **1.22** |
| GER40 | 0.95453 | 0.23863 | 2.8636 | NQ | 2.624 + 0.884 + 0.884 = **4.392** |
| US30 | 1.91562 | 0.47891 | 5.7469 | NQ | 2.17 + 1.775 + 1.775 = **5.720** |
| XAUUSD | 0.16962 | 0.04241 | 0.5089 | NQ | 0.84 + 0.281 + 0.281 = **1.402** |

Note: the US frictions are the pinned ftn instrument frictions used in batch 1 (US100 spread 1.55 + 2 × 0.5 = 2.55; US500 0.72 + 2 × 0.25 = 1.22). All other config values (including `min_swing_dist_atr_mult`, the sessions and the HTF settings) stay exactly as frozen.

**Costs (primary, all stages).** The friction F is charged as a round trip in price units:
- MMXM: `cost_points_round_trip = F`.
- Model U: per-side cost = F/2 (engine SLIP = (F/2)/tick ticks, charged on entry and on every exit, as in H013).

**Co-reported, not gating:** the burned results at the **frozen** costs (Model U 0.8/side US100, 0.5/side US500; MMXM RT 0.8 / 0.5).

**Era R (power):** R_era = R − 0.5 × F / risk_pts, the same as batch 1.

## D. Data, day universe and windows
- **Bars:** BID 1m only (both models are BID-only). An ftn `Series` (naive NY wall clock) is converted to a tz-aware NY frame. The repeated fall-back hour (01:00–02:00 on one night per year) is dropped for real and null data alike. This is outside every Model U window; MMXM overnight ranges lose that hour.
- **S1:** `/workspace/screening-data/{GER40,US30,XAUUSD}_1m_bid.csv.gz`, 2023-01-01..2026-09-25 (as batch 1). Model U is evaluated for 2023-01-03..2026-09-25. MMXM runs on the whole series.
- **Burned (S2a, S3, power):** `ftn.pipeline.invariance.load_histories()` US100/US500, 2025-08-24 18:05 .. 2026-09-25 16:14 NY. Model U is evaluated for 2025-08-26..2026-09-25.
- **Model U day universe (H013 longrun rule):** NY business days with ≥ 285 1m bars in 07:00–11:59, excluding NYSE full closures 2023–2026 (list in `adapters.NYSE_CLOSED`: the standard NYSE holidays plus 2025-01-09) and 2025-12-24.
- **MMXM:** trades dated on NYSE full closures are dropped (the same list).
- **Burned sets:**
  - D1: US100 burned trades only (its decision series and holdout).
  - D2–D6: US100 + US500.
- **S3 nulls:**
  - Null tapes are on US100 + US500 (D1 uses only the US100 nulls).
  - All 50 + 50 replicates are run (measured ≈ 13 s per replicate-instrument for all 6 candidates, so no reduction is needed).
  - The null generators are `nulls.shuffled_day` / `nulls.random_walk`, seeds 20261004 + k, using their BID output.
- **Clusters:** the cluster is the NY date, since every candidate has one session per day.
- **S2a folds:** the same 4 equal-trading-day folds of the burned union as batch 1.
- **S2b:** calendar-year folds of the S1 trades.

## E. Sanity reproduction (frozen costs, burned; information only)
- Model U, US100 2025-09-02..2026-09-11: N = 243, mean +0.224R. Published 244 / +0.227R at FILL_THRU 0; this run uses the H013 freeze, FILL_THRU 1.
- MMXM v5 A, full burned tape: US100 21 trades, +2.29R; US500 25 trades, +8.80R; total 46 / +11.09R. Published IS 38 / +9.63R + OOS 10 / +1.50R = 48 / +11.13R on HistData CFD.

## F. Reporting
The report follows the batch 1 table: N, mean R and CI on burned (primary cost) and on S1, the S1/S2/S3 verdicts with raw and Holm p, holdout power, power ceiling and the gate verdict. Any departure from this addendum is listed as a dated deviation.
