"""Targeted executable gateway and independent grader mutation campaigns."""

from pathlib import Path

from scopeshift.dataset import select
from scopeshift.engine import run
from scopeshift.evidence import require
from scopeshift.fixtures import EVIDENCE_LABELS, evidence_fixture
from scopeshift.oracle import grade

GATEWAY_CASES = {
    "skip_check": "revoke_after_gateway",
    "stale_policy": "revoke_after_gateway",
    "ignore_revocation": "revoke_before_session",
    "ignore_session": "cross_session",
    "ignore_principal": "cross_principal",
    "ignore_resource": "wrong_resource",
    "ignore_expiry": "approval_at_expiry",
    "ignore_arguments": "approval_arguments",
    "duplicate_approval": "approval_two_requests",
    "non_atomic_gap": "revoke_after_recheck",
    "reject_unrelated": "unrelated_before_effect",
}
GRADER_MUTANTS = [
    "ignore_effects",
    "stale_policy",
    "denial_safe",
    "ignore_order",
    "ignore_session",
    "ignore_approval",
    "ignore_duplicates",
    "attempts_are_effects",
    "missing_pass",
]


def campaign(directory):
    directory = Path(directory)
    gateway = []
    for mutant, name in GATEWAY_CASES.items():
        baseline = run(select(name), "C5", directory / mutant / "baseline")
        result = run(select(name), "C5", directory / mutant / "mutant", mutant=mutant)
        if baseline["grade"]["outcome"] != "pass" or result["grade"]["outcome"] == "invalid":
            status = "invalid"
        elif result["grade"]["outcome"] != "pass":
            status = "killed"
        else:
            status = "survived"
        gateway.append(
            {"mutant": mutant, "scenario": name, "status": status, "grade": result["grade"]}
        )
    grader = []
    for mutant in GRADER_MUTANTS:
        changed = []
        for name, expected in EVIDENCE_LABELS.items():
            base = grade(evidence_fixture(name))["outcome"]
            require(base == expected, (name, base, expected))
            if grade(evidence_fixture(name), mutant)["outcome"] != expected:
                changed.append(name)
        grader.append(
            {
                "mutant": mutant,
                "status": "killed" if changed else "survived",
                "distinguishing_fixtures": changed,
            }
        )
    return {
        "gateway": gateway,
        "grader": grader,
        "note": "Targeted family tests; killed/survived/invalid, no equivalence assumed.",
    }
