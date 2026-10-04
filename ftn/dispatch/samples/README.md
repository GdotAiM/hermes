# handoff.v1 reference samples

Real FTN output, committed so the contract has fixtures that don't depend on
`dispatch/out/` (which is git-ignored scratch).

| File | Generated from | What it exercises |
|------|----------------|-------------------|
| `handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json` | `fixtures/m9_reconstruction_eurusd.json` | Market State, candidates (REV selected), FTN four levels, opens, Asian range, session_ticket. `charter` / `pam1_*` are `null` in this fixture. |
| `handoff_v1_pam1_evidence_eurusd_2018-01-10.json` | `fixtures/pam1_evidence_eurusd.json` | Charter recognition + PAM1 evidence/completeness. No FTN four levels / opens in this fixture. |

No single FTN fixture carries both PAM1/Charter **and** FTN levels, so there are two samples.
Nothing in them was hand-edited.

Regenerate (from `ftn/`; scratch output goes to a temp dir via `FTN_OUT_DIR`):

```bash
export FTN_OUT_DIR=$(mktemp -d)
PYTHONPATH=src python3 -m ftn brief --fixture fixtures/m9_reconstruction_eurusd.json --out "$FTN_OUT_DIR/brief.md"
cp "$FTN_OUT_DIR/handoff_latest.json" dispatch/samples/handoff_v1_m9_reconstruction_eurusd_2017-05-30_london.json
PYTHONPATH=src python3 -m ftn brief --fixture fixtures/pam1_evidence_eurusd.json --out "$FTN_OUT_DIR/brief.md"
cp "$FTN_OUT_DIR/handoff_latest.json" dispatch/samples/handoff_v1_pam1_evidence_eurusd_2018-01-10.json
PYTHONPATH=src python3 -m ftn.os.handoff_contract dispatch/samples/*.json
```

`fingerprint` is `sha256:` + the first 16 hex chars of SHA-256 over the canonical
(sorted-key) JSON of the DayContext, so it is identical in every process —
no `PYTHONHASHSEED` needed. `tests/test_handoff_contract.py` compares the samples
(fingerprint included) against a fresh regeneration.

Contract: `../schema/handoff.v1.schema.json` (structure) + `ftn.os.handoff_contract`
(structure + recursive bans; authoritative). Tests: `tests/test_handoff_contract.py`.
