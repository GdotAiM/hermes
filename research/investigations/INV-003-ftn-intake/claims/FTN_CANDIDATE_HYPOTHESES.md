# FTN candidate hypotheses (for QUANT + CASSANDRA) — no verdicts

Intake list of FTN choices that are **untested** (`hermes_interpretation`,
`hermes_governance` used as if it mattered, or numeric parameters with no recorded
justification). Each is a *candidate*, not a hypothesis: no H-ID, no protocol, no run.
Source pointers are into `ftn/`.

| # | Candidate question | FTN choice today | Where | Provenance label in FTN | Notes for QUANT / CASSANDRA |
|---|--------------------|------------------|-------|-------------------------|-----------------------------|
| FTN-C01 | **Does CONSO actually win?** On consolidation-profile days, does the CONSO fade-to-EQ objective get reached more often than a matched baseline (random entry inside the box, same stop/target geometry)? | CONSO fade_edge → EQ; expansion_inside → opposite side | `docs/HERMES_X_BOUNDARY.md` ("does CONSO win empirically?"), `src/ftn/models/conso.py` | fade-to-EQ = `ict_source`; profile gate = `hermes_interpretation` | FTN's own docs name this as Hermes-X's question. Needs box definition frozen before looking. |
| FTN-C02 | Is the arbiter order (REV execution-ready > CONSO > PIP20 > BB) better than any other order — or than no arbiter (all eligible candidates logged)? | `default_preemption_policy`, REV preempts CONSO when HTF turn confirmed | `docs/MONTH9_BLUEPRINT.md` §7, `src/ftn/os/candidates.py` | `hermes_governance` | Governance choice that silently decides which model gets measured. Compare selected vs suppressed outcomes. |
| FTN-C03 | Does requiring an LTF MSS before REV execution improve REV outcomes vs REV eligibility alone? | MSS = REV execution trigger | `docs/MONTH9_BLUEPRINT.md` §6 | `hermes_interpretation` | Fixture `m9_rev_eligible_no_mss` exists as a labelled case, not a sample. |
| FTN-C04 | Does the profile enum (expansion / consolidation / reversal_watch / continuation / unclear) carry information about the day's range or direction beyond a naive baseline? | Profile routes models | `docs/MONTH9_BLUEPRINT.md` §5, `src/ftn/os/profile.py` | `hermes_interpretation` ("Not an ICT enum") | Overlaps the queued H008 market-state classifier — consider merging. |
| FTN-C05 | Do FTN four-number objectives (pivots / CBDR SDs / Asian SDs / Flout halves) get reached more often than equally spaced placebo levels? Which family, if any? | "Four is a baseline, not a cap"; family = max count then nearest to price | `AGENT.md` §3, `src/ftn/workflow/orchestrator.py`, `src/ftn/engine/levels.py` | family choice rule is uncommented code | Classic level-touch study; needs placebo levels + multiple-family correction. |
| FTN-C06 | Is the 20-pip ATR floor (`min_atr_pips: 20`) a useful NO-TRADE filter, or does it just drop days? | compressed ATR → no trade | `config.yaml` | not labelled | Compare filtered vs unfiltered outcome distributions; pre-register the threshold. |
| FTN-C07 | Is the 8-pip PD-array overlap tolerance meaningful (sensitivity 4 / 8 / 12)? | `overlap_tolerance_pips: 8` | `config.yaml` | not labelled | Parameter with no recorded justification. |
| FTN-C08 | Does refusing "expanded" CBDR (40–<50 pips) London days avoid worse outcomes? | expanded CBDR gate refuses classic | `docs/MONTH8_BLUEPRINT.md`, `docs/MONTH8_40_50.md` | `hermes_interpretation` | Boundary values need sensitivity. |
| FTN-C09 | PIP20: does the ADR-remaining ≥ 20 pips gate change outcomes? | `adr_remaining_lt_20` → ineligible | `src/ftn/models/pip20.py` | `hermes_interpretation` | |
| FTN-C10 | Does one-ticket-per-session (first selected wins) bias which setups get measured vs logging all eligible setups? | `session_ticket` | `src/ftn/os/session_ticket.py` | `hermes_governance` | Selection-bias concern for any later FTN performance claim (CASSANDRA). |
| FTN-C11 | PAM1 completeness: do days with `required_complete: true` differ in outcome from days with missing elements? | PAM1 evidence / completeness | `docs/PAM1_*.md`, `src/ftn/os/pam1_*.py` | recognition only | Recognition ≠ clearance; would need many labelled days. |
| FTN-C12 | Williams %R(10) on 15m as the sentiment input: does it add anything to the Market State read beyond price vs opens? | %R(10) m15 | `src/ftn/os/wr.py` | `ict_source` | ATLAS should confirm the lecture timestamp before QUANT spends time. |

## Cross-cutting cautions (CASSANDRA)
- FTN fixtures are hand-labelled reconstructions of days ICT discussed; any test on them is
  survivorship/selection-biased by construction. Real tests need an unlabelled tape.
- FTN is forex-first (EURUSD pips); Wave 1 tape is NQ points. Do not port pip thresholds to
  index points without a new spec.
- Every candidate above needs a pre-registered baseline; "reached the objective" is not an
  edge without a placebo.
