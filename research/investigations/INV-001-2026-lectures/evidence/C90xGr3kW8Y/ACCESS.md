# ACCESS — C90xGr3kW8Y

**Status:** AVAILABLE — video QA completed 2026-09-13 for priority Observed cards  
**Checked:** 2026-09-13 by DATA  
**Blocker:** none for metadata / auto-captions. Full chart-frame visual QA not completed in this pack.

## How obtained
| Step | Method | Result |
|------|--------|--------|
| Playlist membership | yt-dlp flat-playlist on `PLVgHx4Z63paaja3GW0dYSr6y_V2Sttx4-` | Present at position 112; channel ICT |
| Video metadata | yt-dlp `--skip-download` | Title, channel, upload_date 20260311, duration 1660s, URL |
| Captions | yt-dlp `--write-auto-sub --sub-lang en` | Saved `auto_captions.en.vtt` in this folder |
| Official manual captions | yt-dlp `--list-subs` | Auto-captions listed (`en`, `en-orig`); treat as **ASR**, not author transcript |
| Full video download / watch | Not required for DATA register; deferred | Chart OHLC / on-screen instrument still need human or watchVideo QA for tight Observed quotes |

## Files in this pack
| File | Role |
|------|------|
| `META.md` | Source register fields |
| `ACCESS.md` | This file |
| `SEGMENTS.md` | Timestamp stub for ATLAS — empty until extract |
| `auto_captions.en.vtt` | YouTube **automatic** English captions — discovery aid only |
| `lecture.mp4` | Local copy of lecture for DATA timestamp/instrument QA (research ledger; YouTube ToS) |

## License / TOS / disclosure
- YouTube ToS applies; do not redistribute mirrored lecture media outside research ledger needs.
- Video description is CFTC Rule 4.41 / hypothetical performance disclaimer — not trading advice; HERMES-X remains concept research / paper only.
- Captions are machine-generated; expect errors (numbers, ticker names, “ET” vs “east”).

## Blockers
| Item | Status |
|------|--------|
| Playlist / video URL reachable | Clear |
| Metadata | Clear |
| Auto-captions | Clear (partial fidelity) |
| Authoritative human transcript | Missing (optional per CAPTURE_STANDARD) |
| On-screen instrument + TF confirmation | **Open** — ATLAS/DATA visual QA before any instrument-specific Observed Pass |
| Lecture-aligned OHLC tape | **Missing** (org-wide) — does not block claim *extraction*; blocks QUANT |

## Rules for downstream
1. **Primary** = this video on official channel. Taxonomy / student notes = map only.
2. Observed claims require timestamp (HH:MM:SS–HH:MM:SS) + video_id; ASR line alone → Hold until spot-check.
3. Do **not** invent Observed session bounds from taxonomy.
4. Event talk (e.g. CPI mentioned in ASR open) → set `Event-conditioned` correctly; keep MACRO track separate unless lecture conditions the session claim.

## Ready signal
Pilot pack is **READY** for ATLAS claim extraction under CAPTURE_STANDARD (≤15 cards, quality > quantity). DATA will gate cards after extract.

## ORION confirmation (2026-09-13)
- **Pilot ASR path:** `auto_captions.en.vtt` in this folder — confirmed as the caption source for ATLAS G1→caption pass.
- Caption-based CLAIM_CARDs: DATA stamps **Hold** until timestamp spot-check; **no Pass Observed on ASR alone**.
- Policy file: `DATA_ASR_POLICY.md`
- QUANT HOLD unchanged.

## Video QA in progress (2026-09-13)
- Local `lecture.mp4` obtained for DATA timestamp/instrument spot-check (priority Observed 001–006, 009).
- watchVideo pass running; gates remain Hold until that result is filed.

## Video QA complete (2026-09-13)
- Local `lecture.mp4` + `frames/` used for timestamp/instrument spot-check.
- watchVideo speech confirmations for 001–006/009 accepted; **rejected** watchVideo instrument date Mar 2024 and price ~18k (frames+ASR show Mar 2026 and ~25k).
- Open QA on instrument/TF closed for this pack.
