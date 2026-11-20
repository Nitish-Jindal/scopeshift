# ScopeShift development and verification handoff

Updated 2026-11-20 (Asia/Kolkata). The repository is public. PR #1 was merged
into `main` at `c1cbf657ab975369fe653ff99c304668d20758bc`:
https://github.com/Nitish-Jindal/scopeshift/pull/1.
The current documentation cleanup is explicitly authorized on `main`; future
work should follow the branch and scope requested by its task. Do not perform
additional merges or visibility changes without explicit authorization.

The independent review corrections extend the existing implementation; core
transaction architecture, actual two-server MCP, separate reference model and
competing SQLite connections are preserved. Read PROJECT_SPEC.md, AGENTS.md,
docs/authorization-contract.md and reports/verification.md before further work.

## Current verified corrections

Evidence schema 2 has explicit host-fixed/host-model/stateful/fixture modes.
Production grades require external scenario/mode contracts; stateful grades also
require external commands. Lifecycle, event sources/schema/run identity,
applicable scheduled transitions, responses, cancellations and unreachable paths
are mandatory and optimization-safe. Message approvals cannot be burned by
unrelated/non-message operations. Metrics separate proposals, dispatch/receipt,
committed effects, check errors, task noncompletion and actual delivered model
information. Unsupported model false-refusal quantities remain null. An
independent 100-case admission/effect/safety matrix covers the core configurations.

Current local suite: 423 passed; coverage 94.54%. Offline hardened Docker suite:
423 passed; expanded MCP demo passed. Ruff lint/format passed. Current MCP run:
180/180 valid schema-2 trials; unsafe trial counts C0/C2/C3/C4/C5 = 22/14/9/4/0
of 36 each; C5 completed 16/16 legitimate tasks. All exports regrade against
external dataset contracts. All 11 enforcement and nine grader mutants killed;
full replay 180/180 (170 exact, ten concurrent invariants). Stateful C3 failure
shrunk to three commands and replayed; finite C5 campaign found no counterexample.

See results/verification.json for exact current versus historical verification,
source digest, CI observations and retained evidence. Commit 18c50d46 had 267
passing tests and successful remote CI; those are historical checks, not current
schema-2 evidence. Its successful workflow is confirmed at:
https://github.com/Nitish-Jindal/scopeshift/actions/runs/44741335221.
The historical API-publication blocker was resolved; PR #1 is now merged and
API access is working. Verification links below refer to their recorded revisions.
Correction source 4683410e47e785f49bdc824afe6a853499b0245d passed both remote
workflows 44747732315 and 44747724360, including native and container jobs.
The verification-only follow-up preserves the recorded tested source digest.

## Reproduction and scope

Use Python 3.12.16 and `uv sync --locked`; the 36-case generated dataset remains
committed and reproducible. Honor the task-selected ref without automatic branch
switching or worktrees. For managed Cloud use writable UV/MPL paths from
reproducibility.md. Run `uv run pytest` and the README demo, benchmark, mutation,
exploration, fuzzing and replay commands with fresh output directories.

Current exports require schema 2; do not silently upgrade old raw evidence.
Regrading fixed exports requires `grade(evidence, scenario=trusted_contract,
mode="host-fixed-v2")`; stateful grading additionally requires trusted commands.
The retained three-command regression still replays through actual SQLite.

Docker uses an optional ephemeral public CA-bundle mount for managed TLS proxies;
verification is never disabled. Native execution is supported. Live paid model
inference remains unrun and unauthorized. Inspect cases use explicit mock outputs
through actual MCP. The adapter binds one scenario-selected identity/session/
grant/approval; broader dynamic authority discovery and multi-hop delegation are
outside its current supported scope. Finite tests and trusted observer evidence
are not protection against host compromise or general security proofs.
