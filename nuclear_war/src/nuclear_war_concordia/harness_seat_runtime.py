"""Runtime surfaces for one Concordia-controlled player seat."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nuclear_war_env.agent_protocol import DecisionAgent

from .agent import ConcordiaDecisionAgent
from .types import ConcordiaClient


@dataclass
class ConcordiaSeatRuntime:
    strategic_agent: DecisionAgent
    spokesperson_client: ConcordiaClient
    spokesperson_identity: dict[str, str]
    memory_recipients: tuple[ConcordiaDecisionAgent, ...]
    member_traces: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    def set_press_memory(self, messages: list[dict[str, Any]]) -> None:
        for recipient in self.memory_recipients:
            recipient.press_memory = list(messages)


__all__ = ["ConcordiaSeatRuntime"]
