# Project working rules

Follow PROJECT_SPEC.md and docs/checklist.md. Never share enforcement predicates
with the reference model. Never report a check as passed without running it.
No live paid inference without explicit approval. Keep all effects synthetic.
Use Python 3.12.16 and uv; run Ruff and pytest after meaningful changes. Preserve
compact raw evidence. Do not perform merges or visibility changes without explicit
user authorization. Follow the branch and scope requested by the current task.

## Current publication status and historical specification

The implementation and final correctness corrections are merged into public
`main` through PR #1. The public-facing documentation cleanup is authorized on
main. Future changes should use the branch requested by the task; do not infer
permission to merge other work or change visibility.

PROJECT_SPEC.md preserves the original implementation brief, including its
historical private-repository and review-branch requirements. Those status/workflow
statements do not describe the current publication state. HANDOFF.md and
reports/verification.md record current status and historical verification SHAs.
Do not reinterpret earlier WIP migration notes as an unfinished implementation or
rerun unrelated implementation work during documentation-only tasks.

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
- Use the branch and scope explicitly requested by the user. Do not merge other
  work or alter repository visibility without authorization. No messages to others
  without explicit authorization.
- Maintain docs/checklist.md and HANDOFF.md with evidence and exact failures when
  handing off. Preserve unfinished work; document nonessential limitations.
