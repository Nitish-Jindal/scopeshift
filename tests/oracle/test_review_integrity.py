import copy
import json
import subprocess
import sys

import pytest

from scopeshift.contracts import digest
from scopeshift.dataset import select
from scopeshift.engine import run
from scopeshift.fuzzing import History, initial_scenario
from scopeshift.oracle import grade


def rehash(evidence):
    for i, event in enumerate(evidence["events"], 1):
        event["seq"] = i
        event["depends_on"] = [i - 1] if i > 1 else []
        event["previous"] = evidence["events"][i - 2]["hash"] if i > 1 else "0" * 64
        event.pop("hash", None)
        event["hash"] = digest(event)
    return evidence


def checked(evidence, scenario):
    return grade(evidence, scenario=scenario, mode="host-fixed-v2")


@pytest.fixture
def valid(tmp_path):
    result = run(select("authorized_update"), "C5", tmp_path)
    assert result["grade"]["integrity"], result["grade"]
    return result


@pytest.mark.parametrize(
    "missing",
    [
        "session_initialization",
        "session_snapshot",
        "tool_discovery",
        "request_generation",
        "requested",
        "gateway_decision",
        "mcp_dispatch",
        "server_receipt",
        "before_effect",
        "effect_attempt",
        "after_commit",
        "tool_response",
        "request_completion",
        "run_completed",
    ],
)
def test_missing_lifecycle_even_with_valid_hashes(valid, missing):
    e = copy.deepcopy(valid["evidence"])
    e["events"] = [event for event in e["events"] if event["kind"] != missing]
    assert checked(rehash(e), valid["scenario"])["outcome"] == "invalid"


@pytest.mark.parametrize("bad_mode", [None, "host-v1", "unknown", "stateful-v2", "fixture-v2"])
def test_mode_cannot_bypass_host_validation(valid, bad_mode):
    e = copy.deepcopy(valid["evidence"])
    e["evidence_mode"] = bad_mode
    e["events"][-1]["payload"]["evidence_mode"] = bad_mode
    assert checked(rehash(e), valid["scenario"])["outcome"] == "invalid"


@pytest.mark.parametrize(
    "key,value",
    [
        ("source", "host"),
        ("schema_version", 99),
        ("scenario", "another-run"),
        ("run_id", "another-run"),
    ],
)
def test_event_headers_are_validated(valid, key, value):
    e = copy.deepcopy(valid["evidence"])
    e["events"][3][key] = value
    assert checked(rehash(e), valid["scenario"])["outcome"] == "invalid"


def test_omitted_revocation_does_not_pass_as_no_change(tmp_path):
    result = run(select("revoke_after_gateway"), "C5", tmp_path)
    e = result["evidence"]
    e["events"] = [event for event in e["events"] if event["kind"] != "policy_changed"]
    assert checked(rehash(e), result["scenario"])["outcome"] == "invalid"


def test_external_contract_rejects_rewritten_scenario(valid):
    e = copy.deepcopy(valid["evidence"])
    e["events"][0]["payload"]["scenario"]["initial"]["grants"][0]["revoked"] = True
    assert checked(rehash(e), valid["scenario"])["outcome"] == "invalid"
    assert grade(valid["evidence"])["outcome"] == "invalid"


def test_unreachable_checkpoint_is_explicit_not_omitted(tmp_path):
    from scopeshift.contracts import Transition

    s = select("revoke_before_session")
    s.schedule.append(Transition(at="before_effect", kind="unrelated", data={"note": "later"}))
    r = run(s, "C5", tmp_path)
    assert r["grade"]["integrity"], r["grade"]
    assert r["evidence"]["events"][-1]["payload"]["schedule_outcomes"][1] == {
        "index": 1,
        "status": "unreachable",
        "reason": "checkpoint_not_reached",
    }


def test_pending_stateful_request_is_explicitly_cancelled(tmp_path):
    s = initial_scenario()
    h = History(s, "C5", tmp_path)
    h.apply({"kind": "prepare", "operation": s.operation.model_dump()})
    assert h.finish()["integrity"]
    assert any(e["kind"] == "request_cancelled" for e in h.store.export()["events"])


def test_optimized_python_rejects_malformed_evidence(valid, tmp_path):
    malformed = copy.deepcopy(valid["evidence"])
    malformed["events"] = [e for e in malformed["events"] if e["kind"] != "effect_attempt"]
    artifact = tmp_path / "malformed.json"
    artifact.write_text(json.dumps({"evidence": rehash(malformed), "scenario": valid["scenario"]}))
    command = [
        sys.executable,
        "-O",
        "-c",
        "import json,sys; from scopeshift.oracle import grade; "
        "r=json.load(open(sys.argv[1])); "
        'print(grade(r["evidence"], scenario=r["scenario"], mode="host-fixed-v2")["outcome"])',
        str(artifact),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=True)
    assert result.stdout.strip() == "invalid"


@pytest.mark.parametrize("config,missing", [("C4", "effect_recheck"), ("C5", "atomic_decision")])
def test_missing_configuration_check_is_invalid(config, missing, tmp_path):
    r = run(select("authorized_update"), config, tmp_path)
    e = r["evidence"]
    e["events"] = [event for event in e["events"] if event["kind"] != missing]
    assert checked(rehash(e), r["scenario"])["outcome"] == "invalid"


def test_fixture_mode_still_requires_attempt_before_commit():
    from scopeshift.fixtures import evidence_fixture

    e = evidence_fixture("legal-committed-effect")
    e["events"] = [event for event in e["events"] if event["kind"] != "effect_attempt"]
    assert grade(rehash(e))["outcome"] == "invalid"


def test_stateful_grading_requires_external_history_and_rejects_missing_revoke(tmp_path):
    s = initial_scenario()
    h = History(s, "C3", tmp_path)
    h.apply({"kind": "prepare", "operation": s.operation.model_dump()})
    h.apply({"kind": "transition", "transition": "revoke", "data": {"id": "g1"}})
    h.apply({"kind": "effect"})
    assert h.finish()["outcome"] == "fail"
    e = h.store.export()
    assert grade(e, scenario=s.model_dump(), mode="stateful-v2")["outcome"] == "invalid"
    e["events"] = [event for event in e["events"] if event["kind"] != "policy_changed"]
    assert (
        grade(rehash(e), scenario=s.model_dump(), mode="stateful-v2", history=h.commands)["outcome"]
        == "invalid"
    )


def test_fixture_contract_requires_its_authored_policy_history():
    from scopeshift.fixtures import evidence_fixture

    e = evidence_fixture("stale-policy")
    e["events"] = [event for event in e["events"] if event["kind"] != "policy_changed"]
    assert grade(rehash(e))["outcome"] == "invalid"
