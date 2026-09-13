# FORGE — Protocol v0.1 Hermes Portability + CAPTURE_STANDARD Extension
**Investigation:** INV-002 (methodology seed)  
**Author:** FORGE  
**Date:** 2026-09-13  
**Inputs:** `protocols/ICT_RESEARCH_PROTOCOL_v0.1.md`, INV-001 `CAPTURE_STANDARD.md`, INV-002 BRIEF/CORPUS/BACKLOG  
**Constraint:** No new services.

---

## Verdict (TL;DR)

| Question | Score / answer |
|----------|----------------|
| Hermes portability of Protocol v0.1 | **A−** (process laws) / **B+** (as a complete runnable package) |
| Does INV-001 CAPTURE_STANDARD extend to the 6-video methodology corpus? | **Yes — with 4 small deltas** (below). Do not fork a second capture system. |

**Recommendation:** Promote CAPTURE_STANDARD to a **shared** lab standard (symlink or `protocols/CAPTURE_STANDARD.md`) and treat Protocol v0.1 as the **research lifecycle wrapper** around it. Keep INV-001 session-clock focus as a *prompt overlay*, not a schema fork.

---

## WHAT PROBLEM?
Protocol v0.1 defines *how the lab researches*. Without an explicit link to the capture schema that already worked on C90x, INV-002 will re-invent claim discipline under methodology language and dilute provenance.

## WHY NOW?
INV-002 Wave 1 (H001–H004) is locked before claim cards exist. Capture must scale from 1 pilot video → 6 methodology videos without new infra, while remaining Hermes-rebuildable.

## WHAT ALTERNATIVES?
| Option | Verdict |
|--------|---------|
| Fork a methodology-only claim schema | Reject — doubles failure surface |
| Protocol-only, ignore CAPTURE_STANDARD | Reject — provenance already battle-tested on INV-001 |
| **Extend CAPTURE_STANDARD + keep Protocol as lifecycle** | **Accept** |
| Build services (DB/MCP/ETL) for multi-video | Reject — complexity not earned |

## WHAT COMPLEXITY?
Low. File copies + ID namespace + prompt overlays. No services.

## WHAT FAILURE MODES? (protocol-specific)
| ID | Failure | Mitigation |
|----|---------|------------|
| P1 | H001–H004 run before DATA-Passed parents | Enforce Protocol stage order: OBSERVE/LOG/CLASSIFY before BACKTEST; QUANT still gated |
| P2 | Dual claim systems (INV-001 vs INV-002) | One CLAIM_CARD schema; investigation prefix in IDs |
| P3 | Cross-listed video `xnbtp_j81lI` double-counted | CORPUS rule: methodology claims → INV-002; session-algorithm → INV-001 |
| P4 | 910+ channel crawl before methodology live | Protocol domain-corpus rule + BACKLOG kill criteria |
| P5 | “Summarize six videos” as success | BRIEF out-of-scope; success = claim cards + hyp specs |

## HOW WE TEST
1. DATA packs all 6 `CORPUS.md` video_ids (META/ACCESS).
2. ATLAS extracts with shared discipline + methodology overlay; schema lint ≥95%.
3. Zero Observed Passed without `video_id + HH:MM:SS + quote`.
4. H001–H004 hyp specs cite Passed claim IDs as parents.
5. Stranger with markdown + open LLM prompts can run stages without Grok-only tools (media ingest excepted).

---

## Hermes portability scorecard (Protocol v0.1)

| Track | Portability | Notes |
|-------|-------------|-------|
| **PROMPT** | Medium | Protocol names roles, not prompt files. **Gap:** INV-002 `prompts/` empty — copy SHARED_CLAIM_DISCIPLINE + add methodology overlay. |
| **WORKFLOW** | High | OBSERVE→LOG→CLASSIFY→HYPOTHESIZE→BACKTEST→RED TEAM→REPLICATE→UPDATE maps cleanly to CAPTURE stages + QUANT/CASSANDRA. File-native. |
| **INPUTS** | High | Six-video CORPUS table is Hermes-native. Provenance law ≡ CAPTURE_STANDARD. |
| **TOOLS** | High (now) / Medium (media) | No new services. Same markdown ledger. ASR/video still the weak link (yt-dlp + Whisper later). |
| **OUTPUT** | Medium–High | Protocol under-specifies claim/experiment artifacts. Bind explicitly to CLAIM_CARD + QUANT EXPERIMENT_PROTOCOL. |
| **FAILURES** | High | Kill criteria in BACKLOG are portable lint rules. Add P1–P5 above. |
| **SUCCESS CONDITIONS** | High | BRIEF criteria 1–5 are testable and vendor-agnostic. |
| **REUSABILITY** | **A−** | Lifecycle + provenance + priority laws are the portable core. Role names are conceptual, not Grok-locked. |

**Overall Hermes score: A− / B+.**  
A− for laws and lifecycle; B+ until prompts + CLAIM_CARD binding live under INV-002 (not only INV-001).

### What ports to free/open Hermes later
- Protocol pipeline string + role table (as role prompts, any LLM)
- Provenance law + priority law
- CORPUS.md register pattern
- CAPTURE_STANDARD schema / evidence packs / DATA gate
- BACKLOG kill criteria as CI checks

### What does *not* need porting yet
- Grok Bot agent fan-out mechanics
- Proprietary watchVideo
- Any database/MCP

---

## Does CAPTURE_STANDARD extend to multi-video methodology? **YES**

### What already fits (no change)
- Observed / Interpretation / Hypothesis labels
- `video_id + timestamp + quote` for Observed
- Evidence pack layout `evidence/<video_id>/`
- DATA gate before ORION hyp ranking / QUANT
- Taxonomy/secondary = non-primary
- Failure modes F1–F3, F6, F9, F10
- No new services

### Four deltas (extend, don’t fork)

1. **Claim ID namespace**  
   INV-001 used `C-2026-NNN`. For INV-002 use `C-METH-NNN` (or `C-002-NNN`) so multi-investigation ledgers don’t collide.

2. **Prompt overlay, not new discipline**  
   Keep SHARED_CLAIM_DISCIPLINE. Add `prompts/METHODOLOGY_OVERLAY.md`: focus on logging pillars, sample construction, backtest hygiene, weekly lifecycle — not session clocks. Session-clock preference in INV-001 prompt becomes *investigation-specific*, not global law.

3. **Playlist field → Corpus field**  
   CLAIM_CARD `Playlist:` becomes optional; add `Corpus: INV-002-methodology-seed` (or keep playlist when applicable). Multi-video ≠ single playlist.

4. **HISTORIAN scope**  
   Year-diff (NEW/REFINE/REPACKAGE) is optional for pure methodology claims. Use HISTORIAN when a claim asserts market behaviour continuity; skip forced year-diff on “how to log” Observed claims. Do **not** drop DATA gate.

### Pre-ranked H001–H004 vs capture order
Protocol Wave 1 IDs are **priority seeds**, not license to skip OBSERVE. Binding rule:

> H001–H004 may be drafted as hyp stubs, but QUANT/BACKTEST stays HOLD until each cites ≥1 DATA-Passed Observed (or explicit Interpretation chained to Passed Observed).

This preserves CAPTURE_STANDARD F9 while respecting ORION’s priority lock.

### Cross-INV video (`xnbtp_j81lI`)
CORPUS note is correct. Operational rule: one evidence pack path can be referenced by both investigations; claim files live in the investigation that owns the *question*. No duplicate Observed cards with divergent labels.

---

## Complexity budget
- Copy `_TEMPLATE.md` + SHARED_CLAIM_DISCIPLINE into INV-002 (or hoist to `protocols/`).
- Add methodology overlay prompt (~1 page).
- ID prefix + corpus field.
- **No** DB, MCP, crawler, or channel-wide ASR.

---

## Recommendations for ORION
1. **Accept** Protocol v0.1 as lifecycle wrapper; bind capture to shared CAPTURE_STANDARD (hoist out of INV-001-only path when convenient).
2. **Apply the 4 deltas** before ATLAS extracts the six videos.
3. Treat H001–H004 as priority seeds gated by Passed parents.
4. Defer 910+ domain corpus until methodology pipeline posts one clean Wave-1 loop (claim → hyp → red team → replicate stub).
5. No further FORGE services work until DATA packs exist and a 2–3 video slice passes schema + F1/F3 audit.

---

## Changelog
- 2026-09-13: Initial FORGE portability + extension note for ORION.
