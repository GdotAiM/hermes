# Which DayContext layers can populate from bar data (bar-derived `ftn score` context)

The bar-derived DayContext (`research/daycontext.py`) only provides what can be computed from 1m OHLC bars
(+ the calendar since the post-H015b fixes). Every other layer needs a human label or a data source that is not on the box.
They stay **None / unavailable**; nothing is invented.

| Layer | Bar data? | Why / what it would need |
|---|---|---|
| Month 1 foundation | no | needs labelled `identified_setup_elements` / `dealing_range_side` |
| Month 2 risk frame | no | needs labelled `identified_low_risk_frame` / `identified_high_reward_context` |
| Month 3 next-setup | no | needs labelled `selected_timeframe` / `anticipated_setup` |
| Month 4 arrays | no (not wired) | triggers on an `arrays` catalogue. Daily FVGs exist in `pd_matrix`, but a catalogue builder would be a new interpretation. |
| Month 5 / 6 position & swing | no (not wired) | triggers on monthly sponsorship or monthly (`M_`) origin arrays. Monthly candle colour is cheap, but it feeds `pair_institutional` and so REV eligibility. **Wiring it changes tickets → human decision, needs H016.** |
| Month 7 weekly | no (not wired) | needs `week_path` / weekly (`W_`) arrays / `ipda_days`. Derivable, but an interpretation; same ticket-change caveat. |
| **Month 8 day-trade** | **yes** | CBDR, Asian, London gate. Units fixed (instrument points, scaled thresholds). **News gate now fires on FOMC/CPI/NFP days.** |
| Month 10 multi-asset | no | needs COT / asset-class evidence; no COT data on the box |
| Month 11 mega-trade, Month 12 top-down | no | needs labelled evidence |
| Charter / Model 13 bridge | no | needs identified PAMs / an explicit `model13` label; `model13_bridge_enabled: false`. Not derivable from bars. |
| Sentiment: Williams %R(10, m15) | partly | computed on m15 bars **up to the raid bar**, and bars start at 00:00 NY. Raids in the first ~2.5 h leave < 10 bars, so the value is `unavailable` on 130/185 US100 and 110/167 US500 tickets. Fix (prior-evening bars) would change the tape the kernel sees → not done. |
| Sentiment: sponsorship monthly / weekly | no | `not_scored` (see Month 5/6) |
| DXY relationship | **unavailable** | no DXY series on the box (checked `/workspace/marketdata`: Dukascopy/HistData FX, US100/US500, XAU, NQ/ES only). An EURUSD-inverse proxy is possible, but it would be invented data → human decision. |
| **Calendar (FOMC/CPI/NFP)** | **yes (wired)** | `research/data/us_macro_events.csv`, exported from `/workspace/marketdata` `calendar("events")` (federalreserve.gov, BLS archives). These are event dates/times only. The schedule is public in advance, so it is causal. Context only: the kernel does not read it. Regenerate: `/workspace/marketdata/.venv/bin/python -c "import sys; sys.path.insert(0,'/workspace'); from marketdata import calendar; calendar('events')[['date','time_ny','event','kind','note','source']].to_csv('us_macro_events.csv', index=False)"` (then re-add the 3 `#` provenance lines). |
