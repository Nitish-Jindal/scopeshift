import json
import runpy
import subprocess
import sys
from pathlib import Path

from scopeshift.cli import main
from scopeshift.dataset import load_dataset
from scopeshift.metrics import rate


def test_dataset_is_reproducible():
    generated = runpy.run_path("scripts/build_dataset.py")["build"]()
    assert generated == json.loads(Path("scenarios/dataset.json").read_text())
    assert len(load_dataset()) == 36


def test_cli_and_zero_denominators(tmp_path, capsys):
    assert rate(0, 0) == {"numerator": 0, "denominator": 0, "rate": None}
    assert main(["demo", "--transport", "native", "--output", str(tmp_path / "demo")]) == 0
    result = json.loads(capsys.readouterr().out)
    assert len(result["temporal_cases"]) == 5
    assert result["temporal_cases"][0]["grade"]["effect_safety"] is False
    assert result["temporal_cases"][2]["grade"]["effect_safety"] is True
    assert (
        main(
            [
                "replay",
                str(tmp_path / "demo/C5-authorized_update/evidence.json"),
                "--output",
                str(tmp_path / "replay"),
            ]
        )
        == 0
    )
    assert json.loads(capsys.readouterr().out)["consistent"]


def test_cli_refuses_live_without_authorization(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scopeshift.cli",
            "model",
            "--model",
            "openai/not-authorized",
            "--output",
            str(tmp_path),
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "--allow-live" in result.stderr
