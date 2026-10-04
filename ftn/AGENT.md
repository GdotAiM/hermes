# AGENT.md — FTN (Filling The Numbers)

**Codename:** FTN
**Role:** ICT daily-range orchestration — measure four numbers, gate setups, journal
**Sibling:** https://github.com/GdotAiM/mint-agent
**Status:** PAPER default; live locked
**Domain source:** ICT Mentorship Core Content Month 09 — Filling The Numbers

---

## 0. Mission

FTN is a **workflow layer**, not a signal printer.

It consumes OHLC (fixture or feed) and produces:

- four measurement families (0-GMT pivots, CBDR SDs, Asian Range SDs, Flout halves)
- a directional four-level count from a candidate price
- confluence against simple PD-array placeholders
- paper tickets + a decision journal

**Success** includes refusing to trade on low-volatility days and days with no PD-array overlap.

ICT is the vocabulary. Only a human / MINT allowlist may turn a ticket into size.

---

## 1. Hard laws

1. **PAPER default.** `mode: paper`, `live_enabled: false`.
2. **Live dual unlock:** `FTN_LIVE=1` AND `live_enabled: true`. Stub still refuses live.
3. **No secrets in git.**
4. **Tickets ≠ orders.** Dispatch JSON is not a broker ticket.
5. **Pivots are targets, not entries.** Entry remains PD-array after displacement/MSS.
6. **Four is a baseline, not a cap** on expansion days.
7. **Low ATR / compressed session** → NO-TRADE filter.
8. **Risk caps cannot rise without a human.**
9. **Do not call live brokers from agent automation.**

---

## 2. Workflow stages

```
PREP → FILTER → WATCH → GATE → MANAGE → JOURNAL
```

See `src/ftn/workflow/orchestrator.py`. Since 2026-10-04 the GATE stage is the Month-9
kernel (`ftn brief` path): only it may produce a session ticket or MINT draft. The legacy
fixture `setup` booleans are research context and can never make a ticket actionable.

---

## 3. Measurement families

| Family | Unit | Count rule |
|--------|------|------------|
| 0-GMT pivots | PP, midpoints, R/S | sequential 4 from entry in bias direction |
| CBDR | range + stacked SDs | range extreme is level 1 |
| Asian Range | session high/low + SDs | opposite extreme is level 1 |
| Flout | 15:00–00:00 NY, split at 50% | equilibrium gate; half-range units |

Projections without PD-array overlap are logged, not traded.

---

## 4. Handoff

```
Next: MINT (read-only consumer of handoff.v1; HERMES_INTEGRATION_I0)
Path: dispatch/out/handoff_latest.json (+ opt-in research draft dispatch/drafts/ftn_draft_latest.json, FTN_WRITE_MINT_DRAFT=1)
Gate chain: kernel_ticket → direction → risk (0.5% / 2% / 5%) → mint_allowlist → paper mode → contract
Ask: none. actionable_for_mint is always false (contract gate); blocked_by names the first failing gate.
```

Allowlist population is human-only — see `docs/MINT_ALLOWLIST.md`. Today it is empty.

---

**Maintainer:** When laws change, update this charter and `config.yaml`.
