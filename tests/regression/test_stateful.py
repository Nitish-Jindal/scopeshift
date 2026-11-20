from scopeshift.exploration import explore
from scopeshift.fuzzing import campaign, replay_history


def test_c5_stateful_invariants(tmp_path):
    result = campaign(tmp_path, examples=25, steps=15)
    assert not result["counterexample_found"]
    assert result["steps_executed"] > 100


def test_c3_shrinks_and_replays(tmp_path):
    result = campaign(tmp_path, config="C3", examples=100, steps=20)
    assert result["counterexample_found"]
    assert result["minimized_commands"] == 3
    assert replay_history(tmp_path / "counterexample.json")["counterexample_reproduced"]


def test_bounded_exploration(tmp_path):
    result = explore(tmp_path)
    assert result["executions"] == 54
    assert result["exhaustive"]
    assert result["distinct_counterexamples"] > 0
    assert not any(row["unsafe"] for row in result["rows"] if row["config"] == "C5")


def test_preserved_counterexample():
    from pathlib import Path

    artifact = Path("tests/regression/c3-counterexample.json")
    assert replay_history(artifact)["counterexample_reproduced"]
