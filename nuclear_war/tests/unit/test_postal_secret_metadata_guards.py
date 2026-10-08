"""Postal secret metadata guard tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_secret_remove_to_bank_rejects_float_metadata_amount() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"remove_to_bank_millions": 2.0},
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
    assert "secret_population_removed" not in event_types
    assert sum(state.players["p2"].population) == 30


def test_secret_target_loses_turns_rejects_float_metadata_amount() -> None:
    secret = Card(
        "secret",
        CardCategory.SECRET,
        "Secret",
        metadata={"target_loses_turns": 1.0},
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
    assert "secret_turns_lost" not in event_types
    assert state.players["p2"].pending_orders.get("skip_turns") is None
