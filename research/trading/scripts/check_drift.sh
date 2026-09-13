#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HERMES_X="${1:-${HERMES_X_PATH:-}}"
[[ -d "$HERMES_X/trading" ]] || { echo "need hermes-x path"; exit 2; }
diff -q "$ROOT/ALLOWLIST.md" "$HERMES_X/trading/ALLOWLIST.md" >/dev/null
diff -q "$ROOT/config.yaml" "$HERMES_X/trading/config.yaml" >/dev/null
diff -q "$ROOT/src/mint/workflows/W4_EXECUTION.md" "$HERMES_X/trading/workflows/W4_EXECUTION.md" >/dev/null
echo "No drift on ALLOWLIST/config/W4"
