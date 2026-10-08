"""Agent contract for the decision-point loop and a legacy adapter."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .action_models import LegalAction
from .observation import Observation


class DecisionAgent(Protocol):
    def choose(
        self, observation: Observation, options: list[LegalAction]
    ) -> LegalAction: ...


class _LegacyAgent(Protocol):
    def choose(self, actions: list[LegalAction]) -> LegalAction: ...


@dataclass
class _LegacyAdapter:
    legacy: _LegacyAgent

    def choose(
        self, observation: Observation, options: list[LegalAction]
    ) -> LegalAction:
        return self.legacy.choose(options)


def as_decision_agent(legacy_agent: _LegacyAgent) -> DecisionAgent:
    return _LegacyAdapter(legacy_agent)


__all__ = ["DecisionAgent", "as_decision_agent"]
