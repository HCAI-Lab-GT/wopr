"""Integration tests for sequential table play."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.draw import advance_queue, set_face_down_cards
from nuclear_war_env.engine.launch import declare_target, execute_launches
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import GameState, Ruleset, create_players


def _build_table_state(cards: list[Card]) -> GameState:
    players = create_players(["p1", "p2"], starting_population=30)
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=players,
        draw_pile=[],
        rng=SeededRNG(seed=0),
    )
    state.register_cards(cards)
    return state


def test_table_final_retaliation_sequence() -> None:
    cards = [
        Card(
            "delivery_a",
            CardCategory.DELIVERY,
            "Delivery A",
            metadata={"capacity": 1},
        ),
        Card("warhead_a", CardCategory.WARHEAD, "Warhead A", value=30),
        Card(
            "delivery_b",
            CardCategory.DELIVERY,
            "Delivery B",
            metadata={"capacity": 1},
        ),
        Card("warhead_b", CardCategory.WARHEAD, "Warhead B", value=10),
    ]
    state = _build_table_state(cards)
    attacker = state.players["p1"]
    defender = state.players["p2"]
    attacker.hand = ["delivery_a", "warhead_a"]
    defender.hand = ["delivery_b", "warhead_b"]
    defender.population = [20]

    set_face_down_cards(attacker, ["delivery_a", "warhead_a"])
    advance_queue(state, attacker)
    advance_queue(state, attacker)
    declare_target(state, "p1", "delivery_a", "p2")

    events = execute_launches(state)

    assert sum(defender.population) == 0
    assert not defender.alive
    assert any(event.event_type == "final_strike_executed" for event in events)
    speculative_damage = any(
        event.payload.get("target") == "p1"
        for event in events
        if event.event_type == "warhead_detonated"
    )
    spinner_logged = any(event.event_type == "spinner_result" for event in events)
    assert speculative_damage or spinner_logged
