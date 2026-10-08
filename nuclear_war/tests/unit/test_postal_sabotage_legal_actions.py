"""Postal sabotage shared legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_legal_actions_can_queue_launch_sabotage() -> None:
    state = _state()
    state.players["p2"].hand = ["saboteur"]
    state.players["p1"].pending_orders["launches"] = {"delivery": {}}
    action = _action(state, "delivery")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {
        "card": "saboteur",
        "target": "p1",
        "delivery": "delivery",
    }
    assert state.players["p2"].hand == []
    assert "delivery" not in state.players["p1"].pending_orders.get("launches", {})
    assert [event.event_type for event in events] == ["postal_sabotage_ordered"]
    assert any(event.event_type == "sabotage_success" for event in postal_events)


def test_postal_legal_actions_can_queue_atomic_cannon_sabotage() -> None:
    state = _state()
    state.players["p2"].hand = ["saboteur"]
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "fire", "warhead_yield": 10}
    ]
    action = _action(state, "atomic_cannon")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {
        "card": "saboteur",
        "target": "p1",
        "atomic_cannon": "cannon1",
    }
    assert state.players["p2"].hand == []
    assert "atomic_cannon" not in state.players["p1"].pending_orders
    assert [event.event_type for event in events] == ["postal_sabotage_ordered"]
    assert any(event.event_type == "sabotage_success" for event in postal_events)


def test_postal_legal_actions_can_queue_killer_satellite_sabotage() -> None:
    state = _state()
    state.players["p2"].hand = ["saboteur"]
    state.players["p1"].pending_orders["killer_satellite_launch"] = [
        {"satellite": "sat1"}
    ]
    action = _action(state, "satellite")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {"card": "saboteur", "target": "p1", "satellite": "sat1"}
    assert state.players["p2"].hand == []
    assert "killer_satellite_launch" not in state.players["p1"].pending_orders
    assert [event.event_type for event in events] == ["postal_sabotage_ordered"]
    assert any(event.event_type == "sabotage_success" for event in postal_events)


def test_postal_legal_actions_can_queue_space_shuttle_sabotage() -> None:
    state = _state()
    state.players["p2"].hand = ["saboteur"]
    state.players["p1"].pending_orders["space_shuttle_attack"] = [
        {"shuttle": "shuttle1", "target": "p2", "warheads": [10]}
    ]
    action = _action(state, "shuttle")
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {"card": "saboteur", "target": "p1", "shuttle": "shuttle1"}
    assert state.players["p2"].hand == []
    assert "space_shuttle_attack" not in state.players["p1"].pending_orders
    assert [event.event_type for event in events] == ["postal_sabotage_ordered"]
    assert any(event.event_type == "sabotage_success" for event in postal_events)


def test_sabotage_legal_actions_keep_distinct_targets_with_same_id() -> None:
    state = _state()
    state.players["p2"].hand = ["saboteur"]
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "asset1", "action": "fire", "warhead_yield": 10}
    ]
    state.players["p1"].pending_orders["killer_satellite_launch"] = [
        {"satellite": "asset1"}
    ]

    actions = legal_actions(state, "p2", mode="postal")
    sabotage_payloads = [
        action.payload
        for action in actions
        if action.action_type.value == "postal_sabotage"
    ]

    assert {"card": "saboteur", "target": "p1", "atomic_cannon": "asset1"} in (
        sabotage_payloads
    )
    assert {"card": "saboteur", "target": "p1", "satellite": "asset1"} in (
        sabotage_payloads
    )


def _action(state: GameState, sabotaged_key: str):
    matching = [
        action
        for action in legal_actions(state, "p2", mode="postal")
        if action.action_type.value == "postal_sabotage"
        and sabotaged_key in action.payload
    ]
    assert matching
    return matching[0]


def _state() -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(
        [
            Card(
                "saboteur",
                CardCategory.SPECIAL,
                "Saboteur",
                metadata={"postal_effect": "sabotage"},
            )
        ]
    )
    return state
