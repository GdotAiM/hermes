# Screening pipeline (research only)

This pipeline runs cheap screens that rank hypotheses **before** any holdout is spent. Protocol: `PROTOCOL.md`, v1, registered before batch 1.

- `dl.py`: downloads S1 data from Dukascopy (BID+ASK) for GER40, US30 and XAUUSD only, UTC days 2023-01-01..2026-09-25 only, into `$SCREENING_DATA`. The window and instrument guards are hard-coded.
- `instruments.py`: protocol §2 scaling rules. Specs are registered at runtime; no pinned file is edited.
- `core.py`: runs REV unchanged on a BID/ASK pair; cluster bootstrap; Holm.
- `nulls.py`: S3 null generators (shuffled-day block bootstrap; matched-volatility random walk).
- `s4_h016b.py`: S4 stub. It reads H016b sealed outputs only after DATA and CASSANDRA clearance; nothing is read now.
- `batch1.py`: batch 1 (C1/C2/C3). Outputs go to `batch1/`.

Run from the repo root with `PYTHONPATH=ftn/src:.` and numpy available:

    python3 -m research.screening.dl download 64 && python3 -m research.screening.dl build
    python -m research.screening.batch1 s3 && python -m research.screening.batch1 s1 && python -m research.screening.batch1 report
    python -m pytest research/screening/tests

## Batch 2 (Model U v1, MMXM v1–v5)
- Protocol addendum: `PROTOCOL_BATCH2.md` (committed `0a3b052` before any run).
- Frozen code is vendored and sha-pinned in `batch2/vendor` and `batch2/configs`; `batch2/adapters.py` runs it.
- Run: `PYTHONPATH=ftn/src:. python -m research.screening.run_batch2 {burned|s1|s3|report}`.
- Results are in `batch2/REPORT.md` and `batch2/results.json`. Nothing qualifies.

## Batch 3 (simple rules E1–E5)
- Protocol addendum: `PROTOCOL_BATCH3.md` (committed `6389802` before any data read).
- Rules: `batch3/rules.py`.
- Run: `python -m research.screening.run_batch3 {burned|s1|s3|report}`.
- Results: `batch3/REPORT.md`. Nothing qualifies.
