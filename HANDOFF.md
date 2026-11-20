# ScopeShift — work-in-progress Cloud handoff

Checkpoint date: 2026-11-20 (Asia/Kolkata).
Branch: `codex/scopeshift-complete-mvp`.
Base: `4210a3b63aec69c77a378823b99a3f226c902718` (initial repository).
Remote: `https://github.com/Nitish-Jindal/scopeshift.git` (private).

**Status: INCOMPLETE. Source has been written, but no benchmark component has
passed executable verification. This is a preservation checkpoint, not a release.**

The user explicitly requested migration to Codex Cloud due to local hardware
limitations. After this WIP commit is pushed and its remote SHA verified, local
implementation must remain paused to prevent conflicting changes. Do not merge
main, change visibility, discard unfinished work, or interpret this handoff as
completion of the original project. The full original scope is unchanged.

## Authoritative instructions

1. Read `AGENTS.md` and the **full verbatim** 23-section master in
   `PROJECT_SPEC.md`. The original specification was recovered directly from the
   user's chat reply, not reconstructed from a summary.
2. Read `docs/authorization-contract.md`: the concise normative design was
   written before enforcement code and is preserved here after the full master
   replaced the earlier abbreviated PROJECT_SPEC.md.
3. Continue the requirement checklist in `docs/checklist.md`.
4. The latest user steering authorizes only this local preservation/push/pause;
   continue development in Cloud when the user initiates the continuation.

## Completed artifacts and written source (not runtime-verified components)

- Full master specification, persistent engineering instructions, initial
  normative semantics and resumable checklist are saved.
- Python is pinned to 3.12.16 in `.python-version`; src-layout `pyproject.toml`
  defines dependencies, dev checks and an **unimplemented** CLI entry point.
- `uv.lock` was generated: 109 resolved packages. Selected locked versions:
  MCP 1.30.0, Inspect AI 0.3.291, Pydantic 2.14.4, Hypothesis 6.170.16,
  pytest 9.2.0, Ruff 0.17.6, Matplotlib 3.11.2. Resolution succeeded;
  installation and cross-platform compatibility have not been verified.
- `src/scopeshift/contracts.py`: Pydantic identity/operation/scenario/transition
  contracts, canonical JSON, argument hashing, C0–C5 enum and checkpoint names.
- `src/scopeshift/storage.py`: SQLite schema, connection-owned BEGIN IMMEDIATE
  transactions, policy mutation, version/time, request/effect storage,
  hash-linked event append, initialization and export. A prototype checkpoint
  method performs scheduled policy transitions through separate transactions.
- `src/scopeshift/policy.py`: enforcement predicate for grant identity/action/
  resource/arguments, revocation and approval binding/expiry/consumption;
  candidate mutation switches are embedded but have not been exercised.
- `src/scopeshift/gateway.py`: trusted request registration, ID conflict
  handling and C0/C1/C2/C3+ invocation paths. End-to-end trusted context creation
  is still absent.
- `src/scopeshift/effects.py`: candidate synthetic record/message/disclosure
  sink; C4 separate recheck; C5 transactional validation/effect/evidence;
  idempotent result lookup; rollback event handling; five synthetic action
  implementations. There are **no MCP server/client implementations yet**.
- `scripts/build_dataset.py`: proposed scenario generator with 34 variants
  covering controls, revocation timing, identity, approval, retry, read and
  injection cases. It has **not run successfully** and no dataset JSON exists.
- `tests/oracle/fixtures.json`: hand-labelled predicate cases plus intended
  evidence outcomes, written before an oracle exists. These are data, not an
  implemented validation suite. Evidence fixtures still need actual histories.
- `.gitignore` excludes .venv, caches, .env, databases and bulky artifacts;
  `.env.example` contains placeholder provider settings only.

## Architecture decisions to preserve and validate

- SQLite is the single serialized policy/effect consistency domain. Every
  transaction owns/closes its connection; BEGIN IMMEDIATE and a 2-second busy
  timeout are used. No application-level replay of partially executed effects.
- C0 ambient and C1 prompt-only bypass application enforcement. C2 uses a
  session snapshot, C3 current invocation checks, C4 an additional separate
  effect check, C5 validation plus approval consumption and synthetic commitment
  in one transaction. Preserve the deliberately insecure baselines.
- Request identity binds the entire concrete operation. Equal request IDs with
  identical content should return a committed result without another effect;
  mismatching content should be rejected. New IDs are new operations.
- Grants are immutable identifiers; regrant creates a new identifier. Relevant
  narrowing increments generation. Expiry is exclusive: `time < expires_at`.
- The planned independent reference model/oracle must import no enforcement
  predicate. Neutral contracts may be shared. Reconstruct policy from ordered
  transitions, inspect committed effect history, check final resources and
  ledger integrity, and keep observable agent compliance separate from hidden
  revocation effects. No oracle implementation has been written.
- Planned MCP transport is two official-SDK stdio subprocess servers sharing
  the scoped run database; model tools must not select principal/session.
- No scheduler checkpoint may enter a C5 effect transaction. Real competing
  connections/transactions must establish both commitment orderings. Do not
  claim the prototype scheduler already validates causal feasibility.
- Controlled disclosure means a local synthetic disclosure commitment; SQLite
  does not make remote delivery or model knowledge atomic/revocable.
- Multi-hop delegation/cascading revocation is an explicitly deferred extension.
- Live inference remains opt-in. No model API charges have been authorized or
  incurred; no unrelated credentials were accessed.

## Actual commands and results so far

| Check | Observed result |
| --- | --- |
| Initial repository | Clean main, only README.md and .python-version |
| GitHub metadata | Private, main only, no issues; push permission reported |
| `uv python find 3.12.16` | Found pinned interpreter after approved cache access |
| `docker info --format '{{.ServerVersion}}'` | 29.9.2 after approved daemon access; no container run |
| `uv sync` | FAILED during editable wheel build: missing forced include `scenarios/dataset.json`; resolved 109 packages first |
| Dataset generator via Python 3.12.16 with PYTHONPATH=src | FAILED: `ModuleNotFoundError: No module named 'pydantic'` |
| `uv sync --locked` retry | FAILED again: missing `scenarios/dataset.json` |
| Handoff syntax-only validation | Host Python AST parsed all 7 Python source/generator files; no imports or execution |
| Handoff data parse validation | fixtures JSON, pyproject TOML and uv.lock TOML parsed successfully |
| Full master preservation | All 23 numbered sections present; exact text compared with the recovered user reply |
| Ruff | NOT RUN |
| pytest / coverage | NOT RUN; no Python tests exist yet |
| Actual MCP transport | NOT IMPLEMENTED / NOT VERIFIED |
| Deterministic benchmark, demo, replay, mutations, fuzzing | NOT IMPLEMENTED / NOT RUN |
| Inspect live model / adapter fixture evaluation | NOT IMPLEMENTED / NOT RUN |
| Docker build / Compose | NOT IMPLEMENTED / NOT RUN |
| CI | No workflow yet; no remote CI success claimed |

Local `.venv` exists as an incomplete, ignored environment (approximately 60 KiB
at handoff). Do not migrate or commit it. Package downloads may exist in uv's
external cache; they are not repository artifacts and should not be deleted as
part of this handoff.

## Known defects and important unverified risks

1. **Packaging bootstrap cycle:** pyproject wheel force-includes
   `scenarios/dataset.json`, which has not been generated. The generator imports
   contracts/Pydantic, but dependencies have not installed because project build
   fails. Break this cycle in Cloud before claiming a working environment.
2. `scopeshift` entry point targets missing `scopeshift.cli`; every advertised
   command remains a requirement, not current functionality.
3. No execution engine captures session snapshots, drives all checkpoints,
   registers trusted requests, collects responses or orchestrates MCP transport.
4. Checkpoint scheduling currently accepts arbitrary names and does not validate
   causal constraints/impossible histories or concurrent firing. Completion and
   blocked/rolled-back paths need comprehensive event-protocol validation.
5. C4 rechecks happen before the idempotent committed-result lookup in `commit`;
   a revoked retry may be blocked instead of returning its existing result.
   Test and reconcile retry semantics across every configuration.
6. The generator's `approval_two_requests` uses repeats/new IDs, **not true
   concurrent transactions**. Add real barrier-controlled contention tests and
   concurrent benchmark variants; do not label sequential calls as concurrency.
7. Rollback/contention handling is untested; logging a rollback opens another
   write transaction, which can itself contend. Validate bounded failures and
   ensure no rolled-back effect is recorded as committed.
8. `commit` is a low-level trusted function; normal call paths must guarantee
   request registration/operation binding and physical containment. Trusted
   principal/session provenance is not yet implemented end to end.
9. Mutation switches are candidate implementation paths only. All 11 required
   enforcement families and 9 grader mutants still need validation and honest
   killed/survived/invalid/equivalent reporting.
10. Fixture labels are authored independently but are not yet executable full
    evidence fixtures. Implement final-state/compensated-effect/missing-evidence
    cases before trusting aggregate grades.
11. Dataset expected labels, malicious-response handling and all candidate
    security guarantees remain unverified. The README is still the original
    two-line description; no research results exist.

## Exact continuation instructions for Codex Cloud

The following are **continuation/setup instructions**, not claims of previously
successful quickstart commands. Use the Cloud checkout location, not local Mac
paths. Recheck Cloud tool/network/Docker capabilities and native architecture;
the master's ARM64 details describe the original local environment.

```bash
git fetch origin
git switch codex/scopeshift-complete-mvp
git pull --ff-only origin codex/scopeshift-complete-mvp
git status --short --branch
git log -1 --oneline
cat AGENTS.md
cat HANDOFF.md
cat PROJECT_SPEC.md
```

First address the packaging bootstrap without discarding existing source:

```bash
uv sync --locked --no-install-project
PYTHONPATH=src .venv/bin/python scripts/build_dataset.py
uv sync --locked
```

This proposed sequence installs dependencies before building the editable
project; it has **not** been executed here. If it fails, inspect the actual error
and fix the packaging/generator with a reproducible solution. Keep the generated
versioned scenario dataset tracked and verify it matches its generator.

Then proceed autonomously through the unchanged master scope:

1. Validate written contracts, storage, policy and effects with real positive
   and negative unit/transaction tests; fix semantics and candidate defects.
2. Implement actual two-server MCP client/server transport and trusted-context
   request binding; add environment initialization/reset and all five tools.
3. Implement the execution engine, causal schedule validation, snapshots,
   deterministic replay, both real contention orderings, C0–C5 behavior and C1
   applicability distinction.
4. Build a separately specified reference state machine/oracle and executable
   labelled evidence fixtures. Inspect effects independently of gateway claims.
5. Validate/expand dataset and matched controls; add genuine concurrent approval
   scenarios and visible-versus-hidden compliance cases.
6. Implement CLI, targeted gateway/grader mutations, bounded exploration,
   Hypothesis RuleBasedStateMachine shrinking/deduplication/replay, and Inspect
   AI model integration tested with fixtures. Do not spend on live APIs.
7. Run Ruff, pytest, integration/concurrency/oracle/mutation/regression checks;
   execute >=100 meaningful deterministic trials and reliability tracks.
8. Preserve compact raw evidence; calculate scoped metrics with denominators,
   charts and research report from actual runs. Implement Docker/Compose and
   credential-free GitHub Actions; verify quickstart and Docker in Cloud.
9. Conduct the master skeptical self-audit, correct defects and rerun relevant
   verification. Complete README, diagrams, docs, demo, interview walkthrough
   and license. Update checklist with exact evidence.
10. Commit/push further work on this same review branch and create a PR against
    main when appropriate. Never merge or change repository visibility. Report
    actual remote CI status and all limitations; complete the full final report.

## Preservation/security review

Only project source, synthetic fixtures, specification, engineering documents,
dependency metadata/lockfile and placeholder environment configuration belong in
the WIP commit. `.venv`, Python caches and `.env` are ignored. No real keys,
credentials, personal records, database runs, experiment outputs or unrelated
files were intentionally added. A staged-file/pattern review and diff check are
performed before committing; a hash-linked evidence ledger alone must never be
described as protection against compromise of the trusted host.

The WIP commit message identifies this checkpoint. Its SHA is obtained using
`git rev-parse HEAD` and compared with `git ls-remote origin
refs/heads/codex/scopeshift-complete-mvp` after push; it cannot be embedded in its
own committed content. No release or completion PR is being claimed here.
