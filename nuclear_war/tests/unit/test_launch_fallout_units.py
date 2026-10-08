"""Launch fallout population unit tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.launch_resolution import resolve_unblocked_launch
from nuclear_war_env.fallout import resolve_spinner
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, PlayerState, Ruleset, create_players


def test_fallout_adjustments_use_population_millions() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=1),
    )
    state.players["p2"] = PlayerState(player_id="p2", population=[25, 5])
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    state.register_cards(cards)

    events = resolve_unblocked_launch(
        state,
        "p1",
        "p2",
        "delivery",
        {"delivery": "delivery", "warheads": ["warhead"], "target": "p2"},
        10,
        resolve_spinner(80),
    )

    assert sum(state.players["p2"].population) == 10
    assert state.players["p2"].alive
    assert events[-1].payload == {"target": "p2", "yield": 20, "loss": 20}


def test_launch_against_eliminated_target_does_not_reschedule_elimination() -> None:
    cards = [
        Card("delivery", CardCategory.DELIVERY, "Delivery", metadata={"capacity": 1}),
        Card("warhead", CardCategory.WARHEAD, "Warhead", value=10),
    ]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        rng=SeededRNG(seed=1),
    )
    state.players["p2"] = PlayerState(player_id="p2", population=[], alive=False)
    state.register_cards(cards)

    events = resolve_unblocked_launch(
        state,
        "p1",
        "p2",
        "delivery",
        {"delivery": "delivery", "warheads": ["warhead"], "target": "p2"},
        10,
        resolve_spinner(48),
    )

    assert not any(event.event_type == "player_eliminated" for event in events)
    assert not state.players["p2"].pending_orders.get("final_strike")
