"""Neutral, serializable wire contracts; no authorization predicates."""

import hashlib
import json
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


def canonical(value: Any) -> str:
    def keys(v: Any) -> None:
        if isinstance(v, dict):
            if any(not isinstance(k, str) for k in v):
                raise ValueError("canonical JSON requires string keys")
            for item in v.values():
                keys(item)
        elif isinstance(v, list):
            for item in v:
                keys(item)

    keys(value)
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class Configuration(StrEnum):
    C0 = "C0"
    C1 = "C1"
    C2 = "C2"
    C3 = "C3"
    C4 = "C4"
    C5 = "C5"


class Identity(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    principal: str = "alice"
    agent: str = "assistant"
    session: str = "s1"


class Operation(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    request_id: str = "r1"
    identity: Identity = Field(default_factory=Identity)
    action: Literal["read_document", "search_documents", "get_record", "update_record", "send_message"]
    resource: str = "record:1"
    args: dict[str, Any] = Field(default_factory=dict)
    grant_id: str = "g1"
    approval_id: str | None = None

    @field_validator("args")
    @classmethod
    def valid_json(cls, value: dict) -> dict:
        canonical(value)
        return value

    @property
    def argument_digest(self) -> str:
        return digest(self.args)


class Transition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    at: str
    kind: Literal["revoke", "grant", "narrow", "tick", "approve", "unrelated"]
    data: dict = Field(default_factory=dict)
    visible: bool = False


class Scenario(BaseModel):
    model_config = ConfigDict(extra="forbid")
    schema_version: int = 1
    id: str
    family: str
    objective: str
    operation: Operation
    initial: dict
    schedule: list[Transition] = Field(default_factory=list)
    expected_safe_c5: bool = True
    legitimate: bool = True
    repeats: int = 1
    duplicate_new_id: bool = False
    malicious_response: bool = False
    visible_information: str = "Only initial scope is visible; infrastructure changes are hidden."
    invariants: list[str] = Field(default_factory=lambda: ["commit_authority", "identity", "evidence"])


CHECKPOINTS = (
    "session_initialization", "tool_discovery", "request_generation", "gateway_authorization",
    "mcp_dispatch", "server_receipt", "before_effect", "effect_committed", "tool_response",
    "request_completion",
)
