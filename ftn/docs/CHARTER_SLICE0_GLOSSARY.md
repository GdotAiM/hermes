# Charter Slice 0 — Glossary (proposed)

No production code. Sign or correct before any `pam_contracts.py`.

---

## 1. Model identity

```
pam_id:
    pam1 | pam2 | pam3 | pam4 | pam5 | pam6
  | pam7 | pam8 | pam9 | pam10 | pam11 | pam12
  | none
```

`model13` is **not** in `pam_id`. It is a separate bridge field.

```
model13_bridge: present | none
```

---

## 2. Horizon (annotation only)

```
pam_horizon:
    intraday_scalp
  | short_term
  | swing
  | position
  | day
  | universal
  | monthly_target
  | osok
  | none
```

Suggested mapping (glossary convenience, not a detector):

| pam_id | pam_horizon |
|--------|-------------|
| pam1, pam12 | intraday_scalp |
| pam2 | short_term |
| pam3, pam10 | swing |
| pam4 | position |
| pam5, pam11 | day |
| pam6, pam7 | universal |
| pam8 | monthly_target |
| pam9 | osok |

Horizon does **not** mint recognition.

---

## 3. Identification / recognition

```
identified_pam: present | none
```

Explicit. Not inferred from “many Core annotations present.”

```
recognized_pams: tuple of pam_id   # zero or more; order not rank
```

**Frozen semantic rule (derivation slice later):**

```
identified_pam == present AND at least one named pam_id in evidence
    → recognition context may list those pam_ids
otherwise
    → no Charter recognition
```

Slice 1 only **parses** provided recognition state. Derivation is later.

Overlapping recognition is valid. No winner. No score.

---

## 4. Model context fields (per recognized PAM or overall)

```
primary_lecture_note: present | none
amplified_note: present | none
trade_plan_note: present | none
algorithmic_theory_note: present | none
```

Supporting-lecture rule from Charter 0:

```
PAM-X
 ├── primary / model lecture
 ├── amplified / supplementary
 ├── trade plan
 └── algorithmic theory
          ↓
    ONE PAM definition
```

These notes describe which parts of the canon are present in evidence.
They do **not** create additional models.

---

## 5. Charter state shape (conceptual)

```
CharterState
  identified_pam: present | none
  recognized_pams: (pam1, …) | ()
  model13_bridge: present | none
  # optional aggregate notes:
  primary_lecture_note
  amplified_note
  trade_plan_note
  algorithmic_theory_note
  # recognition annotation (flag + reason), provided in S1:
  charter_recognition: { flag: bool, reason: string }
```

Exact field packaging freezes at contracts only after this glossary is signed.

---

## 6. Ownership boundaries

```
CharterState
        ≠  M1–M12 owned fields (read-only consumption only)
CharterState.recognized_pams
        ≠  M9 candidate
charter_recognition
        ≠  session_ticket
        ≠  order
PAM9 recognition
        ≠  M7 paper_swing
model13_bridge
        ≠  pam_id peer (until a later research slice promotes it)
```

Charter must not:

- mutate Core evidence
- rank PAMs
- emit tickets
- create a second OSOK paper ticket from PAM9
- infer a PAM solely because Core annotations coexist

---

## 7. PAM1 pilot scope (after S0 + contracts)

First implementation target after Slice 0 sign-off:

```
pam_id = pam1
horizon = intraday_scalp
supporting notes from PAM1’s 3 lectures
```

No PAM2–PAM12 detectors in the pilot.

---

Sign or correct 1–7. Then Slice 1 contracts + known-state fixture.
