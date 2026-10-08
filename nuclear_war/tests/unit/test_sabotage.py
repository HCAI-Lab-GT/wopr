"""Postal saboteur tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state() -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.rng = SeededRNG(seed=0)
    return state


def test_sabotage_blocks_atomic_cannon_fire() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "fire", "warhead_yield": 10}
    ]
    state.players["p2"].pending_orders["sabotage"] = [
        {"target": "p1", "atomic_cannon": "cannon1"}
    ]
    events = execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 30
    assert any(event.event_type == "sabotage_success" for event in events)


def test_sabotage_blocks_killer_satellite_launch() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["killer_satellite_launch"] = [
        {"satellite": "sat1"}
    ]
    state.players["p2"].pending_orders["sabotage"] = [
        {"target": "p1", "satellite": "sat1"}
    ]
    events = execute_postal_turn(state)
    satellites = state.players["p1"].pending_orders["killer_satellites"]
    assert "sat1" not in satellites
    assert any(event.event_type == "sabotage_success" for event in events)


def test_sabotage_blocks_space_shuttle_attack() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["space_shuttle_attack"] = [
        {"shuttle": "shuttle1", "target": "p2", "warheads": [10]}
    ]
    state.players["p2"].pending_orders["sabotage"] = [
        {"target": "p1", "shuttle": "shuttle1"}
    ]
    events = execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 30
    assert not any(event.event_type == "space_shuttle_attacked" for event in events)
    assert any(event.event_type == "sabotage_success" for event in events)
