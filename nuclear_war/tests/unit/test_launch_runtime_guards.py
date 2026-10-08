"""Launch runtime guard tests."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_launches
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, PlayerState, Ruleset, create_players


def test_execute_launches_rejects_float_warhead_value() -> None:
    malformed_value: Any = 10.0
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=malformed_value),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=10),
        draw_pile=list(cards),
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.players["p2"] = PlayerState(player_id="p2", population=[25, 5])
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }

    events = execute_launches(state)
    event_types = [event.event_type for event in events]

    assert "launch_declared" not in event_types
    assert "warhead_detonated" not in event_types
    assert sum(state.players["p2"].population) == 30


def test_execute_launches_rejects_boolean_intercept_threshold() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=1),
        Card(
            "defense",
            CardCategory.ANTIMISSILE,
            "Defense",
            metadata={"intercept": True},
        ),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=10),
        draw_pile=list(cards),
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.players["p2"] = PlayerState(player_id="p2", population=[25, 5])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["p2"].pending_orders["defense"] = ["defense"]
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }

    events = execute_launches(state)

    assert not any(event.event_type == "intercept_success" for event in events)
