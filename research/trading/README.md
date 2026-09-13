# MINT — Trading Package

**MINT** owns this package: broker I/O, allowlisted execution, fills, and P&L.

**MERCURY** proposes paper decisions. **RISK** gates. **MINT** executes paper orders only when authorized.

**Default: paper. `live_execution: false`.** Wave 1 has **no cleared edge**. This package must be on `main` before any execution path is considered ready. Live still requires human unlock (+ RISK + SURVIVES on allowlist).

Repo: https://github.com/GdotAiM/hermes-x

## What MINT is (and is not)

| MINT owns | MINT does not own |
|-----------|-------------------|
| Paper broker I/O (adapters) | Science priority / board locks (**ORION**) |
| Allowlist enforcement | Process stage machine (**LOOM**) |
| Fills + decision journal + P&L | Hypothesis packaging / red-team (**CASSANDRA**) |
| Caps check at execute time | Raising paper caps or enabling live without human |

ICT is the **domain vocabulary**. Only **cleared** research may drive orders. Frequency / VERIFY COMPLETE is never an entry.

## Vs other layers

| Layer | Role vs MINT |
|-------|----------------|
| **ORION** | Decides what survived science; MINT only acts on **SURVIVES** (plus RISK + human). |
| **LOOM** | Process compliance (W1–W3). MINT owns paper order flow after utilization. |
| **RISK** | Survival gates, caps, PASS / SIZE DOWN / NO-TRADE. MINT refuses tickets RISK rejected. |
| **MERCURY** | Proposes paper decisions. MINT is broker-facing plumbing. |
| **QUANT / CASSANDRA / ATLAS / …** | Upstream research. MINT never invents setups from raw claims. |

## Paper vs live

| Mode | When | Behavior |
|------|------|----------|
| **paper** (default) | `config.yaml` `mode: paper`, `live_execution: false` | Alpaca **paper** adapter stub only. Scaffold incomplete — methods raise. |
| **live** | Human unlock only | Requires `live_execution: true` **and** RISK ack **and** SURVIVES strategy on allowlist. **Not enabled.** No working live branch. |

Hard paper caps (same as RISK / LOOM `agent/config.yaml` `paper_caps`):

- Starting equity: **$100,000**
- Max trade risk: **0.5%**
- Max daily loss: **2%**
- Max portfolio DD: **5%**
- **No live execution** without human unlock
- Caps cannot rise without human

## Package layout

| Path | Purpose |
|------|---------|
| [`config.yaml`](config.yaml) | Paper mode, caps, broker, allowlist, banned moves |
| [`adapters/`](adapters/) | Broker adapter interface + Alpaca paper stub |
| [`strategies/allowlist.yaml`](strategies/allowlist.yaml) | SURVIVES-only trade list (Wave 1: empty) |
| [`journal/`](journal/) | Decision / fill records (`SCHEMA.md`) |
| [`workflows/PAPER_ORDER_FLOW.md`](workflows/PAPER_ORDER_FLOW.md) | PROPOSE → RISK → ALLOWLIST → PAPER_EXECUTE → JOURNAL → P&L |

## Related repo docs

| Doc | Path |
|-----|------|
| RISK gates | [`risk/GATES.md`](../risk/GATES.md) |
| Paper book | [`risk/BOOK.md`](../risk/BOOK.md) |
| Board / utilization | [`summaries/`](../summaries/) — Wave 1: [`2026-09-13_UTILIZATION_FROM_WAVE1.md`](../summaries/2026-09-13_UTILIZATION_FROM_WAVE1.md) |
| LOOM paper caps | [`agent/config.yaml`](../agent/config.yaml) |
| Role prompt | [`docs/prompts/MINT.md`](../docs/prompts/MINT.md) |
| Roster | [`ROSTER.md`](../ROSTER.md) |

## Wave 1 reality (falsification-first)

- **`trade_strategies: []`** — nothing tradeable.
- Allowlist = **NO-TRADE filters** + **logging priors** only.
- H001b CE-by-10:00 ~56% is a **prior**, not an entry. **Not** CE midpoint entries.
- H002b / H003c / H004b **FAILS** → demote.
- H009b **INCONCLUSIVE** → watchlist / logging only; no size.
- Never trade from VERIFY / FAILS / INCONCLUSIVE.

## Secrets

Never commit tokens, `.env`, or credentials. Read from environment only:

| Var | Purpose |
|-----|---------|
| `ALPACA_API_KEY` | Paper key id |
| `ALPACA_SECRET_KEY` | Paper secret |
| `ALPACA_PAPER_BASE_URL` | Optional paper base URL override |

## Hard reminder

Git is the system of record. **VERIFY ≠ edge.** PASS / WAIT / NO-TRADE is success when blocked. Package on `main` ≠ live ready.
