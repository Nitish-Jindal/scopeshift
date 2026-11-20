"""Trusted request registration and invocation-time decisions."""

import json

from scopeshift.contracts import Operation, canonical
from scopeshift.policy import authorize
from scopeshift.storage import Store


def register(store: Store, op: Operation, config: str, snapshot: dict) -> bool:
    with store.transaction() as c:
        old = c.execute("SELECT body FROM requests WHERE id=?", (op.request_id,)).fetchone()
        if old:
            if json.loads(old[0]) != op.model_dump():
                store.event(c, "identity_conflict", "gateway", op.request_id)
                return False
        else:
            c.execute("INSERT INTO requests VALUES (?,?,?,?,NULL)",
                      (op.request_id, canonical(op.model_dump()), config, canonical(snapshot)))
        store.event(c, "requested", "gateway", op.request_id, operation=op.model_dump())
    return True


def invocation(store: Store, op: Operation, config: str, snapshot: dict) -> bool:
    with store.transaction() as c:
        state = store.state(c)
        mutant = store.get(c, "mutant")
        if config in ("C0", "C1"):
            ok, reason = True, "ambient" if config == "C0" else "prompt_only"
        elif config == "C2":
            ok, reason = authorize(snapshot, op, mutant)
        else:
            ok, reason = authorize(state, op, mutant)
        if mutant == "reject_unrelated" and state["version"] != snapshot["version"]:
            ok, reason = False, "version_changed"
        # An idempotent retry returns a committed result even if authority later changed.
        row = c.execute("SELECT result FROM requests WHERE id=?", (op.request_id,)).fetchone()
        if row and row[0] is not None:
            ok, reason = True, "idempotent_replay"
        store.event(c, "gateway_decision", "gateway", op.request_id,
                    allowed=ok, reason=reason, operation=op.model_dump(), state=state)
    store.checkpoint("gateway_authorization", op.request_id, allowed=ok)
    return ok
