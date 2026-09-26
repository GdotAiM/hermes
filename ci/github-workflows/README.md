# Staged GitHub Actions workflows (activate me)

These are the merged, path-filtered workflows for the monorepo. They live here
**temporarily** because the token used to create this repo lacked GitHub's
`workflow` scope, and GitHub refuses pushes that add files under
`.github/workflows/` without it.

| File | Trigger paths | working-directory |
|------|---------------|-------------------|
| `mint-e2e-dry.yml` | `trading/**`, `research/summaries/**`, `research/beliefs/LEDGER.md` | `trading` |
| `mint-notify-on-board.yml` | `research/summaries/**`, `research/beliefs/LEDGER.md` (main) | `trading` |
| `desk-check.yml` | `desk/**` | `desk` |

To activate (one time):

```bash
gh auth refresh -h github.com -s workflow
mkdir -p .github/workflows
git mv ci/github-workflows/*.yml .github/workflows/
git rm ci/github-workflows/README.md
git commit -m "Activate monorepo CI workflows" && git push
```

Until then **no CI runs** in this repo.
