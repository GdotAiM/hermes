#!/usr/bin/env bash
# Per-NY-session runner for the H013 + H014 frozen forward tests (HYPOTHETICAL paper research; no orders).
#   watch : start the H013 live-alert watcher (idempotent; flock). Run at 08:55 NY (re-run as a watchdog any time before 11:30 NY).
#   final : H014 final (needs >= 11:00 NY) then H013 final (needs >= 12:00 NY). Run at 12:05 NY.
#   status: tail of today's logs.
set -u
FT=/workspace/ict-blueprint/forward-test; MX=/workspace/mmxm/forward
case "${1:-}" in
  watch)  cd "$FT" && nohup setsid .venv/bin/python h013_live_watch.py >> "h013_live_watch_$(TZ=America/New_York date +%F).log" 2>&1 < /dev/null &
          sleep 3; tail -n 3 "$FT/h013_live_watch_$(TZ=America/New_York date +%F).log" ;;
  final)  rc=0
          (cd "$MX" && ../.venv/bin/python h014_forward.py today) || rc=1
          (cd "$FT" && .venv/bin/python tv_final.py today) || rc=1
          exit $rc ;;
  status) tail -n 5 "$FT/h013_live_watch_$(TZ=America/New_York date +%F).log" 2>/dev/null; tail -n 2 "$FT/h013_forward_log.csv" "$MX/h014_forward_log.csv" 2>/dev/null ;;
  *) echo "usage: $0 watch|final|status"; exit 2 ;;
esac
