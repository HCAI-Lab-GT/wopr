"""Postal propaganda runtime guard tests."""

from __future__ import annotations

from collections import Counter

from nuclear_war_env.actions import ActionType, apply_action, legal_actions
from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.engine.postal.handlers_misc import phase_propaganda
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_queued_propaganda_skips_eliminated_target() -> None:
    propaganda = Card(
        "propaganda",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 5},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([propaganda])
    state.players["p1"].hand = ["propaganda"]
    action = next(
        item
        for item in legal_actions(state, "p1", mode="postal")
        if item.action_type is ActionType.POSTAL_PROPAGANDA
    )
    apply_action(state, action)
    state.players["p2"].alive = False
    state.players["p2"].population = []

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "propaganda_effect" not in event_types
    assert sum(state.players["p1"].population) == 30
    assert sum(state.players["p2"].population) == 0


def test_queued_propaganda_gain_is_capped_at_card_value_on_inexact_change() -> None:
    propaganda = Card(
        "propaganda",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 3},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([propaganda])
    state.players["p1"].population = [25, 5]
    state.players["p2"].population = [25, 25]
    state.population_bank = []
    state.players["p1"].pending_orders["propaganda"] = ["propaganda"]
    state.players["p1"].pending_orders["propaganda_orders"] = {"propaganda": "p2"}

    events = phase_propaganda(state)

    # Round-down makes the target lose 25 (47 is uncomposable from {25, 25}),
    # but the attacker's gain request stays capped at the 3M card value. 33 is
    # uncomposable for the attacker, so the surplus stays in the bank.
    assert sum(state.players["p2"].population) == 25
    assert sum(state.players["p1"].population) == 30
    assert Counter(state.population_bank) == Counter([25])
    assert any(
        event.event_type == "propaganda_effect" and event.payload.get("migrated") == 0
        for event in events
    )


def test_queued_propaganda_rejects_float_metadata_value() -> None:
    propaganda = Card(
        "propaganda",
        CardCategory.PROPAGANDA,
        "Propaganda",
        metadata={"value_millions": 2.0},
    )
    state = GameState(
        ruleset=Ruleset.POSTAL,
        players=create_players(["p1", "p2"], starting_population=30),
        draw_pile=[],
    )
    state.register_cards([propaganda])
    state.players["p1"].hand = ["propaganda"]
    state.players["p1"].pending_orders["propaganda"] = ["propaganda"]
    state.players["p1"].pending_orders["propaganda_orders"] = {"propaganda": "p2"}

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "propaganda_effect" not in event_types
    assert sum(state.players["p1"].population) == 30
    assert sum(state.players["p2"].population) == 30
