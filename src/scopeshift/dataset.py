"""Versioned synthetic scenario loading from checkout or installed package data."""

import json
from importlib.resources import files
from pathlib import Path

from scopeshift.contracts import Scenario


def load_dataset(path: str | Path | None = None) -> list[Scenario]:
    if path is not None:
        data = Path(path).read_text()
    elif Path("scenarios/dataset.json").is_file():
        data = Path("scenarios/dataset.json").read_text()
    else:
        data = files("scopeshift").joinpath("data/dataset.json").read_text()
    return [Scenario.model_validate(row) for row in json.loads(data)["scenarios"]]


def select(name: str) -> Scenario:
    return next(s for s in load_dataset() if s.id == name)
