"""Population deck composition and per-player deal counts."""

from __future__ import annotations

from collections import Counter

import pytest

from nuclear_war_env.population import (
    add_population_from_bank,
    build_population_deck,
    population_cards_per_player,
    rebalance_population_cards,
    remove_population_with_bank,
)
from nuclear_war_env.state import GameState, Ruleset, create_players


def test_build_population_deck_matches_documented_40_card_distribution() -> None:
    deck = build_population_deck()
    assert len(deck) == 40
    assert sum(deck) == 240  # millions
    assert Counter(deck) == {1: 10, 2: 10, 5: 10, 10: 6, 25: 4}


def test_population_cards_per_player_by_player_count() -> None:
    assert population_cards_per_player(2) == 15
    assert population_cards_per_player(3) == 10
    assert population_cards_per_player(4) == 8
    assert population_cards_per_player(5) == 7
    assert population_cards_per_player(6) == 6


def test_population_cards_per_player_rejects_unsupported_count() -> None:
    with pytest.raises(ValueError):
        population_cards_per_player(1)


def test_rebalance_population_cards_removes_with_bank_make_change() -> None:
    player, bank = rebalance_population_cards([5], [2, 1, 1, 1], target_total=2)

    assert player == [2]
    assert Counter(bank) == Counter([5, 1, 1, 1])


def test_rebalance_population_cards_adds_with_bank_make_change() -> None:
    player, bank = rebalance_population_cards([2], [5], target_total=5)

    assert player == [5]
    assert bank == [2]


def test_rebalance_population_cards_rejects_total_above_all_cards() -> None:
    with pytest.raises(ValueError, match="Cannot make population total"):
        rebalance_population_cards([5], [10], target_total=16)


def test_rebalance_population_cards_rounds_down_uncomposable_total() -> None:
    # {5, 10} cannot compose 7; the largest composable total below it is 5.
    player, bank = rebalance_population_cards([5], [10], target_total=7)

    assert player == [5]
    assert bank == [10]


def test_rebalance_population_cards_rounds_down_with_thin_bank() -> None:
    # {25, 10, 2} cannot compose 30; the largest composable total below is 27.
    player, bank = rebalance_population_cards([25, 10], [2], target_total=30)

    assert Counter(player) == Counter([25, 2])
    assert bank == [10]


def test_rebalance_population_cards_can_round_down_to_zero() -> None:
    player, bank = rebalance_population_cards([25], [], target_total=20)

    assert player == []
    assert bank == [25]


def test_remove_population_with_bank_updates_state_and_alive_flag() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        population_bank=[2, 1, 1, 1],
    )
    state.players["p1"].population = [5]

    loss = remove_population_with_bank(state, "p1", 5)

    assert loss == 5
    assert state.players["p1"].population == []
    assert state.players["p1"].alive is False
    assert Counter(state.population_bank) == Counter([5, 2, 1, 1, 1])


def test_remove_population_with_bank_reports_extra_round_down_loss() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        population_bank=[],
    )
    state.players["p1"].population = [25, 25]

    # Target 47 is uncomposable from {25, 25}; round down to 25.
    loss = remove_population_with_bank(state, "p1", 3)

    assert loss == 25
    assert state.players["p1"].population == [25]
    assert state.players["p1"].alive is True
    assert state.population_bank == [25]


def test_remove_population_with_bank_round_down_to_zero_eliminates() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        population_bank=[],
    )
    state.players["p1"].population = [25]

    # Target 20 is uncomposable from {25}; round down to 0.
    loss = remove_population_with_bank(state, "p1", 5)

    assert loss == 25
    assert state.players["p1"].population == []
    assert state.players["p1"].alive is False
    assert state.population_bank == [25]


def test_add_population_from_bank_rounds_inexact_gain_down() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        population_bank=[5],
    )
    state.players["p1"].population = [2]

    # Target 6 is uncomposable from {2, 5}; round down to 5, a gain of 3.
    gained = add_population_from_bank(state, "p1", 4)

    assert gained == 3
    assert state.players["p1"].population == [5]
    assert state.population_bank == [2]


def test_add_population_from_bank_inexact_gain_can_round_to_zero() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        population_bank=[10],
    )
    state.players["p1"].population = [25]

    # Target 31 is uncomposable from {25, 10}; the player's own 25 stands.
    gained = add_population_from_bank(state, "p1", 6)

    assert gained == 0
    assert state.players["p1"].population == [25]
    assert state.population_bank == [10]


def test_wrapper_deltas_stay_within_round_down_policy_bounds() -> None:
    # The round-down policy promises: a gain is never negative and never
    # exceeds the nominal amount; a loss is never lighter than the nominal
    # amount and never exceeds the player's holdings.
    holdings = ([25], [25, 10], [10, 2], [5, 2, 1], [2], [1, 1])
    for player_cards in holdings:
        for bank_cards in holdings:
            for amount in range(12):
                state = _single_player_state(player_cards, bank_cards)
                gained = add_population_from_bank(state, "p1", amount)
                assert 0 <= gained <= min(sum(bank_cards), amount)

                state = _single_player_state(player_cards, bank_cards)
                before = sum(state.players["p1"].population)
                loss = remove_population_with_bank(state, "p1", amount)
                assert min(before, amount) <= loss <= before


def _single_player_state(player_cards: list[int], bank_cards: list[int]) -> GameState:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        population_bank=list(bank_cards),
    )
    state.players["p1"].population = list(player_cards)
    return state


def test_add_population_from_bank_updates_state() -> None:
    state = GameState(
        ruleset=Ruleset.TABLE,
        players=create_players(["p1"], starting_population=30),
        draw_pile=[],
        population_bank=[5],
    )
    state.players["p1"].population = [2]

    gained = add_population_from_bank(state, "p1", 3)

    assert gained == 3
    assert state.players["p1"].population == [5]
    assert state.population_bank == [2]
