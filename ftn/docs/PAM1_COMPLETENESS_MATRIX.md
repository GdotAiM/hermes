# PAM1 Completeness Reconstruction Matrix — FROZEN

| Case | required_complete | charter_recognition | session_ticket |
|------|-------------------|---------------------|----------------|
| Full labeled evidence + identified_pam | true | true (identified+pam1) | none |
| Missing OTE + identified_pam | false | true (identified still) | none |
| Confirming all none, required present | true | true | none |
| Required complete + identified_pam=none | true | **false** | none |

**Invariant:** Completeness never mints Charter recognition or a ticket.
Recognition remains `identified_pam == present` AND named pam1.

No detector. No Core inference. No PAM ranking.
