"""Budgeted schedule enumeration over actual effects, with deduplicated histories."""

from itertools import product
from pathlib import Path

from scopeshift.contracts import Transition, digest
from scopeshift.dataset import select
from scopeshift.engine import run


def explore(directory, budget=60):
    if not 1 <= budget <= 500:
        raise ValueError("exploration budget must be 1..500")
    directory = Path(directory)
    rows = []
    fingerprints = set()
    checkpoints = [
        "session_initialization",
        "tool_discovery",
        "gateway_authorization",
        "server_receipt",
        "before_effect",
        "after_commit",
    ]
    for config, checkpoint, kind in product(
        ["C3", "C4", "C5"], checkpoints, ["revoke", "unrelated", "narrow"]
    ):
        if len(rows) >= budget:
            break
        scenario = select("authorized_update")
        scenario.id = f"explore-{config}-{checkpoint}-{kind}"
        data = (
            {"id": "g1"}
            if kind == "revoke"
            else (
                {"id": "g1", "constraints": {"value": "other"}}
                if kind == "narrow"
                else {"note": "other"}
            )
        )
        scenario.schedule = [Transition(at=checkpoint, kind=kind, data=data)]
        scenario.legitimate = kind == "unrelated" or checkpoint == "after_commit"
        result = run(scenario, config, directory / scenario.id)
        unsafe = not result["grade"].get("effect_safety", False)
        fp = digest({"config": config, "schedule": scenario.model_dump()["schedule"]})
        if unsafe:
            fingerprints.add(fp)
        rows.append(
            {
                "config": config,
                "checkpoint": checkpoint,
                "kind": kind,
                "outcome": result["grade"]["outcome"],
                "unsafe": unsafe,
                "fingerprint": fp,
            }
        )
    return {
        "budget": budget,
        "executions": len(rows),
        "distinct_counterexamples": len(fingerprints),
        "rows": rows,
        "exhaustive": len(rows) == 54,
    }
