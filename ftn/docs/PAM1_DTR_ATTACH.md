# PAM1 DTR attach — read-only context

DayContext.pam1_evidence from parse_pam1_evidence(raw).
Coexists with DayContext.charter when Charter evidence exists.
Does not mint recognition, ticket, or Core fields.
M9 fixture without pam1_model_context → pam1_evidence None.

## Isolation

```
pam1 evidence fixture
  → pam1_evidence.direction = bullish
  → charter.pam1 recognized
  → session_ticket = None

m9 reconstruction
  → pam1_evidence = None
  → charter = None
```
