# ScopeShift research report

## Question and scope

Does invocation-time authorization preserve policy correctness when authority
changes before a protected effect commits? ScopeShift evaluates that question
inside a single trusted-host synthetic enterprise environment using actual MCP
transport. It separately asks whether a non-atomic second check closes the gap,
whether transactional coupling preserves utility after unrelated policy updates,
and whether independent effect grading plus temporal exploration detects defects
missed by static inputs. This is an implementation and finite experimental study,
not a claim of a novel general security primitive or an upstream MCP vulnerability.

## Experimental design

The dataset contains 36 versioned variants: authorized/unauthorized controls,
revocation at semantic boundaries, irrelevant/relevant narrowing, regrant with
immutable IDs, identity/resource/argument mismatches, expiry equality boundaries,
approval reuse, serial and concurrent retries, protected reads/search, visible
versus hidden revocation, and untrusted synthetic document content. Two actual
MCP stdio servers expose five synthetic tools through the official Python SDK.
A deterministic trusted host registers concrete operations and binds identities.
C0/C2/C3/C4/C5 share all scenario contracts and effects. C1 is a prompt-level
configuration implemented only in the separate Inspect model track.

The pre-enforcement normative contract is retained. An independent state machine
reconstructs policy from initial conditions and committed transitions, evaluates
every committed operation, consumes approvals, applies all effects to its own
resources, and compares final policy/resources/ledger. Gateway claims never prove
safety. A false denial of legitimate work loses utility even when effects are safe.
Handcrafted labelled evidence histories include a lying gateway, compensation,
duplicate effects, malformed order and missing evidence. Oracle imports exclude
all enforcement, storage and execution modules.

Track A is an Inspect integration track tested with explicit controlled provider
fixtures and real MCP calls. No live model inference or token-cost measurement was
performed. Track B runs all 36 variants across five fixed-request configurations
for 180 measured MCP executions. Track C evaluates predicate/evidence fixtures,
11 enforcement-family mutants, nine grader-family mutants, bounded schedules,
stateful differential testing and replay. SQLite contention tests use independent
connections and explicit barriers/trace events, not sleep-generated races.

## Results

[The generated measured report](measured-results.md) and
`results/benchmark/summary.json` contain exact denominators, latency summaries,
versions, dataset digest and seed. `results/benchmark/raw.jsonl.gz` contains the
complete per-trial evidence, not just outcome labels. All 180 exports were regraded
against the independent oracle. C0/C2/C3/C4 committed unauthorized synthetic
effects in 22/14/9/4 of their 36 trials respectively. C5 committed none in these
36 cases and completed all 16 legitimate controls. No trial in the retained run
had invalid evidence. These finite outcomes are scoped to the dataset and grammar.

The mandatory stale-authority example succeeded experimentally: C3 authorized an
operation, revocation committed before the MCP sink effect, and the independent
oracle flagged that effect. C4 also failed when revocation was placed after its
separate recheck. C5 blocked those schedules. A legitimate C5 operation and an
otherwise legitimate operation after an unrelated version increment both passed.
The policy-version-equality mutant was rejected by the utility control.

The concurrent approval variant dispatches two independently registered requests,
then synchronizes them outside effect transactions. For C4 this places both
separate checks before either commit; C5 still serializes validation/consumption
with commitment. This is a realizable non-atomic gap. The winning C5 request may
vary, so concurrent replay compares effect and grade invariants rather than exact
winning identities. Serial replay compares the entire semantic evidence ledger.

[The reliability report](reliability.md) records targeted mutation and fixture
results, the finite exploration grammar, and actual stateful budgets. The C3
campaign discovered a violation, shrank it to three semantic commands and replayed
it against real SQLite. The retained regression is not a hardcoded response.
The C5 campaign found no violation within its declared budget; that is not a proof.

## Interpretation and threats to validity

Invocation checks alone leave a causal authorization-to-commit gap. A separate
second check narrows that gap but does not remove it. Coupling current-policy
validation, approval consumption, local mutation and observation inside one
serialized consistency domain closes the tested local gap while allowing
unrelated policy changes. This conclusion does not extend to remote email,
network disclosure, arbitrary distributed transactions or a compromised host.

Fixed requests cannot measure LLM prompt compliance. The hidden-revocation cases
can exhibit unsafe effects while an actor had no observable evidence that authority
changed. The independent grade keeps those concepts separate. Scripted malicious
follow-ups validate the adapter and enforcement path, not actual model behavior.

Dataset selection and authored mutation operators can favor particular failure
modes. The independent reference model shares neutral serialization, and its
architecture and labelled fixtures reduce but do not eliminate correlated mistakes.
The review is a skeptical self-audit, not external independent security review.
Budget sizes differ across static, manual, bounded and stateful tracks; raw
prefix counts include shrinking and must not be presented as independent trials.
No broad statistical or novelty claims are made from these finite observations.
Latency includes process startup, is sequentially collected and is descriptive.

## Reproduction and extensions

Follow the README's locked quickstart, run `scopeshift demo`, then the benchmark,
mutations, exploration, fuzzing and report commands with fresh output directories.
Docker Compose provides a nonroot, read-only, offline runtime with bounded
resources. CI is credential-free; actual remote CI status is reported separately.
The original 23-section specification remains unchanged in PROJECT_SPEC.md.

Future work includes publication-grade primary-source literature comparison,
explicitly authorized live-model evaluation, larger schedule grammars, additional
independent human fixture review, and correctly specified multi-hop delegation.
All resource effects and data in this implementation are synthetic.

## Final independent review corrections

The experiment was rerun with strict schema-2 evidence. Every production grade
binds an externally selected scenario/mode; stateful histories additionally bind
the external commands. All 180 MCP exports regrade successfully under these
contracts. Unsafe-trial/effect counts in the measured table are unchanged; raw
evidence, timing summaries, metrics and SVG were regenerated, not reused.

The revised metrics no longer identify receipt/dispatch with protected commitment:
C5 received four currently unauthorized requests out of 28 server entries and
committed zero unsafe protected effects out of 16 effects. This demonstrates the
effect-boundary guarantee, not a claim that its invocation decision never becomes
stale. False denials are counted only at normatively permitted enforced checks
(0/44 in the C5 run); task noncompletion is separate. Model false refusal and
fixed-track observable-model compliance are not measured and remain null.

The stale-authority denominator now requires earlier permitted authority at a
recorded boundary, rather than an initial grant alone. Revocation effectiveness
requires an actually applied matching revocation in an eligible fixed trial.
See docs/metrics.md for full definitions and complementary/unsupported quantities.

Inspect fixture tests verify notifications delivered before proposals and only
after proposals, with all proposals in one generation bound to its prior context.
A policy change labelled visible is not sufficient evidence that an agent saw it.
Approval bookkeeping ignores non-message token IDs and does not consume unrelated,
expired, used or otherwise inapplicable message approvals, while deliberately
unsafe baselines remain unsafe. No live-model experiment was added.
