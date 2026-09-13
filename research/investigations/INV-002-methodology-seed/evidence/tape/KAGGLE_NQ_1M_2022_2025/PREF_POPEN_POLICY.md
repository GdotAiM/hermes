# Pref / Popen policy — CONTINUOUS-KAGGLE-NQ1M
**Tied to:** H001b (`QUANT_H001b_RTH_ORG_CE_PROTOCOL_2026-09-13.md` §2.1–2.2)  
**Stream:** KAGGLE_NQ_1M_2022_2025  
**Status:** DATA locked 2026-09-13

| Symbol | Definition on this tape |
|--------|-------------------------|
| Pref / \(P_{ref}\) | Close of bar with ET timestamp minute **16:14** on prior session |
| Popen / \(P_{open}\) | Open of bar with ET timestamp minute **09:30** |
| CE | Midpoint \((P_{ref}+P_{open})/2\) with tick-rounding per H001b R1 |

## Exclusions (primary)
- Prior session US holiday or CME equity-index **early close**
- Missing 16:14 bar on prior session
- Missing 09:30 bar on day \(D\)
- Sundays / empty sessions

## Coverage reporting required
- \(N_{eligible}\), \(N_{excl,holiday}\), \(N_{excl,early}\), \(N_{excl,missing\_1614}\), \(N_{excl,missing\_0930}\)
- Spot-check log: ≥10 random eligible days with Pref/Popen prints recorded

## Labels
Every run: `CONTINUOUS-KAGGLE-NQ1M` · roll undocumented · not MNQ Mar 2026
