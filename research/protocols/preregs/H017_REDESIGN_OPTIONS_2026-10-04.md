# H017 redesign options (memo, 2026-10-04 ~14:30 SAST). DRAFT, not a prereg, not tagged

**Why this memo exists.** The user decided not to lock the H017 baseline (816bca3), because US100 era costs would decide its result.
- In the baseline, CASSANDRA's Q8 pre-data expectation is US100 ≈ −0.10R net: the era off-RTH spread is about 3.46 pt, against 1.18 burned.
- That makes P2 (US100 > 0) the likely failure point. Realistic power is 0.27 at the burned per-instrument means and 0.05 era-cost adjusted.

**Inputs (pre-data facts only).** No certified-untouched bar was opened, loaded or decoded. The inputs are:
- burned H016b trades (254 filter-eligible);
- DATA's and CASSANDRA's published era spreads (US100 pre-switch off-RTH p90 3.53, median 3.46; US500 0.71 until 2022-09-29, then 0.51);
- NYSE session counts and file counts;
- approximate public index levels.

**Method.** The draft's method: burned session-slot resampling, min-stop level thinning, normal-approximation cluster bound, P1–P5 joint, 2,000 reps.
- Code and output: `research/evidence/quant/H017_REDESIGN_POWER_2026-10-04.{py,out}`.
- Every option uses the confirmatory window [2019-02-04, 2022-12-23]. US500 sub-window B stays exploratory, as ruled.
- "Rep" means joint pass AND pooled net mean ≥ +0.10R, the replication bar from CASSANDRA Q4.

**Burned means.** Net: US100 +0.006, US500 +0.183. Gross (approximate, cost added back): US100 +0.066, US500 +0.286.

## Option comparison
| Option | N (central) | equal +0.15 | equal +0.10 | burned per-instr. | era-cost adj. | H016b replication eligible? |
|---|---|---|---|---|---|---|
| **O0 baseline** (pooled net, pinned; = 816bca3) | 653 | 0.78 | 0.47 | 0.27 | 0.05 | YES if R1–R5 hold and the tag is before 2026-10-06 01:00 UTC; realistic rep power 0.27 / 0.05 |
| **O1 US500 confirmatory, US100 gated secondary** (pinned rule) | 220 (US500) | 0.49 | 0.28 | **0.63** | **0.81** | NO under R1 as written (different decision rule/pool); only if ORION rules a per-instrument replication of H016b's US500 leg counts |
| **O2 new ID: US100 era-friction min-stop**, pooled net | 530 | 0.69 | 0.41 | 0.29 | 0.37 | NO (different rule; new ID per Q8) |
| **O4 gross-of-cost primary**, pooled, net secondary | 653 | 0.78 | 0.47 | **0.72** (gross) | 0.72 (gross is unaffected by cost) | Primary NO (cost model differs). The net secondary is identical to O0, so it is eligible with rep power 0.27 / 0.05 |

**Era-cost scenario as modelled:**
- O1: US500 +0.23.
- O2: US100 net = burned +0.006. The era min-stop restores 2026-like friction per R, so the burned US100 net edge applies.
- O4: gross is scale-invariant, so it equals the burned gross means.

## Options in detail
### O1. US500-only confirmatory, US100 gated secondary (recommended)
**Design:**
- **Primary:** the pinned H016b rule on US500 sub-window A, with P1–P6 applied to US500 alone (P2 becomes US500 > 0). Family F2, alpha 0.05.
- **Gated secondary:** US100 is tested as its own P1–P6 only if US500 passes (fixed-sequence gatekeeping, no alpha split).
- **Pooled result:** reported only.

**Why:**
- US100's cost drag no longer decides the verdict.
- US500's era spread (0.71/0.51) is close to the pinned assumed spread (0.72), so US500 costs are era-neutral.
- The rule, pins and costs stay identical (Q8 holds), so it keeps the same ID.

**Power:** 0.63 at the burned US500 mean and 0.81 era-adjusted. At equal +0.15 it is only 0.49, because N is about 220.

**New risks:**
- **(a) Small N.** The pooled floor of N < 400 must become a US500 floor, for example N < 150 → INCONCLUSIVE. That is a new ruling for ORION and CASSANDRA (Q5 is now moot as written). The central N's 1st percentile is 188.
  - If S\* slips to about 2020-08-06, US500 N is about 135, so INCONCLUSIVE becomes likely. The pre-run postpone rule needs an equivalent US500 threshold.
- **(b) Instrument chosen after seeing burned per-instrument results.** The holdout itself is untouched, so the test stays valid, but the prior is selection-inflated. This must be disclosed.
- **(c) No H016b replication.** Unless ORION rules otherwise, a pass is a stand-alone F2 finding.
- **(d) Higher variance.** US500 alone has a larger per-trade SD relative to a ~0.18 edge.
- **(e) Contamination.** None added; B stays exploratory.

### O2. New ID (H018): US100 min-stop scaled to era friction
**Design:**
- min_risk = 4 × (DATA era p90 off-RTH spread + 2 × slip). For US100 that is 4 × (3.53 + 1.0) = **18.1 pt**, against the pinned 10.2. The constant is frozen from DATA's published schedule before any data.
- A skip rule (no ticket when the era friction is above 25% of 1R) is the same idea.

**Requirements:** a new rule commit, new pins and a new ID (Q8: "any level-scaled variant needs a new ID"). Its own reviews and its own harness are needed.

**Power:** 0.29 burned, 0.37 era-adjusted. US100's burned net edge is about 0 even at 2026 friction, so fixing costs does not create power. N drops to about 530.

**New risks:**
- It is a post-hoc rule change motivated by costs.
- It tests a rule that H016b does not trade, so there is no replication.
- The era constant depends on DATA's schedule; procedure S values come later, so it would have to use the published p90.

### O4. Gross-of-cost primary with a net secondary
**Design:**
- **Primary:** P1–P6 on BID-chart gross R (pinned rule; fills at levels without spread or slippage).
- **Secondary:** the binding net correct-side test, which is O0 itself.

**Power:** 0.72 realistic on the primary.

**New risks:**
- A gross pass says nothing about tradeability, and MINT cannot size on it.
- The gross outcome needs a new scorer definition, a non-pinned path that needs its own review and A5 scorer.
- The foil must also be computed gross. The approximation above uses the net foil, so it is optimistic.
- Eligibility comes only from the net secondary, at 0.27 / 0.05.
- It risks rewording a net FAIL as a "gross pass". CASSANDRA Q8 forbids exactly this, so the gross result would have to be explicitly non-promotable.

### O0. Keep the baseline (for reference)
- This is the only design that keeps H016b replication eligibility, if it is tagged before 2026-10-06 01:00 UTC.
- But it is expected to fail on US100 costs: realistic power is 0.27 / 0.05. This is the case the user rejected.

## Recommendation: O1 (US500 confirmatory, US100 gated secondary)
- **Why O1.** It is the only option where:
  - the pinned rule is unchanged (same ID, Q8 holds);
  - era costs do not decide the verdict;
  - realistic power is reasonable (0.63 to 0.81).
- **What it costs.** H016b replication eligibility, unless ORION extends #6 to a per-instrument leg. There is no need to rush the tag for the 2026-10-06 01:00 UTC deadline unless ORION grants that.
- **Rulings needed before re-locking:**
  - ORION and CASSANDRA: a US500 N floor and pre-run postpone threshold (proposed: INCONCLUSIVE if N < 150; postpone if the expected N < 170).
  - ORION: whether a US500-only pass may replicate H016b's US500 component.
  - CASSANDRA: the selection disclosure (US500 chosen on burned per-instrument results).
  - DATA: no change. Same manifest, procedure S, E1–E12.
- **What stays unchanged:** all other baseline rules (DATA E1–E12, CASSANDRA A1–A6, ORION #6/#9).
