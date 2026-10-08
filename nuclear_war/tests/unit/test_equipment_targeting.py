"""Postal equipment targeting tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_state(seed: int = 0) -> GameState:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(ruleset=Ruleset.POSTAL, players=players, draw_pile=[])
    state.register_cards(cards)
    state.rng = SeededRNG(seed=seed)
    return state


def _launch_at_equipment(kind: str, equipment_id: str) -> dict[str, object]:
    return {
        "delivery": "delivery",
        "capacity": 1,
        "warheads": ["warhead"],
        "target": "p2",
        "equipment_target": {"owner": "p2", "kind": kind, "id": equipment_id},
    }


def test_launch_can_destroy_atomic_cannon_target() -> None:
    state = _build_state()
    state.players["p2"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p1", "status": "ready"}
    }
    state.players["p1"].pending_orders["launches"] = {
        "delivery": _launch_at_equipment("atomic_cannon", "cannon1")
    }
    events = execute_postal_turn(state)
    cannon = state.players["p2"].pending_orders["atomic_cannons"]["cannon1"]
    assert sum(state.players["p2"].population) == 30
    assert cannon["status"] == "destroyed"
    assert any(event.event_type == "equipment_destroyed" for event in events)


def test_launch_dud_leaves_equipment_target_intact() -> None:
    state = _build_state(seed=2)
    state.players["p2"].pending_orders["atomic_cannons"] = {
        "cannon1": {"target": "p1", "status": "ready"}
    }
    state.players["p1"].pending_orders["launches"] = {
        "delivery": _launch_at_equipment("atomic_cannon", "cannon1")
    }
    events = execute_postal_turn(state)
    cannon = state.players["p2"].pending_orders["atomic_cannons"]["cannon1"]
    assert sum(state.players["p2"].population) == 30
    assert cannon["status"] == "ready"
    assert any(event.event_type == "equipment_target_missed" for event in events)


def test_launch_can_destroy_exposed_submarine_target() -> None:
    state = _build_state()
    state.players["p2"].pending_orders["submarine_states"] = {
        "sub1": {"target": "p1", "warhead_yield": 10, "status": "exposed"}
    }
    state.players["p1"].pending_orders["launches"] = {
        "delivery": _launch_at_equipment("submarine", "sub1")
    }
    events = execute_postal_turn(state)
    submarine = state.players["p2"].pending_orders["submarine_states"]["sub1"]
    assert sum(state.players["p2"].population) == 30
    assert submarine["status"] == "destroyed"
    assert any(event.event_type == "equipment_destroyed" for event in events)
