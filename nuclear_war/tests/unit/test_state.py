"""Unit tests for state management."""

from __future__ import annotations

import pytest

from nuclear_war_env.cards import Card, CardCategory
from nuclear_war_env.rng import SeededRNG
from nuclear_war_env.state import (
    FACE_DOWN_SLOTS,
    GameState,
    PlayerState,
    Ruleset,
    create_players,
    distribute_population,
)


def _make_card(identifier: str) -> Card:
    return Card(identifier=identifier, category=CardCategory.WARHEAD, name=identifier)


def test_distribute_population_breaks_into_denominations() -> None:
    assert distribute_population(0) == []
    assert distribute_population(7) == [5, 2]
    assert distribute_population(37) == [25, 10, 2]


def test_create_players_initialises_population() -> None:
    players = create_players(["p1", "p2"], starting_population=30)
    assert list(players.keys()) == ["p1", "p2"]
    assert sum(players["p1"].population) == 30


def test_player_face_down_queue_advances() -> None:
    player = PlayerState(player_id="p1", population=[10])
    player.enqueue_face_down("card_a")
    player.enqueue_face_down("card_b")
    assert len(player.face_down_queue) == FACE_DOWN_SLOTS
    player.advance_face_down()
    assert player.face_up == "card_a"
    assert list(player.face_down_queue)[0] == "card_b"


def test_player_remove_population_handles_elimination() -> None:
    player = PlayerState(player_id="p1", population=[10])
    loss = player.remove_population(12)
    assert loss == 10
    assert player.population == []
    assert not player.alive


def test_game_state_draws_and_recycles_discard() -> None:
    deck = [_make_card("c1"), _make_card("c2")]
    rng = SeededRNG(seed=1)
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], 10),
        draw_pile=list(deck),
        rng=rng,
    )
    state.register_cards(deck)
    drawn = state.draw_card()
    state.discard(drawn)
    state.draw_card()
    recycled = state.draw_card()
    assert recycled.identifier == drawn.identifier
    assert state.discard_pile == []


def test_card_lookup_returns_registered_card() -> None:
    deck = [_make_card("c1"), _make_card("c2")]
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], 5),
        draw_pile=list(deck),
    )
    state.register_cards(deck)
    assert state.card_by_id("c1").identifier == "c1"


def test_register_cards_rejects_duplicate_runtime_identifiers() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], 5),
        draw_pile=[],
    )

    with pytest.raises(ValueError, match="Duplicate card identifier: c1"):
        state.register_cards([_make_card("c1"), _make_card("c1")])
