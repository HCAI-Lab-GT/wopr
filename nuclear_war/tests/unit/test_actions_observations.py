"""Tests for legal actions and hidden-information observations."""

from __future__ import annotations

import pytest

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.observation import to_player_observation
from nuclear_war_env.state import GameState, PlayerState, Ruleset, create_players


def _state() -> GameState:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=5),
    ]
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.TABLE, players=players, draw_pile=list(cards))
    state.register_cards(cards)
    return state


def test_legal_actions_include_draw_and_pass_for_live_player() -> None:
    state = _state()
    actions = legal_actions(state, "p1", mode="table")
    action_types = {action.action_type for action in actions}
    assert ActionType.PASS in action_types
    assert ActionType.DRAW in action_types


def test_legal_actions_rejects_unknown_mode() -> None:
    state = _state()

    with pytest.raises(ValueError, match="Unknown mode: space"):
        legal_actions(state, "p1", mode="space")


def test_legal_actions_count_face_down_cards_for_draw_limit() -> None:
    state = _state()
    player = state.players["p1"]
    player.hand = ["delivery"] * 8
    player.face_down_queue.clear()
    player.face_down_queue.extend(["queued_1", "queued_2"])
    actions = legal_actions(state, "p1", mode="table")
    assert ActionType.DRAW not in {action.action_type for action in actions}


def test_legal_actions_count_deterrents_for_draw_limit() -> None:
    state = _state()
    player = state.players["p1"]
    player.hand = ["delivery"] * 8
    player.deterrents = ["deterrent_1", "deterrent_2"]
    actions = legal_actions(state, "p1", mode="table")
    assert ActionType.DRAW not in {action.action_type for action in actions}


def test_postal_legal_actions_can_queue_propaganda_order() -> None:
    propaganda = Card(
        "propaganda",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 5},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([propaganda])
    state.players["p1"].hand = ["propaganda"]
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item for item in actions if item.action_type.value == "postal_propaganda"
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert [event.event_type for event in events] == ["postal_propaganda_ordered"]
    assert any(event.event_type == "propaganda_effect" for event in postal_events)
    assert sum(state.players["p1"].population) == 35
    assert sum(state.players["p2"].population) == 25


def test_postal_legal_actions_can_queue_peace_vote() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.peace = False
    for player_id in ("p1", "p2"):
        actions = legal_actions(state, player_id, mode="postal")
        action = next(
            item for item in actions if item.action_type is ActionType.POSTAL_VOTE_PEACE
        )
        events = apply_action(state, action)
        assert [event.event_type for event in events] == ["postal_peace_voted"]
    postal_events = execute_postal_turn(state)
    assert state.peace
    assert any(event.event_type == "peace_restored" for event in postal_events)


def test_postal_legal_actions_can_queue_secret_target() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"steal_population_millions": 2},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([secret])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["p1"].secrets = ["secret"]
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item for item in actions if item.action_type is ActionType.POSTAL_SECRET_TARGET
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert [event.event_type for event in events] == ["postal_secret_targeted"]
    assert any(
        event.event_type == "secret_population_stolen" for event in postal_events
    )
    assert sum(state.players["p1"].population) == 32
    assert sum(state.players["p2"].population) == 28


def test_observation_hides_opponent_private_cards() -> None:
    state = _state()
    state.players["p1"].hand = ["delivery"]
    state.players["p2"] = PlayerState(
        player_id="p2",
        population=[30],
        hand=["warhead"],
        secrets=["secret"],
    )
    observation = to_player_observation(state, "p1")
    assert observation["self"]["hand"] == ["delivery"]
    assert observation["players"]["p2"]["hand_count"] == 1
    assert "hand" not in observation["players"]["p2"]
    assert observation["players"]["p2"]["secret_count"] == 1
    assert "['secret']" not in str(observation)
