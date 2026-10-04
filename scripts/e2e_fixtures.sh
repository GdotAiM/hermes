#!/usr/bin/env bash
# HERMES monorepo E2E on fixtures (paper only, no network, no orders):
#   FTN brief from a fixture → handoff.v1 contract check → MINT board scan →
#   MINT read-only FTN DayContext reader → Desk adapter acceptance test → how to open the Desk.
#
# Usage (repo root):  scripts/e2e_fixtures.sh            # or: make e2e
#   FIXTURE=fixtures/pam1_evidence_eurusd.json scripts/e2e_fixtures.sh
#   E2E_TESTS=1 scripts/e2e_fixtures.sh                  # also run ftn/ + trading/ pytest (needs pytest)
# Note: clears ftn/dispatch/out/*.json first (git-ignored scratch, incl. FTN's persisted
# session/swing tickets) so the run is reproducible. Committed samples are untouched.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${PYTHON:-python3}"
FIXTURE="${FIXTURE:-fixtures/m9_reconstruction_eurusd.json}"
step() { printf '\n== %s ==\n' "$*"; }

step "0. environment"
echo "repo:    $ROOT"
echo "python:  $($PY --version 2>&1)"
echo "fixture: ftn/$FIXTURE"

if [[ "${E2E_TESTS:-0}" == "1" ]]; then
  step "0b. test suites"
  rm -f "$ROOT"/ftn/dispatch/out/*.json
  (cd "$ROOT/ftn" && $PY -m pytest -q -p no:cacheprovider)
  (cd "$ROOT/trading" && $PY -m pytest -q -p no:cacheprovider)
fi

step "1. FTN brief (ftn brief --fixture $FIXTURE)"
rm -f "$ROOT"/ftn/dispatch/out/*.json
(cd "$ROOT/ftn" && PYTHONPATH=src $PY -m ftn brief --fixture "$FIXTURE" \
    --out dispatch/out/e2e_BRIEFING.md >/dev/null 2>"$ROOT/ftn/dispatch/out/e2e_brief.log")
HANDOFF="$ROOT/ftn/dispatch/out/handoff_latest.json"
test -s "$HANDOFF" || { echo "FAIL: no handoff written"; cat "$ROOT/ftn/dispatch/out/e2e_brief.log"; exit 1; }
echo "brief:   ftn/dispatch/out/e2e_BRIEFING.md ($(wc -l < "$ROOT/ftn/dispatch/out/e2e_BRIEFING.md") lines)"
echo "handoff: ftn/dispatch/out/handoff_latest.json"
$PY - "$HANDOFF" <<'PYEOF'
import json, sys
h = json.load(open(sys.argv[1])); ms = h["market_state"]
sel = [c["module"] for c in h["candidates"] if c["state"] == "selected"]
print(f"  {h['kind']} v{h['schemaVersion']} {h['symbol']} {h['date']} session={h['session']} profile={ms['profile']}")
print(f"  candidates={[(c['module'], c['state']) for c in h['candidates']]} selected={sel or 'none'}")
print(f"  ftn four={[(l['name'], round(l['price'], 5)) for l in h['ftn_annotation']['four']]}")
print(f"  charter={'present' if ms['charter'] else 'null'} pam1_complete={(ms['pam1_completeness'] or {}).get('required_complete')}")
PYEOF

step "2. handoff.v1 contract (structure + recursive bans)"
(cd "$ROOT/ftn" && PYTHONPATH=src $PY -m ftn.os.handoff_contract "$HANDOFF" dispatch/samples/handoff_v1_*.json)

step "3. MINT board scan (trading: mint.dispatch.scan_clears)"
(cd "$ROOT/trading" && PYTHONPATH=src $PY -m mint.dispatch.scan_clears)
$PY - "$ROOT/trading/dispatch/out/latest.json" <<'PYEOF'
import json, sys
d = json.load(open(sys.argv[1]))
for t in d["tickets"]:
    print(f"  {t['kind']:<16} {t['board_status']:<13} {t['hypothesis_hint']}")
print(f"  entry_candidates={d['entry_candidates']} (still need allowlist + RISK + human; no orders)")
PYEOF

step "4. MINT read-only FTN DayContext reader (mint.dispatch.ftn_context)"
(cd "$ROOT/trading" && PYTHONPATH=src $PY -m mint.dispatch.ftn_context --handoff "$HANDOFF")
$PY - "$ROOT/trading/dispatch/out/ftn_context_latest.json" <<'PYEOF'
import json, sys
r = json.load(open(sys.argv[1])); ex = r["execution"]
assert r["kind"] == "ftn_day_context" and ex["order_intents_emitted"] == 0 and ex["actionable_for_mint"] is False
print(f"  kind={r['kind']} board_gate={r['board_gate']['status']} survives={r['board_gate']['survives']}")
print(f"  order_intents_emitted={ex['order_intents_emitted']} actionable_for_mint={ex['actionable_for_mint']}")
print(f"  paper_limits={r['paper_limits']}")
PYEOF

step "5. Desk DayContext adapter acceptance (node)"
if command -v node >/dev/null 2>&1; then
  node "$ROOT/desk/tests/dayContext.test.mjs"
else
  echo "  SKIP: node not installed (run: node desk/tests/dayContext.test.mjs)"
fi

step "6. open the Desk"
cat <<TXT
  cd "$ROOT" && python3 -m http.server 8765 --bind 127.0.0.1
  open http://127.0.0.1:8765/desk/
  - click EURUSD (synthetic bars) in the left rail
  - FTN DayContext card (right rail): path ../ftn/dispatch/out/handoff_latest.json → Load
    (or pick a sample from the list, or File… for a local handoff JSON)
  - FTN four levels / opens / Asian range draw on the chart; Market State, Charter,
    PAM1, candidates render read-only. Nothing is derived by the Desk.
TXT
echo
echo "E2E OK (paper only; no orders; no network)"
