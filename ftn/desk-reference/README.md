# FTN desk — reference copy only (superseded)

This is FTN's original standalone desk (`os_state.js`, `levels.js`, screenshots),
kept **for reference only**. It is not served or maintained.

It is superseded by the monorepo HERMES Desk (`../../desk/`) plus the
`desk/js/adapters/dayContext.js` adapter, which reads the handoff.v1
contract (`ftn/dispatch/out/handoff_latest.json`, samples in
`ftn/dispatch/samples/`) instead of a baked `os_state.js` snapshot.

Why kept, not deleted: `levels.js` contains client-side pivot / range /
four-count math. That math was deliberately **not** ported — the I1
acceptance test forbids the Desk from independently deriving FTN facts —
so this copy documents what the old desk computed and why it went away.
