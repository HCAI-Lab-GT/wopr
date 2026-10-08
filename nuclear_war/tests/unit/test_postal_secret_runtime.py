"""Postal secret runtime guard tests."""

from __future__ import annotations

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_queued_secret_target_skips_eliminated_target() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"steal_population_millions": 2},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([secret])
    state.players["p1"].secrets = ["secret"]
    action = next(
        item
        for item in legal_actions(state, "p1", mode="postal")
        if item.action_type is ActionType.POSTAL_SECRET_TARGET
    )
    apply_action(state, action)
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "secret_triggered" not in event_types
    assert "secret_population_stolen" not in event_types
    assert state.players["p1"].secrets == ["secret"]
    assert sum(state.players["p1"].population) == 30


def test_queued_secret_theft_skips_eliminated_target() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"steal_population_millions": 2},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([secret])
    state.players["p2"].secrets = ["secret"]
    action = next(
        item
        for item in legal_actions(state, "p1", mode="postal")
        if item.action_type is ActionType.POSTAL_STEAL_SECRET
    )
    apply_action(state, action)
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "secret_stolen" not in event_types
    assert state.players["p1"].secrets == []
    assert state.players["p2"].secrets == ["secret"]


def test_secret_steal_population_rejects_float_metadata_amount() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"steal_population_millions": 2.0},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([secret])
    state.players["p1"].secrets = ["secret"]
    state.players["p1"].pending_orders["secret_targets"] = {"secret": "p2"}

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "secret_triggered" in event_types
    assert "secret_population_stolen" not in event_types
    assert sum(state.players["p1"].population) == 30
    assert sum(state.players["p2"].population) == 30


def test_secret_gain_from_bank_rejects_float_metadata_amount() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"gain_from_bank_millions": 2.0},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([secret])
    state.players["p1"].secrets = ["secret"]
    state.players["p1"].pending_orders["secret_targets"] = {"secret": "p2"}

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "secret_triggered" in event_types
    assert "secret_population_gained" not in event_types
    assert sum(state.players["p1"].population) == 30


def test_secret_damage_population_rejects_float_metadata_amount() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"damage_population_millions": 2.0},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([secret])
    state.players["p1"].secrets = ["secret"]
    state.players["p1"].pending_orders["secret_targets"] = {"secret": "p2"}

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "secret_triggered" in event_types
    assert "secret_population_damaged" not in event_types
    assert sum(state.players["p2"].population) == 30
