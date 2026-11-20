# ScopeShift final independent review correction report

## Current verdict and provenance

**APPLICATION-READY WITH LIMITATIONS for the verified synthetic benchmark.**
PR [#1](https://github.com/Nitish-Jindal/scopeshift/pull/1) is merged into public
`main` at `c1cbf657ab975369fe653ff99c304668d20758bc`. Implementation verification
was performed on the former review branch; the owner subsequently merged and
published the repository. The earlier API-publication blocker is resolved.

Previous verification belongs to commit
`18c50d46aa21825cb231b6c580dbd3f68a9a3771`: 267 native/container tests and
[successful remote CI](https://github.com/Nitish-Jindal/scopeshift/actions/runs/44741335221).
That CI success was independently read through GitHub's API, not inferred from
local tests. It does not establish CI success for these corrections. Current
source verification and current CI observations are tracked separately in
`results/verification.json` and the final task report. Legacy schema-1 evidence
is historical and is not silently accepted by the corrected grader.

## Findings resolved

- Evidence now has mandatory schema-2 envelopes/events and explicit fixed-host,
  model-host, stateful and independently authored fixture modes. Missing, unknown
  or conflicting modes, schemas, sources and run/scenario identities fail closed.
- Production grading binds the externally supplied scenario and mode. Stateful
  grading additionally binds external commands, transitions, terminal responses
  and cancellations. Primitive fixtures bind the trusted registry and their
  authored policy histories, while legitimately omitting host transport phases.
- Host lifecycle checks require initialization/snapshot/discovery, generated and
  admitted requests, dispatch/receipt, applicable rechecks/atomic decision evidence,
  attempts and outcomes, terminal responses/completion, and post-commit boundaries.
  Unsupported external schedules, mismatched receipt actions and contradictory
  atomic decisions/outcomes are rejected. Scheduled transitions must occur exactly
  after their applicable checkpoints.
  Unreachable model/denial paths and pending/superseded stateful requests have
  explicit, validated dispositions.
- Security-critical production assertions were replaced with explicit checks and
  typed EvidenceError exceptions, including prior assertions with registration
  side effects. A subprocess regression verifies rejection under `python -O`.
- Non-message approval IDs are ignored for authorization/consumption and cannot
  burn message approvals. Messages consume only live, unused, correctly bound,
  normatively applicable approvals. Deliberately unsafe baseline effects remain
  unsafe; the bookkeeping correction does not repair their authorization gaps.
- Metrics separately count proposed requests, dispatch, server receipt, protected
  effects, model-observable violations, current-policy check errors/false denials,
  and legitimate task noncompletion. Model false-refusal metrics are null.
  Stale-authority and revocation eligibility use observed boundaries/transitions.
- Model observability is based on actual notification/result delivery before each
  generation. Parallel proposals in one generation share its prior information;
  later notifications cannot retroactively establish knowing misconduct.
- A hand-authored, independent 100-case admission/effect/safety matrix covers 20
  core scenarios across C0/C2/C3/C4/C5. C1 remains model-dependent.

Core transaction architecture, actual MCP transport, separate reference model
and actual competing-connection tests were preserved. This was a targeted
correctness pass, not a replacement implementation.

## Current local and container verification

- Requested `uv run ruff check .` and `uv run ruff format --check .`: passed.
- Complete `uv run pytest`: **423 passed**, zero failed/skipped, with coverage
  collection enabled. In-process coverage: **1,611/1,704 statements (94.54%)**.
  MCP subprocess servers are functionally tested but not instrumented here.
- Docker build, hardened offline Compose verification: **423 passed**. Expanded
  MCP demo passed. Runtime remains nonroot, read-only, offline and resource-bounded.
- Targeted regressions ran before the complete suite. New coverage includes 100
  expected-matrix entries, 37 malformed/lifecycle/history cases, 12 approval cases,
  three metric-boundary cases and four notification-timing fixtures.
- The known optimized-Python bypass is directly exercised in a subprocess with
  recomputed hashes and an externally supplied contract, not just bad metadata.

## Revised measured benchmark

The actual MCP benchmark was rerun: **180 executions**, 36 scenarios × five
fixed-request configurations. All 180 exports have valid schema-2 evidence and
regrade consistently against the externally loaded dataset contracts.

| Configuration | Unsafe trials | Unauthorized committed effects | Legitimate completion |
|---|---:|---:|---:|
| C0 | 22/36 | 22/38 | 16/16 |
| C2 | 14/36 | 14/30 | 16/16 |
| C3 | 9/36 | 9/25 | 16/16 |
| C4 | 4/36 | 4/20 | 16/16 |
| C5 | 0/36 | 0/16 | 16/16 |

These effect-safety counts are unchanged, but raw evidence, metrics, timing data,
charts and reports were regenerated. New measurements distinguish C5's four
unauthorized server entries out of 28 from its zero unauthorized commitments out
of 16. Observed C5 check false denials are 0/44 permitted check opportunities;
fixed-track LLM refusal and observable-model compliance are not measured.

Exact metric denominators, versions, seed and dataset digest are in
results/benchmark/summary.json. Complete evidence is in raw.jsonl.gz. Generated
chart/table: reports/measured-results.md. Corrected definitions: docs/metrics.md.
No paid or live-model inference was run; all Inspect outputs/usage are fixtures.

## Mutation, replay and fuzzing reruns

- All **11/11 enforcement** and **9/9 grader** targeted mutants remain killed;
  zero survived/invalid. Skipped-check mutants record explicit unchecked-admission
  instrumentation rather than bypassing the required evidence lifecycle.
- Oracle fixtures: false acceptance **0/6**, false rejection **0/2**, invalid
  rejection **3/3**. The 18 independent predicate labels remain covered.
- Bounded exploration rerun: **54/54** schedules; eight unsafe fingerprints, none C5.
- C3 seeded stateful campaign: 64 example/shrink executions, 434 commands, 318
  prefixes; failure minimized to **three commands** and independently replayed.
- C5 campaign: 62 example/shrink executions, 1,194 commands, **652** distinct
  prefixes in this retained run; no counterexample within the 60 × 20 budget.
  Concurrent winners can change prefix fingerprints. Neither finite pass nor
  shrinking minimality within this grammar is a universal proof.
- Complete benchmark replay: **180/180 consistent**, comprising **170 exact
  serial ledgers** and **10 concurrent effect/grade invariant replays**.

Compact current artifacts are retained under results/reliability/. Historical
counts and earlier evidence can be recovered from the previous commit, not
mistaken for verification of this revision.

## Limitations and remaining review

No unresolved P0/P1 implementation finding remains in this pass. Both native and container CI jobs passed for correction source
`4683410e47e785f49bdc824afe6a853499b0245d`, separately from the previous successful
commit. The verification-record-only follow-up does not change the recorded
source digest; its final workflow status is checked with the final task SHA. The fixed model adapter binds one preselected
identity/session/grant/approval and does not implement dynamic grant selection or
multi-hop delegation. No live-model efficacy/refusal claim is made. Guarantees
cover local synthetic commitments, not real email/network atomicity, retracting
model knowledge or a compromised trusted host. Broader exploration, primary-source
research comparison and external review of these corrections remain future work.

See HANDOFF.md, docs/self-audit.md, reports/research.md and reports/reliability.md.
No project restart, paid model API use or unrelated credential access occurred
during verification. Repository publication and the PR #1 merge were subsequent
owner actions, distinct from the historical implementation/verification runs.

An intermediate correction revision, 31fa782e426f3340f2fed9cdeb5c5b4b18cfe3b7,
passed 419 local/container tests and both remote CI runs 44746281271 and
44746272518. The final four guard regressions raise the current suite to 423;
that intermediate CI success is recorded separately rather than attributed to
the final guard revision.

Final source CI: both [PR workflow 44747732315](https://github.com/Nitish-Jindal/scopeshift/actions/runs/44747732315)
and [push workflow 44747724360](https://github.com/Nitish-Jindal/scopeshift/actions/runs/44747724360)
completed successfully for 4683410, including native and container jobs. The source
digest in results/verification.json is unchanged by this verification-only record.

## Public-facing documentation maintenance

The post-merge cleanup updates status and presentation on main without modifying
implementation, dependencies, measured results or the tested source digest.
Credential/history review scope and its limitations are recorded in
[publication-review.md](../docs/publication-review.md). The recorded test counts
and experimental results above are verification provenance, not a claim that
a documentation edit reran the benchmark.
