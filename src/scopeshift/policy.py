"""Enforcement implementation. The reference model must never import this module."""

from scopeshift.contracts import Operation


def authorize(state: dict, op: Operation, mutant: str | None = None) -> tuple[bool, str]:
    grants = state["grants"]
    grant = next((g for g in grants if g["id"] == op.grant_id), None)
    if not grant:
        return False, "unknown_grant"
    if grant["revoked"] and mutant != "ignore_revocation":
        return False, "revoked"
    for field in ("principal", "agent", "session"):
        if grant[field] != getattr(op.identity, field) and mutant != f"ignore_{field}":
            return False, field
    if grant["action"] != op.action:
        return False, "action"
    if grant["resource"] != op.resource and mutant != "ignore_resource":
        return False, "resource"
    for key, value in grant.get("constraints", {}).items():
        if op.args.get(key) != value and mutant != "ignore_arguments":
            return False, "scope"
    if op.action == "send_message":
        approval = next((a for a in state["approvals"] if a["id"] == op.approval_id), None)
        if approval is None:
            return False, "missing_approval"
        if approval.get("consumed_by") is not None and mutant != "duplicate_approval":
            return False, "consumed"
        if state["time"] >= approval["expires_at"] and mutant != "ignore_expiry":
            return False, "expired"
        for field in ("principal", "agent", "session"):
            if approval[field] != getattr(op.identity, field) and mutant != f"ignore_{field}":
                return False, "approval_" + field
        for field, expected in (("action", op.action), ("resource", op.resource),
                                ("grant_id", op.grant_id), ("digest", op.argument_digest)):
            ignored = ((field == "digest" and mutant == "ignore_arguments") or
                       (field == "resource" and mutant == "ignore_resource"))
            if approval[field] != expected and not ignored:
                return False, "approval_" + field
    return True, "permitted"
