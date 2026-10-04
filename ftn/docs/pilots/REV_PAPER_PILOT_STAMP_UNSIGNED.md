# Paper-pilot stamp — REV (UNSIGNED — prepared by agent, awaiting human signature)

STATUS: UNSIGNED

This stamp was prepared from `docs/templates/PAPER_PILOT_STAMP_TEMPLATE.md`. The factual
fields are filled in. The signature, date and approval fields are blank on purpose. REV is
**not** on `config.yaml → mint_allowlist`. Until a human signs this and adds the allowlist
entry, every REV draft stays `blocked_by: allowlist:not_on_mint_allowlist`.
The allowlist gate also refuses any stamp that still says `STATUS: UNSIGNED` or has a blank
signature line.

- Model id: REV (Month 9 reversal entry model; `src/ftn/models/rev.py`)
- Ticket authority: Month 9 kernel only (`ftn brief` / `ftn run` → session ticket). Months
  1–8, 10–12, Charter and Model 13 are context only and never issue tickets.
- Human: ____________________   Date: ____________________
- Scope: **PAPER ONLY.** Live stays dual-locked (`live_enabled: true` **and** `MINT_LIVE=1`)
  and is out of scope for this pilot. No broker routing. FTN emits drafts only, never orders.
- Instrument: EURUSD (`focus_pair`). No other instrument is in scope.
- Fixture evidence (all from replayed fixtures, none from a live/forward tape). Each one
  reaches a kernel session ticket and passes the kernel_ticket, side, risk and mode gates.
  The only gate that fails is `allowlist:not_on_mint_allowlist`:

  | Fixture | Date (NY) | Side | Entry ref (`last`) | Stop ref | Risk | Size |
  |---|---|---|---|---|---|---|
  | `fixtures/m9_raw_eurusd.json` | 2017-05-30 | buy | 1.1184 | 1.1142 (previous-day low, raided) | $500 (0.5%) | ≈119,048 units |
  | `fixtures/m9_reconstruction_eurusd.json` | 2017-05-30 | buy | 1.1184 | 1.1142 | $500 | ≈119,048 |
  | `fixtures/m9_rev_inside_box.json` | 2017-05-30 | buy | 1.1184 | 1.1142 | $500 | ≈119,048 |
  | `fixtures/m9_calendar_watchlist.json` | 2017-05-30 | buy | 1.1184 | 1.1142 | $500 | ≈119,048 |
  | `fixtures/m9_calendar_idle.json` | 2017-05-30 | buy | 1.1184 | 1.1142 | $500 | ≈119,048 |

  These five are variants of **one** trading day (2017-05-30). That is n = 1 independent
  day, not five samples. No other dated fixture gets a REV ticket from the kernel.
- RISK: caps unchanged. **0.5% per trade, 2% daily loss, 5% max drawdown** on $100,000
  paper equity (`config.yaml`, matching HERMES `trading/` limits). Size is proposed at the
  per-trade cap. The daily-loss and drawdown gates read `dispatch/out/paper_book.json`.
  Nothing writes that file yet (REPORT D13), so those two caps only bite once MINT's paper
  P&L is mirrored into it.
- Kill criteria (any one ends the pilot; remove the allowlist entry the same day):
  1. 3 consecutive losing REV paper trades, **or**
  2. cumulative REV paper loss ≥ 1% of equity ($1,000 = 2R), **or**
  3. any paper day that hits the 2% daily cap, or the book drawdown reaching 5%, **or**
  4. any REV draft marked actionable whose `run`, `brief` and desk status disagree, or
     any attempt to route a live order.
- Expires / review date: **2026-11-04** (30 days after preparation; proposed, and the
  signer may shorten it). An expired pilot is blocked automatically by the allowlist gate.
- Board status at signing: **none — there is no ORION board SURVIVES for REV.** HERMES
  Wave 1 has zero SURVIVES (`trading/ALLOWLIST.md`). This is a human paper pilot (Path B),
  not a validated edge. Journals and drafts must say **pilot**, never SURVIVES.
- Honest caveats:
  - The REV stop reference (the raided previous-day low / named extreme) is a
    `hermes_interpretation`. No lecture source pins it (REPORT D12).
  - The REV origin rule treats any `origin_pd_array` as "HTF PD array at or around the
    raid" (REPORT D7). That was left unchanged and is not independently verified.
  - The arbiter only ever selects REV (REPORT D11). This pilot does not cover CONSO, BB
    or PIP20.
  - The evidence is replayed fixtures from a single day. There are no forward paper results
    yet.

Allowlist entry to add **only after signing**. The agent has NOT applied it. Rename the
file to drop `_UNSIGNED` and change `STATUS:` to `SIGNED` when signing:

```yaml
mint_allowlist:
  - { id: REV, kind: paper_pilot, stamp: "docs/pilots/REV_PAPER_PILOT_STAMP.md", expires: "2026-11-04", kill: "3 consecutive REV paper losses, or cumulative REV paper loss >= 1% equity, or 2% daily / 5% drawdown hit, or any status mismatch / live attempt" }
```

Approved for paper pilot (yes / no): ____________________

Signature: ____________________
