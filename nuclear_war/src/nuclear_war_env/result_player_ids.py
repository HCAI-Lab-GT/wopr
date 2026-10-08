"""Player-id validation helpers for stored results."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int
from .players import player_ids


def expected_player_ids(expected_players: int) -> set[str]:
    return set(player_ids(expected_players))


def validate_final_population_ids(
    final_populations: dict[str, Any],
    expected_players: int,
    context: str,
) -> set[str]:
    expected = expected_player_ids(expected_players)
    actual = set(final_populations)
    if actual != expected:
        raise ValueError(f"{context} final_populations keys must match players")
    return expected


def validate_final_population_values(
    final_populations: dict[str, Any],
    context: str,
) -> None:
    for player_id, population in final_populations.items():
        if not is_strict_int(population):
            raise ValueError(
                f"{context} final_populations {player_id} must be an integer"
            )
        if population < 0:
            raise ValueError(
                f"{context} final_populations {player_id} must be nonnegative"
            )


def validate_winner_id(
    winner: str | None,
    known_player_ids: set[str],
    context: str,
) -> None:
    if winner is not None and winner not in known_player_ids:
        raise ValueError(f"{context} winner must be a known player id or null")


def validate_elimination_id(
    player_id: str,
    index: int,
    known_player_ids: set[str],
    context: str,
) -> None:
    if player_id not in known_player_ids:
        raise ValueError(f"{context} elimination {index} must be a known player id")


def validate_eliminations_match_populations(
    eliminations: list[str],
    final_populations: dict[str, int],
    context: str,
) -> None:
    expected = sorted(
        player_id
        for player_id, population in final_populations.items()
        if population <= 0
    )
    if sorted(eliminations) != expected:
        raise ValueError(f"{context} eliminations do not match final populations")


def validate_player_reference(
    player_id: str | None,
    known_player_ids: set[str],
    context: str,
    *,
    allow_null: bool = False,
) -> None:
    if allow_null and player_id is None:
        return
    if player_id not in known_player_ids:
        suffix = " or null" if allow_null else ""
        raise ValueError(f"{context} must be a known player id{suffix}")


def validate_winner_matches_populations(
    winner: str | None,
    final_populations: dict[str, int],
    context: str,
    termination_reason: str,
) -> None:
    live = {
        player_id: population
        for player_id, population in final_populations.items()
        if population > 0
    }
    if termination_reason != "one_player_remaining":
        if winner is not None:
            raise ValueError(f"{context} winner does not match final populations")
        return
    expected = next(iter(live)) if len(live) == 1 else None
    if winner != expected:
        raise ValueError(f"{context} winner does not match final populations")


def validate_termination_matches_populations(
    termination_reason: str,
    final_populations: dict[str, int],
    context: str,
    allow_max_turns_cutoff: bool = False,
) -> None:
    live_count = sum(1 for population in final_populations.values() if population > 0)
    if termination_reason == "max_turns" and (live_count > 1 or allow_max_turns_cutoff):
        return
    expected = "max_turns"
    if live_count == 0:
        expected = "no_players_remaining"
    if live_count == 1:
        expected = "one_player_remaining"
    if termination_reason != expected:
        raise ValueError(
            f"{context} termination_reason does not match final populations"
        )


__all__ = [
    "expected_player_ids",
    "validate_elimination_id",
    "validate_eliminations_match_populations",
    "validate_final_population_ids",
    "validate_final_population_values",
    "validate_player_reference",
    "validate_termination_matches_populations",
    "validate_winner_id",
    "validate_winner_matches_populations",
]
