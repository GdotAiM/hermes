# Anti-patterns — Wave 1 lessons (paid tuition)

**Status:** Distilled from INV-002 Wave 1 (2026-09-13)  
**Owner:** LOOM / ORION  
**Rule:** If you recognize one of these forming, stop and fix packaging or park INCONCLUSIVE.

| Anti-pattern | What went wrong | Fix |
|--------------|-----------------|-----|
| **Unlocked control / metric** | Protocol allowed multiple “primary” metrics or an underspecified baseline; packaging could not pin FAILS/SURVIVES | CASSANDRA CRITICAL → rewrite as `H*b` with **one** primary estimand and **one** primary control |
| **Post-peek N-gate** | Sample peeked underpowered; temptation to lower N to graduate | **Reject.** Park **INCONCLUSIVE**. Reopen only with frozen N on **new** weeks / new hyp id |
| **Hard one-hot + log-loss** | IS-majority constant encoded as one-hot → hollow log-loss “SURVIVES” (H002b) | Soft **empirical prior** distribution as constant baseline; reject hard-one-hot wins |
| **Frequency-as-edge** | VERIFY COMPLETE frequency narrated as tradeable edge | VERIFY ≠ trade permission; need specialness vs control + expectancy vs costs |
| **First-FVG privilege** | “First” in a clock hour treated as special without later same-polarity control | Event study vs later same-polarity (or explicit foil); do not smuggle selection as edge |
| **Silver Bullet brand** | Brand / session-name language substituted for mechanism test | Test **mechanism** hyps; brand remains untested marketing until specified |
| **Raw 1m in git** | Large continuous tape CSV bloating repo / leaking vendor bulk | META + gates + protocols + result memos + small `day_rows` **in** git; raw 1m **gitignored** |

## Related process bans

- Soft “near miss / promising” when FAILS or INCONCLUSIVE
- MERCURY from VERIFY / FAILS / INCONCLUSIVE
- Relabeling PARAMETER as Observed after results
- RUN without ORION AUTH in `STATUS.md`
- SURVIVES without CASSANDRA results red-team

## Pointers

- Blueprint §9: `docs/WORKFLOW_BLUEPRINT.md`
- LOOM charter: `agent/AGENT.md`
- Utilization example: `summaries/2026-09-13_UTILIZATION_FROM_WAVE1.md`
