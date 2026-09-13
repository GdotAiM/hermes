# Solo mode — one model, all hats

When only one model (or one human) is available, **still wear one role per commit**. Role separation in **artifacts** beats role separation in **processes**.

## Rules

1. **One role per commit.** Example commit subjects:
   - `ATLAS: C-METH-041 claim card (Observed)`
   - `DATA: gate Pass C-METH-041 + tape META`
   - `QUANT: H011c protocol (NO RUN)`
   - `CASSANDRA: H011c packaging DID NOT SURVIVE — need H011d`
   - `ORION: RUN AUTH H011d exploratory (STATUS)`
   - `QUANT: H011d exploratory results`
   - `CASSANDRA: H011d results RT agree FAILS`
   - `ORION: H011d BOARD LOCK FAILS`
2. **Stage order is mandatory.** Do not draft results before packaging SURVIVED + RUN AUTH.
3. **Same file paths** as multi-agent mode (`investigations/_TEMPLATE/` layout).
4. **Name the next role** in the commit body with a file path, even if you will be that role next.
5. **Do not peek then amend.** After seeing outcomes, bump hyp id (`H*b` / `H*c`) or park **INCONCLUSIVE**.
6. **Stop after your stage** unless the human reassigns. Solo mode is not a license to soft-merge roles inside one commit.

## Recommended solo sequence (per hyp)

```
ATLAS → DATA → ORION (spec) → QUANT (protocol) → CASSANDRA (packaging)
  → ORION (RUN AUTH) → QUANT (run) → CASSANDRA (results RT)
  → ORION (board) → LEDGER / utilization
```

Optional inserts: HISTORIAN (diff), MACRO (event context), FORGE (schemas), RISK/MERCURY (only after SURVIVES + human).

## Success metric (unchanged)

Validated discoveries including clean **FAILS** > volume of agent output.
