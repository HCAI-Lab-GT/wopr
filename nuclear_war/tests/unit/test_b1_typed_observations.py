"""B1 typed observation contract tests."""

from __future__ import annotations

from dataclasses import is_dataclass
from typing import Any, get_type_hints

import pytest

from nuclear_war_env import observation as observation_module
from nuclear_war_env.action_models import ActionType, LegalAction, build_action
from nuclear_war_env.agent_protocol import DecisionAgent
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.decision_loop import run_decisions, start_game
from nuclear_war_env.engine.decision import (
    Decision,
    DecisionCursor,
    DecisionType,
    TurnPhase,
)
from nuclear_war_env.simulation import SimulationConfig, run_simulation
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state() -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(
        [
            Card(
                "delivery",
                CardCategory.DELIVERY,
                "Delivery",
                metadata={"capacity": 1},
            ),
            Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
            Card(
                "hidden_am",
                CardCategory.ANTIMISSILE,
                "Anti-Missile",
                metadata={"intercept": "any"},
            ),
        ]
    )
    return state


def test_observe_returns_typed_copied_player_observation() -> None:
    state = _state()
    viewer = state.players["p1"]
    viewer.hand = ["own_hand"]
    viewer.secrets = ["own_secret"]
    viewer.deterrents = ["own_deterrent", None]
    viewer.face_down_queue.clear()
    viewer.face_down_queue.extend(["own_delivery", "own_warhead"])
    viewer.final_strike_cards = ["own_final"]
    viewer.pending_orders = {
        "launches": {"own_delivery": {"target": "p2", "warheads": ["own_warhead"]}}
    }
    hidden = state.players["p2"]
    hidden.hand = ["hidden_hand"]
    hidden.secrets = ["hidden_secret"]
    hidden.deterrents = ["hidden_deterrent", None]
    hidden.face_down_queue.clear()
    hidden.face_down_queue.extend(["hidden_delivery", "hidden_warhead"])

    observation = observation_module.observe(state, "p1")

    assert isinstance(observation, observation_module.Observation)
    assert is_dataclass(observation)
    assert isinstance(observation.self, observation_module.PrivatePlayerObservation)
    assert isinstance(
        observation.players["p2"], observation_module.PublicPlayerObservation
    )
    assert observation.self.hand == ["own_hand"]
    assert observation.self.secrets == ["own_secret"]
    assert observation.self.deterrents == ["own_deterrent", None]
    observation.self.pending_orders["launches"]["own_delivery"]["target"] = "changed"
    assert (
        state.players["p1"].pending_orders["launches"]["own_delivery"]["target"] == "p2"
    )
    assert "hidden_hand" not in str(observation)
    assert "hidden_secret" not in str(observation)
    assert "hidden_deterrent" not in str(observation)
    assert "hidden_delivery" not in str(observation)
    assert "hidden_warhead" not in str(observation)


def test_decision_agent_protocol_uses_typed_observation() -> None:
    hints = get_type_hints(DecisionAgent.choose)

    assert hints["observation"] is observation_module.Observation


def test_observe_uses_cursor_round_when_present() -> None:
    state = _state()
    state.turn = 0
    state.cursor = DecisionCursor("p1", TurnPhase.PLACE, round=7)

    observation = observation_module.observe(state, "p1")

    assert observation.turn == 7


def test_decision_observation_visible_only_to_decision_owner() -> None:
    state = _state()
    state.cursor = DecisionCursor("p1", TurnPhase.SECRETS)
    action = build_action(
        "p1",
        ActionType.SECRET_TARGET,
        "Target secret",
        {"card": "own_secret", "target": "p2"},
    )
    state.cursor.pending = Decision(
        "p1",
        DecisionType.SECRET_TARGET,
        [action],
        context={"card": "own_secret"},
    )

    owner = observation_module.observe(state, "p1")
    other = observation_module.observe(state, "p2")

    assert isinstance(owner.decision, observation_module.DecisionObservation)
    assert owner.decision.decision_type is DecisionType.SECRET_TARGET
    assert owner.decision.options[0].payload == {"card": "own_secret", "target": "p2"}
    owner.decision.options[0].payload["target"] = "changed"
    assert action.payload["target"] == "p2"
    assert other.decision is None
    assert "own_secret" not in str(other)


def test_intercept_options_are_visible_only_to_defender() -> None:
    state = _state()
    state.players["p2"].hand = ["hidden_am"]
    state.cursor = DecisionCursor("p1", TurnPhase.INTERCEPT)
    state.cursor.pending = Decision(
        "p2",
        DecisionType.INTERCEPT,
        [
            build_action(
                "p2",
                ActionType.INTERCEPT,
                "Intercept with hidden_am",
                {"card": "hidden_am"},
            ),
            build_action("p2", ActionType.INTERCEPT, "Decline", {}),
        ],
        context={"attacker": "p1", "delivery": "delivery"},
    )

    defender = observation_module.observe(state, "p2")
    attacker = observation_module.observe(state, "p1")

    assert defender.decision is not None
    assert defender.decision.options[0].payload == {"card": "hidden_am"}
    assert attacker.decision is None
    assert "hidden_am" not in str(attacker)


class _StopAfterObservation(Exception):
    pass


class _CapturingDecisionAgent:
    def __init__(self) -> None:
        self.observation: object | None = None

    def choose(self, observation: Any, options: list[LegalAction]) -> LegalAction:
        self.observation = observation
        raise _StopAfterObservation


def test_run_decisions_passes_typed_observation_to_agent() -> None:
    state = _state()
    start_game(state)
    agent = _CapturingDecisionAgent()
    agents: dict[str, DecisionAgent] = {player_id: agent for player_id in state.players}

    with pytest.raises(_StopAfterObservation):
        run_decisions(state, agents, max_turns=1)

    assert isinstance(agent.observation, observation_module.Observation)


def test_table_simulation_passes_typed_observation_to_agent(monkeypatch) -> None:
    seen: list[object] = []

    class CaptureDecisionAgent:
        def choose(self, observation: Any, options: list[LegalAction]) -> LegalAction:
            seen.append(observation)
            return options[0]

    monkeypatch.setattr(
        "nuclear_war_env.agent_protocol.as_decision_agent",
        lambda agent: CaptureDecisionAgent(),
    )

    run_simulation(SimulationConfig("table", 3, 1, "heuristic", max_turns=1))

    assert any(isinstance(item, observation_module.Observation) for item in seen)


def test_existing_observation_adapters_keep_shapes() -> None:
    state = _state()

    player_observation = observation_module.to_player_observation(state, "p1")
    numeric_observation = observation_module.to_numeric_observation(state, "p1")

    assert player_observation["self"]["hand"] == []
    assert player_observation["players"]["p2"]["hand_count"] == 0
    assert isinstance(numeric_observation, list)
    assert len(numeric_observation) == 6
