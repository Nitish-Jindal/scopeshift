"""Bounded, seeded Hypothesis stateful differential testing over real SQLite."""

import json
import tempfile
import threading
from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
from pathlib import Path

from hypothesis import HealthCheck, seed, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, precondition, rule, run_state_machine_as_test

from scopeshift.contracts import Operation, Scenario, canonical, digest
from scopeshift.dataset import select
from scopeshift.effects import execute
from scopeshift.evidence import require
from scopeshift.gateway import invocation, register
from scopeshift.oracle import grade
from scopeshift.reference import Reference
from scopeshift.storage import Store


class Counterexample(AssertionError):
    pass


def initial_scenario():
    s = select("authorized_update")
    s.id = "stateful"
    s.legitimate = False
    message = select("authorized_message")
    message.initial["grants"][0]["id"] = "g2"
    message.initial["approvals"][0]["grant_id"] = "g2"
    s.initial["grants"].append(message.initial["grants"][0])
    s.initial["approvals"].extend(message.initial["approvals"])
    return s


class History:
    def __init__(self, scenario, config, directory):
        self.scenario, self.config = (scenario, config)
        self.store = Store(Path(directory) / "run.sqlite3")
        self.store.initialize(scenario, config)
        self.model = Reference(scenario.initial)
        self.snapshot = deepcopy(scenario.initial)
        self.pending = None
        self.committed = {}
        self.commands = []
        self.violation = False

    def apply(self, command):
        self.commands.append(deepcopy(command))
        kind = command["kind"]
        if kind == "transition":
            self.store.transition(command["transition"], command["data"])
            self.model.transition(command["transition"], command["data"])
        elif kind == "prepare":
            if self.pending:
                with self.store.transaction() as c:
                    self.store.event(
                        c,
                        "request_cancelled",
                        "host",
                        self.pending[0].request_id,
                        reason="superseded",
                    )
            op = Operation.model_validate(command["operation"])
            registered = register(self.store, op, self.config, self.snapshot)
            allowed = registered and invocation(self.store, op, self.config, self.snapshot)
            self.pending = (op, allowed)
        elif kind == "effect" and self.pending:
            op, dispatched = self.pending
            expected = self.model.permits(op.model_dump())
            result = (
                execute(self.store, op.request_id, op.action)
                if dispatched
                else {"status": "denied"}
            )
            if result["status"] == "committed":
                if op.request_id not in self.committed:
                    self.model.consume(op.model_dump())
                    self.committed[op.request_id] = op
                    if not expected:
                        self.violation = True
            elif self.config == "C5" and expected and dispatched:
                raise AssertionError(f"false denial: {result}")
            self.respond(op, result)
            self.pending = None
        elif kind == "retry":
            op = Operation.model_validate(command["operation"])
            count = len(self.store.export()["effects"])
            require(register(self.store, op, self.config, self.snapshot), "validation failed")
            require(invocation(self.store, op, self.config, self.snapshot), "validation failed")
            result = execute(self.store, op.request_id, op.action)
            require(result["status"] == "committed", "validation failed")
            self.respond(op, result)
            require(len(self.store.export()["effects"]) == count, "validation failed")
        elif kind == "concurrent":
            operations = [Operation.model_validate(item) for item in command["operations"]]
            expected = self.model.permits(operations[0].model_dump())
            allowed = []
            for op in operations:
                require(register(self.store, op, self.config, self.snapshot), "validation failed")
                allowed.append(invocation(self.store, op, self.config, self.snapshot))
            barrier = threading.Barrier(2)

            def worker(item):
                op, permit = item
                barrier.wait(timeout=3)
                return (
                    execute(Store(self.store.path), op.request_id, op.action)
                    if permit
                    else {"status": "denied"}
                )

            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(worker, zip(operations, allowed, strict=True)))
            for op, response in zip(operations, results, strict=True):
                self.respond(op, response)
            winners = [
                op
                for op, response in zip(operations, results, strict=True)
                if response["status"] == "committed"
            ]
            require(len(winners) == int(expected), "validation failed")
            for op in winners:
                self.model.consume(op.model_dump())
                self.committed[op.request_id] = op
        with self.store.transaction() as c:
            require(self.model.normalized() == self.store.state(c), "validation failed")
        return not self.violation

    def respond(self, op, response):
        self.store.checkpoint("tool_response", op.request_id, response=response)
        self.store.checkpoint("request_completion", op.request_id)

    def finish(self):
        with self.store.transaction() as c:
            if self.pending:
                self.store.event(
                    c,
                    "request_cancelled",
                    "host",
                    self.pending[0].request_id,
                    reason="pending_at_end",
                )
                self.pending = None
            self.store.event(c, "run_completed", "host", history_digest=digest(self.commands))
        result = grade(
            self.store.export(),
            scenario=self.scenario.model_dump(),
            mode="stateful-v2",
            history=self.commands,
        )
        require(result["integrity"], result)
        return result


def campaign(directory, *, config="C5", seed_value=20261120, examples=60, steps=20):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    if (directory / "summary.json").exists():
        raise ValueError("Use a fresh campaign output directory; previous results are preserved.")
    stats = {"examples_started": 0, "steps_executed": 0, "histories": set()}
    artifact = directory / "counterexample.json"

    class Machine(RuleBasedStateMachine):
        def __init__(self):
            super().__init__()
            self.tmp = tempfile.TemporaryDirectory()
            self.h = History(initial_scenario(), config, self.tmp.name)
            self.counter = 0
            stats["examples_started"] += 1

        def issue(self, command):
            stats["steps_executed"] += 1
            safe = self.h.apply(command)
            stats["histories"].add(digest(self.h.commands))
            if not safe:
                artifact.write_text(
                    canonical(
                        {
                            "schema_version": 1,
                            "scenario": self.h.scenario.model_dump(),
                            "config": config,
                            "seed": seed_value,
                            "commands": self.h.commands,
                            "fingerprint": digest(self.h.commands),
                        }
                    )
                    + "\n"
                )
                raise Counterexample("unauthorized committed effect")

        @rule(
            action=st.sampled_from(["update_record", "send_message"]),
            session=st.sampled_from(["s1", "s2"]),
            choice=st.integers(0, 100),
        )
        def prepare(self, action, session, choice):
            self.counter += 1
            op = select(
                "authorized_message" if action == "send_message" else "authorized_update"
            ).operation
            op = op.model_copy(
                update={
                    "request_id": f"r{self.counter}",
                    "grant_id": "g2" if action == "send_message" else "g1",
                    "identity": op.identity.model_copy(update={"session": session}),
                }
            )
            grants = [g for g in self.h.model.state["grants"] if g["action"] == action]
            selected = grants[choice % len(grants)]
            approvals = [
                a for a in self.h.model.state["approvals"] if a["grant_id"] == selected["id"]
            ]
            op = op.model_copy(
                update={
                    "grant_id": selected["id"],
                    "approval_id": approvals[choice % len(approvals)]["id"] if approvals else None,
                }
            )
            self.issue({"kind": "prepare", "operation": op.model_dump()})

        @precondition(lambda self: self.h.pending is not None)
        @rule()
        def effect(self):
            self.issue({"kind": "effect"})

        @rule(change=st.sampled_from(["unrelated", "revoke", "narrow"]))
        def authorization_to_effect(self, change):
            self.counter += 1
            op = select("authorized_update").operation.model_copy(
                update={"request_id": f"r{self.counter}"}
            )
            self.issue({"kind": "prepare", "operation": op.model_dump()})
            data = (
                {"id": "g1"}
                if change == "revoke"
                else {"id": "g1", "constraints": {"value": "other"}}
                if change == "narrow"
                else {"note": "other"}
            )
            self.issue({"kind": "transition", "transition": change, "data": data})
            self.issue({"kind": "effect"})

        @rule(grant=st.sampled_from(["g1", "g2"]))
        def revoke(self, grant):
            self.issue({"kind": "transition", "transition": "revoke", "data": {"id": grant}})

        @rule(value=st.sampled_from(["approved", "different"]))
        def narrow(self, value):
            self.issue(
                {
                    "kind": "transition",
                    "transition": "narrow",
                    "data": {"id": "g1", "constraints": {"value": value}},
                }
            )

        @rule(delta=st.integers(0, 5))
        def tick(self, delta):
            self.issue(
                {
                    "kind": "transition",
                    "transition": "tick",
                    "data": {"time": self.h.model.state["time"] + delta},
                }
            )

        @rule()
        def unrelated(self):
            self.issue({"kind": "transition", "transition": "unrelated", "data": {"note": "other"}})

        @rule()
        def grant(self):
            self.counter += 1
            g = deepcopy(self.h.scenario.initial["grants"][0])
            g["id"] = f"g-new-{self.counter}"
            self.issue({"kind": "transition", "transition": "grant", "data": g})

        @rule()
        def approve(self):
            self.counter += 1
            a = deepcopy(self.h.scenario.initial["approvals"][0])
            a["id"] = f"a-new-{self.counter}"
            a["expires_at"] = self.h.model.state["time"] + 2
            self.issue({"kind": "transition", "transition": "approve", "data": a})

        @precondition(lambda self: bool(self.h.committed))
        @rule()
        def retry(self):
            op = next(iter(self.h.committed.values()))
            self.issue({"kind": "retry", "operation": op.model_dump()})

        @precondition(lambda self: config == "C5")
        @rule()
        def concurrent_approval(self):
            operations = []
            for _ in range(2):
                self.counter += 1
                op = select("authorized_message").operation.model_copy(
                    update={"request_id": f"r{self.counter}", "grant_id": "g2"}
                )
                operations.append(op.model_dump())
            self.issue({"kind": "concurrent", "operations": operations})

        def teardown(self):
            self.h.finish()
            self.tmp.cleanup()

    options = settings(
        max_examples=examples,
        stateful_step_count=steps,
        deadline=None,
        database=None,
        suppress_health_check=[HealthCheck.too_slow],
    )
    found = False
    try:
        run_state_machine_as_test(seed(seed_value)(Machine), settings=options)
    except Counterexample:
        found = True
    result = {k: v for k, v in stats.items() if k != "histories"}
    result.update(
        seed=seed_value,
        config=config,
        max_examples=examples,
        max_steps=steps,
        distinct_history_prefixes=len(stats["histories"]),
        counterexample_found=found,
    )
    if found:
        regression = json.loads(artifact.read_text())
        result["minimized_commands"] = len(regression["commands"])
        result["fingerprint"] = regression["fingerprint"]
        result["replay"] = replay_history(artifact)
    (directory / "summary.json").write_text(canonical(result) + "\n")
    return result


def replay_history(path):
    artifact = json.loads(Path(path).read_text())
    with tempfile.TemporaryDirectory() as directory:
        history = History(
            Scenario.model_validate(artifact["scenario"]), artifact["config"], directory
        )
        for command in artifact["commands"]:
            history.apply(command)
        return {"counterexample_reproduced": history.violation, "grade": history.finish()}
