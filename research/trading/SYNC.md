# Sync contract: mint-agent ↔ hermes-x/trading/

**Source of truth (SoT):** this repo — `GdotAiM/mint-agent`  
**Lab mirror:** `GdotAiM/hermes-x` path `trading/`

If they drift, **execution trusts mint-agent**; the lab mirror is for researchers reading one tree.

## How sync works

| Direction | When | How |
|-----------|------|-----|
| **mint-agent → hermes-x/trading/** (primary) | Push to `main` (paths below) or `workflow_dispatch` | GitHub Action [`sync-lab-mirror.yml`](.github/workflows/sync-lab-mirror.yml): runs `scripts/sync_to_hermes_x.sh`, then opens a PR on hermes-x. **Requires** repo secret `HERMES_X_SYNC_TOKEN` (classic PAT with `repo` on hermes-x). Without the secret the Action **fails** (no silent stub). |
| **Local** | Anytime | `./scripts/sync_to_hermes_x.sh /path/to/hermes-x` then PR manually |
| **hermes-x/trading → mint-agent** | Rare hotfix | `scripts/sync_from_hermes_x.sh` then PR here; prefer fixing in mint-agent |

Paths that trigger CI sync: `AGENT.md`, `ALLOWLIST.md`, `config.yaml`, `src/mint/**`, `SYNC.md`, sync script/workflow.

**Not** a git submodule (on purpose): keeps mint-agent independently clonable.

## Secret setup (one-time)

1. Create a classic PAT with `repo` scope (access to `GdotAiM/hermes-x`).
2. mint-agent → Settings → Secrets → Actions → `HERMES_X_SYNC_TOKEN`.
3. Re-run **sync-lab-mirror** via Actions → workflow_dispatch.

## Drift check

```bash
./scripts/check_drift.sh /path/to/hermes-x
# exit 0 = match; 1 = drift
```

## Human rule

Do not edit `hermes-x/trading/` by hand except through sync. Edit mint-agent, sync, PR.
