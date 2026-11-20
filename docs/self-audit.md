# Skeptical security and correctness self-audit

This is the implementing agent's self-audit, not external independent review.
The original source and specification were preserved and extended on the review
branch. No live model inference or unrelated credentials were used.

| Concern | Investigation and correction / evidence |
|---|---|
| Baselines accidentally protected | Full corpus reproduces unsafe C0–C4 effects; C1 fixture follows an unsafe request under ambient enforcement |
| C5 merely checks twice | Validation, approval use, local mutation and effect evidence share BEGIN IMMEDIATE; actual competing-connection tests establish both lock orderings |
| Impossible race schedules | Only causal named boundaries accepted; monotone schedules; no internal C5 checkpoint; concurrent barriers are outside every effect transaction |
| Concurrent replay unstable | Explicitly synchronize concurrent corpus arrivals outside commits; compare invariant outcomes for nondeterministic winners, exact ledgers for serial runs |
| Oracle shares enforcement | Imports restricted to neutral contracts/reference model; AST test forbids enforcement/storage/execution imports |
| Grading trusts gateway | Lying-gateway fixture commits despite denial; oracle grades actual effects unsafe |
| Missing evidence treated safe | Missing ledger/order/duplicate/final-resource corruption rejected; rehashed but noncausal execution is also rejected |
| Final-state-only grading | Compensated-unsafe-effect fixture restores initial resource yet remains unsafe |
| Legitimate work refused | 16 legitimate controls, unrelated-version control, independent utility grade and reject-unrelated mutant |
| Request identity rebinding | Canonical operation equality prevents boolean/integer/float and changed-argument ID reuse; server verifies tool binding and registered dispatch |
| C4 revoked retries blocked | Return committed retries before recheck, including within a concurrent recheck transaction; no duplicate effects |
| Partial effects on rollback | Injected mutation then failure rolls back resources/effects; no application replay of partial work |
| Lock evidence cannot be written | Both effect attempt and rollback evidence writes have bounded waits; unavailable evidence returns inconclusive, never forged rollback success |
| Post-commit failure labelled rollback | Post-commit checkpoint is outside the rollback exception handler |
| Evidence export races | Export reads all tables in one coherent read transaction |
| Approval expiry/identity/arguments | Predicate labels, equality-boundary controls, real contention and targeted mutation probes |
| Scope canonicalization | Constraints reject missing/null confusion and distinguish bool/int/float canonical JSON |
| Synthetic containment | Fixed resource/recipient namespace, parameterized SQL, public-only search, no arbitrary shell/database path/identity tool arguments |
| Package bootstrap | Dataset now committed and generator equality tested; clean wheel and locked installs verified |
| TLS bypass during Docker setup | Initial UnknownIssuer diagnosed; optional public build CA bundle restores trust, preserving TLS/checksums; no insecure flags |
| Container nonroot permissions | Checkout modes initially prevented reads; image grants read/execute, never write, to required application files; offline read-only tests rerun |
| Model results fabricated | Fixture outputs and synthetic usage explicitly labelled; actual MCP calls tested; no live inference reported |
| Mutation score inflated | All 11 gateway and nine grader families retained with killed/survived/invalid fields; no equivalence silently assumed |
| Fuzzing result invented | Actual Hypothesis discovery, shrinking and independent replay; bounded C5 pass reported with finite budgets |
| Timings overclaimed | Startup-inclusive sequential wall times, explicit denominators and no deterministic-case CIs |
| Visibility or secrets changed | No publication/visibility changes, no model key configuration; synthetic fixtures only; generated/cached artifacts excluded from commits |

Remaining limitations are in docs/limitations.md and reports/research.md. Remote
GitHub API/CI access is an external publication concern and is not inferred from
successful native Git access. A prepared PR body is not an actual pull request.
