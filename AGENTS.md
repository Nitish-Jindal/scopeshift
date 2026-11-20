# Project working rules

Follow PROJECT_SPEC.md and docs/checklist.md. Never share enforcement predicates
with the reference model. Never report a check as passed without running it.
No live paid inference without explicit approval. Keep all effects synthetic.
Use Python 3.12.16 and uv; run Ruff and pytest after meaningful changes. Preserve
compact raw evidence. Never merge main or change repository visibility.

## Cloud migration checkpoint — user steering on 2026-11-20

Read HANDOFF.md before continuing. The user requested that all current work be
preserved, committed as WIP and pushed to `codex/scopeshift-complete-mvp`, then
further local implementation paused to avoid conflicting Cloud changes.
This checkpoint is incomplete and unverified; do not claim a working benchmark.
Resume implementation in the Cloud checkout only when the user initiates that
continuation. The full verbatim master specification is in PROJECT_SPEC.md.
The earlier, pre-enforcement normative design is preserved separately in
docs/authorization-contract.md; it supplements, never narrows, the master scope.

## Persistent engineering instructions

- Complete the full master definition of done, including actual MCP transport,
  independent grading, experiments, mutation testing, stateful fuzzing, Docker,
  documentation, CI and review PR. Do not substitute scaffolding for delivery.
- Never fabricate tests, benchmark measurements, model runs, novelty or CI status.
  Distinguish written source, executed code, verified results and unfinished work.
- C0–C4 must retain their intended gaps. C5 must couple current-policy validation,
  approval consumption, local effect and trusted effect evidence transactionally.
- Principal/session identity must come from trusted execution context. Never let
  evaluated model arguments select their authority. Expose no arbitrary shell
  execution or real external effects.
- The reference model/oracle may share neutral contracts, but must not import or
  reuse enforcement predicates. Missing or malformed evidence must fail validity.
- Use explicit event/barrier ordering and real SQLite connections for contention;
  do not manufacture security races with sleeps or impossible transaction histories.
- Keep .venv, caches, keys, .env, personal data and bulky artifacts out of commits.
  Use project-local dependencies and a reproducible uv.lock. Do not delete
  unrelated user files, projects or Docker resources to reclaim disk.
- Live model evaluation is opt-in and requires explicit API-spend authorization.
  Do not inspect unrelated stored credentials. Fixture results are not live results.
- Keep the repository private, work on the dedicated review branch, never merge
  main or change visibility. No messages to others without explicit authorization.
- Maintain docs/checklist.md and HANDOFF.md with evidence and exact failures when
  handing off. Preserve unfinished work; document nonessential limitations.
