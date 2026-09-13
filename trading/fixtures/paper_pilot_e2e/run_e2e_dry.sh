#!/usr/bin/env bash
export HERMES_X_PATH="${HERMES_X_PATH:-}"
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
echo "== 1. Scan hermes-x (if present) =="
if [[ -n "${HERMES_X_PATH:-}" && -d "${HERMES_X_PATH}/summaries" ]]; then
  PYTHONPATH=src python3 -m mint.dispatch.scan_clears --hermes-x "$HERMES_X_PATH" --apply-filters || true
else
  echo "HERMES_X_PATH unset — skipping scan"
fi
echo "== 2. Validate fixture stamp =="
test -f fixtures/paper_pilot_e2e/HUMAN_PAPER_PILOT_STAMP.md
echo "== 3. Dry-run order (no --submit) =="
PYTHONPATH=src python3 -m mint place_order --symbol QQQ --qty 1 --side buy
echo "== 4. Write journal stub =="
OUT=fixtures/paper_pilot_e2e/LAST_JOURNAL.md
cp src/mint/journal/_TEMPLATE_DECISION.md "$OUT"
printf '\n## Fixture run\n- DECISION: PASS (dry-run pipe test)\n- STAMP: fixtures/paper_pilot_e2e/HUMAN_PAPER_PILOT_STAMP.md\n' >> "$OUT"
echo "E2E dry-run OK → $OUT"
