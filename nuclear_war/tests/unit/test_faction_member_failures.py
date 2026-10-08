"""Faction-member failure behavior tests."""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from nuclear_war_agents import DirectMemberFactory, FactionDecisionAgent
from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation


@dataclass
class FailingAfterOneAgent:
    calls: int = 0

    def choose(
        self,
        observation: Observation,
        options: list[LegalAction],
    ) -> LegalAction:
        self.calls += 1
        if self.calls > 1:
            raise RuntimeError("member unavailable")
        return options[0]


@dataclass
class TrackingAgent:
    calls: list[int] = field(default_factory=list)

    def choose(
        self,
        observation: Observation,
        options: list[LegalAction],
    ) -> LegalAction:
        self.calls.append(observation.turn)
        return options[0]


def test_faction_agent_aborts_failed_deliberation_without_stale_result(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    failing = FailingAfterOneAgent()
    follower = TrackingAgent()
    agent = FactionDecisionAgent(
        archetype="council",
        subordinate_factory=DirectMemberFactory(
            [("first", failing), ("follower", follower)]
        ),
        archetype_parameters={"threshold": 0.5},
    )
    agent.choose(faction_observation, faction_options)

    with pytest.raises(RuntimeError, match="member unavailable"):
        agent.choose(faction_observation, faction_options)

    assert agent.last_deliberation is None
    assert len(agent.deliberations) == 1
    assert follower.calls == [1]
