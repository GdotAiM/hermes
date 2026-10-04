# PAM1 Model-Definition Pilot — research brief (not implementation)

Charter S0–S6 is frozen. This is **research only**.
No detector. No M9 changes. No PAM2–12.

## Canon (from Charter 0)

| Role | URL |
|------|-----|
| Primary | https://www.youtube.com/watch?v=vCvRrINpknI |
| Amplified | https://www.youtube.com/watch?v=rNn0JkItAGo |
| Trade plan + algorithmic theory | https://www.youtube.com/watch?v=4f1vjQMlV50 |

Horizon annotation: `intraday_scalp`.

## Research questions (answer from lectures, not invent)

1. **Bias / range:** What defines directional bias (e.g. IPDA / previous day high-low / other)?
2. **Session / time:** Which kill zone(s) are in-scope (e.g. NY only)?
3. **Setup pattern:** What is the named setup (OTE, PD array, raid, etc.)?
4. **Entry:** What constitutes a valid entry under the trade plan?
5. **Invalidation / management:** What ends the idea?
6. **Required vs confirming evidence:** What must be present vs optional?
7. **Relationship to Core:** Which M1–M12 annotations are *read-only inputs*, not recomputed?

## Deliverables before any detector code

1. `PAM1_MODEL_DEFINITION.md` — frozen model card from the three lectures.
2. Evidence-only fixture draft (no pick / expected_winner).
3. Explicit recognition rule proposal (still under Charter `identified_pam` + named pam1).
4. Sign-off that PAM1 does **not** emit tickets or mutate Core.

## Explicit non-goals

- No automatic inference from “Core annotations coexist”
- No ranking vs other PAMs
- No paper_swing / session_ticket
- No PAM2–PAM12 work in this pilot
