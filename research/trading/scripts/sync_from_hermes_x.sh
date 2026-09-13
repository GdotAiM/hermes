#!/usr/bin/env bash
# Emergency: pull lab trading/ into mint-agent working tree (prefer reverse).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_X="${1:-}"
[[ -d "$HERMES_X/trading" ]] || { echo "Usage: $0 /path/to/hermes-x"; exit 2; }
cp "$HERMES_X/trading/ALLOWLIST.md" "$ROOT/ALLOWLIST.md"
cp "$HERMES_X/trading/config.yaml" "$ROOT/config.yaml"
cp "$HERMES_X/trading/AGENT.md" "$ROOT/AGENT.md"
cp "$HERMES_X/trading/workflows/W4_EXECUTION.md" "$ROOT/src/mint/workflows/"
cp "$HERMES_X/trading/adapters/"* "$ROOT/src/mint/adapters/" 2>/dev/null || true
echo "Pulled hermes-x/trading → mint-agent (review + PR). Prefer fixing in mint-agent next time."
