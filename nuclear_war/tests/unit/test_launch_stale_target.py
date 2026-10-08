"""Launch stale target runtime tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import declare_target, execute_launches
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, PlayerState, Ruleset, create_players


def test_execute_launches_clears_eliminated_target_before_spinner() -> None:
    state = _launch_state()
    declare_target(state, "p1", "delivery", "p2")
    state.players["p2"].alive = False
    state.players["p2"].population.clear()

    events = execute_launches(state)
    event_types = [event.event_type for event in events]
    launch = state.players["p1"].pending_orders["launches"]["delivery"]

    assert launch["target"] is None
    assert launch["warheads"] == ["warhead"]
    assert "spinner_result" not in event_types
    assert "launch_declared" not in event_types
    assert "warhead_detonated" not in event_types
    assert not state.peace


def _launch_state() -> GameState:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=10),
        draw_pile=[],
        rng=SeededRNG(seed=1),
    )
    state.register_cards(cards)
    state.players["p2"] = PlayerState(player_id="p2", population=[25, 5])
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": None,
        }
    }
    return state
