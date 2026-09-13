# W1 — Claim to Gate

**Purpose:** Turn lecture / market observations into gated claim cards ready for ORION hyp specs.  
**Stages:** OBSERVE → GATE  
**Exit:** Passed / Hold / Fail claims + tape honesty labels filed in git.

---

## Preconditions

- [ ] Investigation exists under `investigations/INV-XXX-.../` (copy from `investigations/_TEMPLATE/` if new)
- [ ] `BRIEF.md` states primary question and out-of-scope
- [ ] Pull latest `main` before writing
- [ ] Role for this session named (ATLAS / HISTORIAN / MACRO / DATA)

---

## Stage 1 — OBSERVE (ATLAS)

### Checklist

- [ ] Extract **Observed** claims only from primary sources (video_id + timestamp + quote/paraphrase)
- [ ] Separate **Interpretation** and **Hypothesis** on every card (`claims/_TEMPLATE.md`)
- [ ] Label community / taxonomy terms as map-only — not Observed provenance
- [ ] Flag **PARAMETER** candidates explicitly (detectors, thresholds we invent)
- [ ] Optional: HISTORIAN diff (NEW / REFINE / REPACKAGE) for mechanism claims
- [ ] Optional: MACRO event-conditioning note if claim is event-tied
- [ ] Update claim index if the INV uses one
- [ ] Update `STATUS.md` OBSERVE checkboxes

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Claim cards | `investigations/<INV>/claims/C-*.md` |
| Index (optional) | `investigations/<INV>/claims/*_INDEX.md` |
| Corpus register | `investigations/<INV>/CORPUS.md` |

### Handoff

```
Next: DATA
Path: investigations/<INV>/reviews/DATA_GATE_<SCOPE>_<DATE>.md
Ask: Gate claims + tape; Pass / Hold / Fail with reasons.
```

---

## Stage 2 — GATE (DATA)

### Checklist

- [ ] Verify source integrity (META / ACCESS / caption or tape provenance)
- [ ] Pass / Hold / Fail each priority claim with reason
- [ ] Lock tape labels (e.g. CONTINUOUS-KAGGLE, truncation, not lecture identity)
- [ ] File Pref/Popen or other print policies when gap/open claims are in scope
- [ ] Never commit raw large tape CSVs or lecture `.mp4` — META + small day_rows only
- [ ] Update `STATUS.md` GATE checkboxes
- [ ] Refuse silent assumption of missing META

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Data gate memo | `investigations/<INV>/reviews/DATA_GATE_*.md` |
| Tape META | `investigations/<INV>/evidence/tape/.../META.md` (or global `evidence/`) |

### Handoff

```
Next: ORION
Path: investigations/<INV>/STATUS.md + claims/ (Passed only)
Ask: Rank ≤3 hyp specs from Passed Observed claims (W2 SPEC).
```

---

## Exit criteria

W1 is complete when:

1. Priority claims have DATA gate dispositions.
2. Tape / source honesty labels are on disk.
3. `STATUS.md` reflects OBSERVE + GATE.
4. ORION can open W2 without inventing ungated Observed claims.

**Banned:** Treating ungated Interpretation as Passed Observed; inventing video timestamps; committing secrets or raw tape.
