# Delivery checklist

Cloud migration checkpoint (2026-11-20): local implementation paused at user
request after WIP preservation. Read ../HANDOFF.md for actual results and known
defects. All implementation items below remain unverified unless explicitly
checked. Full master specification is now preserved in ../PROJECT_SPEC.md;
the earlier normative design is in authorization-contract.md.

- [x] Inspect clean initial repository and verified Python/Docker availability.
- [x] Record normative contract before enforcement implementation.
- [ ] Hand-labelled independent oracle fixtures.
- [ ] Locked dependencies, src layout, lint/test tooling.
- [ ] SQLite policy, trusted ledger, effects, idempotency and transactions.
- [ ] Two actual MCP servers and client, five tools.
- [ ] C0–C5 configurations and semantic scheduling/replay.
- [ ] Independent reference model, evidence validation and grading.
- [ ] Versioned 20–40 variant dataset and controls.
- [ ] Semantics, MCP, concurrency, reset, CLI and oracle tests.
- [ ] All gateway/grader mutations executed and reported.
- [ ] Bounded exploration, Hypothesis state machine, minimized replay artifacts.
- [ ] Inspect AI opt-in integration tested with fixtures.
- [ ] >=100 deterministic executions, metrics, raw evidence and charts.
- [ ] Docker/Compose verified; credential-free GitHub Actions.
- [ ] Critical self-audit and fixes; quickstart independently rerun.
- [ ] README, architecture, threat model, research report, demo/walkthrough.
- [ ] Logical commits, pushed private review branch and PR.

Live inference: pending, intentionally opt-in; no API spending authorized.
Goal was originally blocked because specification was missing; now supplied.
Current steering is to hand off to Cloud and pause local work, not mark complete.
