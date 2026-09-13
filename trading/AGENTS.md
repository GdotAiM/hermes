# AGENTS.md — how AI agents should operate in this repo

You are working in **MINT**, a paper-first execution agent.

1. Read `AGENT.md` and `config.yaml` before any order logic.
2. Default **PAPER**. Never enable live without human dual unlock (`live_enabled` + `MINT_LIVE=1`).
3. Only act on allowlisted strategies with board refs. VERIFY / FAILS / INCONCLUSIVE are not entries.
4. Caps: $100k · 0.5%/trade · 2%/day · 5% DD.
5. Never commit `.env` or secrets.
6. Upstream research lab: https://github.com/GdotAiM/hermes-x
7. Prefer dry-run CLI; use `--submit` only for deliberate paper smoke tests.
