"""Independent normative state machine. No enforcement or execution imports."""

from copy import deepcopy

from scopeshift.contracts import digest


class Reference:
    def __init__(self, initial: dict):
        self.state = deepcopy(initial)
        self.state.setdefault("time", 0)
        self.state.setdefault("version", 1)
        self.state.setdefault("grants", [])
        self.state.setdefault("approvals", [])

    def permits(self, operation: dict, mutant=None) -> bool:
        who = operation["identity"]
        eligible = [g for g in self.state["grants"] if g["id"] == operation["grant_id"]]
        if not eligible:
            return False
        g = eligible[0]
        fields = ["principal", "agent", "session"]
        if mutant == "ignore_session":
            fields.remove("session")
        if g["revoked"] or any(g[k] != who[k] for k in fields):
            return False
        if (g["action"], g["resource"]) != (operation["action"], operation["resource"]):
            return False
        if any(
            k not in operation["args"] or digest(operation["args"][k]) != digest(v)
            for k, v in g.get("constraints", {}).items()
        ):
            return False
        if operation["action"] != "send_message" or mutant == "ignore_approval":
            return True
        approvals = [a for a in self.state["approvals"] if a["id"] == operation["approval_id"]]
        if not approvals:
            return False
        a = approvals[0]
        return (
            a.get("consumed_by") is None
            and self.state["time"] < a["expires_at"]
            and all(a[k] == who[k] for k in fields)
            and a["action"] == operation["action"]
            and a["resource"] == operation["resource"]
            and a["grant_id"] == operation["grant_id"]
            and a["digest"] == digest(operation["args"])
        )

    def transition(self, kind: str, data: dict):
        if kind in {"grant", "approve"}:
            target = "grants" if kind == "grant" else "approvals"
            if any(item["id"] == data["id"] for item in self.state[target]):
                raise ValueError("immutable identifier reused")
            self.state[target].append(deepcopy(data))
        elif kind in {"revoke", "narrow"}:
            grant = next(g for g in self.state["grants"] if g["id"] == data["id"])
            if kind == "revoke":
                grant["revoked"] = True
            else:
                grant["constraints"] = deepcopy(data["constraints"])
                grant["generation"] += 1
        elif kind == "tick":
            if data["time"] < self.state["time"]:
                raise ValueError("time reversal")
            self.state["time"] = data["time"]
        elif kind != "unrelated":
            raise ValueError("unknown transition")
        self.state["version"] += 1

    def consume(self, operation: dict):
        if operation["action"] == "send_message" and operation.get("approval_id"):
            for approval in self.state["approvals"]:
                matches = (
                    approval["id"] == operation["approval_id"]
                    and approval.get("consumed_by") is None
                    and self.state["time"] < approval["expires_at"]
                    and all(
                        approval[k] == operation["identity"][k]
                        for k in ("principal", "agent", "session")
                    )
                    and all(approval[k] == operation[k] for k in ("action", "resource", "grant_id"))
                    and approval["digest"] == digest(operation["args"])
                )
                if matches and self.permits(operation):
                    approval["consumed_by"] = operation["request_id"]

    def normalized(self):
        state = deepcopy(self.state)
        for key in ("grants", "approvals"):
            state[key].sort(key=lambda item: item["id"])
        return state
