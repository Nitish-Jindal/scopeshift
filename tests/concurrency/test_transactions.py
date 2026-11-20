import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from scopeshift.dataset import select
from scopeshift.effects import commit, execute
from scopeshift.gateway import invocation, register
from scopeshift.storage import Store


def prepared(tmp_path, name="authorized_update"):
    s = select(name)
    store = Store(tmp_path / "run.sqlite3")
    store.initialize(s, "C5")
    register(store, s.operation, "C5", s.initial)
    assert invocation(store, s.operation, "C5", s.initial)
    return store, s


class Contender(Store):
    def __init__(self, path, attempted):
        super().__init__(path)
        self.attempted = attempted

    def connect(self):
        c = super().connect()
        c.set_trace_callback(lambda sql: self.attempted.set() if sql == "BEGIN IMMEDIATE" else None)
        return c


@pytest.mark.parametrize("first", ["effect", "revocation"])
def test_real_competing_transaction_orderings(first, tmp_path):
    store, s = prepared(tmp_path)
    attempted = threading.Event()
    contender = Contender(store.path, attempted)
    with ThreadPoolExecutor(max_workers=1) as pool:
        if first == "effect":

            def hook(c):
                nonlocal future
                future = pool.submit(contender.transition, "revoke", {"id": "g1"})
                assert attempted.wait(2), "competing transaction did not attempt BEGIN"
                assert not future.done(), "revocation crossed open effect transaction"

            future = None
            result = commit(store, s.operation, transaction_hook=hook)
            future.result(timeout=5)
            assert result["status"] == "committed"
        else:
            with store.transaction() as c:
                store._transition(c, "revoke", {"id": "g1"})
                future = pool.submit(commit, contender, s.operation)
                assert attempted.wait(2)
                assert not future.done(), "effect crossed open revocation transaction"
            assert future.result(timeout=5)["status"] == "blocked"
    evidence = store.export()
    assert len(evidence["effects"]) == (1 if first == "effect" else 0)


def test_real_single_use_approval_contention(tmp_path):
    store, s = prepared(tmp_path, "authorized_message")
    other = s.operation.model_copy(update={"request_id": "r2"})
    register(store, other, "C5", s.initial)
    assert invocation(store, other, "C5", s.initial)
    barrier = threading.Barrier(2)

    def worker(op):
        barrier.wait(timeout=3)
        return commit(Store(store.path), op)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = [pool.submit(worker, op) for op in [s.operation, other]]
        results = [f.result(timeout=6) for f in futures]
    assert sorted(r["status"] for r in results) == ["blocked", "committed"]
    assert len(store.export()["messages"]) == 1


def test_rollback_leaves_no_effect_or_resource_change(tmp_path):
    store, s = prepared(tmp_path)

    def fail(c):
        c.execute("UPDATE records SET value='123' WHERE id='record:1'")
        raise ValueError("injected after mutation")

    assert commit(store, s.operation, transaction_hook=fail)["status"] == "rolled_back"
    assert store.export()["records"]["record:1"] == "initial"
    assert store.export()["effects"] == []


def test_request_conflict_and_server_binding(tmp_path):
    store, s = prepared(tmp_path)
    other = s.operation.model_copy(update={"args": {"value": True}})
    assert not register(store, other, "C5", s.initial)
    assert execute(store, "r1", "send_message")["reason"] == "tool_binding"
    assert commit(store, other)["status"] == "rolled_back"
    assert store.export()["effects"] == []


def test_bounded_contention_cannot_forge_rollback_evidence(tmp_path):
    store, s = prepared(tmp_path)
    contender = Store(store.path, busy_timeout_ms=20)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with store.transaction():
            result = pool.submit(commit, contender, s.operation).result(timeout=2)
    assert result == {"status": "inconclusive", "reason": "contention_evidence_unavailable"}
    assert store.export()["effects"] == []
    assert not any(e["kind"] == "effect_rolled_back" for e in store.export()["events"])
