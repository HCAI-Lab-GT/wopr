"""Table-mode propaganda resolution and the shared target policy."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.propaganda_resolution import (
    apply_propaganda_steal,
    resolve_propaganda,
)
from nuclear_war_env.engine.target_policy import highest_population_opponent
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state() -> GameState:
    return GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(
            ["player_0", "player_1", "player_2"], starting_population=30
        ),
        draw_pile=[],
    )


def _propaganda(card_id: str, value: int) -> Card:
    return Card(
        card_id,
        CardCategory.PROPAGANDA,
        f"Propaganda {value}M",
        metadata={"value_millions": value},
    )


def test_highest_population_opponent_excludes_self_and_dead() -> None:
    state = _state()
    state.players["player_1"].population = [25, 10]  # 35M
    state.players["player_2"].alive = False
    assert highest_population_opponent(state, "player_0") == "player_1"


def test_highest_population_opponent_none_when_no_living_opponent() -> None:
    state = _state()
    state.players["player_1"].alive = False
    state.players["player_2"].alive = False
    assert highest_population_opponent(state, "player_0") is None


def test_propaganda_steals_from_opponent_during_peace() -> None:
    state = _state()
    state.players["player_1"].population = [25, 10]  # 35M, richest
    card = _propaganda("prop", 10)
    state.register_cards([card])
    state.players["player_0"].pending_orders["propaganda"] = ["prop"]

    events = resolve_propaganda(state, "player_0")

    assert sum(state.players["player_0"].population) == 40  # 30 + 10 stolen
    assert sum(state.players["player_1"].population) == 25  # 35 - 10 stolen
    assert any(event.event_type == "propaganda_effect" for event in events)


def test_propaganda_steal_conserves_population_bank_cards() -> None:
    state = _state()
    state.players["player_0"].population = [1]
    state.players["player_1"].population = [5]
    state.population_bank = [2, 2, 1]
    card = _propaganda("prop", 3)
    state.register_cards([card])

    events = apply_propaganda_steal(state, "player_0", "prop", "player_1")

    assert state.players["player_0"].population == [2, 1, 1]
    assert state.players["player_1"].population == [2]
    assert Counter(state.population_bank) == Counter([5])
    assert any(
        event.event_type == "propaganda_effect" and event.payload.get("migrated") == 3
        for event in events
    )


def test_propaganda_steal_gain_is_capped_at_card_value_on_inexact_change() -> None:
    state = _state()
    state.players["player_0"].population = [25, 5]
    state.players["player_1"].population = [25, 25]
    state.population_bank = []
    card = _propaganda("prop", 3)
    state.register_cards([card])

    events = apply_propaganda_steal(state, "player_0", "prop", "player_1")

    # Round-down makes the target lose 25 (47 is uncomposable from {25, 25}),
    # but the attacker's gain request stays capped at the 3M card value. 33 is
    # uncomposable for the attacker, so the surplus stays in the bank.
    assert sum(state.players["player_1"].population) == 25
    assert sum(state.players["player_0"].population) == 30
    assert Counter(state.population_bank) == Counter([25])
    assert any(
        event.event_type == "propaganda_effect" and event.payload.get("migrated") == 0
        for event in events
    )


def test_propaganda_is_inert_during_war() -> None:
    state = _state()
    state.peace = False
    card = _propaganda("prop", 10)
    state.register_cards([card])
    state.players["player_0"].pending_orders["propaganda"] = ["prop"]

    events = resolve_propaganda(state, "player_0")

    assert events == []
    assert sum(state.players["player_1"].population) == 30  # untouched
    assert "propaganda" not in state.players["player_0"].pending_orders


def test_propaganda_elimination_logs_event_but_grants_no_final_strike() -> None:
    state = _state()
    state.players["player_1"].population = [20]  # richest opponent, but small
    state.players["player_2"].population = [5]
    card = _propaganda("prop", 25)
    state.register_cards([card])
    state.players["player_0"].pending_orders["propaganda"] = ["prop"]

    events = resolve_propaganda(state, "player_0")

    assert not state.players["player_1"].alive
    assert any(
        event.event_type == "player_eliminated"
        and event.player_id == "player_1"
        and event.payload.get("by") == "player_0"
        for event in events
    )
    # A player eliminated by propaganda gets NO final retaliation.
    assert "final_strike" not in state.players["player_1"].pending_orders
