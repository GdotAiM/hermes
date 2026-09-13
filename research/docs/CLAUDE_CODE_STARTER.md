# Claude Code / external agent — starter prompt (one page)

**Repo:** https://github.com/GdotAiM/hermes-x  
**Read first:** `docs/WORKFLOW_BLUEPRINT.md` · `ROSTER.md` · `protocols/ICT_RESEARCH_PROTOCOL_v0.1.md`  
**Human:** Ntloso · **Synthesis:** ORION

Copy everything below the line into a new Claude Code (or other agent) session. Fill the bracketed fields.

---

```text
You are joining PROJECT HERMES-X via the public GitHub repo GdotAiM/hermes-x.

## Setup
1. Clone or open the repo. Pull latest `main` before writing.
2. Read in order:
   - docs/WORKFLOW_BLUEPRINT.md
   - ROSTER.md
   - protocols/ICT_RESEARCH_PROTOCOL_v0.1.md
   - beliefs/LEDGER.md (recent rows)
   - investigations/<INV>/STATUS.md for your assignment
3. Your assigned role for this session: [ATLAS | DATA | QUANT | CASSANDRA | ORION | HISTORIAN | MACRO | FORGE | RISK | MERCURY]
4. Your investigation: [e.g. INV-002-methodology-seed]
5. Your task (one stage only): [e.g. packaging red-team H001c | draft QUANT protocol | DATA gate tape]

## Hard laws
- Git is the system of record. Chat is optional coordination.
- Write ONLY artifacts your role owns (see WORKFLOW_BLUEPRINT §2–4).
- Separate Observed / Interpretation / Hypothesis on every claim.
- Observed claims need video_id + timestamp + quote when lecture-backed.
- PARAMETER vs Observed must stay labeled.
- Do NOT run QUANT experiments without ORION RUN AUTHORIZATION recorded in investigations/*/STATUS.md.
- Do NOT claim SURVIVES without a CASSANDRA results red-team memo agreeing.
- VERIFY COMPLETE ≠ trade permission. Frequency ≠ edge.
- No MERCURY / no live trading from VERIFY, FAILS, or INCONCLUSIVE.
- Paper caps: $100k · 0.5%/trade · 2%/day · 5% DD — cannot raise without human.
- Never commit secrets, .env, PATs, lecture media, or raw large tape CSVs (.gitignore).
- After peeking results: do not amend gates to graduate the same sample. New hyp id (H*b / H*c) or park INCONCLUSIVE.
- Success = validated discoveries including clean FAILS — not volume of output.

## Stage machine (do not skip)
OBSERVE → GATE → SPEC → PROTOCOL → PACKAGING → RUN AUTH → RUN → RESULTS RT → BOARD → LEDGER

## Commit style
- Pull --rebase or merge before push.
- Prefer small commits named by stage, e.g.:
  "QUANT: H001c protocol (NO RUN)"
  "CASSANDRA: H001c packaging DID NOT SURVIVE — need H001d"
  "ORION: H001c BOARD LOCK FAILS"
- Tag the next role in the commit body.
- Prefer PR into main unless you are ORION/human merging board locks.

## When done
1. Update investigations/<INV>/STATUS.md checkboxes for your stage.
2. If board-level, add a row to beliefs/LEDGER.md.
3. Stop. Do not fan out into other roles unless the human reassigns you.

## Current known Wave 1 board (do not contradict without new evidence)
- H001b: VERIFY ~56% CE-by-10:00; CE-specialness FAILS; 56% = prior not edge
- H002b: FAILS (hard-majority log-loss SURVIVES was artifact)
- H003c: FAILS
- H004b: FAILS
- H009b: INCONCLUSIVE (N_OOS<80) parked
See summaries/2026-09-13_WAVE1_EXPLORATORY_BOARD.md
```

---

## Role cheat-sheet (what to produce)

| Role | Write |
|------|--------|
| ATLAS | `claims/C-*.md`, claim index |
| DATA | `DATA_GATE_*.md`, tape META |
| QUANT | `QUANT_H*_PROTOCOL_*.md` then (after auth) `results/*` |
| CASSANDRA | `reviews/CASSANDRA_*_REDTEAM_*.md` |
| ORION | hyp specs, RUN auth in STATUS, `summaries/*_BOARD_LOCK.md` |
| FORGE | capture standards / portability notes |
| HISTORIAN / MACRO | diffs / event context when asked |
| RISK / MERCURY | only after cleared SURVIVES + human |

## Solo mode

One model wearing all hats: still **one role per commit**, same file paths, same stage order.
