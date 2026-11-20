from copy import deepcopy

import pytest

from scopeshift.dataset import select
from scopeshift.effects import execute
from scopeshift.gateway import invocation, register
from scopeshift.reference import Reference
from scopeshift.storage import Store


@pytest.mark.parametrize("config", ["C0", "C2", "C3", "C4", "C5"])
def test_non_message_approval_id_is_ignored_without_consumption(config, tmp_path):
    scenario = select("authorized_update")
    scenario.initial["approvals"] = select("authorized_message").initial["approvals"]
    op = scenario.operation.model_copy(update={"approval_id": "a1"})
    store = Store(tmp_path / "case.sqlite3")
    store.initialize(scenario, config)
    assert register(store, op, config, scenario.initial)
    assert invocation(store, op, config, scenario.initial)
    assert execute(store, op.request_id, op.action)["status"] == "committed"
    assert store.export()["final_policy"]["approvals"][0]["consumed_by"] is None
    reference = Reference(scenario.initial)
    reference.consume(op.model_dump())
    assert reference.state["approvals"][0]["consumed_by"] is None


@pytest.mark.parametrize(
    "case,consumed",
    [
        ("valid", "r1"),
        ("missing", None),
        ("arguments", None),
        ("session", None),
        ("expired", None),
        ("revoked_grant", None),
        ("consumed", "previous"),
    ],
)
def test_message_consumes_only_a_live_matching_unused_approval(case, consumed, tmp_path):
    s = select("authorized_message")
    if case == "missing":
        s.initial["approvals"] = []
    elif case == "arguments":
        s.initial["approvals"][0]["digest"] = "not-the-approved-arguments"
    elif case == "session":
        s.initial["approvals"][0]["session"] = "other"
    elif case == "revoked_grant":
        s.initial["grants"][0]["revoked"] = True
    elif case == "expired":
        s.initial["time"] = 10
    elif case == "consumed":
        s.initial["approvals"][0]["consumed_by"] = "previous"
    # Ambient authority deliberately still commits unsafe messages; unrelated tokens stay intact.
    store = Store(tmp_path / "case.sqlite3")
    store.initialize(s, "C0")
    assert register(store, s.operation, "C0", s.initial)
    assert invocation(store, s.operation, "C0", s.initial)
    assert execute(store, "r1", "send_message")["status"] == "committed"
    state = store.export()["final_policy"]
    model = Reference(deepcopy(s.initial))
    model.consume(s.operation.model_dump())
    assert model.normalized() == state
    if state["approvals"]:
        assert state["approvals"][0]["consumed_by"] == consumed
