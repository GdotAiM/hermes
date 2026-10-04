# Staged GitHub Actions workflows (activate me)

These are the merged, path-filtered workflows for the monorepo. They live here
**temporarily** because the token used to create this repo lacked GitHub's
`workflow` scope, and GitHub refuses pushes that add files under
`.github/workflows/` without it.

| File | Trigger paths | working-directory |
|------|---------------|-------------------|
| `mint-e2e-dry.yml` | `trading/**`, `research/summaries/**`, `research/beliefs/LEDGER.md`, `ftn/dispatch/samples/**`, `ftn/src/ftn/os/handoff_contract.py` | `trading` (+ `ftn_context` on the committed sample) |
| `mint-notify-on-board.yml` | `research/summaries/**`, `research/beliefs/LEDGER.md` (main) | `trading` |
| `desk-check.yml` | `desk/**`, `ftn/dispatch/samples/**` | `desk` (+ `node tests/dayContext.test.mjs`) |
| `ftn-check.yml` | `ftn/**`, `trading/src/mint/dispatch/**`, `desk/js/adapters/dayContext.js`, `desk/tests/**`, `scripts/e2e_fixtures.sh` | repo root (`ftn/` pytest, sample validation, `scripts/e2e_fixtures.sh`) |

To activate (one time):

```bash
gh auth refresh -h github.com -s workflow
mkdir -p .github/workflows
git mv ci/github-workflows/*.yml .github/workflows/
git rm ci/github-workflows/README.md
git commit -m "Activate monorepo CI workflows" && git push
```

Until then **no CI runs** in this repo.
