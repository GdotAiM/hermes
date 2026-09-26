# HERMES Desk — build status
**Updated:** 2026-09-26
**Next slice:** (none — all blueprint slices built; see "Fix pass" and "Known limitations")
**Resume:** see `BUILD_BLUEPRINT.md`

Paper research only. All chart data is synthetic (or a user-supplied CSV). No live data, no broker routing.

| Slice | Status | Commit(s) |
|-------|--------|-----------|
| A Persist prefs | DONE | in 69435b8 / follow-ups |
| B Keyboard shortcuts | DONE | eddaa15 |
| C PNG export | DONE | 5e9601f |
| D Multi-symbol | DONE | 38dedcb |
| E Sticky drawings | DONE (persistence was missing until the 2026-09-26 fix pass) | b5b94b2, 48c4be2 |
| F Replay scrub | DONE (future-bar hiding added 2026-09-26) | 1e44e67, 8edf4bb |
| G Real tape adapter | DONE | 1ef1b5b |
| H Paper ticket → MINT | DONE (modal was stuck open on load until 2026-09-26) | c7b277e, 181bca1 |
| I 2-up layout | DONE (was broken — single/blank chart — until 2026-09-26) | 653ba96, 31ae054, f43c1b9 |
| J HERMES-X research contract | DONE (board-lock .md support 2026-09-26) | 0d7519b, c7cb63d |
| K Wire board-status chip | DONE | 0e4243d, 181bca1, c7cb63d |

## Fix pass — 2026-09-26 (headless-Chromium screenshot audit)
Earlier "DONE" marks for E, F, H, I, J were optimistic: a Playwright audit found these defects, now fixed.

| # | Defect found | Fix | Commit |
|---|--------------|-----|--------|
| 1 | `.modal-overlay{display:flex}` beat `[hidden]` → paper ticket covered the UI on load and Esc / ✕ / backdrop could not close it | global `[hidden]{display:none!important}` | 181bca1 |
| 2 | Board-status chip (`display:inline-flex`) rendered empty before research loaded | same rule; chip reset on clear / failed load | 181bca1, c7cb63d |
| 3 | 2-up: CSS hid both stages; chart B only built at page load → blank on live toggle, one chart after reload; B was an unrelated random path | both stages flex side by side; chart B created lazily; B = chart A resampled to next-higher TF (`resampleSeries`); per-chart tag | 31ae054, f43c1b9 |
| 4 | Long/short levels were memory-only (lost on reload) | localStorage `hermes-desk:levels:v1:<sym\|csv:src>:<tf>`; saved on add / drag end / Del | 48c4be2 |
| 5 | `hermesX.js`: `text` scoped to `try{}` but read in `catch{}` → any .md threw "text is not defined" | fixed scoping; parser for `research/summaries/*_BOARD_LOCK.md` (id, date, tape, hypothesis, observed table, survived/failed, Decision → status, next experiment) | c7cb63d |
| 6 | Left rail (88px) overflowed; focusing an input scrolled TF / tools / toggles out of view | rail 120px, wrapped input groups, `overflow-x:hidden` | b446cea |
| 7 | Replay: never hid future bars; playhead invisible off-screen; scrubber max stuck at 400; label "1/480" before use; playhead colour undefined; label over time axis | reveal-to-playhead, viewport follows, max from load, "—" until used, ✕ exit, header shows playhead bar, label pill in top padding | 8edf4bb |
| 8 | Minors: first time label clipped; Market read static for every symbol; Lab clears out of date vs board; ticket board status ignored research; overlays bled into axis | clamped labels; Market read generated per symbol (synthetic, descriptive); Lab clears = NQ Wave-1 board locks + "no ES/YM hypotheses" note; ticket shows `<STATUS> · <id>`; overlays clipped to plot | 1e67e66, 9149b48 |

**Verified** (headless Chromium 1600×900 @2x, no injected CSS): 21/21 scripted checks pass, zero console errors/warnings, zero failed requests; `desk-check` steps (node --check all modules + index.html refs) pass; `trading/` pytest 6 passed. Screenshots were kept outside the repo.

## Known limitations (honest)
- Data is synthetic (seeded random walk per symbol/TF); prices/levels mean nothing about real markets.
- 2-up on **D** pairs with a *separately generated* 4H path (no lower-TF source to resample from); tagged "separate synthetic path".
- Board-lock parser is format-specific (headings of `_BOARD_LOCK_TEMPLATE.md`); other markdown falls back to the loose key:value draft parser.
- Replay is chart A only; chart B in 2-up always shows all bars.
- ET offset is fixed at UTC-4 (no DST handling) — prototype simplification in `data.js` / `chart.js`.
- Paper ticket is a read-only stub (no order entry) by design; MINT Path B remains human-explicit.
