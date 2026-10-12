# ICT-2026 descriptive tests: REPORT (EXPLORATORY, IN-SAMPLE on the burned window 2025-08-25..2026-09-25, NOT EVIDENCE)
- **Prereg:** `PREREG.md`, commit 86ebfc5, committed before any result.
- **Code:** `ict2026.py`. **Table:** `results.csv`. **Figures:** `s1.png`…`s5.png`.
- **Data:** US100 and US500 1m BID, NY times. 272 / 271 eligible days.
- **Calendar:** the offline NFP/CPI 8:30 calendar was used (23 / 22 days on the 07:00–08:30 PM window). Other 8:30 reports are not in it.
- **Stats:** day-cluster bootstrap (2,000), Holm over 10 tests.

## Ranking (by |standardized effect| and cross-instrument robustness)

| Rank | Study | US100 effect [95% CI], Holm p | US500 effect [95% CI], Holm p | Robust? | ICT claim |
|---|---|---|---|---|---|
| 1 | **S4 session alternation**: P(next expands \| prev consolidated) − P(next expands \| prev expanded) | **−0.233 [−0.304, −0.156]**, 0.005 | **−0.285 [−0.359, −0.210]**, 0.005 | **yes** (Cohen's h ≈ −0.47 / −0.58) | **Contradicted**: the opposite sign. Sessions cluster; they don't alternate. |
| 2 | S5 PM 07–09 range .375/.5/.625 respect vs random fractions | +0.001 [−0.038, +0.040], 1.0 | +0.012 [−0.030, +0.053], 1.0 | no (h 0.00 / 0.02) | not supported (60.5% vs 60.4%; 60.3% vs 59.1%) |
| 3 | S3 midnight open touched 09:30–11:30 vs mirror level | +0.000 [−0.092, +0.088], 1.0 | +0.017 [−0.078, +0.104], 1.0 | no (h 0.00 / 0.03) | not supported (49.6% vs 49.6%; 53.5% vs 51.7%) |
| 4 | S2 opening-range-gap CE touched by 11:30 vs mirror level | −0.004 [−0.089, +0.089], 1.0 | +0.013 [−0.071, +0.096], 1.0 | no (h −0.01 / 0.03) | not supported as a magnet. The CE is hit often (62% / 66%, median 6–7 min), but so is an equal-distance level on the other side |
| 5 | S1 PM regime → AM range/ATR (PM range days − PM trend days) | −0.004 [−0.160, +0.156], 1.0 | +0.029 [−0.118, +0.178], 1.0 | no (std 0.01 / 0.06) | not supported. AM DR and ER show no difference; Spearman ρ(PM DR, AM range) = +0.05 / +0.02, not the predicted negative |

## Details
- **S1:**
  - AM range/ATR20: 1.03 on PM-range days vs 1.04 on PM-trend days (US100); 1.07 vs 1.04 (US500).
  - About 75–80 days in each class.
  - AM directional ratio Δ −0.01 / +0.01; AM efficiency ratio Δ 0.00 / 0.00, with all CIs spanning 0.
  - "PM trend → AM chop" does not show up in this window.
- **S2 ORG:**
  - Full fill to the 16:14 close by 16:00: 48% (US100) / 56% (US500).
  - CE by 16:00 vs mirror: Δ +0.02 on both, n.s.
  - Gaps are small relative to the AM range, so both levels are usually tagged within minutes.
- **S3 midnight open, touch rate MO / mirror by distance tercile:**
  - US100: near 0.76/0.86, mid 0.54/0.49, far 0.18/0.14.
  - US500: near 0.88/0.79, mid 0.53/0.55, far 0.19/0.21.
  - Distance explains the rate; the midnight open adds no magnet effect.
- **S4, the only robust result.**
  - Per pair (US100 / US500):
    - Asia→London −0.30 / −0.37.
    - London→NY −0.25 / −0.30.
    - NY→next Asia −0.15 / −0.19.
  - Every CI excludes 0. Spearman of consecutive session range ratios is +0.27 to +0.52.
  - This is ordinary volatility clustering: a quiet session predicts a quiet next session, and an expanded one predicts expansion. That is the opposite of the alternation rule.
- **S5:** respect rate for f = .375 / .5 / .625: 0.62 / 0.58 / 0.62 (US100) and 0.61 / 0.60 / 0.60 (US500), vs about 0.60 for random fractions (flat across fractions in `s5.png`).

## Use and next steps
- No ICT rule from the brief survives on these data.
- The one strong effect (S4) is a **volatility-persistence** effect. It could be used as a regime input, for example:
  - scale stops/targets, or skip low-volatility days, by the prior session's range ratio;
  - predict NY AM range from London's range ratio (ρ ≈ +0.36 / +0.39).
- No trading sim was run. The prereg said a sim would follow a robust standardized effect ≥ 0.2, but S4 is not an entry rule, and building one now would be a new, post-hoc hypothesis. That deviation is disclosed here. Any S4 use should be pre-registered and tested forward.

## Caveats
- One year (one regime), in-sample on burned data, and highly correlated instruments, so cross-instrument agreement is weak independence.
- NQ futures (in ICT's material) vs CFD index BID here.
- The 8:30 calendar covers NFP/CPI only.
- The mirror-level nulls assume symmetric drift.
- 1m bars can't order moves inside a bar, so a bar that hits both sides counts as not respected (S5).
