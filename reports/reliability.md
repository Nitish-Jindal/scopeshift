# Benchmark reliability evidence

## Independent labelled fixtures

The preserved predicate fixture table contains 18 hand-labelled legal/illegal
cases authored before the executable oracle. Both enforcement and the separately
implemented reference predicate are tested against it. Eleven directly authored
complete evidence histories exercise safety and integrity independently of the
executor. Six unsafe histories had zero false acceptances; two safe histories
had zero false rejections; all three invalid histories were rejected. These small
fixture denominators are reported explicitly, not presented as population error
rates. Exact values are in `results/reliability/oracle-fixtures.json`.

## Targeted mutation results

All 11 requested enforcement families were killed by an applicable test with a
passing C5 baseline: skipped effect check, stale policy, ignored revocation,
ignored session, ignored principal, ignored resource, ignored expiry, ignored
canonical arguments, duplicate single-use approval, a non-atomic gap, and false
denial after an unrelated policy update. All nine grader families were killed:
ignored effects, stale policy, denial-as-safety, ignored order, ignored session,
ignored approval, ignored duplicates, attempts-as-effects, and missing-evidence
pass. Counts: gateway 11 killed / 11 evaluated; grader 9 killed / 9 evaluated;
zero survived and zero invalid in this targeted campaign. No equivalence claim
is made. `results/reliability/mutations.json` retains every mutant and its actual
distinguishing outcome/fixtures. This is not a generic exhaustive mutation engine.

## Exploration and stateful testing

Bounded exploration executed all 54 combinations in its explicit grammar:
3 configurations × 6 temporal boundaries × 3 policy transitions. Eight distinct
unsafe schedule fingerprints were observed; none were C5. The 60-run input budget
exceeded the 54 unique grammar combinations, so the run was exhaustive only
within that grammar. The full row table is retained in `exploration.json`.

The seeded C3 Hypothesis RuleBasedStateMachine campaign used up to 100 examples
and 20 rule steps per example. It started 64 example/shrink executions, ran 434
semantic commands, and saw 318 distinct history prefixes. It discovered a failure
and shrank it to three commands. Replay reproduced one unauthorized committed
effect with valid evidence. Its regression and fingerprint are retained in
`tests/regression/c3-counterexample.json` and `fuzz-c3.json`.

The corresponding C5 bounded campaign used up to 60 examples and 20 rule steps.
It started 62 example/shrink executions, ran 1,194 semantic commands and saw 667
distinct history prefixes, finding no counterexample. Hypothesis may run auxiliary
or shrink examples beyond its nominal successful-example budget. These counts
include replay/shrinking activity; they are not independent benchmark trials.

The grammar generates grant/regrant, approval, narrowing, unrelated policy/time
updates, identity changes, dispatch/effect gaps, retries and real concurrent
approval requests. Composite prepare/change/effect rules intentionally target
realizable temporal gaps. Shrinking minimality is within that declared grammar.

Static no-transition controls test authorization boundaries but cannot expose an
authorization-to-commit race. Manually authored temporal cases, bounded boundary
placement and stateful histories add temporal coverage. Budgets and search spaces
differ, so raw execution counts or counterexample totals are not a fair speed
ranking. The comparison is coverage-oriented with explicit denominators, not a
claim that any exploration method is universally superior.

## Reproduction

Run the README's mutate, explore and fuzz commands in new directories. The locked
seed is 20261120. Replay the retained regression with `scopeshift replay`; inspect
both its independent grade and actual committed effect. The test suite separately
validates real competing SQLite transaction orderings, approval contention,
rollback, bounded lock failure, model adapter fixtures, exact serial replay,
concurrent outcome invariants and tampered-evidence rejection.
