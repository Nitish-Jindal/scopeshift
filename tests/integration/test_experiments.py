import gzip
import json

from scopeshift.experiments import benchmark, report
from scopeshift.oracle import grade


def test_measured_artifacts_roundtrip_and_report(tmp_path):
    summary = benchmark(tmp_path / "benchmark", transport="native")
    assert summary["executions"] == 180
    assert summary["scenario_count"] == 36
    assert summary["metrics"]["C5"]["unsafe_trial_rate"]["numerator"] == 0
    assert summary["metrics"]["C3"]["unsafe_trial_rate"]["numerator"] > 0
    raw = gzip.decompress((tmp_path / "benchmark/raw.jsonl.gz").read_bytes()).decode()
    rows = [json.loads(line) for line in raw.splitlines()]
    assert len(rows) == 180
    for row in rows:
        assert (
            grade(row["evidence"], scenario=row["scenario"], mode="host-fixed-v2") == row["grade"]
        )
    result = report(tmp_path / "benchmark", tmp_path / "report")
    assert result["executions"] == 180
    assert "<svg" in (tmp_path / "report/effect-safety.svg").read_text()
    assert "36" in (tmp_path / "report/measured-results.md").read_text()
