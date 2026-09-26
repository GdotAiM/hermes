# HERMES Desk (`desk/`)

> Part of the [GdotAiM/hermes](../README.md) monorepo (imported with full history from the former standalone repo `GdotAiM/hermes-desk`). Siblings: [`../research/`](../research/) (board locks / LEDGER) and [`../trading/`](../trading/) (MINT).

Premium dark-terminal charting prototype for ICT / SMC traders. Vanilla HTML/CSS/JS — no build step, no npm.

## Open locally

Serve from the **monorepo root** so the desk can read sibling research / MINT files by relative URL:

```bash
cd hermes            # monorepo root
python3 -m http.server 8765
```

Then open [http://localhost:8765/desk/](http://localhost:8765/desk/).

(Serving from `desk/` alone also works for the chart, but relative paths to `../research/` and `../trading/` will 404.)

Any static server works (`npx serve`, VS Code Live Server, etc.). Opening `index.html` via `file://` may work in some browsers but a local server is preferred for module scripts.

## Layout

| Path | Role |
|------|------|
| `index.html` | Shell layout |
| `styles.css` | Design system |
| `js/data.js` | Synthetic NQ-like OHLC |
| `js/chart.js` | Canvas candlestick engine |
| `js/overlays.js` | ICT session / PDH / FVG overlays |
| `js/app.js` | UI wiring |
| `DESIGN.md` | Product principles & roadmap |

## Monorepo wiring

| Desk feature | In-repo source (relative to `desk/`) |
|---|---|
| Research context / board-status chip (Slice J/K) | Research JSON input accepts relative paths, e.g. `../research/<path>.json`. Board locks live in `../research/summaries/*_BOARD_LOCK.md`. |
| MINT dispatch tickets | `../trading/dispatch/out/latest.json` (written by `python3 -m mint.dispatch.scan_clears` from `trading/`) |
| Paper ticket → MINT (Slice H) | Reference `mint://desk?...` → MINT Path B in `../trading/` (see `../trading/ALLOWLIST.md`, `../trading/fixtures/paper_pilot_e2e/`) |
| CSV tape | any relative path, e.g. under `../research/investigations/…` (large CSVs are git-ignored) |

No code fetches GitHub raw URLs or sibling repos; all references are same-origin relative paths.

## Notes

- Connection pill shows **Paper research** — this is not a live broker.
- Paper ticket button is intentionally disabled.
- Data is synthetic and session-aware (Asia / London / NY), for UI research only.

## Continuing the build

If chat cuts off, open [`BUILD_BLUEPRINT.md`](BUILD_BLUEPRINT.md) and [`STATUS.md`](STATUS.md) — next slice is listed there.
