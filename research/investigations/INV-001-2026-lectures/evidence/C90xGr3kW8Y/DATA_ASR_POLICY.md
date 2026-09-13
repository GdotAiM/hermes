# DATA ASR policy — pilot C90xGr3kW8Y
**Date:** 2026-09-13  
**Owner:** DATA  
**ORION confirm request:** acknowledged

## Pilot ASR path (confirmed)
| Field | Value |
|-------|-------|
| Path | `evidence/C90xGr3kW8Y/auto_captions.en.vtt` |
| Kind | YouTube **automatic** English captions (ASR) |
| Size (2026-09-13) | 218109 bytes |
| Role | Discovery / draft segment aid for ATLAS caption pass |
| Not | Official ICT transcript; not sufficient alone for **Passed Observed** |

## Gate rule (caption-based cards)
1. Any claim sourced primarily from `auto_captions.en.vtt` → **DATA gate = Hold** until timestamp spot-check against the video (player/watch QA).
2. Do **not** Pass Observed on ASR alone.
3. After spot-check: Pass only if quote/paraphrase is findable at cited `HH:MM:SS–HH:MM:SS` on the actual lecture.
4. Title-only / G1 provisional cards remain **not Passed** (already provisional).
5. **QUANT HOLD** unchanged (no lecture-aligned OHLC tape + no Passed Observed).

## Spot-check minimum (to lift Hold → Pass)
- [ ] Video playable or equivalent visual/audio access
- [ ] Timestamp verified in-video
- [ ] Instrument/TF on screen noted if claim is instrument-specific
- [ ] ASR errors corrected in quote field if needed
