"""Population denomination helpers."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import GameState

# The fully source-specified base population deck (older-scan / Scribd card list):
# a 40-card deck in 1/2/5/10/25M denominations totalling 240M.
BASE_POPULATION_DECK_COMPOSITION: dict[int, int] = {1: 10, 2: 10, 5: 10, 10: 6, 25: 4}

# Population cards dealt to each player by player count (older scan / later base rules).
POPULATION_CARDS_PER_PLAYER: dict[int, int] = {2: 15, 3: 10, 4: 8, 5: 7, 6: 6}


def build_population_deck() -> list[int]:
    """Return the base 40-card population deck as a list of denomination values."""
    deck: list[int] = []
    for denomination, count in BASE_POPULATION_DECK_COMPOSITION.items():
        deck.extend([denomination] * count)
    return deck


def population_cards_per_player(player_count: int) -> int:
    """Return the number of population cards each player is dealt at setup."""
    try:
        return POPULATION_CARDS_PER_PLAYER[player_count]
    except KeyError as exc:
        raise ValueError(
            f"Unsupported player count for population deal: {player_count}"
        ) from exc


def distribute_population(total: int) -> list[int]:
    """Split population into available denominations (25, 10, 5, 2, 1)."""
    if total < 0:
        raise ValueError("Population total cannot be negative")
    denominations = [25, 10, 5, 2, 1]
    result: list[int] = []
    remaining = total
    for value in denominations:
        count, remaining = divmod(remaining, value)
        result.extend([value] * count)
    return result


def rebalance_population_cards(
    player_cards: list[int],
    bank_cards: list[int],
    target_total: int,
) -> tuple[list[int], list[int]]:
    """Return player and bank cards after make-change to the target total.

    When no exact subset of the combined cards composes ``target_total`` (the
    5-6 player deal leaves the bank too thin to guarantee change), the target
    is rounded down to the largest composable total: losses land slightly
    heavier and gains slightly lighter than the nominal amount, never the
    reverse. See docs/rule_fidelity_matrix.md.
    """
    if target_total < 0:
        raise ValueError("Population total cannot be negative")
    combined = list(player_cards) + list(bank_cards)
    if target_total > sum(combined):
        raise ValueError(f"Cannot make population total: {target_total}")
    choices = _population_subset_choices(combined, target_total)
    player = choices[max(choices)]
    bank = list(combined)
    for card in player:
        bank.remove(card)
    return player, sorted(bank, reverse=True)


def remove_population_with_bank(
    state: GameState,
    player_id: str,
    amount: int,
) -> int:
    player = state.players[player_id]
    before = sum(player.population)
    loss = min(before, amount)
    player.population, state.population_bank = rebalance_population_cards(
        player.population,
        state.population_bank,
        before - loss,
    )
    if not player.population:
        player.alive = False
    return before - sum(player.population)


def add_population_from_bank(
    state: GameState,
    player_id: str,
    amount: int,
) -> int:
    player = state.players[player_id]
    before = sum(player.population)
    gained = min(sum(state.population_bank), amount)
    player.population, state.population_bank = rebalance_population_cards(
        player.population,
        state.population_bank,
        before + gained,
    )
    return sum(player.population) - before


def _population_subset_choices(
    cards: list[int], target_total: int
) -> dict[int, list[int]]:
    choices: dict[int, list[int]] = {0: []}
    for card in sorted(cards, reverse=True):
        updates = dict(choices)
        for total, choice in choices.items():
            next_total = total + card
            if next_total > target_total:
                continue
            candidate = sorted([*choice, card], reverse=True)
            current = updates.get(next_total)
            if current is None or _population_choice_key(candidate) < (
                _population_choice_key(current)
            ):
                updates[next_total] = candidate
        choices = updates
    return choices


def _population_choice_key(cards: list[int]) -> tuple[int, tuple[int, ...]]:
    return (len(cards), tuple(-card for card in cards))


__all__ = [
    "distribute_population",
    "add_population_from_bank",
    "rebalance_population_cards",
    "remove_population_with_bank",
    "build_population_deck",
    "population_cards_per_player",
    "BASE_POPULATION_DECK_COMPOSITION",
    "POPULATION_CARDS_PER_PLAYER",
]
