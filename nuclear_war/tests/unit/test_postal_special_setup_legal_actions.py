"""Postal special setup shared legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_legal_actions_can_queue_cruise_launch_from_hand() -> None:
    cruise = Card(
        "cruise",
        CardCategory.SPECIAL,
        "Cruise Missile",
        metadata={"postal_effect": "cruise_missile"},
    )
    warhead = Card("warhead10", CardCategory.WARHEAD, "Warhead", value=10)
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards([cruise, warhead])
    state.players["p1"].hand = ["cruise", "warhead10"]
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item for item in actions if item.action_type is ActionType.POSTAL_CRUISE_LAUNCH
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    missile = state.players["p1"].pending_orders["cruise_missiles"]["cruise"]
    assert action.payload == {
        "card": "cruise",
        "target": "p2",
        "warhead": "warhead10",
    }
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == ["postal_cruise_launch_ordered"]
    assert missile["target"] == "p2"
    assert missile["yield"] == 10
    assert any(event.event_type == "cruise_launched" for event in postal_events)


def test_postal_legal_actions_can_queue_submarine_launch_from_hand() -> None:
    submarine = Card(
        "submarine",
        CardCategory.SPECIAL,
        "Submarine",
        metadata={"postal_effect": "submarine"},
    )
    warhead = Card("warhead10", CardCategory.WARHEAD, "Warhead", value=10)
    state = _special_state([submarine, warhead])
    state.players["p1"].hand = ["submarine", "warhead10"]
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_SUBMARINE_LAUNCH
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    sub_state = state.players["p1"].pending_orders["submarine_states"]["submarine"]
    assert action.payload == {
        "card": "submarine",
        "target": "p2",
        "warhead": "warhead10",
    }
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == ["postal_submarine_launch_ordered"]
    assert sub_state["status"] == "at_sea"
    assert any(event.event_type == "submarine_sent_to_sea" for event in postal_events)


def test_postal_legal_actions_can_queue_submarine_reload_from_hand() -> None:
    warhead = Card("warhead20", CardCategory.WARHEAD, "Warhead", value=20)
    state = _special_state([warhead])
    state.players["p1"].hand = ["warhead20"]
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"status": "in_port"}
    }
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_SUBMARINE_RELOAD
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    sub_state = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert action.payload == {
        "submarine": "sub1",
        "target": "p2",
        "warhead": "warhead20",
    }
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == ["postal_submarine_reload_ordered"]
    assert sub_state["status"] == "at_sea"
    assert any(event.event_type == "submarine_reloaded" for event in postal_events)


def _special_state(cards: list[Card]) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    return state
