"""SQLite authority and trusted evidence. Each transaction owns its connection."""

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path

from scopeshift.contracts import CHECKPOINTS, canonical, digest

SCHEMA = """
CREATE TABLE settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE grants (id TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE approvals (id TEXT PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE requests (id TEXT PRIMARY KEY, body TEXT NOT NULL, config TEXT NOT NULL,
 snapshot TEXT NOT NULL, result TEXT, dispatch INTEGER NOT NULL DEFAULT 0);
CREATE TABLE events (seq INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL);
CREATE TABLE effects (id INTEGER PRIMARY KEY AUTOINCREMENT, request_id TEXT NOT NULL,
 body TEXT NOT NULL);
CREATE TABLE records (id TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE messages (id INTEGER PRIMARY KEY, body TEXT NOT NULL);
CREATE TABLE disclosures (id INTEGER PRIMARY KEY, body TEXT NOT NULL);
"""


class Store:
    def __init__(self, path: str | Path, busy_timeout_ms: int = 2000):
        if not 1 <= busy_timeout_ms <= 2000:
            raise ValueError("busy timeout must be bounded to 1..2000 ms")
        self.path = str(path)
        self.busy_timeout_ms = busy_timeout_ms

    def connect(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path, timeout=self.busy_timeout_ms / 1000, isolation_level=None)
        c.row_factory = sqlite3.Row
        c.execute("PRAGMA foreign_keys=ON")
        c.execute(f"PRAGMA busy_timeout={self.busy_timeout_ms}")
        return c

    @contextmanager
    def transaction(self):
        c = self.connect()
        try:
            # SQLite's bounded busy handler retries contention for <=2 seconds.
            # Never retry a partially executed effect at application level.
            c.execute("BEGIN IMMEDIATE")
            yield c
            c.commit()
        except BaseException:
            c.rollback()
            raise
        finally:
            c.close()

    @staticmethod
    def get(c, key):
        row = c.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
        return json.loads(row[0]) if row else None

    @staticmethod
    def put(c, key, value):
        c.execute("INSERT OR REPLACE INTO settings VALUES (?,?)", (key, canonical(value)))

    @staticmethod
    def state(c) -> dict:
        return {
            "grants": [json.loads(r[0]) for r in c.execute("SELECT body FROM grants ORDER BY id")],
            "approvals": [
                json.loads(r[0]) for r in c.execute("SELECT body FROM approvals ORDER BY id")
            ],
            "version": Store.get(c, "version"),
            "time": Store.get(c, "time"),
        }

    @staticmethod
    def event(c, kind, source, request_id=None, **payload):
        row = c.execute("SELECT seq, body FROM events ORDER BY seq DESC LIMIT 1").fetchone()
        seq = row[0] + 1 if row else 1
        previous = json.loads(row[1])["hash"] if row else "0" * 64
        event = {
            "schema_version": 1,
            "run_id": Store.get(c, "run_id"),
            "scenario": Store.get(c, "scenario_id"),
            "config": Store.get(c, "config"),
            "seq": seq,
            "kind": kind,
            "source": source,
            "request_id": request_id,
            "depends_on": [seq - 1] if seq > 1 else [],
            "previous": previous,
            "policy_version": Store.get(c, "version"),
            "logical_time": Store.get(c, "time"),
            "payload": payload,
        }
        event["hash"] = digest(event)
        c.execute("INSERT INTO events(seq,body) VALUES (?,?)", (seq, canonical(event)))
        return seq

    def initialize(self, scenario, config, seed=0, mutant=None):
        from scopeshift.scheduler import validate_schedule

        validate_schedule(scenario)
        if str(config) not in {f"C{i}" for i in range(6)}:
            raise ValueError("unknown configuration")
        if Path(self.path).exists():
            raise ValueError(
                "refusing to overwrite an existing database; use a fresh run directory"
            )
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        c = self.connect()
        try:
            c.execute("PRAGMA journal_mode=WAL")
            c.executescript(SCHEMA)
        finally:
            c.close()
        with self.transaction() as c:
            for key, value in {
                "run_id": f"{scenario.id}-{config}-{seed}",
                "scenario_id": scenario.id,
                "config": str(config),
                "version": scenario.initial.get("version", 1),
                "time": scenario.initial.get("time", 0),
                "seed": seed,
                "mutant": mutant,
                "schedule": [t.model_dump() for t in scenario.schedule],
                "fired": [],
                "malicious_response": scenario.malicious_response,
            }.items():
                self.put(c, key, value)
            for table in ("grants", "approvals"):
                for body in scenario.initial.get(table, []):
                    c.execute(f"INSERT INTO {table} VALUES (?,?)", (body["id"], canonical(body)))
            c.execute("INSERT INTO records VALUES ('record:1',?)", (canonical("initial"),))
            c.execute("INSERT INTO records VALUES ('record:2',?)", (canonical("other"),))
            self.event(
                c,
                "initialized",
                "authority",
                state=self.state(c),
                records={"record:1": "initial", "record:2": "other"},
                scenario=scenario.model_dump(),
            )

    def transition(self, kind, data, visible=False):
        with self.transaction() as c:
            self._transition(c, kind, data, visible)

    def _transition(self, c, kind, data, visible=False):
        if kind in ("revoke", "narrow"):
            row = c.execute("SELECT body FROM grants WHERE id=?", (data["id"],)).fetchone()
            if not row:
                raise ValueError("unknown grant")
            grant = json.loads(row[0])
            if kind == "revoke":
                grant["revoked"] = True
            else:
                grant["constraints"] = data["constraints"]
                grant["generation"] += 1
            c.execute("UPDATE grants SET body=? WHERE id=?", (canonical(grant), data["id"]))
        elif kind in ("grant", "approve"):
            table = "grants" if kind == "grant" else "approvals"
            c.execute(f"INSERT INTO {table} VALUES (?,?)", (data["id"], canonical(data)))
        elif kind == "tick":
            if data["time"] < self.get(c, "time"):
                raise ValueError("logical time cannot go backwards")
            self.put(c, "time", data["time"])
        elif kind != "unrelated":
            raise ValueError("unknown policy transition")
        self.put(c, "version", self.get(c, "version") + 1)
        self.event(
            c,
            "policy_changed",
            "authority",
            transition=kind,
            data=data,
            visible=visible,
            state=self.state(c),
        )

    def checkpoint(self, name, request_id=None, **payload):
        if name not in CHECKPOINTS:
            raise ValueError("unknown or non-causal checkpoint")
        # Claim and apply transitions together: concurrent arrivals cannot overtake them.
        # This transaction is always outside the C5 effect transaction.
        with self.transaction() as c:
            self.event(c, name, "scheduler", request_id, **payload)
            schedule, fired = self.get(c, "schedule"), self.get(c, "fired")
            pending = [(i, t) for i, t in enumerate(schedule) if t["at"] == name and i not in fired]
            for _, transition in pending:
                self._transition(c, transition["kind"], transition["data"], transition["visible"])
            self.put(c, "fired", fired + [i for i, _ in pending])

    def export(self) -> dict:
        c = self.connect()
        try:
            c.execute("BEGIN")  # One coherent read snapshot across all evidence tables.
            return {
                "schema_version": 1,
                "events": [
                    json.loads(r[0]) for r in c.execute("SELECT body FROM events ORDER BY seq")
                ],
                "effects": [
                    dict(id=r["id"], **json.loads(r["body"]))
                    for r in c.execute("SELECT * FROM effects ORDER BY id")
                ],
                "final_policy": self.state(c),
                "records": {r[0]: json.loads(r[1]) for r in c.execute("SELECT * FROM records")},
                "messages": [
                    json.loads(r[0]) for r in c.execute("SELECT body FROM messages ORDER BY id")
                ],
                "disclosures": [
                    json.loads(r[0]) for r in c.execute("SELECT body FROM disclosures ORDER BY id")
                ],
            }
        finally:
            c.close()
