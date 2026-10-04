# Source Map

| Source | Location | Owner | Notes |
|--------|----------|-------|-------|
| ATLAS | Live agent → ORION | Market Intelligence | Structure, liquidity, session behaviour |
| QUANT | Live agent → ORION | Quantitative Research | Experiments, falsification, metrics |
| CASSANDRA | Live agent → ORION | Research Red Team | Attack findings; severity-rated |
| MACRO | Live agent → ORION | Macro Intelligence | Material macro context only |
| HISTORIAN | Live agent → ORION | Market Historian | Analogues + outcome distributions |
| DATA | Live agent → ORION | Data Quality | Dataset trust / integrity gates |
| RISK | Live agent → ORION | Portfolio Risk | Paper risk gates; $100k / 0.5% / 2% / 5% |
| FORGE | Live agent → ORION | Systems Architect | Workflow & architecture evaluation |
| MERCURY | Live agent → ORION | Paper Portfolio Mgr | Timestamped decisions + daily audit |
| Human (Ntloso) | Chat / uploads | Researcher | Final approval; live capital authority |
| FTN (Filling The Numbers) | `ftn/` → `ftn/dispatch/out/handoff_latest.json` (handoff.v1) | DayContext producer (paper-first ICT daily-range engine) | Filed as evidence via `research/scripts/file_ftn_handoff.py` → `evidence/ftn/`; forex-first (EURUSD, some XAUUSD); fixtures are hand-labelled, not tape |
| Local ledger | `/home/box/hermes-x` | ORION | Beliefs, investigations, summaries |

Connectors (GitHub, Drive, etc.): deferred.
