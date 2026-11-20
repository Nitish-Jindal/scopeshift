# Architecture and execution protocol

`contracts.py` holds neutral serialized identities, concrete operations, scenarios,
transitions, canonical JSON and argument hashes. The existing policy, gateway,
storage and effect modules have been preserved and extended, not replaced by a
simulation. `engine.py` is the trusted deterministic host. `model_eval.py` exposes
an Inspect AI adapter with the same trusted registration and real MCP execution.
`transport.py` opens two official-SDK stdio sessions; `mcp_server.py` scopes each
server to a host-selected run database. Document tools and record/message tools
are separate server processes. Sync SQLite effects execute in worker threads,
allowing real concurrent tool calls.

## Configurations

| Configuration | Policy source / check boundary |
|---|---|
| C0 | Ambient application authority; synthetic containment/evidence remain |
| C1 | Additional model prompt constraints; no application authorization check |
| C2 | Snapshot captured at session initialization |
| C3 | Current policy at gateway invocation |
| C4 | C3 plus separate non-atomic sink recheck |
| C5 | Invocation check plus current-policy validation and effect in one transaction |

C1 is excluded from fixed-request model-compliance comparisons. All configurations
share effects, scenario contracts, observation and grading. Idempotent retries
return the original committed response without new effects even after revocation.
A different operation with the same request ID is rejected, including canonical
JSON differences between booleans, integers and floats. A new ID is a new request.

## Causal protocol

Session initialization and scheduled initialization transitions precede snapshot
capture. Tool listing precedes the discovery checkpoint. Requests then pass
request generation, trusted registration, gateway decision, dispatch, server
receipt, optional C4 recheck, before-effect boundary, effect attempt, commit/block,
tool response and completion. Gateway denial omits dispatch/effects. Retries may
omit a new attempt and return their committed result. Concurrent operations may
interleave; per-request prerequisite counts handle duplicate IDs safely.

The schedule accepts only named causal boundaries and monotone boundary order.
The `after_commit` boundary permits a policy transaction only after effect commit.
There is no schedule name permitting a revocation inside a C5 transaction.
Transitions are claimed and applied in a single separate transaction so concurrent
arrivals cannot overtake a claimed but unapplied policy event.

C5's transaction owns and closes its connection. The same connection reads policy,
consumes approval, mutates records/messages/disclosures, inserts the effect row,
updates request results and appends effect evidence. `BEGIN IMMEDIATE` serializes
competing writes; the busy handler is bounded to 2 seconds per transaction. A
failed effect rolls back every partial local change. A separate rollback-evidence
write is also bounded; if it cannot acquire the database, the result is explicitly
inconclusive, never fabricated as a successful rollback record. No application
retry replays a partially applied effect. Post-commit checkpoint errors cannot
be labelled as rolled-back effects.

## Observation and grading

The sink owns committed effect observation. The gateway's approval or denial is
not authoritative evidence of resource safety. Export reads one coherent SQLite
snapshot. Events carry run/config/scenario IDs, sequence, logical time, policy
version, causal predecessor and a canonical hash link. Operations carry identity,
grant/approval IDs and argument digests. The oracle rebuilds policy from initial
state and individual transitions, applies every observed effect to its own
resource model, and compares policy/resources/effect tables with the export.
It imports neither the gateway nor the sink, storage, engine or enforcement
predicate. Labelled handcrafted histories include a lying gateway, duplicate
commit, missing ledger and an unsafe effect later compensated.

Native and MCP runs use the same SQLite sink. Serial replay compares the full
ledger; concurrent replay compares final resource/message cardinality and safety
invariants because actual lock acquisition can select a different winner.
