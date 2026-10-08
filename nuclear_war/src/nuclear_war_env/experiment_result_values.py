"""Experiment result row value validation helpers."""

from __future__ import annotations

from typing import Any

from .result_player_ids import (
    validate_elimination_id,
    validate_eliminations_match_populations,
    validate_final_population_ids,
    validate_final_population_values,
    validate_termination_matches_populations,
    validate_winner_id,
    validate_winner_matches_populations,
)


def validate_result_values(
    result: dict[str, Any], index: int, expected_players: int
) -> None:
    winner = result["winner"]
    if winner is not None and not isinstance(winner, str):
        raise ValueError(f"Experiment result {index} winner must be a string or null")
    population_count = len(result["final_populations"])
    if population_count != expected_players:
        raise ValueError(
            f"Experiment result {index} final_populations count "
            f"{population_count} does not match players: {expected_players}"
        )
    context = f"Experiment result {index}"
    player_ids = validate_final_population_ids(
        result["final_populations"],
        expected_players,
        context,
    )
    validate_final_population_values(result["final_populations"], context)
    validate_winner_id(winner, player_ids, context)
    actual_eliminations: list[str] = []
    for item_index, player_id in enumerate(result["eliminations"]):
        if not isinstance(player_id, str):
            raise ValueError(
                f"Experiment result {index} elimination {item_index} must be a string"
            )
        validate_elimination_id(player_id, item_index, player_ids, context)
        actual_eliminations.append(player_id)
    validate_eliminations_match_populations(
        actual_eliminations,
        result["final_populations"],
        context,
    )
    pending_final_strikes = _pending_final_strikes(result, index)
    validate_termination_matches_populations(
        result["termination_reason"],
        result["final_populations"],
        context,
        pending_final_strikes,
    )
    validate_winner_matches_populations(
        winner,
        result["final_populations"],
        context,
        result["termination_reason"],
    )


def _pending_final_strikes(result: dict[str, Any], index: int) -> bool:
    value = result.get("pending_final_strikes", False)
    if not isinstance(value, bool):
        raise ValueError(
            f"Experiment result {index} pending_final_strikes must be a boolean"
        )
    if value and result["termination_reason"] != "max_turns":
        raise ValueError(
            f"Experiment result {index} pending_final_strikes requires max_turns"
        )
    mode = result["mode"]
    if value and isinstance(mode, str) and mode != "postal":
        raise ValueError(
            f"Experiment result {index} pending_final_strikes requires postal mode"
        )
    if value and all(
        population > 0 for population in result["final_populations"].values()
    ):
        raise ValueError(
            f"Experiment result {index} pending_final_strikes requires an elimination"
        )
    return value


__all__ = ["validate_result_values"]
