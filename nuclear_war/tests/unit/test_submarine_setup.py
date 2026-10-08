"""Postal submarine setup and reload tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state() -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.rng = SeededRNG(seed=0)
    return state


def test_submarine_launch_with_valid_warhead_goes_to_sea() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["submarine_launch"] = [
        {"submarine": "sub1", "target": "p2", "warhead_yield": 10}
    ]
    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert submarine["status"] == "at_sea"
    assert submarine["target"] == "p2"
    assert submarine["warhead_yield"] == 10
    assert any(event.event_type == "submarine_sent_to_sea" for event in events)


def test_submarine_launch_with_invalid_warhead_stays_in_port() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["submarine_launch"] = [
        {"submarine": "sub1", "target": "p2", "warhead_yield": 50}
    ]
    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert submarine["status"] == "in_port"
    assert "warhead_yield" not in submarine
    assert any(event.event_type == "submarine_in_port" for event in events)


def test_submarine_launch_rejects_float_warhead_yield() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["submarine_launch"] = [
        {"submarine": "sub1", "target": "p2", "warhead_yield": 10.0}
    ]

    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]

    assert submarine["status"] == "in_port"
    assert "warhead_yield" not in submarine
    assert any(event.event_type == "submarine_in_port" for event in events)


def test_submarine_launch_to_eliminated_target_stays_in_port() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["submarine_launch"] = [
        {"submarine": "sub1", "target": "p2", "warhead_yield": 10}
    ]
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]

    assert submarine["status"] == "in_port"
    assert "target" not in submarine
    assert "warhead_yield" not in submarine
    assert any(event.event_type == "submarine_in_port" for event in events)


def test_submarine_reload_sends_in_port_submarine_to_sea() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["submarine_states"] = {
        "sub1": {"status": "in_port"}
    }
    state.players["p1"].pending_orders["submarine_reload"] = [
        {"submarine": "sub1", "target": "p2", "warhead_yield": 20}
    ]
    events = execute_postal_turn(state)
    submarine = state.players["p1"].pending_orders["submarine_states"]["sub1"]
    assert submarine["status"] == "at_sea"
    assert submarine["target"] == "p2"
    assert submarine["warhead_yield"] == 20
    assert any(event.event_type == "submarine_reloaded" for event in events)
