# W2 — Hyp to Board (full checklist)

**Purpose:** Take gated claims through frozen protocol, packaging, authorized run, results red-team, and board lock.  
**Stages:** SPEC → PROTOCOL → PACKAGING → AUTH → RUN → RESULTS RT → BOARD → UPDATE  
**Exit:** Board decision in vocabulary + LEDGER row + STATUS stamp.

This is the critical path. **Do not skip packaging. Do not RUN without ORION AUTH in STATUS. Do not claim SURVIVES without CASSANDRA results RT.**

---

## Preconditions (from W1)

- [ ] Passed Observed parents listed on hyp
- [ ] Tape / source gate filed (or explicit HOLD with reason)
- [ ] Pull before write

---

## Stage 3 — SPEC (ORION)

### Checklist

- [ ] Rank **≤3** hyps by expected information gain → decision impact → cost
- [ ] One falsifiable statement per hyp
- [ ] Name primary parents (Passed Observed only)
- [ ] State what would count as VERIFY / SURVIVES / FAILS / INCONCLUSIVE *before* results
- [ ] Kill low-value forks explicitly
- [ ] Update `STATUS.md`

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Hyp specs | `investigations/<INV>/reviews/ORION_*_HYP_SPECS_*.md` or `waveN/` brief |

### Handoff

```
Next: QUANT
Path: investigations/<INV>/experiments/QUANT_H###_<SLUG>_PROTOCOL_<DATE>.md
Ask: Freeze estimand (NO RUN). One primary metric + one primary control.
```

---

## Stage 4 — PROTOCOL (QUANT) — NO RUN

### Checklist

- [ ] Primary **estimand** (one metric)
- [ ] Primary **control / baseline** (one; sensitivities labeled)
- [ ] Population / tape labels honest
- [ ] IS/OOS + **N gates** frozen before outcomes
- [ ] PARAMETER vs Observed labeled
- [ ] Look-ahead / leakage scan
- [ ] SURVIVES vocabulary: what claim is allowed if gates pass
- [ ] Explicit **NO RUN** until packaging + AUTH
- [ ] Soft empirical prior for log-loss constants (Wave 1: no hard one-hot)
- [ ] Update `STATUS.md`

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Protocol | `investigations/<INV>/experiments/QUANT_H*_PROTOCOL_*.md` |

### Handoff

```
Next: CASSANDRA
Path: investigations/<INV>/reviews/CASSANDRA_H###_REDTEAM_<DATE>.md
Ask: Packaging red-team; SURVIVED or DID NOT SURVIVE → H*b.
```

---

## Stage 5 — PACKAGING (CASSANDRA)

### Attack until locked

1. Primary estimand (one metric)
2. Primary control / baseline (one; sensitivities labeled)
3. Population / tape labels
4. IS/OOS + N gates frozen before outcomes
5. PARAMETER vs Observed labels
6. Look-ahead / leakage
7. SURVIVES vocabulary honesty
8. No MERCURY until board + RISK

### Checklist

- [ ] CRITICAL / HIGH / MEDIUM / LOW attacks filed
- [ ] Verdict: **PACKAGING SURVIVED** or **DID NOT SURVIVE**
- [ ] If DID NOT SURVIVE → require new hyp id (`H*b`); keep old as audit draft
- [ ] Peek status stated (pre-reg vs peeked)
- [ ] Update `STATUS.md`

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Packaging RT | `investigations/<INV>/reviews/CASSANDRA_*_REDTEAM_*.md` |

### Handoff (if SURVIVED)

```
Next: ORION
Path: investigations/<INV>/STATUS.md
Ask: Grant exploratory RUN AUTH if coverage gates met; stamp STATUS.
```

### Handoff (if DID NOT SURVIVE)

```
Next: QUANT
Path: investigations/<INV>/experiments/QUANT_H###b_*_PROTOCOL_<DATE>.md
Ask: Rewrite locks; NO RUN; re-enter packaging.
```

---

## Stage 6 — AUTH (ORION)

### Checklist

- [ ] Packaging SURVIVED on disk
- [ ] Coverage / DATA blockers reviewed
- [ ] Explicit **RUN AUTHORIZATION** line in `investigations/<INV>/STATUS.md`
- [ ] Scope named (exploratory vs confirmatory; tape id)
- [ ] No auth-by-chat-only without STATUS stamp

### Handoff

```
Next: QUANT
Path: investigations/<INV>/experiments/results/H###_*_RESULTS_<DATE>.md
Ask: Execute frozen protocol only; file results memo (+ small day_rows if needed).
```

---

## Stage 7 — RUN (QUANT)

### Checklist

- [ ] Confirm STATUS RUN AUTH before any outcome peek
- [ ] Execute **frozen** protocol — no silent gate edits
- [ ] File results memo with decision recommendation in vocabulary
- [ ] Skeptic flags encouraged (e.g. baseline pathology)
- [ ] Small `*_day_rows.csv` OK; raw 1m tape **not** in git
- [ ] If underpowered → recommend **INCONCLUSIVE**, do not lower N post-peek
- [ ] Update `STATUS.md`

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Results memo | `investigations/<INV>/experiments/results/H*_RESULTS_*.md` |
| Day rows (small) | `investigations/<INV>/experiments/results/H*_day_rows.csv` |

### Handoff

```
Next: CASSANDRA
Path: investigations/<INV>/reviews/CASSANDRA_H###_RESULTS_REDTEAM_<DATE>.md
Ask: Results red-team; agree/disagree decision class.
```

---

## Stage 8 — RESULTS RT (CASSANDRA)

### Checklist

- [ ] Attack decision hygiene (baseline honesty, peeking, multiplicity, leakage)
- [ ] Agree or reject proposed SURVIVES / FAILS / VERIFY / INCONCLUSIVE
- [ ] Reject hollow SURVIVES (Wave 1 H002b lesson)
- [ ] Ban post-peek N-gate amend
- [ ] Update `STATUS.md`

### Handoff

```
Next: ORION
Path: summaries/<DATE>_H###_BOARD_LOCK.md
Ask: Board lock in mandatory vocabulary; update LEDGER.
```

---

## Stage 9 — BOARD (ORION)

### Checklist

- [ ] Lock one of: VERIFY COMPLETE / SURVIVES / FAILS / INCONCLUSIVE / HOLD
- [ ] Answer ORION frame: thought / observed / changed / survived / failed / unknown
- [ ] Highest-value next experiment named
- [ ] Explicit **no MERCURY** unless SURVIVES + RISK + human path
- [ ] Use `summaries/_BOARD_LOCK_TEMPLATE.md`

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Board lock | `summaries/<DATE>_H*_BOARD_LOCK.md` |
| Wave board (optional) | `summaries/<DATE>_*_BOARD.md` |

---

## Stage 10 — UPDATE

### Checklist

- [ ] Row in `beliefs/LEDGER.md`
- [ ] `STATUS.md` checkboxes + NEXT line
- [ ] If chapter closed, consider W3 utilization memo
- [ ] Handoff to LOOM/ORION for next priority — or stop

---

## Exit criteria

W2 complete when board lock + LEDGER + STATUS are filed and decision vocabulary is used without soft-sell.

**Banned moves:** skip packaging; RUN without STATUS auth; SURVIVES without results RT; MERCURY from VERIFY/FAILS/INCONCLUSIVE; post-peek gate amend; hard one-hot log-loss “win.”
