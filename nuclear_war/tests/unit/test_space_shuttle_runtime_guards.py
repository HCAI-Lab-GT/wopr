"""Postal space shuttle runtime guard tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_space_shuttle_attack_rejects_float_warhead_before_spinner() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.players["p1"].pending_orders["space_shuttle_attack"] = [
        {"shuttle": "shuttle1", "target": "p2", "warheads": [10.0]}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "spinner_result" not in event_types
    assert "space_shuttle_attacked" not in event_types
    assert "space_shuttle_attack_failed" not in event_types
    assert sum(state.players["p2"].population) == 30


def test_space_shuttle_reload_rejects_float_warhead() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.players["p1"].pending_orders["space_platforms"] = {
        "platform1": {"target": "p2", "warheads": [10]}
    }
    state.players["p1"].pending_orders["space_shuttle_reload"] = [
        {"platform": "platform1", "warheads": [20.0]}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    platform = state.players["p1"].pending_orders["space_platforms"]["platform1"]

    assert "space_shuttle_reloaded" not in event_types
    assert platform["warheads"] == [10]
