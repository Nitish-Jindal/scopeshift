# Independent reference and versioned evidence contracts

The reference consumes neutral operations and trusted evidence. It imports no
policy, gateway, effects, storage or execution implementation. Policy is rebuilt
from initial state and individual transitions; emitted state snapshots, effects,
resources and final policy are checked rather than accepted as ground truth.
Compensating an unsafe effect later cannot erase it.

Permission is a conjunction over the live matching grant, exact identity triple,
action/resource/canonical constraints, and a matching unused/unexpired approval
for messages. Non-message approval IDs are ignored for authorization/consumption.
Messages consume only currently applicable normative authority. The reference
implements this independently from the sink. No policy-version equality rule is
imposed on otherwise permitted operations.

## Schema 2 modes

- `host-fixed-v2`: complete session initialization/snapshot/discovery, externally
  specified request multiplicity/body, admission, dispatch/receipt, applicable
  check, effect attempt/terminal outcome, response/completion and post-commit events.
- `host-model-v2`: the same applicable host lifecycle, but actions are bound to
  actual model-generation proposals. No proposal, budget rejection, conditional
  schedules and tool results have explicit dispositions; fixed request counts are
  not imposed on a model that produces no tool call.
- `stateful-v2`: primitive request/admission/effect histories with explicit pending
  cancellation. The external command sequence binds transitions, requests,
  expected terminal responses and cancellation reasons; its digest is recorded.
- `fixture-v2`: trusted independently authored sparse histories without MCP/session
  checkpoints. The registry binds the fixture identity/initial contract and policy
  history. Commitments still need prior requests/attempts; only the declared
  attempt-only fixture permits its intentional pending primitive attempt.

There is no optional protocol switch. Envelope and initial/terminal metadata must
agree. Every event has a recognized source, event schema, scenario/run identity,
sequence, causal predecessor and hash link. Production modes require external
scenario/mode inputs. Missing metadata or malformed terminal responses fail
closed, including under `python -O`. Old schema-1 exports are historical artifacts
and are rejected by the current grader instead of silently upgraded.

The schedule contract checks exact transition kind/data/visibility/index and
checkpoint placement. Applicable transitions cannot be omitted. Unreachable
checkpoints are explicitly reported and are permitted only when the complete
observed lifecycle did not reach them, for example gateway denial before a sink
boundary or a model that never proposes an action. Stateful command binding and
fixture registry binding prevent those modes from becoming schedule bypasses.

Model observability is reconstructed separately from authoritative policy.
Delivered notifications/results create context versions; each generation and all
its proposals bind to the pre-generation context. A change merely labelled visible
never alters observed compliance on its own. Check correctness, effect safety,
utility and overall integrity remain separate; fixed requests do not measure
model false refusal or observable LLM compliance.
