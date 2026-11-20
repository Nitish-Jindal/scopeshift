# ScopeShift Cloud implementation handoff

Updated 2026-11-20 (Asia/Kolkata). Work continues on the private review branch
`codex/scopeshift-complete-mvp`, extending checkpoint
`c9634cf8a2c2bea26db57658bf689b334f453862`. The original local migration handoff is
preserved in that checkpoint's history. The Cloud continuation goal explicitly
authorized implementation; its earlier local pause is superseded.

## Current implementation

The original contracts/storage/policy/gateway/effects code has been extended with
actual two-server MCP transport, a trusted identity-binding host executor, all
C0–C5 configurations (C1 in the model track), causal schedule validation, actual
transaction-contention tests, an independent reference model/oracle, replay,
targeted mutations, bounded exploration, Hypothesis stateful shrinking, CLI,
Inspect model integration, metric/report generation, Docker Compose and CI.
The dataset is now a committed, reproducible 36-variant corpus; the former force-
include/bootstrap cycle is resolved. No work was discarded or project restarted.

Read AGENTS.md, the full original PROJECT_SPEC.md, docs/authorization-contract.md,
docs/reference-model.md, docs/checklist.md and reports/verification.md before
continuing. Security semantics and intentionally insecure baselines are preserved.

## Executed evidence

- 267 tests passed in the complete native suite; in-process coverage is about 93%
  (see results/verification.json for the exact retained run). MCP subprocess
  execution is functionally tested but not included in in-process coverage.
- Offline hardened container suite: 267 tests passed; expanded MCP demo passed.
- Complete 180-trial MCP benchmark: C0/C2/C3/C4/C5 unsafe-trial counts
  22/14/9/4/0 out of 36 each. C5 completed all 16 legitimate tasks. All retained
  exports regrade consistently. Exact latencies, versions, seed, dataset digest
  and full evidence are in results/benchmark/.
- All 11 targeted enforcement and nine grader mutants detected. Labelled oracle
  fixture false acceptance 0/6, false rejection 0/2, invalid rejection 3/3.
- All 54 bounded schedule combinations executed; eight unsafe fingerprints,
  none C5. C3 stateful failure shrunk to three commands and independently
  replayed. C5 bounded campaign found no violation; no proof is claimed.
- A non-editable wheel installed in a fresh runtime-only environment and ran
  actual MCP demo/mutations/fuzz replay plus packaged-data/native benchmark checks
  outside the checkout, without pytest/Ruff runtime dependencies.
- Ruff check and format checks pass. No live model API call was performed;
  Inspect fixtures use explicit synthetic responses/usage through actual MCP.

## Reproduction

From `/workspace/scopeshift`, use Python 3.12.16 and `uv sync --locked`.
In managed Cloud export writable `UV_PYTHON_INSTALL_DIR`, `UV_CACHE_DIR` and
`MPLCONFIGDIR` as documented in docs/reproducibility.md. Honor the task-selected
checkout; do not automatically switch branches or create worktrees.

Run `uv run pytest`, `uv run scopeshift demo`, and the README's benchmark,
mutation, exploration, fuzzing and replay commands in fresh output directories.
The raw benchmark is compressed JSONL for compact independent regrading; transient
SQLite files live under ignored artifacts/. Serial replay is exact semantic
ledger comparison; concurrent replay compares declared effect/grade invariants.
The retained regression is tests/regression/c3-counterexample.json.

For Cloud TLS interception, build Docker with the optional public CA-bundle mount
shown in docs/reproducibility.md, then run `docker compose run --rm verify` and
`docker compose run --rm demo`. TLS and artifact hash verification remain enabled.
No model secrets or runtime network are required.

## Publication and limitations

No merge or visibility change is authorized. The complete review changes and
PR body are prepared; see docs/review-pr.md. Native Git works, but api.github.com
is currently rejected by the environment network policy. A restricted-domain
addition for api.github.com was saved in environment settings without adding
secrets or removing package-manager access. Saving it does not apply it to the
running instance. Actual PR creation and remote CI inspection require that access;
do not claim remote CI passed or invent a PR URL.

Live-model experiments remain unrun and require explicit spending authorization.
Multi-hop delegation/cascading revocation is a deferred extension. Related-work
paper leads are explicitly unverified; no novelty claim is based on them.
The model, synthetic-effect, trusted-host and finite-grammar limitations are
recorded in docs/limitations.md and reports/research.md.
