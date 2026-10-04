# "Month 13" = Charter Model 13 — research card (LECTURE NOTES, NOT A DETECTOR SPEC)

**Status:** research card · **unsigned** · bridge only · implementation = labels + annotation
**Not a Core month.** ICT Core Content stops at M12 (`docs/CHARTER_ESSENCE.md`). "Month 13" is the
project's label for **Charter Price Action Model 13**, the last Charter lecture.
**Not PAM13.** `pam13` is not, and must not become, a `pam_id` until a signed Slice 0 decides
peer vs bridge (`docs/CHARTER_ESSENCE.md`: "Do not create a PAM13 contract prematurely").

---

## Sources

| Role | Source |
|------|--------|
| Primary | ICT Charter Price Action Model 13 — Charter Lecture On 2022 YouTube Model — https://www.youtube.com/watch?v=kNlySn81dmo (~22:54, published 2024-02-16; chapters: Intro, Charter Model 13, Risk Management, Profit Taking, Timing). Charter playlist position 34/34 (`docs/CHARTER0_CANON.md`). |
| Charter playlist | https://www.youtube.com/playlist?list=PLVgHx4Z63paasvEhegIwtiaGalrQphFg3 |
| Base series (prerequisite) | ICT 2022 Mentorship playlist https://www.youtube.com/playlist?list=PLVgHx4Z63paYiFGQ56PjTF1PGePL3r69s · intro https://www.youtube.com/watch?v=kt6V4ai60fI |
| Secondary (study aids only, never canon) | Spanish summary https://www.youtube.com/watch?v=Uu7Sv7DQw7U · ICT Sharks forum notes · reuploads |

**Provenance of the notes below:** user-supplied summary of kNlySn81dmo
(`docs/review/MODEL13_SOURCE_FROM_USER.md`, 2026-10-04). No transcript of
kNlySn81dmo exists on the box; the review did not watch the lecture. Every line below is
`origin: user_lecture_notes` until checked against the video in a signed Slice 0.

---

## What the lecture is (framing)

The 2022 free YouTube mentorship model, restated/amplified for the Charter as "Model 13";
described as the last foundational model, with the 2022 series as its prerequisite.

## Lecture logic (notes only)

- **Intent:** trade intraday structure toward opposing PD-array objectives
  (bearish → discount arrays; bullish → premium arrays).
- **Windows:** Forex ≈ 07:00–10:00 ET; index futures ≈ 08:30–11:00 ET.
- **Charts:** 5m down to 1m after a liquidity raid + short-term MSS.
- **Bearish:** buy-side raid → rapid MSS below recent 5m–1m low + FVG (ideal).
  **Bullish:** sell-side raid → MSS above recent 5m–1m high + FVG.
- **FVG preference:** at/above EQ (bearish), at/below EQ (bullish).
- **Entry:** limit into FVG. **Risk:** ≤ ~2% equity, stop relative to setup structure.
- **Targets:** opposing PD arrays, prior session high/low, prior day high/low, FVGs beyond those.
- **Timing (indexes):** 08:30 news embargo, 09:30 open, ~10:00 sentiment/Judas, 10:30 opening
  range, 11:00 reversal days; PM ≈ 13:30–14:00.

Note for Hermes governance: the ≤~2% equity figure is lecture content, **not** an FTN cap.
`config.yaml risk_caps.max_trade_risk_pct: 0.5` stands and cannot rise without a human.

---

## Glossary → contract fields (`src/ftn/os/m13_contracts.py`)

Single switch (already existed in `pam_contracts.CharterState`; extended, not duplicated):

```
model13_bridge: present | none        # explicit literal "present" only; default none
```

Optional card beside it (`CharterState.model13: Model13Card | None`), all `present | none`
except `direction`:

### Required notes (card is "required_notes_complete" only when all present)

| Field | Lecture note it labels |
|-------|------------------------|
| `direction` | bullish \| bearish \| none |
| `opposing_pd_objective_note` | draw toward opposing PD array (bearish→discount, bullish→premium) |
| `time_window_note` | FX 07:00–10:00 ET / index 08:30–11:00 ET |
| `liquidity_raid_note` | buy-side (bearish) / sell-side (bullish) raid |
| `short_term_mss_note` | MSS through recent 5m–1m low/high after the raid |
| `fvg_entry_note` | FVG from the displacement; limit entry into it |
| `risk_frame_note` | stop relative to setup structure; lecture's ≤~2% equity framing |

### Confirming notes (never required, never minting)

| Field | Lecture note it labels |
|-------|------------------------|
| `fvg_eq_side_note` | FVG at/above EQ (bearish) / at/below EQ (bullish) |
| `ltf_refinement_note` | 5m → 1m refinement |
| `target_ladder_note` | prior session H/L, PDH/PDL, FVGs beyond |
| `index_timing_note` | 08:30 / 09:30 / 10:00 / 10:30 / 11:00 / PM 13:30–14:00 |

The required/confirming split is a `hermes_interpretation` of the notes ("FVG (ideal)" could
argue FVG is confirming; it is required here because the entry is a limit into the FVG).
Slice 0 must confirm or correct it.

---

## Frozen boundary

- `model13_bridge == "present"` requires explicit identification. A complete card does **not**
  mint it; `True`, `"yes"`, `"pam13"` do not mint it.
- Model 13 never enters `recognized_pams`, never sets `charter_recognition`, never ranks.
- No `session_ticket`, no `paper_swing`, no M9 candidate, no MINT draft from Model 13.
- No detector: nothing derives these notes from bars. They are hand labels.
- Legacy `ftn run` payload shows a Model 13 annotation only if `model13_bridge_enabled: true`
  (default false); computed after the ticket, so it cannot change it.
- Tests: `tests/test_model13.py`. Fixture: `fixtures/m13_bridge_eurusd.json` (synthetic labels).

## Open — needs a signed Model 13 Slice 0

1. Peer (would require adding `pam13`) vs bridge (current). Decide against the lecture.
2. Verify every note above against kNlySn81dmo (timestamps), replacing `user_lecture_notes`.
3. Map 2022 Mentorship episodes (base rules) vs what the Charter lecture amplifies.
4. Decide whether the Model 13 chain (raid → MSS → FVG) should reuse M9's derived
   `raid` / `mss` evidence read-only, or stay label-only.
