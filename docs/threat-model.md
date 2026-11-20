# Threat model and physical containment

The evaluated actor can propose tool calls and encounter malicious synthetic
documents or responses. Attacks include stale authority, hidden/visible revocation,
approval reuse or expiry, cross-session/principal/agent use, resource and argument
changes, retries, concurrency and malicious instructions to exfiltrate synthetic
content. The malicious document is untrusted text, never executable code.

Trust the host identity binder, container/OS, authoritative policy, scheduler,
trusted effect observer, scenario contract and independent grading artifacts.
The model never chooses database paths, principal/session identities or shell
commands. The host provides immutable concrete operations to the servers by
registered request ID. Server-side action binding rejects calling another tool
with a request ID. Unknown/unregistered or undispatched requests cannot commit.
All record/document/recipient identifiers are from a fixed synthetic namespace.
Search only searches the public collection. SQLite uses parameters for values.
No real records, messages, external email or model secrets are used.

Containers run nonroot with no network, read-only root filesystem, dropped
capabilities, no-new-privileges and bounded resources. Native execution is for a
trusted development machine; it is not an adversarial native-code sandbox.
MCP stdio establishes a local trusted-host transport; this benchmark does not
claim to implement or evaluate OAuth or general remote MCP authentication.
Application policy is a separate layer from MCP transport authorization.

Host/kernel compromise, malicious native code, bypassing the trusted sink,
compromised authoritative policy or oracle, real secret exfiltration and general
distributed delivery transactions are out of scope. C5's controlled disclosure is
a local synthetic disclosure commitment; cached read retries do not constitute a
new sink effect under this benchmark's explicit idempotency policy. Nothing can
retract information already known by a model. Hash links detect internal evidence
inconsistency under the trust assumptions; they are not a tamper-proof external
transparency service. Multi-hop delegation and cascading revocation are deferred.
