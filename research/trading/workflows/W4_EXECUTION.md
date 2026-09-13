# W4 — Execution (MINT)

**Purpose:** Turn cleared board / utilization products into **paper** tickets, journals, and daily P&L — without laundering VERIFY/FAILS/INCONCLUSIVE into edge.  
**Owner:** MINT  
**Upstream:** W3 utilization · ORION board · RISK · MERCURY (optional proposer)  
**Exit:** Journal + book/P&L update, **or** explicit idle / NO-TRADE artifact

---

## Stage flow

```
READ_BOARD → CANDIDATE → RISK_CHECK → SIZE → PAPER_ORDER → JOURNAL → DAILY_PNL
```

Skip forward only when a stage outputs **NO-TRADE / IDLE** (still journal the refusal).

---

## Preconditions

- [ ] At least one ORION board lock or utilization memo on disk
- [ ] `trading/config.yaml` `mode: paper`, `live_enabled: false` (unless human dual-unlocked live)
- [ ] Strategy id on allowlist **or** human paper-pilot stamp + RISK
- [ ] Pull before write; no secrets in commit

---

## Hard rules

1. **require_board_ref: true** — every candidate cites a board/utilization path.
2. **No orders** from VERIFY / FAILS / INCONCLUSIVE / packaging-only.
3. **RISK binding** — NO-TRADE and HOLD stop the pipeline; SIZE DOWN is max size.
4. **Paper default** — stub dry-run unless `--submit` **and** mode paper.
5. **Live refuse** if `live_enabled` false or `MINT_LIVE` unset/≠1, or base URL is live while locked.
6. Wave 1: expect **IDLE** — empty entry allowlist is success.

---

## Stage — READ_BOARD

### Checklist

- [ ] Open latest `summaries/*_BOARD_LOCK.md` and utilization memo
- [ ] Record labels per hyp (SURVIVES / FAILS / VERIFY / INCONCLUSIVE)
- [ ] Confirm whether **any** SURVIVES exists (Wave 1: no)

### Outputs

| Artifact | Notes |
|----------|-------|
| Working notes in journal draft | Cite paths |

---

## Stage — CANDIDATE

### Checklist

- [ ] Map candidate → `trading/strategies/<id>.md` (or refuse)
- [ ] Confirm allowlist id + required board status
- [ ] ICT vocabulary only as labeled on strategy card (Observed vs PARAMETER)
- [ ] If only filters/logging → **IDLE** path

### Outputs

| Artifact | Path pattern |
|----------|--------------|
| Candidate block in decision journal | `trading/journal/<DATE>_DECISION_*.md` |

---

## Stage — RISK_CHECK

### Checklist

- [ ] File or cite RISK memo / gate outcome (`risk/GATES.md`, `risk/BOOK.md`)
- [ ] Caps: 0.5% / trade · 2% / day · 5% DD · equity base $100k
- [ ] Correlation / cluster / event notes if any open book
- [ ] Outcome: PASS · SIZE DOWN · NO-TRADE · HOLD

If NO-TRADE / HOLD → jump to JOURNAL (refusal) → DAILY_PNL (likely flat).

---

## Stage — SIZE

### Checklist

- [ ] Dollar risk ≤ RISK-approved and config caps
- [ ] Stop / invalidation explicit
- [ ] No size for INCONCLUSIVE or research_logging ids

---

## Stage — PAPER_ORDER

### Checklist

- [ ] Adapter = Alpaca paper (or stub) per `adapters/alpaca.md`
- [ ] Env vars present for real paper submit; stub dry-run default
- [ ] Refuse live URL when locked
- [ ] `--submit` only if mode paper and RISK PASS/SIZE DOWN
- [ ] Record broker response ids in journal (or dry-run payload)

```bash
# Example dry-run (no network required for local validation of flags):
python trading/adapters/alpaca_paper_stub.py account
python trading/adapters/alpaca_paper_stub.py place_order --symbol FAKE --qty 1 --side buy --type market
# Add --submit only for intentional paper submit when keys + paper URL configured
```

**Do not call live APIs from agent automation.**

---

## Stage — JOURNAL

### Checklist

- [ ] Fill `trading/journal/_TEMPLATE_DECISION.md`
- [ ] MERCURY-compatible fields (thesis, size, stop, board ref, RISK outcome)
- [ ] Explicit **IDLE / NO-TRADE** when Wave 1 empty

---

## Stage — DAILY_PNL

### Checklist

- [ ] Update or propose update to `risk/BOOK.md` (equity, daily P&L, DD)
- [ ] Flat book → $0 P&L is valid
- [ ] LEDGER row only when belief/process state changes (e.g. first paper fill)

### Handoff examples

```
Next: RISK
Path: risk/BOOK.md
Ask: Acknowledge flat book; no Wave 1 tickets.

Next: ORION
Path: trading/journal/2026-09-13_DECISION_IDLE_WAVE1.md
Ask: Confirm MINT idle; no SURVIVES for allowlist promotion.
```

---

## Exit criteria

W4 complete when either:

1. Paper order (or dry-run) + journal + P&L/book sync exist, **or**
2. Documented IDLE/NO-TRADE journal cites board + allowlist emptiness.

**Success reminder:** Refusing to trade Wave 1 is correct execution.
