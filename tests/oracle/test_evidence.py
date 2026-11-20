import ast
import copy
from pathlib import Path

import pytest

from scopeshift.fixtures import EVIDENCE_LABELS, evidence_fixture
from scopeshift.oracle import grade


@pytest.mark.parametrize("name,expected", EVIDENCE_LABELS.items())
def test_independent_evidence_labels(name, expected):
    assert grade(evidence_fixture(name))["outcome"] == expected


@pytest.mark.parametrize("field", ["effects", "records", "messages", "disclosures", "final_policy"])
def test_tampered_final_state(field):
    e = evidence_fixture("legal-committed-effect")
    e[field] = {} if field in {"records", "final_policy"} else [{"forged": True}]
    assert grade(e)["outcome"] == "invalid"


def test_compensation_does_not_erase_violation():
    e = evidence_fixture("compensated-unauthorized-effect")
    assert e["records"]["record:1"] == "initial"
    assert grade(e)["unauthorized_effects"] == [{"request_id": "r1", "effect_id": 1}]


def test_refuses_malformed_inputs_without_mutating_them():
    e = evidence_fixture("legal-committed-effect")
    original = copy.deepcopy(e)
    assert grade(e)["outcome"] == "pass"
    assert e == original
    for malformed in [None, {}, {"events": [None]}]:
        assert grade(malformed)["outcome"] == "invalid"


def test_oracle_import_independence():
    forbidden = {"policy", "gateway", "effects", "storage", "engine"}
    for path in ["src/scopeshift/reference.py", "src/scopeshift/oracle.py"]:
        for node in ast.walk(ast.parse(Path(path).read_text())):
            if isinstance(node, ast.ImportFrom) and node.module:
                assert not forbidden.intersection(node.module.split("."))


def test_rehashed_noncausal_history_is_invalid(tmp_path):
    from scopeshift.contracts import digest
    from scopeshift.dataset import select
    from scopeshift.engine import run

    result = run(select("authorized_update"), "C5", tmp_path)
    e = result["evidence"]
    events = e["events"]
    dispatch = next(i for i, event in enumerate(events) if event["kind"] == "mcp_dispatch")
    receipt = next(i for i, event in enumerate(events) if event["kind"] == "server_receipt")
    events[dispatch], events[receipt] = events[receipt], events[dispatch]
    for i, event in enumerate(events, 1):
        event["seq"] = i
        event["depends_on"] = [i - 1] if i > 1 else []
        event["previous"] = events[i - 2]["hash"] if i > 1 else "0" * 64
        event.pop("hash")
        event["hash"] = digest(event)
    assert grade(e)["outcome"] == "invalid"
