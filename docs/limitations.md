# Limitations and future extensions

- The 36 scenarios and 54 enumerated schedules cover a finite synthetic grammar.
  They do not establish C5 safety for arbitrary authorization systems or all schedules.
- SQLite serializes policy and local effects in one database. Cross-service
  network delivery, remote messages and revocable model knowledge are not atomic.
- C0–C4 deliberately retain policy gaps. Do not deploy them as secure gateways.
- C1's adapter is implemented and fixture-tested, but no live LLM/API evaluation
  was authorized or run. Scripted fixtures say nothing about actual LLM compliance.
- The independent oracle shares neutral serialization/contracts, not enforcement
  logic. Independence is architectural, not an external independent human review.
- Hash chains assume a trusted observer/host and are not cryptographic protection
  against an attacker controlling the host or rewriting the whole evidence set.
- Targeted mutation families are useful defect probes, not an exhaustive mutation
  system; no surviving/invalid/equivalent classifications are silently dropped.
- Counterexample shrinking searches the declared legal history grammar. A composite
  prepare/change/effect production is deliberately included to target temporal
  gaps. Minimality is within that grammar, not across every possible program.
- Concurrency tests use real competing SQLite connections and barriers/trace events.
  Actual winning request identities can vary; replay only promises the documented
  invariant mode for those variants, not deterministic thread scheduling.
- Wall times include process startup and were collected sequentially, with no
  randomized order or statistical microbenchmark controls. Overhead is descriptive.
- Multi-hop delegation and cascading revocation are deferred. Grant-level scope
  attenuation is implemented through action/resource/canonical argument constraints.
- Remote CI and PR publication depend on GitHub access; a locally passing suite
  or committed workflow is not proof of remote CI success.

## Model adapter scope and reviewed metrics

The adapter binds one scenario-selected principal/agent/session, grant ID and
optional approval ID. Model tools select only a synthetic action/resource/argument
set; the adapter does not dynamically select among grants, create delegation
chains or implement general enterprise authority discovery. C1 alone adds the
explicit safeguards prompt. No live model experiment has been run.

Observable grades use actual pre-generation delivery records, not authoritative
changes labelled visible. The fixed-request benchmark reports no model compliance
or false-refusal measurement. Task noncompletion, observed enforcement decision
errors, unauthorized dispatch, server receipt and committed effects are distinct.
Legacy schema-1 evidence and earlier metric definitions remain in Git history;
they are not accepted as current verification by the schema-2 grader.
