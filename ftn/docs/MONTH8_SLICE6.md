# Month 8 Slice 6 — HTF overlap annotation

File: `src/ftn/os/m8_htf.py`
Wired in `derive_month8_profile`.

If `origin_pd_array` (or first daily matrix id) exists →
`present=true`, `relationship=seed_only`, `timeframe` from prefix D_/W_/M_.

No array → `present=false`.

Does not modify risk, size, candidate priority, or session tickets.

Path fixture → `D_FVG_bear` / daily / seed_only.
