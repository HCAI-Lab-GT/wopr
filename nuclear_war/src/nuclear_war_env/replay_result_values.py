"""Single-game replay result value validation helpers."""

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


def validate_replay_result_values(payload: dict[str, Any]) -> None:
    final_populations = payload["final_populations"]
    eliminations = payload["eliminations"]
    if not isinstance(final_populations, dict):
        raise ValueError("Replay final_populations must be an object")
    if not isinstance(eliminations, list):
        raise ValueError("Replay eliminations must be a list")
    _validate_population_count(final_populations, payload["players"])
    player_ids = validate_final_population_ids(
        final_populations,
        payload["players"],
        "Replay",
    )
    validate_final_population_values(final_populations, "Replay")
    pending_final_strikes = _pending_final_strikes(payload, final_populations)
    validate_winner_id(payload["winner"], player_ids, "Replay")
    _validate_eliminations(eliminations, final_populations)
    validate_termination_matches_populations(
        payload["termination_reason"],
        final_populations,
        "Replay",
        pending_final_strikes,
    )
    validate_winner_matches_populations(
        payload["winner"],
        final_populations,
        "Replay",
        payload["termination_reason"],
    )


def _validate_population_count(
    final_populations: dict[str, Any], expected_players: int
) -> None:
    population_count = len(final_populations)
    if population_count != expected_players:
        raise ValueError(
            f"Replay final_populations count {population_count} "
            f"does not match players: {expected_players}"
        )


def _validate_eliminations(
    eliminations: list[Any], final_populations: dict[str, Any]
) -> None:
    actual: list[str] = []
    for index, player_id in enumerate(eliminations):
        if not isinstance(player_id, str):
            raise ValueError(f"Replay elimination {index} must be a string")
        validate_elimination_id(player_id, index, set(final_populations), "Replay")
        actual.append(player_id)
    validate_eliminations_match_populations(actual, final_populations, "Replay")


def _pending_final_strikes(
    payload: dict[str, Any], final_populations: dict[str, Any]
) -> bool:
    value = payload.get("pending_final_strikes", False)
    if not isinstance(value, bool):
        raise ValueError("Replay pending_final_strikes must be a boolean")
    if value and payload["termination_reason"] != "max_turns":
        raise ValueError("Replay pending_final_strikes requires max_turns")
    if value and payload["mode"] != "postal":
        raise ValueError("Replay pending_final_strikes requires postal mode")
    if value and all(population > 0 for population in final_populations.values()):
        raise ValueError("Replay pending_final_strikes requires an elimination")
    return value


__all__ = ["validate_replay_result_values"]
