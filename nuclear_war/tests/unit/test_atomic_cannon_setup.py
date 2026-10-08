"""Postal atomic cannon setup phase tests."""

from __future__ import annotations

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_atomic_cannon_setup_rejects_eliminated_target() -> None:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.rng = SeededRNG(seed=0)
    state.players["p2"].alive = False
    state.players["p2"].population = []
    state.players["p1"].pending_orders["atomic_cannon_setup"] = {
        "cannon": "cannon1",
        "target": "p2",
    }

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    cannons = state.players["p1"].pending_orders["atomic_cannons"]

    assert "atomic_cannon_failed" in event_types
    assert "atomic_cannon_setup" not in event_types
    failed = next(
        event for event in events if event.event_type == "atomic_cannon_failed"
    )
    assert failed.payload == {"reason": "target_not_alive"}
    assert "cannon1" not in cannons
