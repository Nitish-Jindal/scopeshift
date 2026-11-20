"""Deterministic host executor; model-facing arguments never select identity."""

import asyncio
import json
import threading
from contextlib import AsyncExitStack
from pathlib import Path
from time import perf_counter

from scopeshift.contracts import Configuration, Scenario, canonical
from scopeshift.effects import execute
from scopeshift.gateway import invocation, register
from scopeshift.oracle import grade
from scopeshift.storage import Store
from scopeshift.transport import MCPTransport


async def run_scenario(
    scenario: Scenario,
    config: str,
    directory: Path | str,
    *,
    transport="native",
    seed=0,
    mutant=None,
    allow_c1=False,
) -> dict:
    Configuration(config)
    if config == "C1" and not allow_c1:
        raise ValueError("C1 prompt compliance is only applicable to the model track")
    if transport not in {"native", "mcp"}:
        raise ValueError("unknown transport")
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    store = Store(directory / "run.sqlite3")
    store.initialize(scenario, config, seed, mutant)
    start = perf_counter()
    responses = []
    async with AsyncExitStack() as stack:
        wire = (
            await stack.enter_async_context(
                MCPTransport(store.path, 2 if scenario.concurrent_requests else 0)
            )
            if transport == "mcp"
            else None
        )
        # Session-init transitions occur before capture, unlike discovery-time changes.
        store.checkpoint("session_initialization")
        with store.transaction() as c:
            snapshot = store.state(c)
        if wire:
            tools = await wire.list_tools()
            assert len(tools) == 5
        store.checkpoint("tool_discovery")
        operations = []
        for index in range(scenario.repeats):
            op = scenario.operation
            if index and scenario.duplicate_new_id:
                op = op.model_copy(update={"request_id": f"{op.request_id}-{index}"})
            operations.append(op)

        effect_gate = threading.Barrier(2) if scenario.concurrent_requests else None

        async def request(op, gate=None):
            store.checkpoint("request_generation", op.request_id)
            registered = register(store, op, config, snapshot)
            allowed = registered and invocation(store, op, config, snapshot)
            if gate:
                await gate.wait()
            if not registered:
                response = {"status": "blocked", "reason": "identity_conflict"}
            elif not allowed:
                response = {"status": "denied", "reason": "gateway"}
            else:
                store.checkpoint("mcp_dispatch", op.request_id, transport=transport)
                response = (
                    await wire.call(op.action, op.request_id)
                    if wire
                    else (
                        await asyncio.to_thread(
                            execute, store, op.request_id, op.action, effect_gate
                        )
                    )
                )
            store.checkpoint("tool_response", op.request_id, response=response)
            store.checkpoint("request_completion", op.request_id)
            return response

        if scenario.concurrent_requests:
            # Simultaneously dispatch independent requests; the sink serializes writes.
            # These two fixed concurrent variants authorize both at invocation time.
            gate = asyncio.Barrier(len(operations))
            responses = list(await asyncio.gather(*(request(op, gate) for op in operations)))
        else:
            for op in operations:
                responses.append(await request(op))
    with store.transaction() as c:
        store.event(c, "run_completed", "host", protocol="host-v1", responses=responses)
    evidence = store.export()
    result = {
        "scenario": scenario.model_dump(),
        "config": config,
        "seed": seed,
        "transport": transport,
        "mutant": mutant,
        "responses": responses,
        "duration_ms": (perf_counter() - start) * 1000,
        "grade": grade(evidence),
        "evidence": evidence,
    }
    (directory / "evidence.json").write_text(canonical(result) + "\n")
    return result


def run(scenario, config, directory, **kwargs):
    return asyncio.run(run_scenario(scenario, config, directory, **kwargs))


def replay(path, directory):
    original = json.loads(Path(path).read_text())
    current = run(
        Scenario.model_validate(original["scenario"]),
        original["config"],
        directory,
        transport=original["transport"],
        seed=original["seed"],
        mutant=original["mutant"],
        allow_c1=original["config"] == "C1",
    )
    concurrent = original["scenario"].get("concurrent_requests", False)
    if concurrent:
        consistent = (
            current["grade"]["effect_safety"] == original["grade"]["effect_safety"]
            and current["grade"]["effect_count"] == original["grade"]["effect_count"]
            and current["evidence"]["records"] == original["evidence"]["records"]
            and current["evidence"]["messages"] == original["evidence"]["messages"]
        )
    else:
        consistent = current["evidence"] == original["evidence"]
    return {
        "consistent": consistent,
        "grade": current["grade"],
        "comparison": "concurrent effect/grade invariants" if concurrent else "exact evidence",
    }
