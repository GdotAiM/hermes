# HERMES-X GitHub labels

Documented process labels for issues/PRs. Create these in the GitHub UI (or `gh label create`) to match.

| Label | Color suggestion | Meaning |
|-------|------------------|---------|
| `needs-data-gate` | `#FBCA04` (yellow) | Claims or tape await DATA Pass/Hold/Fail + META honesty |
| `needs-packaging` | `#D93F0B` (orange) | QUANT protocol filed; CASSANDRA packaging not yet SURVIVED |
| `awaiting-run-auth` | `#5319E7` (purple) | Packaging SURVIVED; waiting for ORION RUN AUTHORIZATION in `STATUS.md` |
| `needs-results-rt` | `#B60205` (red) | Results filed; CASSANDRA results red-team outstanding |
| `board-ready` | `#0E8A16` (green) | Packaging + run + results RT complete enough for ORION board lock |

## Usage

1. Apply **one primary blocker** label when possible.
2. Remove the label when the artifact lands (gate memo, packaging RT, STATUS AUTH stamp, results RT, board lock).
3. Do not mark `board-ready` if SURVIVES is asserted without results RT.
4. `awaiting-run-auth` is **not** permission to run — only ORION’s STATUS stamp is.

## Related

- Stage machine: `agent/AGENT.md`
- Workflows: `agent/workflows/`
- Blueprint: `docs/WORKFLOW_BLUEPRINT.md`
