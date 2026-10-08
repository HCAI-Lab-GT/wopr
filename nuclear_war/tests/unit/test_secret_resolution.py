"""Table-mode secret resolution and deterministic target policy."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine.postal.secret_effects import apply_secret_effect
from nuclear_war_env.engine.secret_resolution import (
    resolve_secrets,
    select_secret_target,
)
from nuclear_war_env.state import GameState, Ruleset, create_players


def _state() -> GameState:
    return GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(
            ["player_0", "player_1", "player_2"], starting_population=30
        ),
        draw_pile=[],
    )


def test_select_secret_target_picks_highest_population_opponent() -> None:
    state = _state()
    state.players["player_1"].population = [25, 10]  # 35M, the richest opponent
    card = Card(
        "s",
        CardCategory.SECRET,
        "Raises Taxes",
        metadata={"steal_population_millions": 5},
    )
    assert select_secret_target(state, "player_0", card) == "player_1"


def test_select_secret_target_routes_gains_to_self() -> None:
    state = _state()
    card = Card(
        "g",
        CardCategory.SECRET,
        "Population Explosion",
        metadata={"gain_from_bank_millions": 5},
    )
    assert select_secret_target(state, "player_0", card) == "player_0"


def test_resolve_secrets_applies_steal_and_clears_the_queue() -> None:
    state = _state()
    state.players["player_1"].population = [25, 10]  # 35M, the richest opponent
    state.population_bank = [5]
    secret = Card(
        "steal",
        CardCategory.SECRET,
        "First on Moon",
        metadata={"steal_population_millions": 5},
    )
    state.register_cards([secret])
    state.players["player_0"].secrets.append("steal")

    events = resolve_secrets(state, "player_0")

    assert sum(state.players["player_0"].population) == 35  # 30 + 5 stolen
    assert sum(state.players["player_1"].population) == 30  # 35 - 5 stolen
    assert state.players["player_0"].secrets == []
    assert any(event.event_type == "secret_population_stolen" for event in events)


def test_secret_steal_gain_is_capped_at_card_value_on_inexact_change() -> None:
    state = _state()
    state.players["player_0"].population = [25, 5]
    state.players["player_1"].population = [25, 25]
    state.population_bank = []
    secret = Card(
        "steal",
        CardCategory.SECRET,
        "First on Moon",
        metadata={"steal_population_millions": 3},
    )
    state.register_cards([secret])

    events = apply_secret_effect(state, "player_0", "steal", "player_1")

    # Round-down makes the target lose 25 (47 is uncomposable from {25, 25}),
    # but the stealer's gain request stays capped at the 3M card value. 33 is
    # uncomposable for the stealer, so the surplus stays in the bank.
    assert sum(state.players["player_1"].population) == 25
    assert sum(state.players["player_0"].population) == 30
    assert Counter(state.population_bank) == Counter([25])
    assert any(
        event.event_type == "secret_population_stolen"
        and event.payload.get("migrated") == 0
        for event in events
    )


def test_resolve_self_gain_secret_does_not_emit_self_targeted_trigger() -> None:
    state = _state()
    state.population_bank = [5]
    gain = Card(
        "gain",
        CardCategory.SECRET,
        "Population Explosion",
        metadata={"gain_from_bank_millions": 5},
    )
    state.register_cards([gain])
    state.players["player_0"].secrets.append("gain")

    events = resolve_secrets(state, "player_0")

    assert sum(state.players["player_0"].population) == 35  # gained 5 from the bank
    # A self-benefiting gain must not "trigger against" the drawer (replay logs
    # reject a secret_triggered whose target is the acting player).
    assert not any(
        event.event_type == "secret_triggered"
        and event.payload.get("target") == "player_0"
        for event in events
    )
    assert any(event.event_type == "secret_population_gained" for event in events)


def test_secret_population_gain_consumes_bank_cards() -> None:
    state = _state()
    state.players["player_0"].population = [2]
    state.population_bank = [5]
    gain = Card(
        "gain",
        CardCategory.SECRET,
        "Population Explosion",
        metadata={"gain_from_bank_millions": 3},
    )
    state.register_cards([gain])

    events = apply_secret_effect(state, "player_0", "gain", "player_0")

    assert state.players["player_0"].population == [5]
    assert Counter(state.population_bank) == Counter([2])
    assert any(event.event_type == "secret_population_gained" for event in events)


def test_secret_population_damage_returns_bank_cards() -> None:
    state = _state()
    state.players["player_1"].population = [5]
    state.population_bank = [2, 1, 1, 1]
    damage = Card(
        "dmg",
        CardCategory.TOP_SECRET,
        "Supergerm",
        metadata={"damage_population_millions": 3},
    )
    state.register_cards([damage])

    events = apply_secret_effect(state, "player_0", "dmg", "player_1")

    assert state.players["player_1"].population == [2]
    assert Counter(state.population_bank) == Counter([5, 1, 1, 1])
    assert any(
        event.event_type == "secret_population_damaged"
        and event.payload.get("loss") == 3
        for event in events
    )


def test_secret_that_kills_a_player_emits_player_eliminated() -> None:
    state = _state()
    state.players["player_1"].population = [20]  # richest opponent, but killable
    state.players["player_2"].population = [5]
    secret = Card(
        "dmg",
        CardCategory.TOP_SECRET,
        "Supergerm",
        metadata={"damage_population_millions": 25},
    )
    state.register_cards([secret])
    state.players["player_0"].secrets.append("dmg")

    events = resolve_secrets(state, "player_0")

    assert not state.players["player_1"].alive
    # An elimination by a secret must be logged like one by a warhead.
    assert any(
        event.event_type == "player_eliminated"
        and event.player_id == "player_1"
        and event.payload.get("by") == "player_0"
        for event in events
    )
