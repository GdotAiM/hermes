# MINT Strategy Allowlist

**Owner:** MINT (enforcement) · **ORION** (science clearance) · **RISK** (survival) · **Human** (paper pilot / live unlock)

Nothing on this list may generate **entries** unless its `board_status_required` is satisfied **and** RISK accepts.

---

## How a strategy gets on the list

A strategy id may be added to `trading/config.yaml` → `strategy_allowlist` only via **one** of:

### Path A — ORION board **SURVIVES** (preferred)

1. Packaging SURVIVED → exploratory/confirmatory RUN → CASSANDRA **results** RT agree.
2. ORION board lock labels **SURVIVES** (not VERIFY, not packaging-only).
3. W3 utilization memo states what is tradeable vs prior-only.
4. RISK gate **PASS** or **SIZE DOWN** (not NO-TRADE / HOLD).
5. Human ack for first paper pilot of that strategy (MERCURY may propose; MINT journals).
6. Strategy file under `trading/strategies/` maps `hypothesis_id` → entry/stop/target → required board status.
7. PR / commit updates allowlist + LEDGER row.

### Path B — Human-explicit paper pilot + RISK

1. Human writes an explicit paper-pilot stamp (path cited in journal).
2. RISK still gates size against hard caps.
3. ORION is notified; board may still say FAILS/INCONCLUSIVE for the *science* claim — pilot must not launder labels (journal must say **pilot**, not SURVIVES).
4. Allowlist entry marked `kind: paper_pilot` with expiry / kill criteria.

**Live** is never granted by allowlist alone. Live needs `MINT_LIVE=1` **and** `live_enabled: true`.

---

## What does **not** get you on the list

| Claim | Why blocked |
|-------|-------------|
| VERIFY COMPLETE frequency | Prior / logging only |
| PACKAGING SURVIVED | Design clearance ≠ edge |
| FAILS | Demote / no-trade filter only |
| INCONCLUSIVE | No size |
| Soft “promising / near miss” | Banned vocabulary |
| Chat-only approval | Git is system of record |

---

## Wave 1 — nothing tradeable yet

**Status as of 2026-09-13:** exploratory chapter CLOSED on CONTINUOUS-KAGGLE. **Zero SURVIVES.** MINT allowlist holds **filters + logging only**.

| Hyp | Board | Allowlist implication |
|-----|-------|------------------------|
| H001b CE hit-by-10:00 ≈ **56%** | VERIFY COMPLETE; specialness **FAILS** | **Prior only** — not entry. Folklore ~70% demoted. |
| H002b 7–9 → first-side | **FAILS** | **Demote** — no-trade filter; no side bias from labels alone |
| H003c REL/REH → opposite | **FAILS** | **Demote** — no standalone sweep→opposite entry |
| H004b first-10:00 FVG | **FAILS** | **Demote** — no preferential first-FVG entry |
| H009b nearest weekly DOL | **INCONCLUSIVE** | **No size** — logging / watchlist framing only |

Active allowlist ids (see `config.yaml`):

- `no_trade_filters` — encode the demotions above
- `research_logging` — priors / H009b watchlist frames; **never sizes**

**CE 56% is a prior, not an entry.**

---

## Changing the list

1. Edit `trading/config.yaml` `strategy_allowlist`.
2. Add/update `trading/strategies/<id>.md` from `_TEMPLATE.md`.
3. Cite board lock + RISK memo paths in the PR body.
4. Add `beliefs/LEDGER.md` row.
5. Never enable live in the same change without separate human unlock docs.

---

## Reminder

Falsification-first: clean **FAILS** and honest **INCONCLUSIVE** keep capital alive. An empty entry allowlist in Wave 1 is correct behavior, not a backlog bug.
