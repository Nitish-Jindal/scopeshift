# Final correctness corrections for ScopeShift PR #1

Require explicit versioned evidence modes, external scenario/history contracts,
mandatory lifecycle/transition/terminal validation and optimization-safe checks.
Correct approval applicability and separate proposed/dispatched/received/committed
operations, observed check errors, task utility and model information visibility.
The original transactional/MCP/reference architecture is preserved.

Add independent 100-case admission/effect/safety expectations, adversarial
schema/lifecycle/history and python -O regressions, approval integrity cases,
metric-boundary tests and actual pre-/post-proposal notification fixtures.

Current verification: 419 native and 419 offline Docker tests passed; Ruff checks
passed. Regenerated 180-trial MCP evidence: unsafe C0/C2/C3/C4/C5 trials
22/14/9/4/0 out of 36; C5 legitimate completion 16/16. All 11 enforcement and nine
grader mutants killed; 180/180 replays consistent. Corrected metrics and research
artifacts are retained. See reports/verification.md for previous/current CI status.

No paid inference, secrets, merge or visibility change. Finite synthetic results
and bounded fuzzing are not universal security claims.
