# Sync contract — RETIRED

`trading/` is now the **single source of truth** for MINT inside the
[GdotAiM/hermes](../README.md) monorepo. It was imported with full git history
from the former standalone repo `GdotAiM/mint-agent` (main @ `7fd5855`).

Previously:

- `GdotAiM/mint-agent` was SoT and `GdotAiM/hermes-x` carried a flattened
  `trading/` lab mirror.
- `scripts/sync_to_hermes_x.sh`, `scripts/sync_from_hermes_x.sh`,
  `scripts/check_drift.sh` and the `sync-lab-mirror` GitHub Action (needing
  secret `HERMES_X_SYNC_TOKEN`) kept them aligned.

All of that is removed: there is one tree, so there is nothing to sync or drift.
The old mirror (byte-identical to mint-agent@7fd5855 apart from its generated
README stub) remains in history under `research/trading/` before the import.

Research inputs are read in-repo: `mint.dispatch.scan_clears` defaults to
`../research` (summaries/ board locks + beliefs/LEDGER.md).

`HERMES_X_SYNC_TOKEN` is no longer needed; revoke that PAT if it was created.
