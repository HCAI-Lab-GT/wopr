"""Baseline agent tests."""

from __future__ import annotations

from nuclear_war_agents import HeuristicAgent, RandomAgent
from nuclear_war_env.actions import ActionType, LegalAction
from nuclear_war_env.rng import SeededRNG


def test_heuristic_agent_prioritizes_postal_propaganda() -> None:
    agent = HeuristicAgent(SeededRNG(seed=1))
    selected = agent.choose(
        [
            LegalAction("p1:pass", "p1", ActionType.PASS, "Pass"),
            LegalAction("p1:enqueue", "p1", ActionType.ENQUEUE, "Queue"),
            LegalAction(
                "p1:postal_propaganda",
                "p1",
                ActionType.POSTAL_PROPAGANDA,
                "Propaganda p2",
            ),
        ]
    )
    assert selected.action_type is ActionType.POSTAL_PROPAGANDA


def test_random_agent_selects_supplied_legal_action() -> None:
    actions = [
        LegalAction("p1:pass", "p1", ActionType.PASS, "Pass"),
        LegalAction("p1:draw", "p1", ActionType.DRAW, "Draw"),
    ]
    agent = RandomAgent(SeededRNG(seed=1))

    assert agent.choose(actions) in actions


def test_heuristic_agent_fallback_selects_supplied_legal_action() -> None:
    actions = [
        LegalAction("p1:secret", "p1", ActionType.POSTAL_SECRET_TARGET, "Secret"),
    ]
    agent = HeuristicAgent(SeededRNG(seed=1))

    assert agent.choose(actions) in actions
