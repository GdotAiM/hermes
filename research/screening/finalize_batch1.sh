#!/usr/bin/env bash
# Wait for the S1 download, retry failures once, build the CSVs, then run S1 and the report (local only; no git push).
set -euo pipefail
cd "$(dirname "$0")/../.."
while pgrep -f "research.screening.dl download" >/dev/null; do sleep 60; done
python3 -m research.screening.dl download 32
python3 -m research.screening.dl build
PYTHONPATH=ftn/src:. ${PY:-/workspace/cb-venv/bin/python} -m research.screening.batch1 s1
PYTHONPATH=ftn/src:. ${PY:-/workspace/cb-venv/bin/python} -m research.screening.batch1 report
echo FINALIZED "$(date -Is)"
