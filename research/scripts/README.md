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


## `file_ftn_handoff.py`

Files an FTN handoff.v1 DayContext as evidence under `evidence/ftn/` (validates the contract,
copies byte-for-byte, appends a provenance row to `evidence/ftn/INDEX.md`). `--origin` is
required (`fixture` | `historical_tape` | `live_observation`). See `evidence/ftn/README.md`.
