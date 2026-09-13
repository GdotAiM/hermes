# LOOM — Workflow Agent Package

**LOOM** is the Workflow Conductor for PROJECT HERMES-X: a portable **stage machine** that keeps multi-agent research honest when collaboration happens through **GitHub**, not chat.

Any model or human that can read markdown and commit files can join the lab. LOOM does not invent science priorities — that is **ORION**. LOOM enforces **process compliance**: stage order, decision vocabulary, packaging gates, and handoff hygiene.

## Why this package exists

Wave 1 taught us that role volume is not progress. Validated discoveries (including clean **FAILS**) are. This package freezes the collaboration contract so Claude Code, Cursor, Grok specialists, Codex, or a solo model all write the **same artifacts** in the **same order**.

## Start here

| Doc | Purpose |
|-----|---------|
| [`AGENT.md`](AGENT.md) | Full system charter for LOOM (hard laws, W1/W2/W3, handoffs, ORION relationship) |
| [`config.yaml`](config.yaml) | Machine-readable roles, workflows, vocabulary, caps |
| [`SOLO_MODE.md`](SOLO_MODE.md) | One model, one role per commit, stage order |
| [`workflows/W1_CLAIM_TO_GATE.md`](workflows/W1_CLAIM_TO_GATE.md) | Observe → DATA gate |
| [`workflows/W2_HYP_TO_BOARD.md`](workflows/W2_HYP_TO_BOARD.md) | Spec → protocol → packaging → run → results RT → board |
| [`workflows/W3_UTILIZATION.md`](workflows/W3_UTILIZATION.md) | Board → utilization / demotion / no-trade rules |

## Related repo docs

| Doc | Path |
|-----|------|
| Workflow blueprint | [`docs/WORKFLOW_BLUEPRINT.md`](../docs/WORKFLOW_BLUEPRINT.md) |
| Role prompts | [`docs/prompts/`](../docs/prompts/) |
| Investigation templates | [`investigations/_TEMPLATE/`](../investigations/_TEMPLATE/) |
| Board / utilization templates | [`summaries/_BOARD_LOCK_TEMPLATE.md`](../summaries/_BOARD_LOCK_TEMPLATE.md), [`summaries/_UTILIZATION_TEMPLATE.md`](../summaries/_UTILIZATION_TEMPLATE.md) |
| Anti-patterns (Wave 1) | [`docs/ANTI_PATTERNS.md`](../docs/ANTI_PATTERNS.md) |
| External agent starter | [`docs/CLAUDE_CODE_STARTER.md`](../docs/CLAUDE_CODE_STARTER.md) |
| Roster | [`ROSTER.md`](../ROSTER.md) |

## Repo

https://github.com/GdotAiM/hermes-x

## Hard reminder

Git is the system of record. Chat is optional coordination. Never skip packaging. Never RUN without ORION auth in `STATUS.md`. Never claim **SURVIVES** without a CASSANDRA results red-team. **VERIFY ≠ edge.** No MERCURY from VERIFY / FAILS / INCONCLUSIVE.
