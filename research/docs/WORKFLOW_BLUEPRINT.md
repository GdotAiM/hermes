# HERMES-X Workflow Blueprint
**Audience:** Humans + any agent stack (Grok Bot specialists, Claude Code, Cursor, Codex, local LLMs) collaborating through **GitHub**  
**Owner:** ORION  
**Status:** v1 — distilled from INV-002 Wave 1 (2026-09-13)  
**Repo:** https://github.com/GdotAiM/hermes-x

This document is the portable “how we work.” If an agent can read markdown and commit files, it can join the lab.


> **Agent package:** Executable stage-machine + role prompts live under [`agent/`](../agent/README.md) (LOOM). Start with [`agent/AGENT.md`](../agent/AGENT.md). Solo: [`agent/SOLO_MODE.md`](../agent/SOLO_MODE.md). Workflows W1/W2/W3: [`agent/workflows/`](../agent/workflows/). Role prompts: [`docs/prompts/`](prompts/). Anti-patterns: [`docs/ANTI_PATTERNS.md`](ANTI_PATTERNS.md).


---

## 0. Success definition

| Success | Failure disguised as success |
|---------|------------------------------|
| Small number of **validated discoveries** (including clean **FAILS**) | High volume of agent chat / memos |
| Reproducible from files in git | “We talked about it” with no artifact |
| Beliefs updated when evidence changes | Narrative that ignores gates |

**Priority law:** expected information gain → decision impact → cost → time → reproducibility.

**Hard paper caps (never raise without human):** $100k · 0.5% / trade · 2% / day · 5% DD · **no live execution**.

---

## 1. The shared bus is the repo (not the chat)

Chat is ephemeral coordination. **Git is the system of record.**

```
Any agent / IDE / human
        │
        ▼
  clone / pull hermes-x
        │
        ▼
  write artifacts under conventions below
        │
        ▼
  commit + push (or PR)
        │
        ▼
  other agents pull → continue pipeline
```

### Rules for multi-stack collaboration (Claude Code, etc.)

1. **Pull before you write.** Never invent parallel folders.
2. **One investigation path** — put work under `investigations/INV-XXX-.../`.
3. **Commit atomic stages** — e.g. “DATA gate”, “QUANT protocol”, “results”, “CASSANDRA red-team”, “ORION board lock” as separate commits when practical.
4. **Never commit secrets** — tokens, `.env`, PATs, lecture `.mp4`, large raw tape CSVs (see `.gitignore`).
5. **Address the next role in the commit body** — e.g. `CASSANDRA: packaging review H004b`.
6. **Do not re-run a hyp after peeking** and pretend it was pre-registered — bump id (`H004` → `H004b`).
7. **Human** (Ntloso) is final authority on risk caps, live data spend, and MERCURY promotion.

### Suggested branch model

| Branch | Use |
|--------|-----|
| `main` | Curated ledger (ORION merges board locks) |
| `inv/002-wave1` (example) | Parallel exploratory work → PR into `main` |
| Agent forks OK | Prefer PRs over force-push to `main` |

Claude Code / Cloud agents: open a PR with the artifact set for that stage; ORION (or human) merges after checklist.

---

## 2. Roster — who does what

| Role | Responsibility | Primary outputs |
|------|----------------|-----------------|
| **ORION** | Synthesis, priority, kill low-value, board locks | `summaries/*_BOARD_LOCK.md`, hyp specs, RUN auth |
| **ATLAS** | Observe structure / lecture claims | `claims/C-*.md`, indexes |
| **DATA** | Evidence integrity, gates | `DATA_GATE_*.md`, tape META |
| **HISTORIAN** | Analogues / NEW vs REPACKAGE | `HISTORIAN_DIFF_*.md` |
| **MACRO** | Event context when conditioned | calendars, macro notes |
| **QUANT** | Protocols + statistical runs | `QUANT_H*_PROTOCOL_*.md`, `results/*` |
| **CASSANDRA** | Attack packaging + results | `reviews/CASSANDRA_*_REDTEAM_*.md` |
| **FORGE** | Capture standard, portability | workflows, schemas |
| **RISK** | Portfolio survival | reject/accept risk memos |
| **MERCURY** | Paper decisions only after clearance | trade journal (none from Wave 1) |

**Canonical pipeline (research loop):**

```
ATLAS / MACRO / HISTORIAN / DATA
            │
            ▼
         QUANT  (protocol · then run only after clearance)
            │
            ▼
       CASSANDRA  (packaging before run · results after run)
            │
            ▼
     RISK → MERCURY   (only if SURVIVES + ORION + human allow)
            │
            ▼
         ORION  (board lock · next experiment)
```

FORGE sits **beside** the loop (schemas, tooling), not in the trade path.

**Who talks to whom (minimum viable):**

| From → To | When | Artifact |
|-----------|------|----------|
| ORION → ATLAS/DATA | Open INV / register sources | `BRIEF.md`, corpus register |
| ATLAS → DATA | Claims ready for gate | claim cards |
| DATA → ORION | Gate PASS/HOLD | `DATA_GATE_*.md` |
| ORION → QUANT | Hyp specs | `ORION_*_HYP_SPECS_*.md` |
| QUANT → CASSANDRA | Protocol filed | protocol path |
| CASSANDRA → ORION | SURVIVED / DID NOT | red-team memo |
| ORION → QUANT | RUN AUTHORIZATION | chat or `STATUS.md` stamp |
| QUANT → ORION+CASSANDRA | Results filed | results memo + day_rows |
| CASSANDRA → ORION | Agree/disagree decision | results red-team |
| ORION → all | Board lock | `summaries/*_BOARD_LOCK.md` + LEDGER |

Agents **do not** need live multiplayer chat. File paths + commits are enough.

---

## 3. Stage machine (every hypothesis)

```
1 OBSERVE     ATLAS extracts Observed claims (timestamped)
2 GATE        DATA Pass / Hold / Fail claims + tape
3 SPEC        ORION ranks ≤3 hyps
4 PROTOCOL    QUANT drafts frozen estimand (NO RUN)
5 PACKAGING   CASSANDRA attacks protocol → SURVIVED or H*b rewrite
6 AUTH        ORION grants exploratory RUN (coverage gates)
7 RUN         QUANT executes on labeled tape → results memo
8 RESULTS RT  CASSANDRA attacks decision / hygiene
9 BOARD       ORION locks VERIFY / FAILS / INCONCLUSIVE / SURVIVES
10 UPDATE     LEDGER + STATUS + next experiment
```

### Decision vocabulary (mandatory)

| Label | Meaning |
|-------|---------|
| **VERIFY COMPLETE** | Frequency / descriptive product filed — **≠ trade permission** |
| **SURVIVES** | Pre-registered gates passed under honest baseline |
| **FAILS** | Gates fail or scientific baseline kills claim |
| **INCONCLUSIVE** | Underpowered / blocked (e.g. N gate) — do not upgrade by amending after peek |
| **HOLD** | Not run-ready |

**Banned moves**

- Soft “near miss / promising” when FAILS or INCONCLUSIVE.
- Post-peek gate amend to graduate a peeked sample (optional stopping).
- MERCURY trades from VERIFY / FAILS / INCONCLUSIVE.
- Relabeling PARAMETER as Observed after results.

---

## 4. File layout (copy this for new INVs)

```
hermes-x/
  README.md
  ROSTER.md
  protocols/ICT_RESEARCH_PROTOCOL_v0.1.md
  docs/WORKFLOW_BLUEPRINT.md          ← this file
  beliefs/LEDGER.md                  ← what we believed / what changed
  evidence/SOURCE_MAP.md
  summaries/                         ← ORION board products
  investigations/
    INV-002-methodology-seed/
      BRIEF.md
      STATUS.md
      CORPUS.md
      claims/C-METH-*.md             ← CLAIM_CARDs
      evidence/tape/.../DATA_GATE_*.md
      experiments/
        QUANT_H00Xb_*_PROTOCOL_*.md
        results/H00Xb_*_RESULTS_*.md
        results/H00Xb_day_rows.csv   ← small OK; raw 1m tape gitignored
      reviews/CASSANDRA_*_REDTEAM_*.md
```

### CLAIM_CARD discipline (FORGE Option C)

Every claim separates:

1. **Observed** — lecture said (video_id + timestamp + quote)  
2. **Interpretation** — our reading  
3. **Hypothesis** — falsifiable statement  

Community terms / taxonomy PDF = **map only**, not primary evidence.

---

## 5. Packaging checklist (CASSANDRA before any RUN)

Attack until locked:

1. **Primary estimand** (one metric)  
2. **Primary control / baseline** (one; sensitivities labeled)  
3. **Population / tape labels** (CONTINUOUS-KAGGLE, truncation, not lecture identity, …)  
4. **IS/OOS + N gates** frozen before outcomes  
5. **PARAMETER vs Observed** labels  
6. **Look-ahead / leakage**  
7. **SURVIVES vocabulary** (what claim is allowed if gates pass)  
8. **No MERCURY** until board + RISK  

If CRITICAL fails → **new hyp id** (`H004b`), keep old as audit draft.

**Wave 1 lesson:** “IS-majority constant” for **log-loss** must be a **soft empirical prior**, not one-hot (H002b false SURVIVES).

---

## 6. Worked example — how Wave 1 conclusions happened

### Setup

- Human seeded 6-video methodology corpus → **INV-002** + Protocol v0.1.  
- Free tape path: Kaggle NQ 1m 2022–2025 (`CONTINUOUS-KAGGLE-NQ1M`, roll undocumented, truncated ~2025-12-11).  
- Large CSV **not** in git; META + gates + protocols + result memos + day_rows **are**.

### Collaboration graph (actual)

```
Human
  │ corpus + priorities
  ▼
ORION ──opens INV / ranks hyps──► ATLAS (claims) ──► DATA (gate)
  │                                      │
  │◄─────────────────────────────────────┘
  ├──► QUANT (H001b/H003c/H004b/H002b protocols)
  │         │
  │         ▼
  │    CASSANDRA (packaging) ──DID NOT SURVIVE?──► QUANT rewrite (H*b)
  │         │ SURVIVED
  │         ▼
  ├──► ORION RUN AUTH ──► QUANT exploratory run ──► results/
  │                              │
  │                              ▼
  │                         CASSANDRA results RT
  │                              │
  ▼                              ▼
BOARD LOCK (summaries/) ◄────────┘
  │
  ▼
LEDGER + git push (af1e683 Wave 1 closed)
```

### Conclusions (board-locked)

| Hyp | Who ran | Who attacked | Board | Why |
|-----|---------|--------------|-------|-----|
| **H001b** | QUANT | CASSANDRA | VERIFY ~56% CE-by-10:00; CE-specialness **FAILS** | Frequency filed; CE not special vs random-on-gap |
| **H002b** | QUANT | CASSANDRA | **FAILS** | Soft-prior lift≈0; hard-majority log-loss “SURVIVES” = artifact |
| **H003c** | QUANT | CASSANDRA | **FAILS** | REL→opposite worse than Foil A |
| **H004b** | QUANT | CASSANDRA | **FAILS** | First 10:00 FVG ≈ later same-polarity on 60m revisit |
| **H009b** | QUANT | CASSANDRA | **INCONCLUSIVE** | Strong Δ but N_OOS=38<80; no post-peek N amend |

ORION synthesis products: `summaries/2026-09-13_WAVE1_EXPLORATORY_BOARD.md`, `*_BOARD_LOCK.md`, `UTILIZATION_FROM_WAVE1.md`.

### What we utilize vs what we don’t

- **Utilize:** ~56% as **planning prior** (retire 70%); negative playbooks from FAILS; H009b as unfinished positive research.  
- **Do not utilize:** MERCURY entries from VERIFY/FAILS/INCONCLUSIVE; “56% = edge” without conditional lift + expectancy.

---

## 7. Onboarding a new agent (Claude Code / Cloud / local)

**Agent package (LOOM):** [`agent/README.md`](../agent/README.md) · charter [`agent/AGENT.md`](../agent/AGENT.md) · workflows W1/W2/W3 under [`agent/workflows/`](../agent/workflows/).

**One-pager:** [`docs/CLAUDE_CODE_STARTER.md`](CLAUDE_CODE_STARTER.md) (copy-paste prompt + role cheat-sheet).

Paste this into the new agent’s system or first message:

```text
You are joining PROJECT HERMES-X via GitHub repo GdotAiM/hermes-x.
Read: docs/WORKFLOW_BLUEPRINT.md, ROSTER.md, protocols/ICT_RESEARCH_PROTOCOL_v0.1.md,
beliefs/LEDGER.md, and investigations/*/STATUS.md for the INV you are assigned.
Your role is: <ATLAS|DATA|QUANT|CASSANDRA|ORION|...>.
Write only your role’s artifacts. Do not RUN QUANT experiments without ORION auth
recorded in STATUS.md. Do not claim SURVIVES without CASSANDRA results red-team.
Commit with message tagging the next role. Never commit secrets or raw large tape.
Success = validated discoveries including FAILS, not chat volume.
```

### Minimal “one agent does everything” mode

If only one model is available, **still write the same files in order**, wearing one hat per commit:

1. ATLAS commit → 2. DATA commit → 3. QUANT protocol commit → 4. CASSANDRA packaging commit → 5. QUANT results commit → 6. CASSANDRA results commit → 7. ORION board commit  

Role separation in **artifacts** beats role separation in **processes**.

---

## 8. ORION review frame (end of every major investigation)

1. What did we think?  
2. What did we observe?  
3. What changed?  
4. What survived?  
5. What failed?  
6. What remains unknown?  

Deliver: Intelligence Summary · Key Findings · Contradictions · Confidence · Failed Assumptions · Open Questions · Highest-Value Next Experiment.

---

## 9. Quick reference — Wave 1 anti-patterns we already paid for

| Anti-pattern | Fix |
|--------------|-----|
| Unlocked control / metric | CASSANDRA CRITICAL → H*b |
| Post-peek N-gate lower | Reject; park INCONCLUSIVE |
| Hard one-hot baseline + log-loss | Soft empirical prior |
| Frequency called “edge” | VERIFY ≠ trade; need specialness + expectancy |
| Silver Bullet / brand language | Test mechanism, not brand |
| Raw 1m CSV in git | META + day_rows only |

---

## 10. Pointers

| Doc | Path |
|-----|------|
| LOOM agent package | `agent/README.md` · `agent/AGENT.md` |
| Role prompts | `docs/prompts/` |
| Anti-patterns | `docs/ANTI_PATTERNS.md` |
| Protocol v0.1 | `protocols/ICT_RESEARCH_PROTOCOL_v0.1.md` |
| Roster | `ROSTER.md` |
| Capture standard | `investigations/INV-001-2026-lectures/CAPTURE_STANDARD.md` |
| Wave 1 board | `summaries/2026-09-13_WAVE1_EXPLORATORY_BOARD.md` |
| Utilization | `summaries/2026-09-13_UTILIZATION_FROM_WAVE1.md` |
| Belief ledger | `beliefs/LEDGER.md` |

**Maintainer note:** When the workflow changes, bump this file’s version line and add a LEDGER row.
