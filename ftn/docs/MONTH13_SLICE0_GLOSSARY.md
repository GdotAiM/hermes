# Model 13 Slice 0 — glossary (PROPOSED, UNSIGNED)

Sign or correct before Model 13 is treated as anything but a bridge.
Source card: `docs/MONTH13_RESEARCH_CARD.md` (user-supplied notes on kNlySn81dmo).

```
model13_bridge: present | none          # existing CharterState field; explicit only
model13_context:                        # optional labeled card (evidence or charter block)
  direction: bullish | bearish | none
  required:
    opposing_pd_objective_note | time_window_note | liquidity_raid_note
    short_term_mss_note | fvg_entry_note | risk_frame_note      : present | none
  confirming:
    fvg_eq_side_note | ltf_refinement_note | target_ladder_note
    index_timing_note                                           : present | none
```

Not in this glossary on purpose: `pam13`, any score/fit %, any ticket kind, any detector
threshold, any time constant in code.

Signature: ______ (human) · date ______ · decision: bridge | peer
