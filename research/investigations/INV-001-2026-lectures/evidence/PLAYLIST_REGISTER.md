# Primary source register — 2026 ICT SMC playlist
**Investigation:** INV-001  
**Registered by:** DATA  
**Date:** 2026-09-13  
**Status:** REGISTERED (primary catalog)

## SOURCE
| Field | Value |
|-------|-------|
| Type | YouTube playlist |
| Title | 2026 ICT Smart Money Concept Lecture |
| Playlist ID | `PLVgHx4Z63paaja3GW0dYSr6y_V2Sttx4-` |
| URL | https://www.youtube.com/playlist?list=PLVgHx4Z63paaja3GW0dYSr6y_V2Sttx4- |
| Channel | The Inner Circle Trader (`@InnerCircleTrader`) |
| Channel ID | `UCtjxa77NqamhVC8atV85Rog` |
| Verification | yt-dlp 2026-09-13 — 135 entries, 132 titled, 3 empty metadata rows |

## TIMEZONE
- Catalog metadata: YouTube upload timestamps (treat as UTC epoch / `upload_date` YYYYMMDD from yt-dlp).
- Lecture **content** clocks for INV-001 research: **America/New_York (ET)**. EST vs EDT must be recorded per lecture date.
- Do not use taxonomy session windows as Observed clocks.

## GRANULARITY
Playlist item = video ID + title + duration (+ optional per-video `upload_date`).

## DATE RANGE
- Register snapshot: 2026-09-13
- Sampled upload dates on channel content: 2026-01-02 → 2026-09-09 (incomplete matrix; refresh as needed)

## INSTRUMENT
Playlist is not a price series. Demo instruments appear only inside individual lecture packs.

## KNOWN LIMITATIONS
- Titles ≠ claims.
- Taxonomy PDF / student curricula / third-party transcript indexes = **map/secondary only**.
- MOC / Market-On-Close: **no title match** in this playlist inventory (2026-09-13).
- 3 playlist rows with empty metadata (`g2QvEkLbjZI`, `vS9dUFe3eJY`, `qMdHD-JrqOQ`).
- Full inventory: `PLAYLIST_INVENTORY_2026-09-13.txt`
- Gate: `DATA_GATE_2026-09-13.md`

## Pilot
| Field | Value |
|-------|-------|
| Pilot video_id | `C90xGr3kW8Y` |
| Reason | Explicit NY Lunch session-algorithm title; CAPTURE_STANDARD preferred pilot class |
| Pack | `evidence/C90xGr3kW8Y/` |
