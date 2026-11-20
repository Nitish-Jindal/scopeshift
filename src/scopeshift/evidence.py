"""Versioned evidence contracts and explicit, optimization-safe lifecycle checks.

These validate a trusted observer's evidence; they cannot authenticate a hostile
host. Production callers must supply their externally selected scenario contract.
"""

from collections import Counter, defaultdict

from scopeshift.contracts import CHECKPOINTS, Operation, Scenario, digest

MODES = {"host-fixed-v2", "host-model-v2", "stateful-v2", "fixture-v2"}


class EvidenceError(ValueError):
    """Malformed, incomplete, incompatible or contract-inconsistent evidence."""


def require(condition, message):
    if not condition:
        raise EvidenceError(message)


def validate_evidence(evidence, scenario, mode, mutant=None, history=None):
    require(isinstance(evidence, dict), "evidence must be an object")
    require(evidence.get("schema_version") == 2, "unknown evidence schema")
    actual_mode = evidence.get("evidence_mode")
    require(actual_mode in MODES, "missing or unknown evidence mode")
    require(mode is None or actual_mode == mode, "unexpected evidence mode")
    events = evidence["events"]
    require(bool(events), "missing ledger")
    require(events[0]["kind"] == "initialized", "missing initialization")
    require(events[-1]["kind"] == "run_completed", "missing completion")
    embedded = events[0]["payload"]["scenario"]
    if actual_mode == "fixture-v2":
        from scopeshift.fixtures import EVIDENCE_LABELS, evidence_fixture

        name = embedded.get("fixture_id")
        require(name in EVIDENCE_LABELS, "unknown independent fixture")
        trusted = evidence_fixture(name)["events"][0]["payload"]["scenario"]
        require(scenario is None or digest(scenario) == digest(trusted), "wrong fixture contract")
        scenario = trusted
        scenario_id = name
    else:
        require(mode in MODES, "trusted external evidence mode required")
        require(scenario is not None, "trusted external scenario contract required")
        scenario = Scenario.model_validate(scenario).model_dump()
        require(scenario["schema_version"] == 1, "unknown scenario schema")
        scenario_id = scenario["id"]
    require(digest(embedded) == digest(scenario), "embedded scenario differs from trusted contract")
    contract_hash = digest(scenario)
    require(evidence.get("contract_digest") == contract_hash, "contract digest mismatch")
    for terminal in (events[0], events[-1]):
        require(
            terminal["payload"].get("evidence_mode") == actual_mode, "inconsistent evidence mode"
        )
        require(
            terminal["payload"].get("contract_digest") == contract_hash,
            "terminal contract mismatch",
        )
        require("protocol" not in terminal["payload"], "obsolete protocol metadata")
    require(sum(e["kind"] == "initialized" for e in events) == 1, "duplicate initialization")
    require(sum(e["kind"] == "run_completed" for e in events) == 1, "duplicate completion")
    source_kinds = {
        "authority": {"initialized", "policy_changed"},
        "gateway": {"requested", "gateway_decision", "identity_conflict"},
        "sink": {
            "effect_attempt",
            "atomic_decision",
            "effect_recheck",
            "effect_blocked",
            "effect_committed",
            "effect_rolled_back",
            "idempotent_replay",
        },
        "scheduler": set(CHECKPOINTS),
        "host": {
            "run_completed",
            "request_cancelled",
            "model_proposal",
            "model_notification",
            "model_generation",
            "session_snapshot",
            "proposal_rejected",
        },
    }
    for event in events:
        require(event["schema_version"] == 2, "unknown event schema")
        require(event["scenario"] == scenario_id, "cross-scenario evidence")
        require(event["config"] in {f"C{i}" for i in range(6)}, "unknown configuration")
        require(event["kind"] in source_kinds.get(event["source"], set()), "unknown event/source")
        if "operation" in event["payload"]:
            operation = Operation.model_validate(event["payload"]["operation"])
            require(operation.request_id == event["request_id"], "operation/request mismatch")
    if actual_mode == "fixture-v2":
        validate_fixture_protocol(events, scenario["fixture_id"])
        expected_policies = [
            e["payload"]
            for e in evidence_fixture(scenario["fixture_id"])["events"]
            if e["kind"] == "policy_changed"
        ]
        actual_policies = [e["payload"] for e in events if e["kind"] == "policy_changed"]
        require(
            digest(actual_policies) == digest(expected_policies),
            "fixture policy history omitted/altered",
        )
    else:
        validate_lifecycle(events, scenario, actual_mode)
        validate_transitions(events, scenario, actual_mode)
        if actual_mode == "stateful-v2":
            require(isinstance(history, list), "trusted external stateful commands required")
            require(
                events[-1]["payload"].get("history_digest") == digest(history),
                "stateful command digest mismatch",
            )
            expected_policies = [
                (c["transition"], c["data"]) for c in history if c["kind"] == "transition"
            ]
            actual_policies = [
                (e["payload"]["transition"], e["payload"]["data"])
                for e in events
                if e["kind"] == "policy_changed"
            ]
            require(
                digest(actual_policies) == digest(expected_policies),
                "stateful transitions omitted/altered",
            )
            expected_requests = []
            expected_responses, expected_cancellations = Counter(), Counter()
            pending = None
            for command in history:
                kind = command["kind"]
                if kind in {"prepare", "retry"}:
                    operation = command["operation"]
                    expected_requests.append(operation)
                    if kind == "prepare":
                        if pending is not None:
                            expected_cancellations[(pending, "superseded")] += 1
                        pending = operation["request_id"]
                    else:
                        expected_responses[operation["request_id"]] += 1
                elif kind == "concurrent":
                    expected_requests.extend(command["operations"])
                    expected_responses.update(op["request_id"] for op in command["operations"])
                elif kind == "effect":
                    require(pending is not None, "effect command without pending operation")
                    expected_responses[pending] += 1
                    pending = None
                else:
                    require(kind == "transition", "unknown stateful command")
            if pending is not None:
                expected_cancellations[(pending, "pending_at_end")] += 1
            actual_responses = Counter(
                e["request_id"] for e in events if e["kind"] == "tool_response"
            )
            actual_cancellations = Counter(
                (e["request_id"], e["payload"]["reason"])
                for e in events
                if e["kind"] == "request_cancelled"
            )
            require(
                actual_responses == expected_responses
                and actual_cancellations == expected_cancellations,
                "stateful effects/responses/cancellations differ from external commands",
            )
            actual_requests = [
                e["payload"]["operation"] for e in events if e["kind"] == "requested"
            ]
            require(
                digest(actual_requests) == digest(expected_requests),
                "stateful requests omitted/altered",
            )
    return scenario, actual_mode


def validate_transitions(events, scenario, mode):
    schedule = scenario["schedule"]
    fired = set()
    if mode == "stateful-v2":
        require(not schedule, "stateful transitions must be explicit history commands")
    else:
        for position, event in enumerate(events):
            pending = [
                i for i, t in enumerate(schedule) if t["at"] == event["kind"] and i not in fired
            ]
            if event["source"] != "scheduler":
                continue
            for offset, index in enumerate(pending, 1):
                require(position + offset < len(events), "missing scheduled transition")
                observed = events[position + offset]
                payload, expected = observed["payload"], schedule[index]
                require(observed["kind"] == "policy_changed", "scheduled transition omitted")
                require(payload.get("schedule_index") == index, "wrong scheduled transition index")
                require(payload.get("checkpoint") == expected["at"], "wrong transition checkpoint")
                require(
                    payload["transition"] == expected["kind"]
                    and digest(payload["data"]) == digest(expected["data"])
                    and payload["visible"] == expected["visible"],
                    "scheduled transition altered",
                )
                fired.add(index)
        actual = [
            e["payload"].get("schedule_index") for e in events if e["kind"] == "policy_changed"
        ]
        require(Counter(actual) == Counter(fired), "extra, unscheduled or duplicate transition")
    expected_outcomes = [
        {
            "index": i,
            "status": "applied" if i in fired else "unreachable",
            "reason": None if i in fired else "checkpoint_not_reached",
        }
        for i in range(len(schedule))
    ]
    require(
        events[-1]["payload"].get("schedule_outcomes") == expected_outcomes,
        "missing or incorrect schedule disposition",
    )


def validate_lifecycle(events, scenario, mode):
    host = mode.startswith("host-")
    counts, global_counts = defaultdict(Counter), Counter()
    operations, decisions, effect_results = {}, defaultdict(list), {}
    terminal_statuses = defaultdict(Counter)
    responses = []
    proposal_ids = set()
    proposals = {}
    recheck_denials = Counter()
    for event in events:
        kind, rid, payload = event["kind"], event["request_id"], event["payload"]
        c = counts[rid]
        if kind == "session_initialization":
            require(not global_counts["tool_discovery"], "late session initialization")
        if kind == "tool_discovery":
            require(global_counts["session_initialization"] == 1, "discovery before session")
        if kind == "model_proposal":
            require(mode == "host-model-v2", "model proposal in non-model evidence")
            require(rid not in proposal_ids, "duplicate model proposal")
            proposal_ids.add(rid)
            proposals[rid] = payload["operation"]
        if kind == "proposal_rejected":
            require(
                mode == "host-model-v2"
                and rid in proposal_ids
                and payload.get("reason") == "tool_budget",
                "unbound proposal rejection",
            )
            require(
                not c["proposal_rejected"] and not c["requested"],
                "proposal rejected twice/after admission",
            )
        if kind == "request_generation":
            require(host and global_counts["tool_discovery"] == 1, "request before discovery")
            if mode == "host-model-v2":
                require(rid in proposal_ids, "request without model proposal")
        if kind == "session_snapshot":
            require(
                global_counts["session_initialization"] == 1
                and not global_counts["tool_discovery"],
                "snapshot outside initialization boundary",
            )
        if kind == "requested":
            if host:
                require(c["request_generation"] > c["requested"], "request without generation")
            op = payload["operation"]
            if mode == "host-model-v2":
                require(digest(op) == digest(proposals[rid]), "proposal/request rebound")
            if mode == "host-fixed-v2":
                expected = dict(scenario["operation"])
                expected_rids = {expected["request_id"]}
                if scenario["duplicate_new_id"]:
                    expected_rids.update(
                        f"{expected['request_id']}-{i}" for i in range(1, scenario["repeats"])
                    )
                require(rid in expected_rids, "unexpected fixed request identity")
                expected["request_id"] = rid
                require(digest(op) == digest(expected), "fixed operation differs from contract")
            require(
                rid not in operations or digest(operations[rid]) == digest(op), "request rebound"
            )
            operations[rid] = op
        if kind in {"gateway_decision", "effect_recheck", "atomic_decision"}:
            require(isinstance(payload["allowed"], bool), "non-boolean authorization decision")
        if kind == "effect_recheck" and not payload["allowed"]:
            recheck_denials[rid] += 1
        if kind == "gateway_decision":
            require(c["requested"] > c["gateway_decision"], "decision without request")
            require(digest(payload["operation"]) == digest(operations[rid]), "decision binding")
            decisions[rid].append(payload["allowed"])
        if kind == "mcp_dispatch":
            require(sum(decisions[rid]) > c["mcp_dispatch"], "dispatch without admission")
        if kind == "server_receipt":
            prerequisite = c["mcp_dispatch"] if host else sum(decisions[rid])
            require(prerequisite > c["server_receipt"], "receipt without dispatch/admission")
        if kind in {"effect_recheck", "before_effect", "effect_attempt", "idempotent_replay"}:
            require(c["server_receipt"] > 0, "effect lifecycle before server receipt")
        if kind == "atomic_decision":
            require(c["effect_attempt"] > c["atomic_decision"], "atomic decision without attempt")
        if kind == "after_commit":
            require(
                c["effect_committed"] > c["after_commit"], "post-commit checkpoint before commit"
            )
        if kind == "effect_attempt":
            require(
                digest(payload["operation"]) == digest(operations[rid]), "attempt operation binding"
            )
            require(c["before_effect"] > c["effect_attempt"], "attempt without effect boundary")
        if kind in {"effect_committed", "effect_blocked"}:
            used = c["effect_committed"] + c["effect_blocked"]
            early_blocks = terminal_statuses[rid]["early_block"]
            available = c["effect_attempt"] + early_blocks
            if kind == "effect_blocked" and c["effect_attempt"] == used - early_blocks:
                require(recheck_denials[rid] > early_blocks, "block without failed check/attempt")
                terminal_statuses[rid]["early_block"] += 1
                available += 1
            require(available > used, "commit/block without unmatched attempt")
        if kind == "effect_committed":
            effect_results[payload["effect_id"]] = {
                "status": "committed",
                "effect_id": payload["effect_id"],
                "result": payload["result"],
            }
        if kind == "idempotent_replay":
            if (
                c["before_effect"]
                > c["effect_attempt"]
                + c["effect_rolled_back"]
                + terminal_statuses[rid]["late_replay"]
            ):
                terminal_statuses[rid]["late_replay"] += 1
            require(payload["effect_id"] in effect_results, "replay without prior commit")
        if kind == "request_cancelled":
            require(
                payload.get("reason") in {"superseded", "pending_at_end"}, "unknown cancellation"
            )
            require(
                c["requested"] > c["tool_response"] + c["request_cancelled"],
                "cancellation without pending request",
            )
        if kind == "tool_response":
            require(c["requested"] > c["tool_response"] + c["request_cancelled"], "extra response")
            response = payload["response"]
            status = response["status"]
            require(
                status in {"committed", "denied", "blocked", "rolled_back"},
                "invalid terminal response",
            )
            used = terminal_statuses[rid][status]
            if status == "committed":
                require(
                    c["effect_committed"] + c["idempotent_replay"] > used,
                    "response without commitment",
                )
                require(
                    response == effect_results.get(response.get("effect_id")),
                    "committed response mismatch",
                )
            elif status == "denied":
                require(len(decisions[rid]) - sum(decisions[rid]) > used, "denial without decision")
            else:
                require(
                    c["effect_blocked" if status == "blocked" else "effect_rolled_back"] > used,
                    "response without terminal effect evidence",
                )
            terminal_statuses[rid][status] += 1
            responses.append(response)
        if kind == "request_completion":
            require(c["tool_response"] > c["request_completion"], "completion without response")
        c[kind] += 1
        global_counts[kind] += 1
    if host:
        require(
            global_counts["session_initialization"] == global_counts["tool_discovery"] == 1,
            "missing mandatory session/discovery checkpoint",
        )
        require(global_counts["session_snapshot"] == 1, "missing session snapshot")
        require(
            Counter(map(digest, events[-1]["payload"].get("responses", [])))
            == Counter(map(digest, responses)),
            "terminal response summary mismatch",
        )
    if mode == "host-model-v2":
        require(global_counts["model_generation"] > 0, "missing model generation")
        require(
            global_counts["model_proposal"]
            == global_counts["requested"] + global_counts["proposal_rejected"],
            "unterminated proposal",
        )
        require(
            events[-1]["payload"].get("termination") in {"model_finished", "turn_budget"},
            "missing model termination disposition",
        )
    if mode == "host-fixed-v2":
        require(global_counts["requested"] == scenario["repeats"], "missing fixed requests")
        require(not global_counts["request_cancelled"], "fixed request cancelled")
        expected_requests = []
        for index in range(scenario["repeats"]):
            operation = dict(scenario["operation"])
            if index and scenario["duplicate_new_id"]:
                operation["request_id"] = f"{operation['request_id']}-{index}"
            expected_requests.append(digest(operation))
        observed = [digest(e["payload"]["operation"]) for e in events if e["kind"] == "requested"]
        require(
            Counter(expected_requests) == Counter(observed), "fixed request multiplicity mismatch"
        )
    for rid, c in counts.items():
        if rid is None:
            continue
        require(
            c["requested"] == c["request_completion"] + c["request_cancelled"],
            "unterminated request",
        )
        require(c["tool_response"] == c["request_completion"], "missing request completion")
        require(c["requested"] == c["gateway_decision"], "missing admission decision")
        if host:
            require(c["request_generation"] == c["requested"], "dangling generation")
        if mode == "host-model-v2":
            require(
                c["model_proposal"] == c["requested"] + c["proposal_rejected"],
                "proposal identity/termination mismatch",
            )
        require(
            c["effect_attempt"]
            == c["effect_committed"] + c["effect_blocked"] - terminal_statuses[rid]["early_block"],
            "unterminated effect attempt",
        )
        require(
            c["before_effect"]
            == c["effect_attempt"]
            + c["effect_rolled_back"]
            + terminal_statuses[rid]["late_replay"],
            "missing attempt/rollback",
        )
        require(c["after_commit"] == c["effect_committed"], "missing post-commit checkpoint")
        require(
            c["server_receipt"]
            == c["before_effect"]
            + c["idempotent_replay"]
            - terminal_statuses[rid]["late_replay"]
            + terminal_statuses[rid]["early_block"],
            "unterminated received request",
        )
        if events[0]["config"] == "C4":
            require(
                c["effect_recheck"]
                == c["server_receipt"]
                - c["idempotent_replay"]
                + terminal_statuses[rid]["late_replay"],
                "missing C4 recheck",
            )
        if events[0]["config"] == "C5":
            require(c["atomic_decision"] == c["effect_attempt"], "missing C5 decision evidence")
        if host:
            require(c["mcp_dispatch"] == c["server_receipt"], "dispatch missing server receipt")


def validate_fixture_protocol(events, name):
    """Fixtures omit host transport checkpoints, not primitive attempt/commit causality."""
    counts = defaultdict(Counter)
    for event in events:
        kind, rid = event["kind"], event["request_id"]
        require(
            kind
            in {
                "initialized",
                "requested",
                "gateway_decision",
                "policy_changed",
                "effect_attempt",
                "effect_committed",
                "run_completed",
            },
            "host-only event in a primitive fixture",
        )
        c = counts[rid]
        if kind == "gateway_decision":
            require(c["requested"] > c["gateway_decision"], "fixture decision without request")
        if kind == "effect_attempt":
            require(c["gateway_decision"] > 0, "fixture attempt without decision")
        if kind == "effect_committed":
            require(c["effect_attempt"] > c["effect_committed"], "fixture commit without attempt")
        c[kind] += 1
    for rid, c in counts.items():
        if rid is not None:
            pending = 1 if name == "attempt-only" else 0
            require(
                c["effect_attempt"] == c["effect_committed"] + pending,
                "fixture has undeclared pending attempts",
            )
