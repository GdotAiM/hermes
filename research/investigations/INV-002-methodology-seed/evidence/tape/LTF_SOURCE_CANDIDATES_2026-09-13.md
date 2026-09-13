# Low-timeframe data candidates (keyless / low-friction)
**Filed:** 2026-09-13 · ORION / DATA scout

## Already in ledger
| Stream | Granularity | Keyless? | Use |
|--------|-------------|----------|-----|
| `FREE_YF_NQ` | 1wk / 1d / 1h | Yes | Wave 2 H008–H010 only |

## Ranked candidates for Stream C / Wave 1

### 1. Kaggle — NQ Futures 1min Bar 2022–2025 (BEST FREE BULK)
- URL: https://www.kaggle.com/datasets/tgtanalytics/nq-futures-1min-bar-2022-2025
- ~1.05M rows, Dec 2022 → Dec 11 2025, RTH+ETH claimed, ET timestamps in docs
- Keyless download needs **Kaggle account + API token** (free) or manual UI download
- **Gap:** ends Dec 2025 — misses 2026 lecture dates (Mar 2026 lunch pilot, Aug 2026 Week Lifecycle)
- License: check Kaggle dataset terms (research use typical)
- **Action:** if you have/create free Kaggle login, we can ingest as STREAM_C_KAGGLE_NQ1M with PASS WITH CONDITIONS

### 2. Kaggle — Nasdaq-CME-Future-NQ (TradingView-derived multi-TF)
- URL: https://www.kaggle.com/datasets/youneseloiarm/nasdaq-cme-future-nq
- Includes `NQ_in_1_minute.csv` + 15m/etc.
- Shorter / TV-sourced — provenance weaker than exchange capture
- Same: Kaggle login for download

### 3. Databento / dbn-cache (NOT keyless)
- https://github.com/azizuysal/dbn-cache · https://databento.com
- True CME `ohlcv-1m` for NQ/MNQ including contract months (e.g. Mar 2026)
- Needs API key; free credits may exist for new accounts — **not** keyless
- Best quality for lecture-aligned Mar 2026 if you authorize a free Databento signup

### 4. TradingView
- Chart CSV export: **paid plan feature** (not Basic) — https://www.tradingview.com/support/solutions/43000537255-how-to-export-chart-data/
- CME real-time often needs separate exchange add-on
- Manual path: you export loaded bars → drop CSV into `evidence/tape/` → DATA gates
- **Do not** scrape TV (ToS). No public free TV market-data API for bots

### 5. Yahoo / yfinance
- Already used: daily/hourly only at useful depth — **not** 1m futures

## GitHub scout note
Public GitHub search did **not** surface a maintained keyless CME NQ/MNQ 1m dump comparable to Kaggle. Taiwan futures 1m dumps exist but wrong market.

## ORION recommendation
1. **Immediate:** you download Kaggle NQ 1m (2022–2025) → we gate as exploratory Stream C-lite for H001b/H003c out-of-sample **pre-2026**.
2. **Lecture-aligned 2026:** Databento free trial **or** TradingView paid export of MNQ/NQ 1m covering Mar 10–11 2026 + Aug 2026 Week Lifecycle week.
3. Keep FREE_YF for Wave 2 HTF.

## Explicit rejects
- Scraping TradingView / TradingView Pine “data export” bots
- Undocumented Discord “NQ tick” zips without license

## Scout confirmation (executor, 2026-09-13)
Kaggle tgtanalytics set confirmed CC0; Databento best quality with credits; QC cloud cross-check; avoid TV scrapers and gitignored “data in README” repos.
Kaggle ingest: **auth skipped by user** — proceed Wave 2 H009b on FREE_YF; revisit Kaggle when credentials provided.
