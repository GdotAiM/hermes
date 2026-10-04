# Hermes X vs Month-9 OS

Hermes X (`GdotAiM/hermes-x`) is the research agent: claims, investigations, beliefs ledger, lecture capture (INV-001).

Month-9 OS (`ftn-agent`) is the deterministic kernel: Market State → candidates → paper ticket.

| | Month-9 OS | Hermes X |
|--|------------|----------|
| Job | Reconstruct ICT day-trade reasoning from evidence | Interpret, compare, investigate, learn *around* that kernel |
| Writes Market State | DTR only | never |
| Invents Month-9 rules | no — labeled ict_source / interpretation / governance | no |
| Reads | fixtures / later tape | kernel briefing + fingerprint + candidate set |
| Question it asks | what is eligible / executable / selected | why was REV selected? what did we suppress? does CONSO win empirically? |

Handoff object later:

```
fingerprint
candidate_set (selected + suppressed + invalidated + ineligible + annotate)
rule provenance
FTN objectives
contrary scenario
```

No MINT, no desk, no live feeds in this milestone.


## Shipped handoff (Stage E)

`dispatch/out/handoff_latest.json` is written by `ftn brief`.

X reads: fingerprint, market_state, candidates[], ftn_annotation, session_ticket, contrary.

X does not write this file as Market State. Treat it as a question pack: "Why was REV selected?"
