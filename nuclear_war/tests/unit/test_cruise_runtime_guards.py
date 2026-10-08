"""Postal cruise missile runtime guard tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_cruise_launch_rejects_float_payload_yield() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.players["p1"].pending_orders["cruise_launch"] = [
        {"missile": "cruise1", "target": "p2", "yield": 10.0}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "cruise1" not in state.players["p1"].pending_orders["cruise_missiles"]
    assert "spinner_result" not in event_types
    assert "cruise_launched" not in event_types
    assert "cruise_launch_failed" in event_types


def test_cruise_drop_rejects_float_stored_yield_before_spinner() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "yield": 10.0}
    }
    state.players["p1"].pending_orders["cruise_drop"] = ["cruise1"]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "spinner_result" not in event_types
    assert "cruise_dropped" not in event_types
    assert "cruise_drop_failed" in event_types
    assert sum(state.players["p2"].population) == 30
