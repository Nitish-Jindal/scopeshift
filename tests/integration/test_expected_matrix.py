import json
from pathlib import Path

import pytest

from scopeshift.dataset import select
from scopeshift.engine import run

MATRIX = json.loads(Path("tests/oracle/expected_matrix.json").read_text())
CASES = [
    (name, config, expected)
    for name, rows in MATRIX["cases"].items()
    for config, expected in zip(MATRIX["configs"], rows, strict=True)
]


@pytest.mark.parametrize("name,config,expected", CASES)
def test_independent_admission_effect_safety_matrix(name, config, expected, tmp_path):
    result = run(select(name), config, tmp_path)
    evidence = result["evidence"]
    admitted = sum(
        e["payload"]["allowed"] for e in evidence["events"] if e["kind"] == "gateway_decision"
    )
    assert [admitted, len(evidence["effects"]), result["grade"].get("effect_safety")] == expected
    assert result["grade"]["integrity"], result["grade"]
