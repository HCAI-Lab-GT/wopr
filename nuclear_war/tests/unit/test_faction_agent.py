"""Composite faction C2 decision agent tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_agents import ScriptedLLMClient
from nuclear_war_agents.faction_agent import (
    FactionDecisionAgent,
    ScriptedSubordinateFactory,
)
from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation


def test_faction_council_agent_returns_aggregated_action(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    options = faction_options
    members = [
        ("advisor_a", ScriptedLLMClient([_response(options[0].action_id)])),
        ("advisor_b", ScriptedLLMClient([_response(options[1].action_id)])),
        ("advisor_c", ScriptedLLMClient([_response(options[1].action_id)])),
    ]
    agent = FactionDecisionAgent(
        archetype="council",
        subordinate_factory=ScriptedSubordinateFactory(members),
        archetype_parameters={"threshold": 0.5},
    )

    selected = agent.choose(faction_observation, options)

    assert selected == options[1]
    assert agent.last_deliberation is not None
    assert agent.last_deliberation.selected_action_id == options[1].action_id
    assert len(agent.last_deliberation.member_votes) == 3


def test_faction_automated_agent_returns_policy_action(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    options = faction_options
    members = [("advisor_a", ScriptedLLMClient([_response(options[0].action_id)]))]
    agent = FactionDecisionAgent(
        archetype="automated",
        subordinate_factory=ScriptedSubordinateFactory(members),
        archetype_parameters={"policy_action_id": options[1].action_id},
    )

    selected = agent.choose(faction_observation, options)

    assert selected == options[1]
    assert agent.last_deliberation is not None
    assert agent.last_deliberation.selected_action_id == options[1].action_id
    assert agent.last_deliberation.rule == "pre_armed_policy"


def test_faction_automated_agent_falls_back_when_policy_illegal(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    options = faction_options
    members = [("advisor_a", ScriptedLLMClient([_response(options[0].action_id)]))]
    agent = FactionDecisionAgent(
        archetype="automated",
        subordinate_factory=ScriptedSubordinateFactory(members),
        archetype_parameters={"policy_action_id": "p1:not-legal-here"},
    )

    selected = agent.choose(faction_observation, options)

    # The pre-armed policy id is not legal at this decision, so the agent falls
    # back to the first legal option and records the fallback in the deliberation.
    assert selected == options[0]
    assert agent.last_deliberation is not None
    assert agent.last_deliberation.selected_action_id == options[0].action_id
    assert agent.last_deliberation.rule != "pre_armed_policy"
    assert "pre_armed_policy" in agent.last_deliberation.rule


def test_faction_automated_agent_requires_policy_action_id(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    options = faction_options
    members = [("advisor_a", ScriptedLLMClient([_response(options[0].action_id)]))]
    agent = FactionDecisionAgent(
        archetype="automated",
        subordinate_factory=ScriptedSubordinateFactory(members),
        archetype_parameters={},
    )

    with pytest.raises(ValueError, match="policy_action_id"):
        agent.choose(faction_observation, options)


def test_faction_agent_choose_returns_legal_action(
    faction_observation: Observation,
    faction_options: list[LegalAction],
) -> None:
    options = faction_options
    members = [("advisor_a", ScriptedLLMClient([_response(options[0].action_id)]))]
    agent = FactionDecisionAgent(
        archetype="council",
        subordinate_factory=ScriptedSubordinateFactory(members),
        archetype_parameters={"threshold": 0.5},
    )

    selected = agent.choose(faction_observation, options)

    assert isinstance(selected, LegalAction)
    assert selected in options


def _response(action_id: str) -> str:
    return json.dumps({"action_id": action_id, "rationale": "vote"})
