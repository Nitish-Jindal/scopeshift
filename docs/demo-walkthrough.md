# Demonstration and interview walkthrough

Run `uv run scopeshift demo` from a fresh output location. Read its JSON and the
SQLite-backed evidence under `artifacts/demo/`.

1. C3: the gateway authorizes an update, a separate policy transaction revokes the
   grant, and the MCP record server still commits. The independent oracle reports
   an unsafe effect even though the actor could not observe the hidden revocation.
2. C4: revocation commits after the separate recheck. The sink still commits;
   checking twice does not create an atomic consistency boundary.
3. C5: validation and commitment share the policy database transaction. Revocation
   before the transaction blocks the effect. A competing revocation after an
   acquired C5 transaction cannot cross the transaction; both orderings are
   tested using real connections and trace-event synchronization, not sleeps.
4. C5 legitimate and unrelated-update controls still succeed. A deny-all or
   policy-version-equality strategy loses utility and is detected by the tests.
5. The demo runs 11 enforcement-family mutants and nine grader-family mutants.
   Open a mutant's independent evidence instead of trusting the gateway decision.
6. Hypothesis discovers a C3 stale-effect history and shrinks it to
   prepare → revoke/narrow → effect. The recorded JSON is replayed against real
   SQLite; it is not a hardcoded expected answer. C5's bounded campaign is
   separate and does not convert a finite passing campaign into a proof.

Explain the trust boundary: model proposals are untrusted, identity is host-bound,
MCP carries scoped registered requests, SQLite owns the local consistency domain,
and the oracle reconstructs actual effects independently. Point out the distinction
between hidden revocation and knowing agent misconduct, and between fixture models
and genuine live inference. Discuss read-disclosure and remote-delivery limitations
before making security claims.

Application description: ScopeShift is an executable AI tool-use authorization
benchmark combining actual MCP transport, temporal policy schedules, transactional
synthetic effects, independent evidence grading, targeted mutations and stateful
counterexample discovery/replay. It measures stale-authority failures while
preserving separate security, utility and evidence-integrity outcomes.
