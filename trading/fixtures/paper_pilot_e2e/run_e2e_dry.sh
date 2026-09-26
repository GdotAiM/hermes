#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"
# Monorepo default: research spine is ../research next to trading/.
if [[ -z "${HERMES_X_PATH:-}" && -d "$ROOT/../research/summaries" ]]; then
  HERMES_X_PATH="$(cd "$ROOT/../research" && pwd)"
fi
export HERMES_X_PATH="${HERMES_X_PATH:-}"

echo "== 1. Scan research spine (${HERMES_X_PATH:-unset}) =="
if [[ -n "${HERMES_X_PATH}" && -d "${HERMES_X_PATH}/summaries" ]]; then
  PYTHONPATH=src python3 -m mint.dispatch.scan_clears --hermes-x "$HERMES_X_PATH" --apply-filters
  test -f dispatch/out/latest.json
  echo "scan OK → dispatch/out/latest.json"
elif [[ "${REQUIRE_HERMES_SCAN:-}" == "1" ]]; then
  echo "ERROR: REQUIRE_HERMES_SCAN=1 but HERMES_X_PATH missing or has no summaries/" >&2
  echo "  HERMES_X_PATH='${HERMES_X_PATH}'" >&2
  exit 1
else
  echo "HERMES_X_PATH unset — skipping scan (set REQUIRE_HERMES_SCAN=1 to fail instead)"
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
