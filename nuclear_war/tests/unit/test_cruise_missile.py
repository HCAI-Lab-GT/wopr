"""Postal cruise missile launch and drop tests."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state(seed: int = 0) -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.rng = SeededRNG(seed=seed)
    state.population_bank = [10, 5]
    return state


def test_cruise_launch_success_creates_lurking_missile() -> None:
    state = _build_state()  # seed 0 -> Radioactive Fallout die 4 (success)
    state.players["p1"].pending_orders["cruise_launch"] = [
        {"missile": "cruise1", "target": "p2", "yield": 10}
    ]
    events = execute_postal_turn(state)
    missile = state.players["p1"].pending_orders["cruise_missiles"]["cruise1"]
    assert missile["target"] == "p2"
    assert missile["yield"] == 10
    assert missile["visited"] == ["p2"]
    assert any(event.event_type == "cruise_launched" for event in events)
    # Cruise launch rolls the Radioactive Fallout die, not the two-d10 spinner.
    die = next(e for e in events if e.event_type == "fallout_die_result")
    assert die.card_id == "cruise1"
    assert die.payload["cloud"] is False
    assert "spinner_result" not in [e.event_type for e in events]


def test_cruise_launch_failure_discards_missile() -> None:
    state = _build_state(seed=31)  # seed 31 -> Radioactive Fallout die 1 (cloud)
    state.players["p1"].pending_orders["cruise_launch"] = [
        {"missile": "cruise1", "target": "p2", "yield": 10}
    ]
    events = execute_postal_turn(state)
    missiles = state.players["p1"].pending_orders["cruise_missiles"]
    assert "cruise1" not in missiles
    assert any(event.event_type == "cruise_launch_failed" for event in events)
    die = next(e for e in events if e.event_type == "fallout_die_result")
    assert die.payload["raw_result"] == 1
    assert die.payload["cloud"] is True


def test_cruise_launch_skips_eliminated_target_before_spinner() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["cruise_launch"] = [
        {"missile": "cruise1", "target": "p2", "yield": 10}
    ]
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    missiles = state.players["p1"].pending_orders["cruise_missiles"]

    assert "spinner_result" not in event_types
    assert "cruise_launched" not in event_types
    assert "cruise1" not in missiles
    assert any(event.event_type == "cruise_launch_failed" for event in events)


def test_cruise_drop_detonates_and_removes_missile() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "yield": 10, "visited": ["p2"]}
    }
    state.players["p1"].pending_orders["cruise_drop"] = ["cruise1"]
    events = execute_postal_turn(state)
    missiles = state.players["p1"].pending_orders["cruise_missiles"]
    assert "cruise1" not in missiles
    assert sum(state.players["p2"].population) == 20
    assert Counter(state.population_bank) == Counter([25])
    assert any(event.event_type == "cruise_dropped" for event in events)


def test_cruise_drop_skips_eliminated_target_before_spinner() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "yield": 10, "visited": ["p2"]}
    }
    state.players["p1"].pending_orders["cruise_drop"] = ["cruise1"]
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    missiles = state.players["p1"].pending_orders["cruise_missiles"]

    assert "spinner_result" not in event_types
    assert "cruise_dropped" not in event_types
    assert "cruise1" not in missiles
    assert any(event.event_type == "cruise_drop_failed" for event in events)


def test_cruise_move_to_eliminated_target_returns_to_sender() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2", "p3"], starting_population=30),
        draw_pile=[],
    )
    state.players["p1"].pending_orders["cruise_missiles"] = {
        "cruise1": {"target": "p2", "yield": 10, "visited": ["p2"]}
    }
    state.players["p1"].pending_orders["cruise_move"] = [
        {"missile": "cruise1", "target": "p3"}
    ]
    state.players["p3"].alive = False
    state.players["p3"].population = []

    events = execute_postal_turn(state)
    missile = state.players["p1"].pending_orders["cruise_missiles"]["cruise1"]

    assert missile["target"] == "p1"
    assert missile["drop_next_turn"] is True
    assert any(
        event.event_type == "cruise_move"
        and event.payload == {"target": "p1", "status": "return_to_sender"}
        for event in events
    )
