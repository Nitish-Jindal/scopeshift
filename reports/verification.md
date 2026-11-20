# ScopeShift verification and completion report

## Executive verdict

**APPLICATION-READY WITH LIMITATIONS for the verified synthetic local benchmark.**
Remote review publication remains blocked by GitHub API access; no PR or remote
CI success is claimed. No paid model inference was authorized or run. Finite
passing tests and experiments are not a universal safety proof.

## Implemented components and architecture

The preserved WIP contracts, SQLite store, policy, gateway and effects are now
integrated with actual two-server official-SDK MCP transport, trusted host-bound
identity and request registration, C0–C5 boundaries, causal scheduling, actual
concurrent connections, independent reference-state reconstruction and grading,
replay, mutation campaigns, bounded exploration, Hypothesis stateful shrinking,
CLI, Inspect AI adapter, metrics/charts, Docker Compose and GitHub Actions.

C5's current-policy validation, approval consumption, local effect and trusted
effect evidence share one serialized SQLite transaction. Revocation uses that
same consistency domain. C4 deliberately keeps a gap. Oracle imports exclude
enforcement, storage and execution. Details: docs/architecture.md and
reference-model.md. Multi-hop delegation is an explicitly deferred extension.

## Automated tests and MCP evidence

- Complete native suite: **267 passed**, zero failures or skips in the retained run.
- Complete offline hardened Compose suite: **267 passed**; expanded MCP demo passed.
- In-process line coverage is approximately **93%**; exact counts/percentage are in
  results/verification.json. Subprocess server code is functionally exercised by
  actual MCP tests but is not instrumented by this coverage run.
- Ruff lint and format checks and Git whitespace checks passed.
- Locked editable installation, `uv build`, and a fresh non-editable runtime-only
  wheel installation passed. Packaged dataset/fixtures and actual MCP demo,
  mutations, stateful replay and benchmark ran outside the source checkout.
- Two actual MCP stdio servers, initialization/list-tools, all five tool families,
  tool binding, hidden-revocation cases and concurrent barrier variants executed.
- Real competing SQLite transaction tests establish both revocation/effect
  orderings. Approval contention, canonical request conflicts, rollback, bounded
  evidence-write failure and idempotent revoked retries are tested.

## Measured temporal authorization results

All **180 MCP benchmark trials** had valid evidence; all exports were independently
regraded. Each deterministic configuration ran the same 36 scenarios.

| Configuration | Unsafe trials | Unauthorized effects / effects | Legitimate completion |
|---|---:|---:|---:|
| C0 | 22/36 | 22/38 | 16/16 |
| C2 | 14/36 | 14/30 | 16/16 |
| C3 | 9/36 | 9/25 | 16/16 |
| C4 | 4/36 | 4/20 | 16/16 |
| C5 | 0/36 | 0/16 | 16/16 |

C1 is applicable in the Inspect model track; fixed requests cannot measure prompt
compliance. Controlled C1 adapter fixtures execute real MCP effects, but they are
not LLM experiments. The mandatory C3 gap and C4 non-atomic recheck failure occur
in actual execution. C5 blocks their corresponding schedules and allows legitimate
and unrelated-policy-update controls. The final C4 count uses explicit concurrent
barriers outside transactions, correcting the earlier timing-dependent variant.

## Reliability, mutations, fuzzing and replay

- Gateway mutation campaign: **11/11 killed**, zero survived/invalid; every named
  family retained. Grader mutations: **9/9 killed**, zero survived; no equivalence
  classification assumed. Exact per-mutant outcomes/fixtures are retained.
- Oracle labelled evidence histories: false acceptance **0/6**, false rejection
  **0/2**, invalid histories rejected **3/3**. Eighteen pre-existing predicate
  labels also test both the enforcement and independent reference predicates.
- Bounded exploration: **54/54** schedules in its grammar, eight unsafe fingerprints,
  none C5. This is finite grammar coverage, not exhaustive program verification.
- C3 stateful campaign: seed 20261120, budget 100 examples × 20 rule steps;
  64 actual example/shrink executions, 434 semantic commands, 318 distinct
  prefixes. Hypothesis found and shrank a failure to **three commands**.
- C5 stateful campaign: budget 60 × 20; 62 example/shrink executions, 1,194 semantic
  commands, 667 distinct prefixes; **no counterexample within that budget**.
- The retained regression replays against real SQLite and yields an independently
  graded unsafe effect. The full benchmark replayed **180/180 consistently**:
  **170 exact semantic ledgers**, **10 concurrent effect/grade invariant replays**.
  Concurrent lock winners are not claimed deterministic.

Counts include shrinking/auxiliary executions where stated. The static, manual,
bounded and stateful spaces differ; their counts are not a fair speed ranking.
See reports/reliability.md and results/reliability/ for all retained evidence.

## Metrics and research output

Exact numerator/denominator rates, all measured latencies, startup-inclusive
overhead, environment/library versions, seed and dataset digest are in
results/benchmark/summary.json. Complete raw per-trial evidence is compressed in
results/benchmark/raw.jsonl.gz. Generated chart/table: reports/measured-results.md
and effect-safety.svg. Research interpretation, threats to validity, scoped
claims and extensions are in reports/research.md. Zero denominators and unavailable
live-model token counts remain null; no invented confidence intervals or model
measurements are reported.

## Container, model and CI status

Docker Engine 29.9.2 and Compose v2.40.3 worked on Linux x86_64. Containers use
nonroot users, no runtime network, read-only root, dropped capabilities and bounded
CPU/memory/tmpfs. The managed proxy's public CA bundle was mounted only during
build to preserve certificate verification. Native execution remains supported.

The optional Inspect model adapter is implemented and fixture-tested through
actual MCP. Six fixture cases include benign operations, revocation, malicious
content and an unauthorized follow-up. Fixture usage metadata is synthetic;
**live LLM inference and paid APIs remain unrun**. A separately authorized live
command is gated and bounded; no secrets were configured.

Credential-free native/container GitHub Actions jobs are committed, with local
equivalents passing. **Remote CI has not been observed.** The runtime blocks
api.github.com. Its required domain addition was saved to environment settings
while retaining restricted package-manager networking; saving does not apply it
or create credentials. Direct Git capability is reported separately below.

## Self-audit and limitations

The skeptical self-audit fixed C4 revoked retries, typed canonical binding,
non-causal histories, transition-claim races, evidence snapshot consistency,
bounded lock-evidence failures, post-commit rollback mislabelling, C1 prompt
separation, concurrent boundary reproducibility and nonroot image permissions.
See docs/self-audit.md for evidence and docs/limitations.md for remaining risks.
This is not external independent security review. SQLite's guarantees cover local
synthetic commitments, not real network delivery or revoking model knowledge.
Related-work paper leads are explicitly unverified; no novelty claims are inferred.

## Quickstart and demonstration

```bash
uv python install 3.12.16
uv sync --locked
uv run pytest
uv run scopeshift demo
uv run scopeshift benchmark --output artifacts/new-benchmark
uv run scopeshift report --input artifacts/new-benchmark --output artifacts/new-report
uv run scopeshift replay tests/regression/c3-counterexample.json
docker compose run --build --rm verify
docker compose run --rm demo
```

Use fresh output directories; see docs/reproducibility.md for managed proxy CA
and writable cache settings. README contains all CLI and model-track commands.

## Git and review publication

Branch: `codex/scopeshift-complete-mvp`; base checkpoint:
`c9634cf8a2c2bea26db57658bf689b334f453862`. The final commit hash is supplied by the
final task report and `git log -1`. Review body is prepared at docs/review-pr.md.
No PR number/link is fabricated. No merge, release or visibility change occurred.
The repository remains private by preserving its existing visibility.

Application description: ScopeShift is a reproducible AI tool-use authorization
benchmark combining real MCP communication, temporal policy schedules,
transactional synthetic effects, independent grading, targeted mutations and
stateful counterexample discovery/replay, with separately measured safety,
utility and evidence integrity.
