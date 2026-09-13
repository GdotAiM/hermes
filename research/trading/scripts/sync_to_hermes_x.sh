#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_X="${1:-${HERMES_X_PATH:-}}"
if [[ -z "$HERMES_X" || ! -d "$HERMES_X" ]]; then
  echo "Usage: $0 /path/to/hermes-x" >&2
  exit 2
fi
T="$HERMES_X/trading"
mkdir -p "$T/adapters" "$T/workflows" "$T/journal" "$T/strategies" "$T/scripts"
cp "$ROOT/AGENT.md" "$ROOT/ALLOWLIST.md" "$ROOT/config.yaml" "$ROOT/SYNC.md" "$T/"
cp "$ROOT/src/mint/workflows/W4_EXECUTION.md" "$T/workflows/"
cp "$ROOT/src/mint/adapters/"*.md "$ROOT/src/mint/adapters/alpaca_paper_stub.py" "$T/adapters/"
rm -f "$T/adapters/__init__.py"
cp "$ROOT/src/mint/journal/"* "$T/journal/"
cp "$ROOT/src/mint/strategies/"* "$T/strategies/"
cp "$ROOT/scripts/"*.sh "$T/scripts/"
chmod +x "$T/scripts/"*.sh
cat > "$T/README.md" << 'EOR'
# MINT — lab mirror (`trading/`)

**SoT:** https://github.com/GdotAiM/mint-agent  
Sync with `mint-agent/scripts/sync_to_hermes_x.sh` — do not edit this folder by hand. See `SYNC.md`.
EOR
# requirements if present
[[ -f "$ROOT/requirements.txt" ]] && cp "$ROOT/requirements.txt" "$T/"
echo "Synced mint-agent → $T"
