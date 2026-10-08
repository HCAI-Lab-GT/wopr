"""Final strike legal action tests."""

from __future__ import annotations

from nuclear_war_env.actions import apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_eliminated_postal_player_can_target_pending_final_strike() -> None:
    delivery = Card("delivery", CardCategory.DELIVERY, "Delivery", value=1)
    warhead = Card("warhead", CardCategory.WARHEAD, "Warhead", value=15)
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards([delivery, warhead])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["p1"].alive = False
    state.players["p1"].population = []
    state.players["p1"].pending_orders["final_strike"] = [
        {"delivery": "delivery", "warheads": ["warhead"], "target": None}
    ]

    actions = legal_actions(state, "p1", mode="postal")
    matching = [
        action
        for action in actions
        if action.action_type.value == "final_strike_target"
    ]
    assert matching

    events = apply_action(state, matching[0])
    postal_events = execute_postal_turn(state)

    assert matching[0].payload == {"target": "p2"}
    assert [event.event_type for event in events] == ["final_strike_targeted"]
    assert sum(state.players["p2"].population) == 15
    assert any(event.event_type == "final_strike_executed" for event in postal_events)


def test_final_strike_target_action_requires_live_target_at_apply_time() -> None:
    delivery = Card("delivery", CardCategory.DELIVERY, "Delivery", value=1)
    warhead = Card("warhead", CardCategory.WARHEAD, "Warhead", value=15)
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards([delivery, warhead])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.players["p1"].alive = False
    state.players["p1"].population = []
    state.players["p1"].pending_orders["final_strike"] = [
        {"delivery": "delivery", "warheads": ["warhead"], "target": None}
    ]
    action = next(
        item
        for item in legal_actions(state, "p1", mode="postal")
        if item.action_type.value == "final_strike_target"
    )
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = apply_action(state, action)
    postal_events = execute_postal_turn(state)
    postal_event_types = [event.event_type for event in postal_events]

    assert events == []
    assert "warhead_detonated" not in postal_event_types
    assert state.players["p1"].pending_orders.get("final_strike") is None
    assert sum(state.players["p2"].population) == 0
