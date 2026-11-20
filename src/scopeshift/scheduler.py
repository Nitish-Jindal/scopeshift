"""Causal constraints on serializable schedules; never schedule inside C5 commits."""

from scopeshift.contracts import CHECKPOINTS, Scenario


def validate_schedule(scenario: Scenario) -> None:
    if scenario.schema_version != 1:
        raise ValueError("unknown scenario schema")
    if scenario.concurrent_requests and (scenario.schedule or scenario.repeats != 2):
        raise ValueError("Concurrent corpus variants require two requests and no policy schedule")
    positions = []
    for transition in scenario.schedule:
        if transition.at not in CHECKPOINTS:
            raise ValueError(f"Unknown or impossible checkpoint: {transition.at}")
        positions.append(CHECKPOINTS.index(transition.at))
    if positions != sorted(positions):
        raise ValueError("Schedule must preserve causal checkpoint order")
    if scenario.repeats < 1 or scenario.repeats > 10:
        raise ValueError("Requests must be bounded to 1..10 repeats")
