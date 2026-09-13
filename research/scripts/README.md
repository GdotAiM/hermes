# HERMES-X scripts

## `ingest_youtube.py`

YouTube → INV evidence pack (RAW). Does not triage or promote.

```bash
pip install yt-dlp   # if needed
python3 scripts/ingest_youtube.py 'https://youtu.be/VIDEO_ID' \
  --hermes-x . \
  --investigation INV-002-methodology-seed
```

Writes `investigations/<INV>/evidence/<video_id>/` (META.md layout matching lab packs)
and `evidence/intake_tickets/intake_<id>_<stamp>.json` for ATLAS triage queue.
