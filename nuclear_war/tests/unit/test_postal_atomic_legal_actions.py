"""Postal atomic cannon shared legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_legal_actions_can_queue_atomic_cannon_fire() -> None:
    state = _atomic_state(["p1", "p2"])
    warhead = Card("warhead10", CardCategory.WARHEAD, "Warhead", value=10)
    state.register_cards([warhead])
    state.players["p1"].hand = ["warhead10"]
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_ATOMIC_CANNON_FIRE
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {"cannon": "cannon1", "warhead": "warhead10"}
    assert state.players["p1"].hand == []
    assert [event.event_type for event in events] == [
        "postal_atomic_cannon_fire_ordered"
    ]
    assert any(event.event_type == "atomic_cannon_fired" for event in postal_events)


def test_postal_legal_actions_can_queue_atomic_cannon_reposition() -> None:
    state = _atomic_state(["p1", "p2", "p3"])
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_ATOMIC_CANNON_REPOSITION
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    cannon = state.players["p1"].pending_orders["atomic_cannons"]["cannon1"]
    assert action.payload == {"cannon": "cannon1", "target": "p3"}
    assert [event.event_type for event in events] == [
        "postal_atomic_cannon_reposition_ordered"
    ]
    assert cannon["target"] == "p3"
    assert any(
        event.event_type == "atomic_cannon_repositioned" for event in postal_events
    )


def test_postal_atomic_cannon_fire_requires_live_target() -> None:
    state = _atomic_state(["p1", "p2", "p3"])
    warhead = Card("warhead10", CardCategory.WARHEAD, "Warhead", value=10)
    state.register_cards([warhead])
    state.players["p1"].hand = ["warhead10"]
    state.players["p2"].alive = False
    state.players["p2"].population = []
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }

    actions = legal_actions(state, "p1", mode="postal")

    assert not any(
        item.action_type is ActionType.POSTAL_ATOMIC_CANNON_FIRE for item in actions
    )
    assert any(
        item.action_type is ActionType.POSTAL_ATOMIC_CANNON_REPOSITION
        and item.payload == {"cannon": "cannon1", "target": "p3"}
        for item in actions
    )


def _atomic_state(player_ids: list[str]) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(player_ids, starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.population_bank = [10, 5]
    return state
