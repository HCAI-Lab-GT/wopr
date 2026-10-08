"""Postal space equipment shared legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_postal_legal_actions_can_queue_space_platform_drop() -> None:
    state = _space_state()
    state.players["p1"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10, 20]}
    }
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_SPACE_PLATFORM_DROP
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    platform = state.players["p1"].pending_orders["space_platforms"]["platform1"]
    assert action.payload == {"platform": "platform1", "target": "p2"}
    assert [event.event_type for event in events] == [
        "postal_space_platform_drop_ordered"
    ]
    assert platform["warheads"] == [20]
    assert any(event.event_type == "space_platform_dropped" for event in postal_events)


def test_postal_legal_actions_can_queue_killer_satellite_attack() -> None:
    state = _space_state()
    state.players["p1"].pending_orders["killer_satellites"] = {
        "sat1": {"status": "orbit"}
    }
    state.players["p2"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10]}
    }
    actions = legal_actions(state, "p1", mode="postal")
    action = next(
        item
        for item in actions
        if item.action_type is ActionType.POSTAL_KILLER_SATELLITE_ATTACK
    )
    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    assert action.payload == {
        "satellite": "sat1",
        "target_player": "p2",
        "platform": "platform1",
    }
    assert [event.event_type for event in events] == [
        "postal_killer_satellite_attack_ordered"
    ]
    assert "sat1" not in state.players["p1"].pending_orders["killer_satellites"]
    assert "platform1" not in state.players["p2"].pending_orders["space_platforms"]
    assert any(
        event.event_type == "killer_satellite_destroyed_platform"
        for event in postal_events
    )


def _space_state() -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.population_bank = [10, 5]
    return state
