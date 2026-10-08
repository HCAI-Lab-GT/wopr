"""Postal secret-theft runtime guard tests."""

from __future__ import annotations

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.engine import execute_postal_turn
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_queued_secret_theft_skips_dead_actor() -> None:
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
    state.players["p1"].alive = False
    state.players["p1"].population = []
    state.players["p1"].pending_orders["steal_secret"] = "p2"
    state.players["p2"].secrets = ["secret"]

    events = execute_postal_turn(state)
    event_types = [event.event_type for event in events]

    assert "secret_stolen" not in event_types
    assert state.players["p1"].secrets == []
    assert state.players["p2"].secrets == ["secret"]
