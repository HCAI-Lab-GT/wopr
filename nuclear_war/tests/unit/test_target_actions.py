"""Target action runtime guard tests."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_launches
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_target_action_requires_live_target_at_apply_time() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    state.players["p1"].pending_orders["launches"] = {
        "delivery": {
            "delivery": "delivery",
            "capacity": 1,
            "warheads": ["warhead"],
            "target": None,
        }
    }
    action = next(
        item
        for item in legal_actions(state, "p1", mode="table")
        if item.action_type is ActionType.TARGET
    )
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = apply_action(state, action)
    launch = state.players["p1"].pending_orders["launches"]["delivery"]
    launch_events = execute_launches(state)
    launch_event_types = [event.event_type for event in launch_events]

    assert events == []
    assert launch["target"] is None
    assert "warhead_detonated" not in launch_event_types
    assert state.peace
