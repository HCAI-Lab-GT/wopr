"""War-state timing tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_launches, execute_postal_turn
from nuclear_war_env.engine.launch import declare_target
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_target_declaration_ends_peace_even_when_attack_is_intercepted() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
        Card(
            "defense",
            CardCategory.ANTIMISSILE,
            "Defense",
            metadata={"intercept": "any"},
        ),
        Card("propaganda", CardCategory.PROPAGANDA, "Propaganda", value=5),
    ]
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(cards)
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    state.players["p1"].pending_orders["propaganda"] = ["propaganda"]
    state.players["p1"].pending_orders["propaganda_orders"] = {"propaganda": "p2"}
    state.players["p2"].pending_orders["defense"] = ["defense"]
    declare_target(state, "p1", "delivery", "p2")

    execute_postal_turn(state)

    assert not state.peace
    assert all(player.at_war for player in state.players.values())
    assert sum(state.players["p1"].population) == 30
    assert sum(state.players["p2"].population) == 30


def test_table_peace_restores_after_elimination_without_final_strike() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=30),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.players["p2"].population = [20]
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
        }
    }
    declare_target(state, "p1", "delivery", "p2")

    execute_launches(state)

    assert state.peace
    assert not any(player.at_war for player in state.players.values())
