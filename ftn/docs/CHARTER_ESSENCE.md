# ICT Charter Content — ESSENCE FROZEN

Source: Official ICT playlist
https://www.youtube.com/playlist?list=PLVgHx4Z63paasvEhegIwtiaGalrQphFg3

Description (ICT): “These lectures are my ICT Private Mentorship Charter content.”
34 videos. Last updated Feb 2024.

Prerequisite (ICT sequencing): complete Core Content M1–M12 first.

---

## Placement in Hermes / FTN

```
                    HERMES / FTN
                         │
        ┌────────────────┴────────────────┐
        │                                 │
   CORE CONTENT                        CHARTER
      M1–M12                         PAM1–PAM12
        │                            + Model 13 bridge
 Teaching / context                  Named model
 opportunity annotations             definitions
        │                                 │
        └──────────────┬──────────────────┘
                       ↓
                Charter recognition
                       ↓
                M9 governance
                       ↓
                 session_ticket
```

Core teaches and annotates the vocabulary.
Charter defines and recognizes named models.
**M9 remains the sole session-ticket authority.**

Charter is **not** another sequence of monthly annotations like M10–M12.

---

## Ownership of evidence

Charter may **consume** already-derived Core context.
Charter must **not** recompute, reinterpret, or mutate Core layers.

```
M5 position_opportunity ─┐
M7 paper_swing           ├──→ available context (read-only)
M8 London / day          │
M9 market state          │
M10 multi-asset          │
M11 mega-trade           │
M12 top-down             ─┘
                              ↓
                    Charter PAM recognition
```

M1–M12 own their evidence.
Charter owns model recognition.
M9 owns session selection.

---

## Frozen Charter process

```
Core context / evidence
        ↓
Charter model recognition
        ↓
PAM-X context / evidence   (not a score, not a “fit %”)
        ↓
M9 candidate governance
        ↓
session_ticket
```

Explicitly:

```
PAM recognition ≠ candidate
PAM recognition ≠ ticket
PAM recognition ≠ order
```

Overlapping recognition is valid:

```
PAM3 recognized
PAM9 recognized
PAM12 recognized
```

No Charter-level winner. No ranking / scoring router.

---

## Canon (provisional until Charter 0)

| ID | Focus (from titles / indexes) |
|----|-------------------------------|
| PAM1 | Intraday scalping (PDH/PDL, NY KZ, OTE) |
| PAM2 | Short-term model |
| PAM3 | Swing trading |
| PAM4 | Position trading |
| PAM5 | Day trading — intraday volatility expansions |
| PAM6 | Universal trading model |
| PAM7 | Universal trading model (continued) |
| PAM8 | Targeting ~6% per month |
| PAM9 | One Shot One Kill |
| PAM10 | Swing trading |
| PAM11 | Day trading |
| PAM12 | Scalping intraday model |
| Model 13 | Charter lecture on the **2022 YouTube model** (bridge; schema TBD) |

PAM1…PAM12 = proposed peer model definitions.
Model 13 = bridge/reference until the lecture decides peer vs bridge.
**Do not create a PAM13 contract prematurely.**

---

## PAM9 vs M7 OSOK

| Layer | Role |
|-------|------|
| **M7** | Core teaching of OSOK as weekly/swing process → frozen `paper_swing` governance |
| **Charter PAM9** | Named Charter Price Action Model 9 → recognition / model context only |

They may share vocabulary and underlying evidence.
PAM9 **must not** overwrite M7 `paper_swing` or create a second OSOK ticket.

---

## Frozen-out

- Automatic ticket from any PAM
- PAM ranking / scoring / router
- Second `paper_swing` from PAM9
- Core M1–M12 mutation
- `pair_institutional` mutation
- `session_ticket` emission
- Broker / live routing
- **Inferring a PAM merely because a collection of Core annotations is present**

---

## Implementation shape

```
Charter
  │
  ├── PAM1  ← pilot
  ├── PAM2
  ├── ...
  ├── PAM12
  └── Model13 bridge
```

One Charter process. Many named model definitions. One M9 ticket authority.

---

## Next

1. **Charter 0** — map Models 1–13 → exact lecture URL(s) from the playlist.
2. **Slice 0 glossary** — after canon verification.
3. **No `pam_contracts.py` until Slice 0 is signed.**
4. **PAM1 pilot** only after Slice 0.
