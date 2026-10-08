"""Postal killer satellite tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state(seed: int = 0) -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.rng = SeededRNG(seed=seed)
    return state


def test_killer_satellite_launch_reaches_orbit() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["killer_satellite_launch"] = [
        {"satellite": "sat1"}
    ]
    events = execute_postal_turn(state)
    satellite = state.players["p1"].pending_orders["killer_satellites"]["sat1"]
    assert satellite["status"] == "orbit"
    assert any(event.event_type == "killer_satellite_launched" for event in events)


def test_killer_satellite_destroys_space_platform() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["killer_satellites"] = {
        "sat1": {"status": "orbit"}
    }
    state.players["p2"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10]}
    }
    state.players["p1"].pending_orders["killer_satellite_attack"] = [
        {"satellite": "sat1", "target_player": "p2", "platform": "platform1"}
    ]
    events = execute_postal_turn(state)  # seed 0 -> Radioactive Fallout die 4
    assert "sat1" not in state.players["p1"].pending_orders["killer_satellites"]
    assert "platform1" not in state.players["p2"].pending_orders["space_platforms"]
    assert any(
        event.event_type == "killer_satellite_destroyed_platform" for event in events
    )
    # The attack rolls the Radioactive Fallout die, not the two-d10 spinner.
    die = next(e for e in events if e.event_type == "fallout_die_result")
    assert die.card_id == "sat1"
    assert die.payload["cloud"] is False
    assert "spinner_result" not in [e.event_type for e in events]


def test_killer_satellite_failure_discards_satellite_only() -> None:
    state = _build_state(seed=31)
    state.players["p1"].pending_orders["killer_satellites"] = {
        "sat1": {"status": "orbit"}
    }
    state.players["p2"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10]}
    }
    state.players["p1"].pending_orders["killer_satellite_attack"] = [
        {"satellite": "sat1", "target_player": "p2", "platform": "platform1"}
    ]
    events = execute_postal_turn(state)  # seed 31 -> Radioactive Fallout die 1 (cloud)
    assert "sat1" not in state.players["p1"].pending_orders["killer_satellites"]
    assert "platform1" in state.players["p2"].pending_orders["space_platforms"]
    assert any(event.event_type == "killer_satellite_failed" for event in events)
    die = next(e for e in events if e.event_type == "fallout_die_result")
    assert die.payload["raw_result"] == 1
    assert die.payload["cloud"] is True


def test_killer_satellite_attack_skips_eliminated_target_before_spinner() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["killer_satellites"] = {
        "sat1": {"status": "orbit"}
    }
    state.players["p2"].pending_orders["space_platforms"] = {
        "platform1": {"warheads": [10]}
    }
    state.players["p1"].pending_orders["killer_satellite_attack"] = [
        {"satellite": "sat1", "target_player": "p2", "platform": "platform1"}
    ]
    state.players["p2"].alive = False
    state.players["p2"].population.clear()
    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    assert "sat1" in state.players["p1"].pending_orders["killer_satellites"]
    assert "platform1" in state.players["p2"].pending_orders["space_platforms"]
    assert "spinner_result" not in event_types
    assert "killer_satellite_failed" not in event_types
    assert "killer_satellite_destroyed_platform" not in event_types
