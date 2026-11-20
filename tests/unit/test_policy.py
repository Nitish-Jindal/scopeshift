import copy
import json
from pathlib import Path

import pytest

from scopeshift.contracts import Operation, canonical, digest
from scopeshift.dataset import select
from scopeshift.policy import authorize
from scopeshift.reference import Reference

FIXTURES = json.loads(Path("tests/oracle/fixtures.json").read_text())["fixtures"]


def changed_case(change):
    scenario = select("authorized_message")
    state = copy.deepcopy(scenario.initial)
    op = scenario.operation.model_dump()
    grant, approval = state["grants"][0], state["approvals"][0]
    if change == "missing_grant":
        state["grants"] = []
    elif change == "revoked":
        grant["revoked"] = True
    elif change in {"principal", "session", "agent", "action", "resource"}:
        grant[change] = "different"
    elif change == "scope":
        grant["constraints"] = {"body": "different"}
    elif change == "missing_approval":
        state["approvals"] = []
    elif change.startswith("expiry_"):
        state["time"] = {"expiry_equal": 10, "expiry_after": 11, "expiry_before": 9}[change]
    elif change == "consumed":
        approval["consumed_by"] = "previous"
    elif change == "digest":
        approval["digest"] = digest({"body": "different"})
    elif change == "approval_grant":
        approval["grant_id"] = "g2"
    elif change == "approval_session":
        approval["session"] = "s2"
    elif change == "unrelated":
        state["version"] += 1
    return state, Operation.model_validate(op)


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f["id"])
def test_hand_labelled_predicates(fixture):
    state, op = changed_case(fixture["change"])
    assert authorize(state, op)[0] is fixture["permitted"]
    assert Reference(state).permits(op.model_dump()) is fixture["permitted"]


@pytest.mark.parametrize("actual,expected", [(True, 1), (1, 1.0), (None, "missing")])
def test_canonical_constraint_binding(actual, expected):
    s = select("authorized_update")
    s.initial["grants"][0]["constraints"] = {"value": expected}
    op = s.operation.model_copy(update={"args": {"value": actual}})
    assert not authorize(s.initial, op)[0]
    assert not Reference(s.initial).permits(op.model_dump())


def test_canonical_json():
    assert canonical({"b": 1, "a": 2}) == '{"a":2,"b":1}'
    assert digest(1) != digest(True) != digest(1.0)
    for value in [{1: "bad"}, {"x": float("nan")}]:
        with pytest.raises(ValueError):
            canonical(value)
