"""Member factories for faction C2 decision agents."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from nuclear_war_env.agent_protocol import DecisionAgent

from .llm_agent import LLMDecisionAgent
from .llm_types import LLMModelClient


class SubordinateFactory(Protocol):
    def build_members(self) -> Sequence[tuple[str, DecisionAgent]]: ...


@dataclass
class DirectMemberFactory:
    members: Sequence[tuple[str, DecisionAgent]]

    def build_members(self) -> Sequence[tuple[str, DecisionAgent]]:
        return tuple(self.members)


@dataclass
class ScriptedSubordinateFactory:
    members: Sequence[tuple[str, LLMModelClient]]

    def build_members(self) -> Sequence[tuple[str, DecisionAgent]]:
        return tuple(
            (member_id, LLMDecisionAgent(client, max_retries=0, fallback="first"))
            for member_id, client in self.members
        )


__all__ = [
    "DirectMemberFactory",
    "ScriptedSubordinateFactory",
    "SubordinateFactory",
]
