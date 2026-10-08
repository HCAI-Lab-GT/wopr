"""Shared types for Concordia-backed WOPR runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from nuclear_war_agents import LLMCompletion


@dataclass(frozen=True)
class ConcordiaRuntimeStatus:
    runtime_path: str
    available: bool
    detail: str
    version: str | None = None


@dataclass(frozen=True)
class ConcordiaScene:
    text: str
    payload: dict[str, Any]


@dataclass(frozen=True)
class ParsedConcordiaDecision:
    action_id: str | None
    rationale: str | None = None


@dataclass(frozen=True)
class ParsedPressMessage:
    text: str | None = None
    rationale: str | None = None
    declined: bool = False
    recipient: str | None = None
    commitment: dict[str, Any] | None = None

    @property
    def visibility(self) -> str:
        if self.recipient is not None:
            return "private"
        return "public"

    @property
    def is_decline(self) -> bool:
        return self.declined and self.text is None


@dataclass(frozen=True)
class PressMessage:
    message_id: str
    turn: int
    round_no: int
    speaker: str
    audience: str
    visibility: str
    pass_no: int
    text: str | None
    is_decline: bool


class ConcordiaClient(Protocol):
    def complete(self, scene_text: str) -> str | LLMCompletion: ...
