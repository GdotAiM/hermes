# FTN DayContext evidence index

Filed by `research/scripts/file_ftn_handoff.py`. One row per distinct handoff (sha256).
`origin` is the provenance label given at filing time: `fixture` = built from an FTN
test fixture (hand-labelled evidence, **not** tape); `historical_tape` / `live_observation`
= built from real market data. Rows are evidence intake, not claims or verdicts.

| filed_at (UTC) | file | origin | symbol | date | session | fingerprint | sha256[:12] | source |
|---|---|---|---|---|---|---|---|---|
| 2026-10-04T06:01:43Z | `handoffs/2017-05-30_EURUSD_london_caaf6b54.json` | fixture | EURUSD | 2017-05-30 | london | 3725971691324029648 | caaf6b54e359 | `ftn/dispatch/samples/handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json` |
| 2026-10-04T06:01:43Z | `handoffs/2018-01-10_EURUSD_nosession_38b42b0a.json` | fixture | EURUSD | 2018-01-10 | — | 2107889760851263150 | 38b42b0a5c8f | `ftn/dispatch/samples/handoff_v1_pam1_evidence_eurusd_2018-01-10.json` |
| 2026-10-04T06:17:00Z | `handoffs/2017-05-30_EURUSD_london_9adddf11.json` | fixture | EURUSD | 2017-05-30 | london | sha256:aa85d1816aa399ac | 9adddf11ec83 | `ftn/dispatch/samples/handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json` |
| 2026-10-04T06:17:00Z | `handoffs/2018-01-10_EURUSD_nosession_c95d4fea.json` | fixture | EURUSD | 2018-01-10 | — | sha256:39727b7637254d7c | c95d4fea0f1d | `ftn/dispatch/samples/handoff_v1_pam1_evidence_eurusd_2018-01-10.json` |
