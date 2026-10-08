"""Postal stochastic event audit tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state(seed: int = 0) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=seed)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def _assert_spinner_sources(events: list[EngineEvent]) -> None:
    spinner_events = [event for event in events if event.event_type == "spinner_result"]
    assert spinner_events
    for event in spinner_events:
        assert event.payload["randomizer"] == "base_two_d10_fallout_chart"
        assert event.payload["source_table_id"] == "base_two_d10_fallout_chart"


def _assert_fallout_die_sources(events: list[EngineEvent]) -> None:
    die_events = [event for event in events if event.event_type == "fallout_die_result"]
    assert die_events
    assert not any(event.event_type == "spinner_result" for event in events)
    for event in die_events:
        assert event.payload["randomizer"] == "postal_radioactive_fallout_die"
        assert event.payload["source_table_id"] == "postal_radioactive_fallout_die"


def test_atomic_cannon_spinner_logs_source_metadata() -> None:
    state = _state()
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "fire", "warhead_yield": 10}
    ]
    _assert_spinner_sources(execute_postal_turn(state))


def test_cruise_spinner_logs_source_metadata() -> None:
    state = _state()
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "yield": 10, "visited": ["p2"]}
    }
    state.players["p1"].pending_orders["cruise_drop"] = ["cruise1"]
    _assert_spinner_sources(execute_postal_turn(state))


def test_submarine_spinner_logs_source_metadata() -> None:
    state = _state()
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p2", "warhead_yield": 10, "status": "at_sea"}
    }
    state.players["p1"].pending_orders["submarines"] = [
        {"submarine": "sub1", "action": "fire"}
    ]
    _assert_spinner_sources(execute_postal_turn(state))


def test_space_spinner_logs_source_metadata() -> None:
    state = _state()
    state.players["p1"].pending_orders["space_shuttle_attack"] = [
        {"shuttle": "shuttle1", "target": "p2", "warheads": [10]}
    ]
    _assert_spinner_sources(execute_postal_turn(state))


def test_killer_satellite_fallout_die_logs_source_metadata() -> None:
    # Killer satellite attacks roll the Radioactive Fallout die, not the spinner.
    state = _state()
    state.players["p1"].pending_orders["killer_satellites"] = {
        "sat1": {"status": "orbit"}
    }
    state.players["p2"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10]}
    }
    state.players["p1"].pending_orders["killer_satellite_attack"] = [
        {"satellite": "sat1", "target_player": "p2", "platform": "platform1"}
    ]
    _assert_fallout_die_sources(execute_postal_turn(state))
