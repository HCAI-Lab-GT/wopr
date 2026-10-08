"""Smart Bomb launch modifier tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_launches
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, PlayerState, Ruleset, create_players


def test_smart_bomb_doubles_ten_or_twenty_megaton_warhead() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]
    players = create_players(["p1"], starting_population=30)
    state = GameState(ruleset=Ruleset.TABLE, players=players, draw_pile=[])
    state.register_cards(cards)
    state.players["p2"] = PlayerState(player_id="p2", population=[25, 5])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": "p2",
            "smart_bomb": True,
        }
    }
    state.rng = SeededRNG(seed=0)
    events = execute_launches(state)
    assert sum(state.players["p2"].population) == 10
    assert any(
        event.event_type == "launch_declared" and event.payload["yield"] == 20
        for event in events
    )
