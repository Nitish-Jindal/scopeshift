from scopeshift.dataset import select
from scopeshift.engine import run
from scopeshift.metrics import summarize


def test_proposal_dispatch_execution_and_effect_boundaries_differ(tmp_path):
    rows = [
        run(select(name), "C3", tmp_path / name)
        for name in ["revoke_after_gateway", "revoke_after_receipt"]
    ]
    a, b = [row["grade"] for row in rows]
    assert a["unauthorized_attempt_count"] == b["unauthorized_attempt_count"] == 0
    assert a["unauthorized_dispatch_count"] == a["unauthorized_execution_count"] == 1
    assert b["unauthorized_dispatch_count"] == b["unauthorized_execution_count"] == 0
    assert len(a["unauthorized_effects"]) == len(b["unauthorized_effects"]) == 1
    assert a["enforcement_decisions_correct"] is True  # Invocation was valid; effect safety failed.
    metrics = summarize(rows)["C3"]
    assert metrics["unauthorized_execution_rate"]["numerator"] == 1
    assert metrics["unauthorized_protected_effect_rate"]["numerator"] == 2
    assert metrics["model_false_refusal_rate"] is None
    assert metrics["model_observable_violation_rate"]["rate"] is None


def test_false_denial_is_not_task_noncompletion_or_safety(tmp_path):
    result = run(select("unrelated_before_effect"), "C5", tmp_path, mutant="reject_unrelated")
    grade = result["grade"]
    assert grade["effect_safety"] is True
    assert grade["legitimate_task_completed"] is False
    assert grade["false_denial_count"] == 1
    assert grade["enforcement_decisions_correct"] is False
    metrics = summarize([result])["C5"]
    assert metrics["legitimate_task_noncompletion_rate"]["rate"] == 1
    assert metrics["enforcement_false_denial_rate"]["numerator"] == 1
    assert metrics["model_false_refusal_rate"] is None


def test_no_stale_authority_claim_when_revoked_before_snapshot(tmp_path):
    result = run(select("revoke_before_session"), "C0", tmp_path)
    assert result["grade"]["stale_eligible_effect_count"] == 0
    assert result["grade"]["stale_unauthorized_effect_count"] == 0
    assert summarize([result])["C0"]["stale_authority_effect_rate"]["rate"] is None
