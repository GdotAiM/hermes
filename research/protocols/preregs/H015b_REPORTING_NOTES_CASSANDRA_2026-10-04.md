# H015b reporting notes: CASSANDRA clearance and non-blocking items (2026-10-04)

**Status:** not part of the harness manifest and not a prereg edit. The registered digest `733499035da5e33dcf3f177619144b5e893f7b7c9fd62086c49b9e17a7f208be` is unchanged. Paper research only.

**Applies to:**
- H015b prereg `research/protocols/preregs/H015b_FORWARD_PREREG_2026-10-04.json` (tag `prereg-H015b` → 49be2d6, sha256 3ee30e04…)
- harness registration note `research/protocols/preregs/H015b_HARNESS_REGISTRATION_2026-10-04.json`

## CASSANDRA clearance
- **Verdict:** **CLEARED** for harness digest 733499035da5e33dcf3f177619144b5e893f7b7c9fd62086c49b9e17a7f208be.
- **Scope:** harness and prereg integrity only. This is not a RUN authorization or a board lock.
- **Source:** `/home/box/hermes-x/reviews/post-wave1/CASSANDRA_H015B_CLEARANCE_2026-10-04.md` (outside git).
- **What CASSANDRA verified:**
  - the rule and the 96 pinned hashes;
  - the prereg sha256 and the 4 manifest files (the digest recomputes);
  - `cluster_boot`: cluster = (date, killzone), lower-bound index 500, upper-bound index 9749;
  - futility on the first 200 canonical trades, kill at −45R, N = 824, the six pass criteria;
  - the seal and the counting rules;
  - the power simulation (ρ 0.554, DEFF 1.425);
  - the D22 reproduction (185/185, 167/167);
  - that no forward row exists yet.
- **Still required before the first R is shown:** DATA's clearance and pipeline certification (C1–C13), and the clearance flag files in the data dir.

## Non-blocking items the final report must carry
These need no amendment. Each must appear in every H015b report from N = 100 on, and in the final report.

1. **Futility is weak against a zero edge.** By simulation it catches a 0R rule only about 8.9% of the time. The kill and the final bound do the real work. Passing futility is **not evidence** of an edge.
2. **The sigma behind the power calculation came from the HistData-merged build tape** (erratum, DATA F2). That tape diverges from canonical Dukascopy BID from 2026-05-29, by up to 94 pts. This is disclosed and acceptable.
3. **Freeze the futility set.** The first time counted N reaches 200, log the 200 row keys (date, instrument, session) that futility was evaluated on. If a later backfill of an earlier-dated session changes which trades are the "first 200 canonical trades", report the reshuffle. Never use the reshuffled set silently.
4. **Report short_session-dropped trades next to the headline.** Trades dropped as `short_session` (exit bars missing or a gap over 5 min) keep their R in `sealed/outcomes.csv`. Every headline must show their count and summed R beside it.
5. **The seal is display-only.** `log.csv` carries side, entry and stop, so R can be derived from public prices. That is acceptable because the rule is frozen. Any harness change after the first forward row means **H015c**.
6. **Cosmetic:** `kill_walk` returns `min_cum=None`. It is not used for any decision.

## Manual steps at report time
The harness is frozen; editing it would change the digest. Items (3) and (4) are therefore manual steps for whoever runs `report`:

- **(3)** When the `report` output first shows `n_counted >= 200`:
  - copy the canonical first-200 keys into a dated note next to the ledger, e.g. `$HERMES_FWD_DATA/H015b/FUTILITY_SET_<date>.json`, together with the futility result;
  - on every later report, compare against that set and disclose any difference.
- **(4)** Read `sealed/outcomes.csv` rows whose `log.csv` status is `short_session`, and only after clearance. Report their count and summed R beside the headline.

Items (1), (2), (5) and (6) are wording that the report author adds to the report.
