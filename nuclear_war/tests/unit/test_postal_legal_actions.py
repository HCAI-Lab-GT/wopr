"""Postal-specific shared legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_legal_actions_can_queue_secret_theft_without_secret_id() -> None:
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
    state.players["p2"].secrets = ["secret"]
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item for item in actions if item.action_type is ActionType.POSTAL_STEAL_SECRET
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {"target": "p2"}
    assert [event.event_type for event in events] == ["postal_secret_theft_ordered"]
    assert state.players["p1"].secrets == ["secret"]
    assert state.players["p2"].secrets == []
    assert any(event.event_type == "secret_stolen" for event in postal_events)


def test_postal_legal_actions_can_queue_cruise_drop() -> None:
    state = _cruise_state()
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item for item in actions if item.action_type is ActionType.POSTAL_CRUISE_DROP
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {"missile": "cruise1"}
    assert [event.event_type for event in events] == ["postal_cruise_drop_ordered"]
    assert "cruise1" not in state.players["p1"].pending_orders["cruise_missiles"]
    assert any(event.event_type == "cruise_dropped" for event in postal_events)


def test_postal_legal_actions_can_queue_cruise_move() -> None:
    state = _cruise_state()
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item for item in actions if item.action_type is ActionType.POSTAL_CRUISE_MOVE
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    missile = state.players["p1"].pending_orders["cruise_missiles"]["cruise1"]
    assert action.payload == {"missile": "cruise1", "target": "p3"}
    assert [event.event_type for event in events] == ["postal_cruise_move_ordered"]
    assert missile["target"] == "p3"
    assert any(event.event_type == "cruise_move" for event in postal_events)


def test_postal_legal_actions_can_queue_submarine_fire() -> None:
    state = _submarine_state()
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item for item in actions if item.action_type is ActionType.POSTAL_SUBMARINE_FIRE
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert action.payload == {"submarine": "sub1"}
    assert [event.event_type for event in events] == ["postal_submarine_fire_ordered"]
    assert submarine["status"] == "exposed"
    assert any(event.event_type == "submarine_strike" for event in postal_events)


def test_postal_legal_actions_can_queue_submarine_return() -> None:
    state = _submarine_state()
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_SUBMARINE_RETURN
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert action.payload == {"submarine": "sub1"}
    assert [event.event_type for event in events] == ["postal_submarine_return_ordered"]
    assert submarine["status"] == "in_port"
    assert any(event.event_type == "submarine_returned" for event in postal_events)


def _cruise_state() -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2", "p3"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.population_bank = [10, 5]
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "yield": 10, "visited": ["p2"]}
    }
    return state


def _submarine_state() -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.population_bank = [10, 5]
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p2", "warhead_yield": 10, "status": "at_sea"}
    }
    return state
