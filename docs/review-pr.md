# Complete ScopeShift temporal authorization benchmark

Invocation-time approval can become stale before an MCP tool commits its effect.
This implementation reproduces that failure through two official-SDK MCP servers
and compares ambient, session, invocation, separate-recheck and atomic-boundary
policies against an independent effect-history oracle. C5 couples current-policy
validation, approval consumption, local synthetic mutation and evidence in one
SQLite transaction while preserving legitimate utility after unrelated updates.

The benchmark includes 36 versioned scenarios, trusted host-bound identities,
actual transaction-contention tests, serial/concurrent replay, 11 enforcement
and nine grader mutation families, seeded Hypothesis stateful shrinking, bounded
exploration, a complete CLI, Inspect AI fixture-tested model integration, offline
hardened Docker Compose, credential-free CI, measured artifacts and documentation.

Validation: 267 automated tests; Ruff check/format; installed non-editable wheel;
180 actual MCP benchmark trials; complete evidence regrading; native and offline
container tests and demos. Unsafe trials: C0 22/36, C2 14/36, C3 9/36, C4 4/36,
C5 0/36. C5 completed 16/16 legitimate controls. All 11 targeted enforcement
and nine grader mutants were detected. The C3 stateful counterexample shrank to
three commands and reproduces against real SQLite.

No live model inference, paid API use, real data/effects, visibility change or
merge. Finite synthetic results and bounded fuzzing are not universal safety
proofs. Remote CI status must be checked on the pushed commit before approval.
Review reports/verification.md, reports/research.md and docs/self-audit.md.
