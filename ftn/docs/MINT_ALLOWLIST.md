# MINT allowlist for FTN entry models

`config.yaml → mint_allowlist` decides gate 4 of the FTN research-draft chain
(`src/ftn/os/mint_draft.py`). Gate 6 (`contract`) then always fails under the frozen
HERMES_INTEGRATION_I0 contract, so even an allowlisted model's draft stays
`actionable_for_mint: false`; the allowlist only records `gates_before_contract_pass`.
Changing that needs a new integration contract, not an allowlist entry. It mirrors HERMES `trading/ALLOWLIST.md`
(https://github.com/GdotAiM/hermes, `trading/ALLOWLIST.md`).

## What is allowlisted today

**Nothing.** `mint_allowlist: []`. HERMES Wave 1 has **zero SURVIVES**
(`trading/ALLOWLIST.md`: "MINT allowlist holds filters + logging only"), and no human
paper-pilot stamp exists for REV / CONSO / BB / PIP20. So every kernel ticket's draft is
`blocked_by: allowlist:not_on_mint_allowlist`. An empty entry allowlist is correct
behaviour, not a bug.

## How a model gets on the list (human only)

Exactly one of:

**Path A — ORION board SURVIVES**

```yaml
mint_allowlist:
  - { id: REV, kind: survives, board_ref: "path/to/<...>_BOARD_LOCK.md" }
```

**Path B — human paper pilot (+ RISK still gates size)**

```yaml
mint_allowlist:
  - { id: REV, kind: paper_pilot, stamp: "docs/pilots/REV_PILOT_STAMP.md", expires: "2026-12-31", kill: "3 consecutive paper losses or 1R drawdown" }
```

Rules enforced by `config_load.validate_config` and `mint_draft.allowlist_gate`:

- `id` ∈ {REV, CONSO, BB, PIP20} (Month 1–8, 10–12, Charter, Model 13 can never be listed).
- `survives` needs `board_ref`; `paper_pilot` needs `stamp`, `expires` (YYYY-MM-DD) and `kill`.
- The referenced file must exist (relative to the repo root, or absolute); an expired pilot is blocked.
- A `paper_pilot` stamp must be **signed**. A `STATUS: UNSIGNED` marker or a blank,
  underscore or `<placeholder>` `Signature:` line blocks with `paper_pilot_stamp_unsigned`.
- Duplicate ids and unknown keys are config errors.
- A pilot must not launder labels: the journal says **pilot**, not SURVIVES.

Use `docs/templates/PAPER_PILOT_STAMP_TEMPLATE.md` for the stamp. Commit the stamp and the
config change together. Never enable live in the same change.


## Prepared, not signed

`docs/pilots/REV_PAPER_PILOT_STAMP_UNSIGNED.md` is a REV paper-pilot stamp prepared for
human signature (2026-10-04). It is **not** referenced by `config.yaml`, and the allowlist
gate would refuse it as unsigned anyway.
