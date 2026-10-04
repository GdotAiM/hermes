# Forward-test family rule (ORION, 2026-10-04)

Applies to the concurrent forward-only tests H013 (Model U v1), H014 (MMXM v5 A) and H015b (FTN REV, D22 stop), and to any later forward test added to the active family.

This rule governs **promotion**, not each lock's own verdict. The individual board locks and preregs are not edited by it.

1. Each test is judged on its own binding criteria, as frozen in its prereg.
2. A test that PASSES its own criteria is recorded as `PASSES (unadjusted)`. It becomes a MINT-clearable `SURVIVES` only if its primary one-sided lower bound also clears a Holm-adjusted alpha across the active family. With three tests at a one-sided alpha of 0.05, the smallest p-value must be below 0.0167, the next below 0.025 and the last below 0.05. Use each test's own binding bound method, e.g. the session-cluster bootstrap for H015b.
3. Otherwise the status is `PASSES (unadjusted), replication required`. That means a fresh forward test under a new ID before any clearance.
4. Rationale: three independent-ish tests at alpha 0.05 give about a 14% chance that at least one passes by luck when there is no edge.
5. Kills and binding futility rules stay per-test and are never relaxed by this rule.
