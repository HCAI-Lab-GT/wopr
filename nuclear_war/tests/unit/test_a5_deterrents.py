from __future__ import annotations

import pytest

from nuclear_war_agents.baseline import HeuristicAgent
from nuclear_war_env.action_models import ActionType, build_action
from nuclear_war_env.actions import apply_action
from nuclear_war_env.actions_deterrents import (
    apply_deterrent_action,
    deterrent_actions,
)
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.decision import DecisionType, TurnPhase
from nuclear_war_env.replay_action_payload_validation import validate_action_payload
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _modify_deterrent_action(payload: dict) -> dict:
    return {
        "action_type": "modify_deterrent",
        "payload": payload,
    }


def test_deterrent_decision_enum_members_exist() -> None:
    assert DecisionType.MODIFY_DETERRENT.value == "modify_deterrent"
    assert TurnPhase.DETERRENTS.value == "deterrents"
    assert ActionType.MODIFY_DETERRENT.value == "modify_deterrent"


def test_heuristic_prioritizes_deterrent_skip_before_place() -> None:
    agent = HeuristicAgent(SeededRNG(0))
    skip = build_action("p1", ActionType.MODIFY_DETERRENT, "Skip deterrents", {})
    place = build_action("p1", ActionType.ENQUEUE, "Place card", {"cards": ["a"]})

    selected = agent.choose([place, skip])

    assert selected == skip


def test_replay_accepts_modify_deterrent_payload_shapes() -> None:
    validate_action_payload(_modify_deterrent_action({}), 0)
    validate_action_payload(
        _modify_deterrent_action({"card": "card_a", "to_slot": 0}), 1
    )
    validate_action_payload(_modify_deterrent_action({"from_slot": 1}), 2)


def test_replay_rejects_malformed_modify_deterrent_payload() -> None:
    with pytest.raises(ValueError, match="modify_deterrent payload fields"):
        validate_action_payload(
            _modify_deterrent_action({"card": "card_a", "to_slot": 0, "extra": 1}),
            0,
        )
    with pytest.raises(ValueError, match="modify_deterrent to_slot must be an int"):
        validate_action_payload(
            _modify_deterrent_action({"card": "card_a", "to_slot": "0"}),
            1,
        )
    with pytest.raises(ValueError, match="modify_deterrent from_slot must be an int"):
        validate_action_payload(_modify_deterrent_action({"from_slot": "1"}), 2)


def _deterrent_state() -> GameState:
    cards = [
        Card("hand_a", CardCategory.WARHEAD, "Hand A", value=10),
        Card("hand_b", CardCategory.WARHEAD, "Hand B", value=20),
        Card("stored", CardCategory.DELIVERY, "Stored", metadata={"capacity": 1}),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(cards)
    state.players["p1"].hand = ["hand_a", "hand_b"]
    state.players["p1"].deterrents = [None, "stored"]
    return state


def test_deterrent_actions_offer_skip_first_and_legal_moves() -> None:
    state = _deterrent_state()

    options = deterrent_actions(state, "p1")

    assert options[0].payload == {}
    payloads = [action.payload for action in options]
    assert {"card": "hand_a", "to_slot": 0} in payloads
    assert {"card": "hand_b", "to_slot": 0} in payloads
    assert {"from_slot": 1} in payloads


def test_apply_deterrent_action_moves_hand_card_to_empty_slot() -> None:
    state = _deterrent_state()
    action = build_action(
        "p1",
        ActionType.MODIFY_DETERRENT,
        "Store hand_a",
        {"card": "hand_a", "to_slot": 0},
    )

    events = apply_deterrent_action(state, action)

    assert events == []
    assert state.players["p1"].hand == ["hand_b"]
    assert state.players["p1"].deterrents == ["hand_a", "stored"]


def test_apply_action_dispatches_modify_deterrent() -> None:
    state = _deterrent_state()
    action = build_action(
        "p1",
        ActionType.MODIFY_DETERRENT,
        "Store hand_a",
        {"card": "hand_a", "to_slot": 0},
    )

    events = apply_action(state, action)

    assert events == []
    assert state.players["p1"].hand == ["hand_b"]
    assert state.players["p1"].deterrents == ["hand_a", "stored"]
