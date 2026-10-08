"""Persistent faction-member behavior tests."""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from nuclear_war_agents.faction_agent import (
    DirectMemberFactory,
    FactionDecisionAgent,
)
from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation


@dataclass
class SequencedDecisionAgent:
    selections: list[int]
    calls: list[int] = field(default_factory=list)

    def choose(
        self,
        observation: Observation,
        options: list[LegalAction],
    ) -> LegalAction:
        self.calls.append(observation.turn)
        return options[self.selections[len(self.calls) - 1]]


@dataclass
class CountingMemberFactory:
    member: SequencedDecisionAgent
    build_count: int = 0

    def build_members(self) -> tuple[tuple[str, SequencedDecisionAgent], ...]:
        self.build_count += 1
        return (("advisor", self.member),)


def test_faction_agent_reuses_direct_member_across_decisions(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    member = SequencedDecisionAgent([0, 1])
    agent = FactionDecisionAgent(
        archetype="council",
        subordinate_factory=DirectMemberFactory([("advisor", member)]),
        archetype_parameters={"threshold": 0.5},
    )

    first = agent.choose(faction_observation, faction_options)
    second = agent.choose(faction_observation, faction_options)

    assert first == faction_options[0]
    assert second == faction_options[1]
    assert member.calls == [1, 1]


def test_faction_agent_builds_members_once_for_its_lifetime(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    factory = CountingMemberFactory(SequencedDecisionAgent([0, 1]))
    agent = FactionDecisionAgent(
        archetype="council",
        subordinate_factory=factory,
        archetype_parameters={"threshold": 0.5},
    )

    agent.choose(faction_observation, faction_options)
    agent.choose(faction_observation, faction_options)

    assert factory.build_count == 1


def test_faction_agent_records_contextual_deliberation_history(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    first = SequencedDecisionAgent([0, 0])
    second = SequencedDecisionAgent([1, 1])
    third = SequencedDecisionAgent([1, 1])
    agent = FactionDecisionAgent(
        archetype="council",
        subordinate_factory=DirectMemberFactory(
            [("first", first), ("second", second), ("third", third)]
        ),
        archetype_parameters={"threshold": 0.5},
    )

    first_selected = agent.choose(faction_observation, faction_options)
    second_selected = agent.choose(
        replace(faction_observation, turn=2), faction_options
    )

    assert [item.player_id for item in agent.deliberations] == ["p1", "p1"]
    assert [item.turn for item in agent.deliberations] == [1, 2]
    assert [item.decision_type for item in agent.deliberations] == [
        "launch_target",
        "launch_target",
    ]
    assert first.calls == [1, 2]
    assert second.calls == [1, 2]
    assert third.calls == [1, 2]
    assert first_selected == faction_options[1]
    assert second_selected == faction_options[1]
    latest = agent.last_deliberation
    assert latest is not None
    assert latest == agent.deliberations[-1]
    assert latest.selected_action_id == faction_options[1].action_id
    assert latest.rule == "weighted_majority"
    assert latest.parameters == {"threshold": 0.5}
    assert [vote.member_id for vote in latest.member_votes] == [
        "first",
        "second",
        "third",
    ]
    assert [vote.action_id for vote in latest.member_votes] == [
        faction_options[0].action_id,
        faction_options[1].action_id,
        faction_options[1].action_id,
    ]
