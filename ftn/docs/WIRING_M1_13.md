# FTN Months 1–13 wiring (F1–F5, F7) — paper only

Approved changes from the Months 1–13 audit. **No change to which trades REV takes**; the F1 guard proves it.
H016 was superseded pre-data by **H016b** (tag `prereg-H016b`, same rule pins); H015b is WITHDRAWN-PRE-DATA.
No H016b- (or H016-) pinned file is modified (`ftn/tests/test_h016b_prereg.py` and `test_h016_prereg.py` pass);
everything new is in unpinned modules (`ftn/pipeline/`, `ftn/journal/results.py`, `workflow/orchestrator.py`,
`__main__.py`). H016b itself must run from a frozen checkout at its registered **harness tag** (the
`research/forward/H016b/` harness, registered in its own `H016b_HARNESS_REGISTRATION_<date>.json`), never from
this branch.

| ID | What | Where |
|----|------|-------|
| F1 | Ticket-set guard: regenerates H016b's registration inputs (the burned H016 trade CSVs, sha256 checked against the H016b prereg) from the burned tape and asserts byte identity (US100 146/185, US500 112/167), also with the trace on; H016b's eligibility filters (killzone ≥171/180 BID+ASK, entry-1m BID+ASK bar, exit bar in [15:45,16:00)) drop exactly the 4 trades the prereg lists → 254 | `pipeline/invariance.py`, `tests/test_ticket_invariance.py`, `ftn guard [--trace]` |
| F2 | `ftn run --fixture <DTR fixture>` goes through the Month 9 kernel (same path as `ftn brief`); legacy run-packs are labelled `legacy_four_count` | `workflow/orchestrator.py` |
| F3 | Per-ticket trace `ftn.trace.v1`: bias → context → setup → ticket → gates → result, each layer labelled with role (`filter`/`decide`/`eligibility_only`/`annotate`) and `feeds_rev` | `pipeline/trace.py`, `pipeline/kernel_trace.py`, `ftn trace` |
| F4 | Months 5/6/7/12 + `features` computed from bars (causal, ≤ entry close) as context only | `pipeline/layers_bar.py` |
| F5 | Williams %R from the prior-evening m15 bars under its own key `W%R_prior_evening`; the kernel's `sentiment.indicator` is untouched | `pipeline/layers_bar.py` |
| F7 | Forward paper results journal; any date after 2026-09-25 is `sealed_pending_cassandra_data_clearance` and its outcome is never computed until a human-signed stamp naming only H016b with `CASSANDRA: CLEARED` and `DATA: CLEARED` is supplied (H016/H015b stamps never open it) | `journal/results.py`, `ftn results` |

The trace is built by re-running the same causal `kernel_step` at the ticket's entry time and checking that the
MarketState fingerprint equals the logged one (`TraceMismatch` otherwise). Context lives only in the trace, never
in DayContext / evidence / handoff, so the fingerprint and the CSV bytes are unchanged.

Data: burned window 2025-08-25 → 2026-09-25 only (`FTN_GUARD_DATA_DIR`, default `/workspace/ftn-demo-output/data`;
tape tests skip when it is absent).
