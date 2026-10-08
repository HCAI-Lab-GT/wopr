"""MX missile postal weapon tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.launch import execute_launches
from nuclear_war_env.engine.launch_helpers import can_load_warhead
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state(cards: list[Card]) -> GameState:
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards(cards)
    state.population_bank = [25, 10, 10, 5, 5, 2, 2, 1, 1, 1]
    return state


def test_mx_missile_loads_one_warhead_larger_than_10mt() -> None:
    cards = [
        Card(
            "mx",
            CardCategory.DELIVERY,
            "MX Missile",
            metadata={"postal_effect": "mx_missile", "capacity": 1},
        ),
        Card("small", CardCategory.WARHEAD, "10 Mt", value=10),
        Card("large", CardCategory.WARHEAD, "20 Mt", value=20),
    ]
    state = _state(cards)
    launch = {"delivery": "mx", "warheads": []}

    assert not can_load_warhead(state, "mx", launch, state.card_by_id("small"))
    assert can_load_warhead(state, "mx", launch, state.card_by_id("large"))
    launch["warheads"] = ["large"]
    assert not can_load_warhead(state, "mx", launch, state.card_by_id("large"))


def _mx_and_warhead() -> list[Card]:
    return [
        Card(
            "mx",
            CardCategory.DELIVERY,
            "MX Missile",
            metadata={"postal_effect": "mx_missile", "capacity": 1},
        ),
        Card("large", CardCategory.WARHEAD, "20 Mt", value=20),
    ]


def test_mx_missile_resolves_one_attack_per_10mt_segment() -> None:
    state = _state(_mx_and_warhead())
    state.rng = SeededRNG(seed=41)  # Radioactive Fallout die rolls 4, then 3
    state.players["p1"].pending_orders["launches"] = {
        "mx": {"delivery": "mx", "warheads": ["large"], "target": "p2"}
    }

    events = execute_launches(state)

    # Each 10Mt segment rolls the Radioactive Fallout die and destroys
    # 2 million + the die face: (2 + 4) + (2 + 3) = 11 -> 30 - 11 = 19.
    assert sum(state.players["p2"].population) == 19
    dice = [event for event in events if event.event_type == "fallout_die_result"]
    assert [event.payload["raw_result"] for event in dice] == [4, 3]
    assert dice[0].payload["source_table_id"] == "postal_radioactive_fallout_die"
    assert "spinner_result" not in [event.event_type for event in events]
    detonations = [event for event in events if event.event_type == "warhead_detonated"]
    assert [event.payload["yield"] for event in detonations] == [6, 5]


def test_mx_missile_cloud_segment_is_cancelled() -> None:
    state = _state(_mx_and_warhead())
    state.rng = SeededRNG(seed=14)  # Radioactive Fallout die rolls cloud (1), then 5
    state.players["p1"].pending_orders["launches"] = {
        "mx": {"delivery": "mx", "warheads": ["large"], "target": "p2"}
    }

    events = execute_launches(state)

    dice = [event for event in events if event.event_type == "fallout_die_result"]
    assert [event.payload["raw_result"] for event in dice] == [1, 5]
    assert dice[0].payload["cloud"] is True
    # The cloud ("explodes on launchpad") cancels only that one 10Mt segment:
    # no detonation, no attacker backfire. The surviving segment deals 2 + 5 = 7.
    detonations = [event for event in events if event.event_type == "warhead_detonated"]
    assert [event.payload["yield"] for event in detonations] == [7]
    assert "launch_backfire" not in [event.event_type for event in events]
    assert sum(state.players["p2"].population) == 23
