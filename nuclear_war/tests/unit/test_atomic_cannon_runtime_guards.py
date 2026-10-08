"""Postal atomic cannon runtime guard tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_atomic_cannon_rejects_float_ten_warhead_yield() -> None:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=0)
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "fire", "warhead_yield": 10.0}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert sum(state.players["p2"].population) == 30
    assert "spinner_result" not in event_types
    assert "atomic_cannon_fired" not in event_types
    assert "atomic_cannon_failed" in event_types
