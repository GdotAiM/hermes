# ICT-2026 descriptive study: prereg (no results computed yet)
**Status: EXPLORATORY, DESCRIPTIVE, IN-SAMPLE on the burned window 2025-08-25..2026-09-25. NOT EVIDENCE, no trading.**
- **Source:** `/workspace/ict-time-price/ICT_2026_MENTORSHIP_BRIEF.md` (rules R1, R2, R3, R5, R6).
- **Data:** US100 and US500 1m BID from `/workspace/ftn-demo-output/data` (sha-checked by `research/nowick/nowick.py load`). Nothing after 2026-09-25, no holdout data, no screening instruments (GER40/US30/XAU), no downloads.
- **Times:** all NY.
- **Days:** weekdays with ≥ 300 1m bars in 09:30–15:59 and ≥ 100 bars in 07:00–09:00.
- **News calendar:** an offline 8:30 calendar exists: `ftn/src/ftn/research/data/us_macro_events.csv`. It covers only NFP and CPI (08:30), so other 8:30 reports (PPI, claims, retail sales…) are NOT covered. This is disclosed as a limitation.

**Common definitions.**
- **Directional ratio:** DR(window) = |close_end − open_start| / (high − low) (the brief's metric).
- **Efficiency ratio:** ER = |close_end − open_start| / Σ|Δclose 1m| (Kaufman).
- **ATR:** ATR20(window) = the mean of the same window's range over the previous 20 eligible days, with no current-day data.
- **Bootstrap:** day-cluster, 2,000 resamples, seed 20261012. 95% percentile CI. Two-sided p = 2 × min(share ≤ 0, share ≥ 0).
- **Holm correction:** across the family of 10 primary tests (5 studies × 2 instruments).
- **Robust:** the same sign on both instruments AND Holm p < 0.05 on both.
- **Ranking:** by |effect| / pooled scale (the standardized effect stated per study), then by robustness.

**S1, pre-market regime → AM regime (R1).**
- **PM window:** 07:00–09:00. On NFP/CPI days it is 07:00–08:30.
- **Classification:** PM trend if DR ≥ 0.6, PM range if DR ≤ 0.3 (the brief's thresholds); otherwise neutral.
- **AM window:** 09:30–11:30.
- **Primary:** Δ = mean(AM range / ATR20_AM | PM range) − mean(… | PM trend). ICT predicts Δ > 0.
- **Secondary:**
  - The same Δ for AM DR and AM ER.
  - Spearman ρ(PM DR, AM range/ATR20). ICT predicts ρ < 0.
- **Null:** Δ = 0 (day bootstrap).

**S2, opening range gap CE (R5).**
- **Gap:** prev close = the BID close of the 16:14 1m bar of the previous eligible day; open = the 09:30 bar open.
- **Sample:** gaps with |gap| ≥ 0.05 × ATR20_AM.
- **Levels:** CE = (prev close + open) / 2, at distance d = |gap|/2 toward the prev close. Mirror level = open ± d on the opposite side.
- **Touch:** a 1m high/low crosses the level from the 09:30 bar onward.
- **Primary:** Δ = P(CE touched by 11:30) − P(mirror touched by 11:30).
- **Secondary:** by 16:00; full fill by 16:00; median minutes to the CE touch.

**S3, midnight-open magnet (R6).**
- **Level:** MO = the open of the 00:00 1m bar (that bar must exist). d = |09:30 open − MO|, requiring d ≥ 0.05 × ATR20_AM.
- **Primary:** Δ = P(MO touched 09:30–11:30) − P(mirror level 09:30 open ± d on the opposite side, touched in the same window).
- **Secondary:** by 16:00; split by d/ATR terciles.

**S4, session alternation (R2).**
- **Sessions:** Asia 20:00–00:00 (the evening before the day), London 02:00–05:00, NY 09:30–11:30.
- **Ratio:** each session's range / the median of its previous 20 eligible sessions. Consolidated = ratio < 1; expanded = ratio > 1.
- **Pairs:** Asia→London, London→NY (same day), NY→next Asia.
- **Primary (pooled over the 3 pairs):** Δ = P(next expanded | prev consolidated) − P(next expanded | prev expanded). ICT predicts Δ > 0; volatility clustering predicts Δ < 0.
- **Secondary:** per-pair Δ, and Spearman of the log ratios.

**S5, PM-range fractions (R3).**
- **Levels:** PM range H/L over 07:00–09:00, R = H − L. Level(f) = L + f × R.
- **ICT fractions:** {0.375, 0.5, 0.625}.
- **Random control:** 20 fractions per day from U(0.05, 0.95), seeded, at least 0.03 from any ICT fraction.
- **Eligibility:** a level counts only if the 09:00 close is ≥ 0.05 R from it. It must be touched in 09:00–12:00 (first 1m bar whose range crosses it).
- **Respect:** after the first touch, price moves ≥ 0.15 R back to the approach side before moving ≥ 0.15 R beyond the level, by 12:00. Unresolved counts as not respected.
- **Primary:** Δ = respect rate(ICT) − respect rate(random), day cluster.

**Pre-declared nulls and caveats.**
- The mirror levels assume no drift. With 0.05-ATR minimums, the distances are matched by construction.
- 1m bars can't order the ±0.15 R moves within a bar, so a bar that hits both counts as not respected (conservative for the ICT fractions and the random ones alike).

**Outputs:** `ict2026.py`, `results.csv`, PNGs `s1.png` … `s5.png`, `REPORT.md`. A trading sim is run only if a robust |standardized effect| ≥ 0.2; otherwise just a suggestion.
