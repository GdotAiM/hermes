# FORGE — Lecture → Claim Capture Workflow
**Investigation:** INV-001 (2026 ICT SMC lectures)  
**Author:** FORGE  
**Date:** 2026-09-13  
**Status:** Proposed — ready for ORION acceptance + ATLAS/DATA pilot  
**Scope:** Concept/model research only. No production trading infra. No secrets.

---

## Decision frame (required)

### WHAT PROBLEM?
HERMES-X needs a **reproducible path from lecture media → labeled claims** that:
1. Separates **Observed** (lecture said) / **Interpretation** / **Hypothesis**
2. Diffs vs prior years without inventing “new physics”
3. Produces ≤3 falsifiable hyps for QUANT without drowning in named-model zoo
4. Survives agent handoffs (ATLAS → HISTORIAN → DATA → ORION)
5. Can later be rebuilt in **Hermes** with free/open tooling

Without this, claim extraction drifts into paraphrase, community lore leaks in as “ICT said,” and QUANT inherits untestable mush.

### WHY NOW?
- INV-001 is OPEN; human prioritized 2026 lectures over locking 2022 first.
- Taxonomy PDF is a **map only** — not primary evidence (STATUS blocker: playlist access).
- FOMC Wed Sep 16 is a separate MACRO track; this workflow must keep session-delivery claims **non-event-conditioned** unless a lecture explicitly conditions them.
- Early workflow debt compounds: every bad claim label pollutes HISTORIAN diffs and QUANT designs.

### WHAT ALTERNATIVES?

| Option | Pros | Cons | Verdict |
|--------|------|------|---------|
| **A. Ad-hoc chat extraction** | Fast | Non-reproducible; label bleed; no audit trail | Reject |
| **B. Full transcript → LLM dump → claims** | High recall | High hallucination; loses timestamps; expensive | Reject as sole path |
| **C. Structured capture pipeline (this proposal)** | Auditable; Hermes-portable; DATA-gated | Upfront schema cost | **Recommend** |
| **D. Human-only note taking** | Highest fidelity | Doesn't scale; no agent reuse | Fallback for contested claims only |
| **E. Wait for perfect video tooling** | — | Blocks INV-001 | Reject |

### WHAT COMPLEXITY?
- **Low–medium** for v0: markdown claim cards + evidence stubs + agent prompts.
- **Defer:** ASR pipeline, vector store, custom UI, automated YouTube sync.
- Complexity budget: one schema, three agent prompts, one validation checklist. No new services.

### WHAT FAILURE MODES?
See § FAILURES below. Top risks: (1) community terms treated as lecture-backed, (2) interpretation labeled Observed, (3) testing named packages before one falsifiable session claim, (4) FOMC conflation, (5) transcript/hallucination without timestamp anchor.

### HOW WILL WE TEST IT?
See § SUCCESS CONDITIONS + § Test plan. Pilot on **one** 2026 lecture (shortest session-algorithm video) before playlist-wide extraction.

---

## Tracked workflow package

### PROMPT (agent contracts)

#### Shared claim discipline (all extractors)
```
You are extracting claims from ICT lecture evidence for HERMES-X INV-001.

HARD RULES:
1. Every claim MUST have label: Observed | Interpretation | Hypothesis.
   - Observed = speaker stated it (quote or tight paraphrase + timestamp).
   - Interpretation = our reading of what that implies for markets.
   - Hypothesis = falsifiable statement we might test later.
2. Never promote community/vendor terms (Zircon, rigid CHoCH two-candle rules, etc.) to Observed unless the lecture itself uses and defines them.
3. Prefer session-delivery clocks (Asia / London / NY AM / NY lunch / NY PM / MOC) over named-model zoo.
4. If timestamp or primary source is missing → status = UNVERIFIED; do not feed QUANT.
5. Separate FOMC/event talk unless the lecture explicitly conditions the claim on an event.
6. Output ONLY claim cards matching the schema. No trading advice. No live capital language.
```

#### ATLAS extractor prompt (lecture → behaviour claims)
```
Role: ATLAS — Market Intelligence.
Input: one lecture evidence pack (video id, title, optional transcript segments with timestamps, notes).
Task: Extract market-behaviour / session-delivery claims.
For each claim fill CLAIM_CARD schema.
Focus: Asia / London / NY AM / NY lunch / NY PM / MOC; killzones; macros; raid → displacement/MSS|CISD → PD array → opposing liquidity.
Flag: new | refine | repackage | unverified relative to prior years ONLY if HISTORIAN has not yet run — else leave Diff blank for HISTORIAN.
```

#### HISTORIAN diff prompt
```
Role: HISTORIAN.
Input: ATLAS claim set (Observed only for diffs) + prior-year anchors (2022 Model, 2024 CISD/OR, 2025 Venom as lecture-backed only).
Task: Tag each Observed claim: NEW | REFINE | REPACKAGE | UNVERIFIED.
Reject “new” unless lecture text supports a material change in mechanism or clock, not branding.
```

#### DATA gate prompt
```
Role: DATA.
Input: claim cards + evidence stubs.
Task: Pass/Fail each claim on evidence integrity.
Fail if: no playlist/video id, no timestamp for Observed, secondary/student write-up used as primary, taxonomy PDF used as primary.
Emit EVIDENCE_GATE record.
```

### WORKFLOW (v0 — file-native, Hermes-portable)

```
1. INTAKE
   ORION opens investigation BRIEF + STATUS.
   DATA registers primary sources in evidence/ (playlist id, video ids).
   Taxonomy PDF = MAP ONLY (never primary).

2. EVIDENCE PACK (per lecture)
   Path: investigations/INV-001-2026-lectures/evidence/<video_id>/
   Files:
     META.md          — title, url, upload date, duration, playlist position
     SEGMENTS.md      — optional: timestamped notes or transcript slices
     ACCESS.md        — how obtained; blockers; license/TOS notes

3. CLAIM EXTRACT (ATLAS)
   Path: investigations/INV-001-2026-lectures/claims/<claim_id>.md
   One file per claim. IDs: C-2026-<nnn>
   Run ATLAS prompt; write cards.

4. YEAR DIFF (HISTORIAN)
   Update Diff field on Observed cards only.
   Write rollup: reviews/HISTORIAN_DIFF_*.md

5. EVIDENCE GATE (DATA)
   Stamp each card Pass/Fail/Hold.
   Failures blocked from ORION hyp ranking.

6. SYNTHESIS (ORION)
   From Passed Observed + supporting Interpretation:
   Produce ≤3 falsifiable hypotheses ranked by information gain.
   Hold QUANT / CASSANDRA until that set exists.

7. DOWNSTREAM (held)
   QUANT designs per EXPERIMENT_PROTOCOL.md
   CASSANDRA attacks before RISK/MERCURY paper use

8. REVIEW FRAME (ongoing)
   WHAT DID WE THINK? → OBSERVE → CHANGED → SURVIVED → FAILED → UNKNOWN?
```

**Handoff diagram (logical):**
DATA(source register) → ATLAS(extract) → HISTORIAN(diff) → DATA(gate) → ORION(≤3 hyps) → QUANT → CASSANDRA → (RISK/MERCURY only if event-conditioned or later paper use)

FORGE sits beside the loop: schema, prompts, failure modes, Hermes portability score.

### INPUTS
| Input | Required? | Owner | Notes |
|-------|-----------|-------|-------|
| Official playlist id `PLVgHx4Z63paaja3GW0dYSr6y_V2Sttx4-` | Yes | DATA | Primary |
| Per-video id + title + URL | Yes | DATA | Primary |
| Timestamped segment / quote for Observed | Yes for Observed | ATLAS | Without → UNVERIFIED |
| Transcript (ASR or official) | Optional | DATA | Nice-to-have; not required if human timestamped notes exist |
| Taxonomy PDF / ICT_TAXONOMY_NOTES | Map only | ORION | Never primary claim source |
| Prior-year lecture anchors | Yes for Diff | HISTORIAN | 2022 / 2024 CISD·OR / 2025 Venom as lecture-backed |
| Student/community write-ups | Secondary only | DATA | Flag; cannot alone Pass Observed |

### TOOLS (HERMES-X now vs Hermes later)

| Capability | HERMES-X (now) | Hermes / free-open later | Reuse |
|------------|----------------|--------------------------|-------|
| File ledger | `/home/box/hermes-x` markdown | git + markdown / Obsidian / plain FS | High |
| Agent prompts | Grok Bot agent messages | OpenLLM + same prompt files | High |
| Video access | Human / browser / watchVideo when available | yt-dlp (metadata) + optional local Whisper | Medium (TOS) |
| ASR | Defer | faster-whisper / whisper.cpp | High once added |
| Claim schema | markdown CLAIM_CARD | same schema → optional SQLite/JSONL | High |
| Diff / gate | HISTORIAN + DATA agents | scripts + checklist, or same roles | High |
| Vector search | Not needed v0 | optional later (sqlite-vss / LanceDB) | Low priority |
| CI check | Manual STATUS.md | pre-commit: schema lint on claims/*.md | Medium |

**Do not build yet:** custom MCP for YouTube, production ETL, paid transcript APIs (unless human approves cost).

### OUTPUT

#### CLAIM_CARD schema (`claims/C-2026-NNN.md`)
```markdown
# C-2026-NNN
**Label:** Observed | Interpretation | Hypothesis
**Status:** Draft | Passed | Failed | Hold | UNVERIFIED
**Session clock:** Asia | London | NY AM | NY lunch | NY PM | MOC | Multi | N/A
**Family:** (one of eight taxonomy families)
**Statement:** <one sentence>
**Quote / paraphrase:** <tight>
**Source:** video_id | title | timestamp (HH:MM:SS–HH:MM:SS)
**Playlist:** PLVgHx4Z63paaja3GW0dYSr6y_V2Sttx4-
**Diff (HISTORIAN):** NEW | REFINE | REPACKAGE | UNVERIFIED | (blank until run)
**Event-conditioned:** No | Yes — <event>
**Attribution risk:** none | community-term | taxonomy-only | secondary-source
**DATA gate:** Pass | Fail | Hold — <reason>
**Links:** evidence/<video_id>/
**Owner:** ATLAS (extract) / HISTORIAN (diff) / DATA (gate)
```

#### Evidence pack stub (`evidence/<video_id>/META.md`)
```markdown
# <title>
- video_id:
- url:
- playlist_position:
- upload_date:
- duration:
- access: available | blocked | partial
- primary: yes
```

#### ORION hyp ranking output (downstream of this workflow)
≤3 items, each mappable to QUANT EXPERIMENT_PROTOCOL fields (population, session, entry, falsification).

### FAILURES (monitor + mitigations)

| ID | Failure | Signal | Mitigation |
|----|---------|--------|------------|
| F1 | Interpretation labeled Observed | No timestamp / soft paraphrase | DATA auto-Fail; schema requires timestamp for Observed |
| F2 | Community lore as ICT | Terms not in lecture | Attribution risk flag; CASSANDRA later |
| F3 | Taxonomy PDF as primary | Source = PDF only | DATA Fail |
| F4 | Named-model zoo explosion | >N claims on brands not clocks | ORION cap: session clocks first; out-of-scope list |
| F5 | FOMC conflation | Event language in non-conditioned claim | Event-conditioned field; MACRO track separate |
| F6 | Transcript hallucination | Claim not findable at timestamp | Spot-check audit: 3 random Observed per lecture |
| F7 | Diff inflation (“everything NEW”) | NEW rate >> refine/repackage | HISTORIAN prior: branding ≠ mechanism change |
| F8 | Pipeline stall on playlist access | STATUS blocker | Human provides access OR work from timestamped notes on available videos only |
| F9 | Premature QUANT | Hyps without Passed Observed | ORION gate: QUANT held until ≤3 ranked |
| F10 | Irreproducible prompts | Prompts only in chat | Prompts live in this file + optional `prompts/` copy |

### SUCCESS CONDITIONS
1. **Schema compliance:** ≥95% claim files parse against CLAIM_CARD fields.
2. **Label purity:** Spot audit — 0 Observed without timestamp+video_id among Passed.
3. **Gate effectiveness:** DATA Fail catches taxonomy-only and secondary-only sources.
4. **Diff discipline:** HISTORIAN NEW rate justified in rollup; ORION can explain each NEW.
5. **Throughput:** One lecture → claim set in one ATLAS pass without schema renegotiation.
6. **Downstream ready:** ORION can emit ≤3 falsifiable hyps from Passed cards alone.
7. **Hermes portability:** A stranger with markdown + this doc + open LLM prompts can reproduce the pipeline without Grok-specific tools (video access excepted).
8. **No scope breach:** No live capital language; no production infra changes.

### REUSABILITY
| Asset | Reusable? | Port target |
|-------|-----------|-------------|
| CLAIM_CARD schema | Yes | Hermes core |
| Agent prompts above | Yes | Prompt library (open models) |
| Workflow stages 1–8 | Yes | Same folder conventions |
| Evidence pack layout | Yes | git-backed research repos |
| watchVideo / Grok Bot specifics | Partial | Replace with Whisper + human QA |
| ORION/ATLAS/… personas | Conceptual | Re-implement as roles, not vendor lock-in |
| INV-001 content | Investigation-specific | Template for INV-00N lecture series |

**Reusability score (FORGE):** **A−** for process/schema/prompts; **C** for media ingest until open ASR path is documented. Overall package: **ship v0**.

---

## Test plan (pilot before playlist-wide)

1. Pick **one** 2026 lecture focused on session algorithms (prefer NY lunch or killzone clock if available).
2. DATA creates `evidence/<video_id>/` with META + ACCESS.
3. ATLAS produces ≤15 claim cards (quality > quantity).
4. FORGE + DATA audit: schema + F1/F3 checks.
5. HISTORIAN diffs Observed subset.
6. ORION attempts ≤3 hyps; if underpowered, refine extraction — do not lower gates.
7. Log failures in `reviews/FORGE_PILOT_NOTES.md`.
8. Only then scale to more 2026 videos.

**Pass criteria for pilot:** Success conditions 1–2, 5–6 met on the single lecture.

---

## Complexity budget / non-goals
- No new databases, MCP servers, or CI until pilot passes.
- No automated download of full channel.
- No proving “ICT works.”
- No Venom/Suspension/Enigma/etc. unless 2026 lecture explicitly defines it.
- No production trading infra changes (ever, without explicit human approval).

---

## Recommendations for ORION
1. **Accept** this workflow as INV-001 capture standard.
2. Unblock **DATA** on playlist/video access (human) — taxonomy remains map-only.
3. Brief **ATLAS** with CLAIM_CARD schema + shared discipline prompt (copy from this file).
4. Run **pilot on one lecture** before fan-out.
5. Keep MACRO FOMC track in `summaries/` / macro evidence — do not merge into claim cards unless Event-conditioned=Yes.

## Hermes portability note (special assignment)
Successful Grok pieces to reproduce later with free/open tooling:
- **PROMPT** files (this doc)
- **WORKFLOW** stages + folder layout
- **INPUTS** registry discipline
- **OUTPUT** CLAIM_CARD markdown
- **FAILURES** checklist as lint rules
- **SUCCESS CONDITIONS** as acceptance tests

Replace later: proprietary video-watch agents → `yt-dlp` metadata + local Whisper + human timestamp QA. Keep claims and gates identical so research continuity survives tooling change.

---

## Changelog
- 2026-09-13: Initial proposal (FORGE) for ORION acceptance.
