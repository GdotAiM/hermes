# Sync contract: mint-agent ↔ hermes-x/trading/

**Source of truth (SoT):** this repo — `GdotAiM/mint-agent`  
**Lab mirror:** `GdotAiM/hermes-x` path `trading/`

If they drift, **execution trusts mint-agent**; the lab mirror is for researchers reading one tree.

## How sync works

| Direction | When | How |
|-----------|------|-----|
| **mint-agent → hermes-x/trading/** (primary) | After merges to `mint-agent` `main` | GitHub Action `sync-lab-mirror.yml` opens a PR on hermes-x **or** run `scripts/sync_to_hermes_x.sh` locally |
| **hermes-x/trading → mint-agent** | Rare (lab-only hotfix) | `scripts/sync_from_hermes_x.sh` then PR here; prefer fixing in mint-agent instead |

**Not** a git submodule (on purpose): keeps mint-agent independently clonable for Claude Code / Cursor without pulling the whole research ledger.

## Drift check

```bash
./scripts/check_drift.sh /path/to/hermes-x
# exit 0 = match; 1 = drift
```

## Human rule

Do not edit `hermes-x/trading/` by hand except through sync. Edit mint-agent, sync, PR.
