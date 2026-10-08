"""Postal atomic cannon phase tests."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state(player_ids: list[str] | None = None) -> GameState:
    players = create_players(player_ids or ["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.rng = SeededRNG(seed=0)
    state.population_bank = [10, 5]
    return state


def test_atomic_cannon_fires_ten_megaton_warhead() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "fire", "warhead_yield": 10}
    ]
    events = execute_postal_turn(state)
    cannon = state.players["p1"].pending_orders["atomic_cannons"]["cannon1"]
    assert sum(state.players["p2"].population) == 20
    assert Counter(state.population_bank) == Counter([25])
    assert cannon["status"] == "ready"
    assert any(event.event_type == "atomic_cannon_fired" for event in events)


def test_atomic_cannon_setup_creates_ready_cannon() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["atomic_cannon_setup"] = {
        "cannon": "cannon1",
        "target": "p2",
    }
    events = execute_postal_turn(state)
    cannon = state.players["p1"].pending_orders["atomic_cannons"]["cannon1"]
    assert cannon["status"] == "ready"
    assert cannon["target"] == "p2"
    assert any(event.event_type == "atomic_cannon_setup" for event in events)


def test_atomic_cannon_setup_discards_second_ready_cannon() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon_setup"] = {
        "cannon": "cannon2",
        "target": "p2",
    }
    events = execute_postal_turn(state)
    cannons = state.players["p1"].pending_orders["atomic_cannons"]
    assert "cannon2" not in cannons
    assert any(event.event_type == "atomic_cannon_discarded" for event in events)


def test_atomic_cannon_repositions_without_firing() -> None:
    state = _build_state(["p1", "p2", "p3"])
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "reposition", "target": "p3"}
    ]
    events = execute_postal_turn(state)
    cannon = state.players["p1"].pending_orders["atomic_cannons"]["cannon1"]
    assert cannon["target"] == "p3"
    assert sum(state.players["p2"].population) == 30
    assert sum(state.players["p3"].population) == 30
    assert any(event.event_type == "atomic_cannon_repositioned" for event in events)


def test_atomic_cannon_rejects_reposition_to_eliminated_target() -> None:
    state = _build_state(["p1", "p2", "p3"])
    state.players["p3"].alive = False
    state.players["p3"].population = []
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "reposition", "target": "p3"}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]
    cannon = state.players["p1"].pending_orders["atomic_cannons"]["cannon1"]

    assert "atomic_cannon_failed" in event_types
    assert "atomic_cannon_repositioned" not in event_types
    failed = next(
        event for event in events if event.event_type == "atomic_cannon_failed"
    )
    assert failed.payload == {"reason": "target_not_alive"}
    assert cannon["target"] == "p2"


def test_atomic_cannon_rejects_non_ten_megaton_warhead() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "fire", "warhead_yield": 20}
    ]
    events = execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 30
    assert any(event.event_type == "atomic_cannon_failed" for event in events)


def test_atomic_cannon_rejects_eliminated_target_before_spinner() -> None:
    state = _build_state()
    state.players["p2"].alive = False
    state.players["p2"].population = []
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "cannon1", "action": "fire", "warhead_yield": 10}
    ]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "atomic_cannon_failed" in event_types
    assert "spinner_result" not in event_types
    assert "atomic_cannon_fired" not in event_types
    failed = next(
        event for event in events if event.event_type == "atomic_cannon_failed"
    )
    assert failed.payload == {"reason": "target_not_alive"}
    assert sum(state.players["p2"].population) == 0


def test_final_strike_can_fire_played_atomic_cannon() -> None:
    state = _build_state()
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p2", "status": "ready"}
    }
    state.players["p1"].pending_orders["final_strike"] = [
        {"atomic_cannon": "cannon1", "warhead_yield": 10}
    ]
    events = execute_postal_turn(state)
    assert sum(state.players["p2"].population) == 20
    assert any(event.event_type == "final_strike_executed" for event in events)
    assert any(event.event_type == "atomic_cannon_fired" for event in events)


def _ready_cannon_state(seed: int = 0):
    from nuclear_war_env.rng import SeededRNG
    from nuclear_war_env.state import GameState, Ruleset, create_players

    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.rng = SeededRNG(seed=seed)
    state.population_bank = [10, 5]
    state.players["p1"].pending_orders["atomic_cannons"] = {
        "c1": {"status": "ready", "target": "p2"}
    }
    state.players["p1"].pending_orders["atomic_cannon"] = [
        {"cannon": "c1", "action": "fire", "warhead_yield": 10}
    ]
    return state


def test_atomic_cannon_skips_dead_owner_when_requested() -> None:
    from nuclear_war_env.engine.postal.atomic_cannon import apply_atomic_cannon_orders

    state = _ready_cannon_state()
    state.players["p1"].alive = False  # eliminated earlier this turn
    events = apply_atomic_cannon_orders(state, skip_dead_owners=True)
    assert [e.event_type for e in events] == []  # corpse does not fire


def test_atomic_cannon_final_strike_still_fires_for_dead_owner() -> None:
    from nuclear_war_env.engine.postal.atomic_cannon import apply_atomic_cannon_orders

    state = _ready_cannon_state()
    state.players["p1"].alive = False  # a final strike fires FOR the dead player
    events = apply_atomic_cannon_orders(state)  # default: skip_dead_owners=False
    types = [e.event_type for e in events]
    assert "spinner_result" in types  # retaliation resolves
