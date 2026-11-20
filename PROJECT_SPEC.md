# ScopeShift — Complete Autonomous Project Implementation

## 1. Your Role and Execution Mandate

Act as a senior AI safety researcher, security engineer, distributed systems engineer, Python developer and evaluation infrastructure specialist.

Your task is to independently design, implement, test, debug, evaluate, document and deliver the complete ScopeShift project in one continuous development session.

You are authorized to proceed through all implementation milestones without awaiting separate approval from me.

Do not stop after producing a plan, architecture document, project scaffold or initial prototype. Proceed to actual implementation, testing, experiments and documentation.

Internally break the project into milestones, verify each component, fix discovered defects and continue automatically.

Prioritize a complete, genuinely working and independently reproducible research-grade MVP over unnecessary architectural complexity.

If a nonessential feature is blocked, document the limitation and continue implementing everything else. Ask me only when an essential external credential, permission or genuinely blocking decision is required.

The project is time-sensitive because it is intended for an upcoming AI safety research internship application.

## 2. Project Identity

**Project name:** ScopeShift

**Full title:** ScopeShift — A Temporal Authorization Consistency Benchmark for MCP-Enabled AI Agents

**Objective:** Build a reproducible AI security evaluation framework that investigates whether MCP-enabled LLM agents and their execution infrastructure preserve authorization correctness when permissions, consent, approvals and policy state change between tool discovery, request authorization and protected-effect commitment.

The central problem is stale authority: an operation may be authorized when approved but no longer authorized when its protected effect occurs.

ScopeShift must systematically reproduce, detect, measure and compare such failures.

## 3. Application Context

This project is intended as the flagship portfolio project for the Solumn AI Winter Internship, which values:

- Frontier AI safety evaluation.
- MCP and tool-use security.
- Containerized agentic environments.
- Deterministic grading.
- Model alignment.
- Adversarial evaluation.
- Executable verification.
- Fuzzing and testing infrastructure.
- Reproducibility.
- Rigorous software engineering.
- Original benchmarks and experimental findings.

The final project should demonstrate these capabilities through actual implementation and experimental evidence, not merely descriptions.

## 4. Verified Environment

Use the existing repository and verified development tools.

- macOS 15.7.4.
- Apple Silicon ARM64.
- 8 CPU cores.
- 8 GiB physical RAM.
- Approximately 11–12 GiB available disk space at preflight.
- Docker memory allocation approximately 3.82 GiB.
- Python 3.12.16, pinned using uv.
- uv 0.13.9.
- SQLite 3.53.1 available through the host Python interpreter.
- Docker 29.9.2.
- Docker Compose 5.6.1.
- Git and GitHub CLI authenticated.

Local repository: `~/Projects/scopeshift`

Remote repository: `https://github.com/Nitish-Jindal/scopeshift.git`

Initial branch: `main`

Initial commit: `4210a3b63aec69c77a378823b99a3f226c902718`

The repository is private.

Codex sandbox approval may be required for Git operations, network access, uv cache operations and Docker.

Use native ARM64-compatible dependencies and images. Minimize disk usage, build-cache duplication, container count and parallel execution.

Do not delete unrelated files, Docker resources or existing projects to reclaim storage.

## 5. Research Questions

**RQ1:** Under which controlled policy transitions and event interleavings do MCP-enabled agents and their execution infrastructure permit stale-authority effects?

**RQ2:** How does authorization enforcement at different execution boundaries affect security, legitimate task utility and execution overhead?

**RQ3:** Can systematic schedule exploration, independent effect-level grading and stateful fuzzing discover temporal authorization failures missed by conventional static evaluations?

**Supporting question:** How effectively can independently specified fixtures and mutation testing identify weaknesses in the benchmark's authorization oracle?

## 6. Research Positioning

ScopeShift does not claim to invent continuous authorization, temporal access control, concurrency testing, state machines, mutation testing or property-based testing.

Its proposed contribution is an executable methodology combining:

- Actual MCP communication.
- Temporal authorization contracts.
- Deterministic semantic event scheduling.
- Controlled authorization-to-effect race conditions.
- Independent effect-level grading.
- Transactionally consistent authorization enforcement.
- Gateway and grader mutation testing.
- Stateful counterexample discovery and minimization.

Related-work leads include AgentDojo, AgentCap, AuthorizationBench, GatewayBench, MCP Security Bench, UCON, CHESS, Coyote, formal MCP safety verification and execution-finality authorization literature.

Verify primary sources before citing their details. Clearly label unverified references. Do not fabricate papers, citations or novelty claims.

Do not spend excessive time on the literature review at the expense of implementation.

## 7. Required Architecture

Implement the following logical components in one maintainable Python repository.

### Component A — Containerized MCP Environment

Implement actual MCP client-server communication using the official MCP Python SDK.

Create two lightweight synthetic MCP servers exposing approximately three to five tools, such as:

- `read_document`
- `search_documents`
- `get_record`
- `update_record`
- `send_message`

Use synthetic enterprise documents, records, identities and recipients.

Include reproducible environment initialization and reset, controlled tool access, resource restrictions and trusted execution evidence.

Do not expose arbitrary shell execution or uncontrolled external network effects to evaluated agents.

Docker is used for reproducibility and scoped containment, not as proof of absolute security.

### Component B — Versioned Policy Authority

Implement authoritative authorization state containing:

- Principals and agents.
- Sessions.
- Resources and actions.
- Canonicalized operation arguments.
- Delegated task scope.
- Grant identifiers.
- Grant generations and revocations.
- Policy versions.
- Approval records.
- Approval expiry and consumption.
- Logical event time.
- Request identities.

Use SQLite as the authoritative consistency domain.

Principal and session identities must originate from trusted execution context, not freely chosen model arguments.

### Component C — Configurable Authorization Gateway

Implement six experimental configurations:

**C0 — Ambient authority:** No additional application-level authorization enforcement. Physical containment and trusted effect observation remain active.

**C1 — Prompt-level safeguards:** Authorization constraints communicated through model instructions without additional runtime application-level enforcement.

**C2 — Static session permissions:** Authorization evaluated using a snapshot captured at session initialization.

**C3 — Dynamic invocation-time authorization:** Current authorization checked before forwarding an MCP tool request.

**C4 — Non-atomic effect-time rechecking:** Current authorization checked again near the effect boundary, but validation and protected-effect commitment remain separate operations.

**C5 — Atomic effect-boundary authorization:** Current authorization validation and protected-effect commitment occur within the same transactional consistency boundary.

All configurations must retain the same underlying environment, normative scenario contracts and trusted evidence collection.

C0–C4 must not be accidentally protected by C5 enforcement. Deliberately insecure configurations must genuinely be capable of producing unauthorized synthetic effects.

C1 must be distinguished from other configurations in deterministic replay because replaying fixed requests cannot measure prompt-level model compliance.

### Component D — Protected Effect Sink

Implement observable protected effects, including:

- Durable database record updates.
- Synthetic message delivery.
- Controlled information-disclosure events.

For the C5 reference implementation, use an appropriate SQLite transaction, such as `BEGIN IMMEDIATE`, covering:

1. Reading authoritative current policy state.
2. Re-evaluating the concrete operation.
3. Consuming single-use approval where required.
4. Applying the protected state change.
5. Recording the corresponding committed effect.
6. Committing the transaction.

Revocation and protected mutations must participate in the same serialized transactional consistency domain.

Specify rollback behavior, connection ownership, bounded retries and handling of database contention.

Do not equate checking twice with atomic enforcement.

Do not claim that SQLite makes real-world network transmissions or external email delivery atomic.

For protected reads, either implement a defensible controlled disclosure boundary or restrict atomicity claims to durable local mutations and synthetic message commitments. Document exactly what is and is not guaranteed.

### Component E — Deterministic Semantic Event Scheduler and Replay

Implement explicit checkpoints, synchronization barriers and logical event ordering around:

- Session initialization.
- Tool discovery.
- Request generation.
- Gateway authorization.
- MCP dispatch.
- Server receipt.
- Optional non-atomic effect-time recheck.
- Protected-effect attempt.
- Effect commitment or blocking.
- Tool response.
- Request completion.

Support controlled grant, revocation, expiry, approval and policy-change events.

Do not rely on arbitrary sleeps to create security races.

Implement actual controlled execution with independent transactions or connections where necessary, not merely a simulation that returns the desired outcome.

Distinguish valid event interleavings from impossible histories.

C5 must not expose an artificial checkpoint that permits revocation to commit inside an atomic transaction. Instead, test which competing transaction becomes authoritative first.

Implement:

- Seeded execution.
- Serializable schedules.
- Deterministic infrastructure replay.
- Replay of recorded agent requests.
- Bounded schedule exploration.
- Causal event constraints.
- Reproducible counterexamples.

Do not claim deterministic LLM inference.

### Component F — Trusted Evidence Ledger

Implement structured, versioned evidence containing relevant fields such as:

- Run, scenario and configuration identifiers.
- Event identifiers and logical sequence.
- Request identifiers.
- Principal, agent and session.
- Grant and approval identifiers.
- Action and resource.
- Canonical argument digest.
- Policy generation.
- Authorization decision.
- Event source.
- Causal dependencies.
- Committed effect identity and status.

Distinguish attempted, approved, denied, dispatched, received, executed, blocked, rolled-back and committed operations.

Trusted effect evidence must not depend exclusively on the gateway's claims.

Policy transitions and committed mutation evidence should be consistent with actual database state.

A rolled-back operation must not appear as a committed effect.

### Component G — Independent Reference Model and Grading Oracle

Implement a separately designed authorization state machine and deterministic oracle.

The oracle must not import or reuse the gateway's authorization implementation as its normative ground truth.

Shared neutral data structures are acceptable. Shared enforcement predicates are not.

The oracle must independently evaluate:

- Actual authorization state at relevant event boundaries.
- Requested operations.
- Committed effects.
- Current grant and approval validity.
- Legitimate task completion.
- Session and principal binding.
- Evidence integrity.
- Final resource state.
- Intermediate unauthorized effects, including effects later compensated or reversed.

Return separate grades for:

- Agent-observable authorization compliance.
- Enforcement correctness.
- Actual effect safety.
- Legitimate task completion.
- Evaluation integrity.
- Overall outcome.

Missing, malformed or inconsistent evidence must produce an invalid or inconclusive evaluation outcome rather than an automatic safety pass.

An agent that refuses every legitimate operation must not receive a perfect overall grade.

### Component H — Gateway and Grader Mutation Testing

Implement deliberate enforcement mutations, including representative defects:

- Skip required effect-time checks.
- Use stale policy state.
- Ignore revocation.
- Ignore session binding.
- Ignore principal binding.
- Ignore resource restrictions.
- Ignore approval expiry.
- Ignore canonical argument binding.
- Permit duplicate single-use approval consumption.
- Introduce a non-atomic authorization-to-effect gap.
- Reject all operations after unrelated policy updates.

Implement independent oracle mutations, including:

- Ignore committed effects.
- Grade using stale policy versions.
- Treat gateway denial as conclusive proof of safety.
- Ignore event ordering.
- Ignore session identity.
- Ignore approval validity.
- Ignore duplicate effects.
- Confuse attempted and committed operations.
- Treat missing evidence as a pass.

Run the applicable validation suite against these mutations.

Report killed, survived, invalid and equivalent mutants where distinguishable.

Do not silently remove surviving mutants to inflate the mutation score.

### Component I — Authorization-Aware Stateful Differential Fuzzer

Use Hypothesis rule-based state machines and controlled event-sequence generation.

Generate valid combinations of:

- Grants.
- Revocations.
- Session changes.
- Policy narrowing.
- Unrelated policy changes.
- Approval issuance and expiry.
- Concurrent requests.
- Dispatch.
- Effect attempts.
- Retries and duplicate requests.

Check the independent reference-model invariants against observed behavior.

Implement seeded reproducibility, schedule serialization, failure shrinking, deduplication and automatic regression-artifact preservation.

Compare static testing, manually authored schedules, bounded exploration and stateful testing.

Use explicit resource and exploration limits.

The fuzzer should discover meaningful authorization counterexamples rather than generate arbitrary prompt noise.

## 8. Mandatory Authorization Semantics

Formalize and document the normative authorization contract before implementing enforcement.

A protected effect may commit only when the concrete operation is authorized under the applicable authoritative policy at the effect commitment point.

Implement the following semantics:

1. Deny by default where authorization enforcement applies.
2. Revocation committed before an effect invalidates applicable revoked authority.
3. Revocation committed after an effect does not retroactively invalidate that effect.
4. Unrelated policy-version changes must not automatically invalidate otherwise permitted actions.
5. Relevant policy changes require re-evaluating the concrete operation.
6. Permissions bind principals, sessions, actions, resources and applicable arguments.
7. Approvals bind the intended operation and applicable identity.
8. Expired and consumed single-use approvals cannot authorize new effects.
9. Concurrent requests cannot consume one single-use approval multiple times.
10. Revocation followed by regranting does not revive a revoked grant identifier.
11. Retries and duplicates have explicit request identity and idempotency semantics.
12. Expiry equality boundaries must be precisely defined.
13. Delegation must be attenuated and cascading revocation explicitly specified if implemented.

Mark delegation as a documented extension if it cannot be implemented correctly within the initial MVP.

Distinguish benchmark-specific policy choices from general MCP protocol guarantees.

## 9. Threat Model

In scope:

- Malicious synthetic documents and tool responses.
- Direct and indirect prompt injection.
- Stale tool metadata.
- Unauthorized agent-proposed tool calls.
- Stale and revoked authority.
- Approval reuse.
- Cross-session authority attempts.
- Modified operation arguments.
- Repeated and concurrent requests.
- Controlled policy changes during in-flight operations.

Trusted:

- Host and container runtime.
- Authoritative policy state.
- Scheduler.
- Trusted effect observation infrastructure.
- Reference scenario contracts.
- Independent evaluation artifacts.

Out of scope:

- Host or kernel compromise.
- Arbitrary hostile native code execution.
- Malicious bypass of the trusted effect sink.
- Compromise of the authoritative policy service.
- Real user credentials and confidential records.
- Uncontrolled external effects.
- General distributed transaction guarantees.

Document the boundary between MCP transport authorization and application-level authorization.

## 10. Benchmark Dataset

Create a versioned, machine-readable scenario dataset.

Target at least 8–12 meaningful scenario templates and 20–40 executable variants, prioritizing correctness and diversity over arbitrary counts.

Include the following families:

1. Authorized operation without policy changes.
2. Unauthorized operation without policy changes.
3. Revocation before session initialization.
4. Revocation after tool discovery.
5. Revocation after gateway approval.
6. Revocation after server receipt.
7. Revocation after C4 non-atomic rechecking.
8. Revocation after effect commitment.
9. Unrelated policy-version change.
10. Relevant permission narrowing.
11. Irrelevant permission narrowing.
12. Revocation followed by regranting.
13. Cross-session grant reuse.
14. Approval expiry.
15. Approval argument mismatch.
16. Concurrent single-use approval consumption.
17. Duplicate requests and retries.
18. Agent-visible versus infrastructure-only revocation.
19. Controlled malicious tool-response scenarios.
20. Delegation revocation, if implemented.

Include matched benign controls and task-utility checks.

Each scenario must define the initial state, legitimate objective, principal/session, authorization contract, protected resources, event schedule, expected outcomes, visible information, applicable invariants and independently derived ground truth.

Create hand-labelled positive and negative fixtures before relying on automated grading.

The oracle must correctly distinguish an agent that knowingly exceeds visible authorization from one that cannot observe a hidden revocation.

## 11. Mandatory Demonstration

Produce a runnable demonstration that reproduces the following:

1. Permission is granted.
2. The agent requests an operation.
3. The gateway approves it.
4. Applicable permission is revoked.
5. The protected effect is attempted.

Expected behavior:

- C3 can commit an unauthorized synthetic effect.
- The independent oracle detects the violation.
- C5 prevents the effect under the same applicable schedule.

Also reproduce:

- C4 committing an unauthorized effect when revocation occurs after its non-atomic recheck.
- C5 permitting a legitimate operation.
- C5 permitting an otherwise valid operation after an unrelated policy update.
- A deliberately mutated enforcement implementation being detected.
- A deliberately mutated grader being detected.
- A stateful counterexample being minimized and replayed.

These are expected experimental behaviors, not predetermined results to fabricate.

If actual results differ, investigate and correct the implementation or transparently report the discrepancy.

## 12. Experimental Methodology

Conduct three separate experimental tracks.

### Track A — Live LLM Evaluation

Integrate Inspect AI and an appropriate tool-using model adapter.

Evaluate model behaviour through actual MCP tools.

Support configuration through environment variables and documented provider settings.

If legitimate model API access is already available, run a bounded live evaluation with explicit cost limits.

If model credentials or credits are unavailable:

- Complete the actual model integration.
- Provide an opt-in live evaluation command.
- Test the adapter using controlled fixtures.
- Run the complete deterministic benchmark.
- Explicitly report that live model evaluation has not been executed.

Do not substitute scripted agents for live LLM results or access unrelated stored credentials.

### Track B — Deterministic Infrastructure Evaluation

Run fixed requests and controlled schedules across C0, C2, C3, C4 and C5.

Measure actual effects and compare them against the independent normative oracle.

Support C1 through the live model track.

Target at least 100 meaningful deterministic evaluation executions if practical.

Collect exact counts, denominators, configurations, schedules, evidence and reproducible results.

### Track C — Benchmark Reliability

Evaluate:

- Independently labelled fixtures.
- Gateway mutation detection.
- Grader mutation detection.
- Static scenarios.
- Hand-authored temporal scenarios.
- Systematic bounded exploration.
- Stateful fuzzing and failure minimization.

Use comparable exploration budgets where appropriate.

Report any surviving mutants, invalid evaluations and unresolved failures.

## 13. Metrics

Implement well-defined metrics with correct units and denominators:

- Unauthorized attempt rate.
- Unauthorized execution rate.
- Unauthorized protected-effect rate.
- Stale-authority effect rate.
- Revocation effectiveness.
- Authorization consistency.
- Legitimate task-completion rate.
- Safe task-completion rate.
- False refusal rate.
- Enforcement false-denial rate.
- Oracle false-acceptance and false-rejection rates.
- Invalid or inconclusive evaluation rate.
- Gateway mutation detection rate.
- Grader mutation detection rate.
- Distinct schedules explored.
- Distinct validated counterexamples.
- Replay consistency.
- Execution latency and overhead.
- Live-model token usage where available.

Explicitly handle zero denominators.

Distinguish event, request, effect and trial-level measurements.

Do not report inappropriate confidence intervals for exhaustive deterministic cases or treat correlated events within the same trajectory as independent samples.

Produce tables and charts based on actual measured results.

## 14. Technology Stack

Use:

- Python 3.12.16.
- uv.
- Official MCP Python SDK.
- Inspect AI.
- Docker and Docker Compose.
- SQLite.
- Pydantic.
- pytest.
- Hypothesis.
- Ruff or equivalent lightweight linting.
- Explicit state machines.
- Targeted mutation testing.
- GitHub Actions.
- Matplotlib and lightweight statistical tooling where useful.

Verify compatible dependency versions and commit a reproducible lockfile.

Avoid unnecessary heavy dependencies, Kubernetes, Redis, PostgreSQL, large local models and frontend development.

Do not install global packages when project-local dependencies suffice.

## 15. Repository Structure

Use a maintainable src-layout, approximately:

```text
scopeshift/
├── AGENTS.md
├── README.md
├── PROJECT_SPEC.md
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── .env.example
├── LICENSE
├── Dockerfile
├── compose.yaml
├── src/scopeshift/
│   ├── contracts/
│   ├── policy/
│   ├── gateway/
│   ├── mcp/
│   ├── effects/
│   ├── events/
│   ├── scheduler/
│   ├── replay/
│   ├── reference_model/
│   ├── oracle/
│   ├── scenarios/
│   ├── mutations/
│   ├── fuzzing/
│   ├── evaluation/
│   ├── metrics/
│   └── cli.py
├── scenarios/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── concurrency/
│   ├── oracle/
│   ├── mutation/
│   └── regression/
├── experiments/
├── results/
├── reports/
├── docs/
├── scripts/
└── .github/workflows/
```

Adjust module organization where justified, avoiding empty directories and unnecessary abstraction.

Keep specification documents concise, internally consistent and directly relevant to the implementation.

## 16. CLI and Reproducibility

Provide a usable command-line interface with commands equivalent to:

```bash
uv sync --locked
uv run pytest
uv run scopeshift demo
uv run scopeshift benchmark
uv run scopeshift replay
uv run scopeshift explore
uv run scopeshift mutate
uv run scopeshift fuzz
uv run scopeshift report
```

Implement a documented one-command deterministic benchmark workflow.

Provide a reproducible Docker Compose workflow.

Provide optional live inference commands separately.

All documented commands must correspond to actual working functionality.

Verify the quickstart yourself.

Do not present unimplemented commands as available features.

## 17. Automated Verification and CI

Implement meaningful tests covering:

- Authorization semantics.
- Actual MCP communication.
- Both transaction-ordering outcomes.
- Revocation races.
- C4 versus C5 behavior.
- Policy-update transparency.
- Identity and session boundaries.
- Approval expiry and consumption.
- Idempotency.
- Concurrent transactions.
- Independent oracle behavior.
- Malformed and missing evidence.
- Gateway mutations.
- Oracle mutations.
- Stateful regression cases.
- Environment reset.
- CLI behavior.
- Containerized execution.

Aim for substantial coverage rather than inflated test counts.

Run linting, automated tests, relevant integration tests and the actual benchmark.

Fix failures before declaring the corresponding component complete.

Add GitHub Actions that automatically run relevant checks without requiring model API credentials.

Do not claim remote CI success unless the actual workflow has completed successfully.

## 18. Research Report and Documentation

Generate:

- A professional GitHub README.
- Architecture and trust-boundary diagrams.
- Formal authorization semantics and invariants.
- Threat model.
- Event and transaction specifications.
- Independent oracle design.
- Scenario documentation.
- Experimental methodology.
- Actual results and analysis.
- Mutation-testing report.
- Fuzzing and counterexample report.
- Reproducibility instructions.
- Related-work positioning.
- Limitations and future extensions.

The README should prominently include:

1. The stale-authorization problem.
2. The research contribution.
3. An architecture diagram.
4. C0–C5 comparison.
5. Actual measured results.
6. A reproducible demonstration.
7. Installation and quickstart.
8. The independent oracle architecture.
9. Testing and mutation evidence.
10. Limitations.

Generate a research-style report under `reports/`.

Use clear charts and tables derived from real execution data.

Do not fabricate model results, scientific novelty, performance measurements or external vulnerabilities.

Add a short demonstration script and interview-oriented technical walkthrough.

Use an appropriate open-source license, documenting the choice.

## 19. Autonomous Implementation Workflow

Proceed automatically through these internal milestones:

1. Inspect the existing repository and validate the environment.
2. Write concise formal specifications and hand-labelled ground truth.
3. Initialize project dependencies and development tooling.
4. Implement the policy authority and trusted effect environment.
5. Implement actual MCP servers and client.
6. Implement all authorization configurations.
7. Implement deterministic scheduling and replay.
8. Implement the independent reference model and oracle.
9. Implement the scenario dataset.
10. Build and run positive and negative verification suites.
11. Implement and execute mutation testing.
12. Implement and execute bounded exploration and stateful fuzzing.
13. Implement optional Inspect AI live-model integration.
14. Execute deterministic comparative experiments.
15. Execute live-model experiments only if legitimate access is available.
16. Analyze measured results.
17. Complete Docker integration and CI.
18. Conduct a critical security and correctness audit.
19. Fix discovered defects and rerun verification.
20. Complete research documentation and demonstration.
21. Commit and push the completed implementation to a dedicated review branch.

Do not stop between milestones to request my approval unless an actual permission prompt or unavoidable blocker requires it.

Maintain an implementation checklist in the repository so work can be resumed without losing progress if context or execution limits are reached.

If execution limits approach, prioritize preserving a runnable, verified project rather than leaving many incomplete components.

## 20. Final Independent Self-Audit

Before declaring completion, act as a skeptical external security reviewer rather than the original implementation author.

Specifically investigate:

- Whether the baseline configurations are accidentally protected.
- Whether C5 genuinely uses transactional coupling.
- Whether concurrent revocation tests exercise actual contention.
- Whether scheduler checkpoints manufacture impossible event histories.
- Whether the oracle shares enforcement logic.
- Whether logged effects match actual environment changes.
- Whether unauthorized effects can be hidden by subsequent updates.
- Whether legitimate operations are unnecessarily denied.
- Whether missing evidence incorrectly passes grading.
- Whether mutation tests genuinely detect defective behavior.
- Whether minimized counterexamples can be independently replayed.
- Whether all reported metrics are calculated from real raw results.
- Whether the documented quickstart works.
- Whether Docker and dependency versions are reproducible.
- Whether security and novelty claims are supported by evidence.
- Whether secrets or sensitive information entered tracked files.

Fix substantive problems and rerun the relevant verification suite.

Clearly distinguish self-audit from external independent review.

## 21. Git and Publication

Create and work on a dedicated branch such as:

`feat/scopeshift-complete-mvp`

Make logical commits as useful for preserving verified milestones.

After completing tests and reviewing the diff, commit and push the implementation to that branch.

Create a pull request against main if GitHub access permits.

Keep the repository private.

Do not merge the pull request or change repository visibility. Final independent review will occur before publication.

Do not commit:

- API keys.
- Credentials.
- Personal data.
- Virtual environments.
- Large dependency caches.
- Sensitive machine-specific logs.
- Unnecessary generated artifacts.

Preserve compact raw experiment results and appropriate reproducibility evidence.

## 22. Definition of Done

The project is application-ready when:

- Actual MCP communication works.
- All six authorization configurations are implemented or explicitly supported by their applicable evaluation mode.
- Controlled revocation races are reproducible.
- C3 and C4 failures can be observed and independently graded.
- C5 prevents the corresponding prohibited local effects.
- Legitimate operations and unrelated policy updates remain functional.
- The independent oracle is validated against independently specified positive/negative fixtures.
- Gateway and grader mutation testing has been executed.
- Stateful fuzzing and bounded exploration have been executed.
- Deterministic counterexamples can be replayed.
- Automated tests have been run.
- Actual experimental results are preserved.
- Docker execution has been verified, or any hardware-related blocker is explicitly reported.
- CI and reproducibility documentation are present.
- Live-model support is implemented, with actual live experiments accurately reported as executed or pending.
- The repository contains no misleading completion claims.
- The project has been committed and pushed for review.

Treat partial or unverified features honestly.

## 23. Final Completion Report

Return a structured completion report containing:

1. Executive summary.
2. Implemented components and any incomplete components.
3. Architecture and key technical decisions.
4. Actual MCP verification evidence.
5. Automated test results and coverage, where measured.
6. Controlled temporal authorization results for C0–C5, with applicability explained.
7. Gateway mutation results.
8. Grader mutation results.
9. Fuzzing and bounded exploration results.
10. Independently reproducible counterexamples.
11. Security and utility measurements.
12. Docker verification.
13. Live LLM evaluation status.
14. CI status.
15. Security self-audit findings and corrections.
16. Remaining limitations.
17. Exact quickstart and demonstration commands.
18. Git branch, commit hash and pull-request URL.
19. A short description suitable for an internship application.
20. Final verdict: APPLICATION-READY, APPLICATION-READY WITH LIMITATIONS, or INCOMPLETE.

Do not merely tell me how you would implement the project. Implement it and provide actual evidence.

Begin now and continue autonomously until the project has been implemented and verified as far as the available environment and permissions permit.
