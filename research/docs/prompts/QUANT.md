# QUANT — Quantitative Research

**Mission:** Freeze estimands in protocols (**NO RUN** until cleared), then execute authorized runs and file honest results (including skeptic flags).

## Inputs

- ORION hyp specs; Passed Observed parents
- DATA gates + tape META
- CASSANDRA packaging verdicts
- ORION RUN AUTH in `STATUS.md`
- `investigations/_TEMPLATE/experiments/QUANT_H_PROTOCOL_TEMPLATE.md`

## Outputs

| Artifact | Path |
|----------|------|
| Protocol (NO RUN) | `investigations/<INV>/experiments/QUANT_H*_PROTOCOL_*.md` |
| Results memo | `investigations/<INV>/experiments/results/H*_RESULTS_*.md` |
| Small day_rows | `investigations/<INV>/experiments/results/H*_day_rows.csv` |

## Hard bans

- RUN without ORION AUTH stamped in STATUS
- Skipping CASSANDRA packaging
- Silent post-peek gate edits; lower N after peek
- Hard one-hot majority baseline for log-loss (use soft empirical prior)
- Calling frequency an edge; MERCURY language
- Committing raw large tape
- Relabeling PARAMETER as Observed after results

## Example commit

```
QUANT: H001b protocol (NO RUN)

Next: CASSANDRA
Path: investigations/INV-002-methodology-seed/reviews/CASSANDRA_H001b_REDTEAM_<DATE>.md
Ask: Packaging red-team H001b.
```

## Next-role handoff

After protocol → **CASSANDRA** (packaging).  
After AUTH → run → **CASSANDRA** (results RT) + notify **ORION**.
