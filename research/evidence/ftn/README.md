# FTN DayContext evidence (`research/evidence/ftn/`)

Intake point for FTN (`../../ftn/`) **handoff.v1** DayContext snapshots
(`schemaVersion "1"`, `kind "day_context_handoff"`). The research spine consumes FTN
exports; it does not reconstruct FTN state (FTN `docs/HERMES_INTEGRATION_I0.md`).

| Path | What |
|------|------|
| `handoffs/` | Filed handoffs, byte-for-byte copies, named `<date>_<symbol>_<session>_<sha8>.json` |
| `INDEX.md` | One provenance row per filed handoff (origin label, fingerprint, sha256, source path) |

## Filing a handoff

```bash
# from the monorepo root; validates against the contract first (structure + bans)
python3 research/scripts/file_ftn_handoff.py --origin fixture  ftn/dispatch/samples/<file>.json
python3 research/scripts/file_ftn_handoff.py --origin live_observation   # = ftn/dispatch/out/handoff_latest.json
```

`--origin` is required: `fixture` (built from an FTN test fixture — hand-labelled, **not** tape),
`historical_tape`, or `live_observation`. Pick the honest one.

## Rules

- A filed handoff is **evidence intake**, not a claim, a verdict or a clearance. It does not
  touch `beliefs/LEDGER.md` or `summaries/`; ORION decides what (if anything) becomes a
  hypothesis (see `../../investigations/INV-003-ftn-intake/`).
- FTN's `candidates[].state == "selected"`, `session_ticket`, PAM1 completeness and Charter
  recognition are FTN's *reconstruction* of ICT rules on that day. None of them is evidence
  that the rule makes money. Recognition ≠ clearance ≠ execution.
- All rows so far are the committed contract samples — `origin: fixture` (rows 1–2: old salted
  fingerprints; rows 3–4: the same samples regenerated with the deterministic sha256 fingerprint).
- `fingerprint`: rows filed before ftn-fixes carry FTN's old salted `hash()` fingerprint
  (digits only, not reproducible across processes); they are kept as filed. Newer FTN output
  carries `sha256:<16 hex>` over the canonical DayContext, which is deterministic. The file's
  own `sha256` column remains the identity of a filed handoff.
