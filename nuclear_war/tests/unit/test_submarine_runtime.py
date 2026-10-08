"""Postal submarine runtime guard tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_submarine_fire_skips_eliminated_target_before_spinner() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p2", "warhead_yield": 10, "status": "at_sea"}
    }
    state.players["p1"].pending_orders["submarines"] = [
        {"submarine": "sub1", "action": "fire"}
    ]
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]

    assert "spinner_result" not in event_types
    assert "submarine_strike" not in event_types
    assert submarine["status"] == "at_sea"
    assert "returning_to_port" not in submarine


def test_submarine_fire_rejects_float_stored_warhead_before_spinner() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p2", "warhead_yield": 10.0, "status": "at_sea"}
    }
    state.players["p1"].pending_orders["submarines"] = [
        {"submarine": "sub1", "action": "fire"}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]

    assert "spinner_result" not in event_types
    assert "submarine_strike" not in event_types
    assert sum(state.players["p2"].population) == 30
    assert submarine["status"] == "at_sea"
    assert "returning_to_port" not in submarine


def test_submarine_legacy_strike_rejects_float_yield() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.players["p1"].pending_orders["submarines"] = [{"target": "p2", "yield": 10.0}]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "submarine_strike" not in event_types
    assert sum(state.players["p2"].population) == 30
