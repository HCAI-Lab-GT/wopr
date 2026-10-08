"""Experiment-level validation for no-press LLM batch configs."""

from __future__ import annotations

from typing import Any

from .llm_harness_batch_agent_fields import validate_agent_specific_fields
from .llm_harness_seats import (
    LLM_SCRIPTED_SEAT,
    known_llm_harness_seats,
)
from .players import player_ids

CONFIG_FIELDS = {
    "players",
    "seed_start",
    "runs",
    "max_turns",
    "variant_id",
    "seats",
}
SEAT_FIELDS = {
    "agent",
    "scripted_responses",
    "scripted_provider_latency_ms",
    "scripted_provider_cost",
    "max_retries",
    "fallback",
    "client",
    "archetype",
    "archetype_parameters",
    "members",
}


def validate_no_press_llm_batch_payload(payload: dict[str, Any]) -> None:
    _validate_fields(payload, CONFIG_FIELDS, "LLM experiment config")


def validate_no_press_llm_batch_seat_payload(
    payload: dict[str, Any],
    context: str,
) -> None:
    _validate_fields(payload, SEAT_FIELDS, context)
    validate_agent_specific_fields(payload, context)


def validate_no_press_llm_batch_config(config: Any) -> None:
    _validate_positive(config.runs, "runs")
    _validate_positive(config.max_turns, "max_turns")
    expected = _expected_seats(config.players)
    actual = set(config.seats)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"LLM experiment seats must match players: missing={missing}, extra={extra}"
        )
    _validate_known_agents(config.seats)
    _validate_scripted_provider_metadata_lengths(config.seats)


def _validate_positive(value: int, field: str) -> None:
    if value < 1:
        raise ValueError(f"LLM experiment {field} must be positive")


def _expected_seats(players: int) -> set[str]:
    try:
        return set(player_ids(players))
    except ValueError as exc:
        raise ValueError("LLM experiment players must be at least 2") from exc


def _validate_known_agents(seats: Any) -> None:
    allowed = known_llm_harness_seats()
    labels = sorted(allowed)
    for player_id, seat in seats.items():
        if seat.agent not in allowed:
            raise ValueError(
                f"LLM experiment seat {player_id} agent must be one of {labels}"
            )


def _validate_scripted_provider_metadata_lengths(seats: Any) -> None:
    for player_id, seat in seats.items():
        if seat.agent != LLM_SCRIPTED_SEAT:
            continue
        response_count = len(seat.scripted_responses)
        _validate_metadata_length(
            player_id,
            "scripted_provider_latency_ms",
            len(seat.scripted_provider_latency_ms),
            response_count,
        )
        _validate_metadata_length(
            player_id,
            "scripted_provider_cost",
            len(seat.scripted_provider_cost),
            response_count,
        )


def _validate_metadata_length(
    player_id: str,
    field: str,
    metadata_count: int,
    response_count: int,
) -> None:
    if metadata_count > response_count:
        raise ValueError(
            f"LLM experiment seat {player_id} {field} "
            "must not exceed scripted_responses"
        )


def _validate_fields(
    payload: dict[str, Any],
    allowed_fields: set[str],
    context: str,
) -> None:
    if set(payload) - allowed_fields:
        raise ValueError(f"{context} fields are invalid")


__all__ = [
    "validate_no_press_llm_batch_config",
    "validate_no_press_llm_batch_payload",
    "validate_no_press_llm_batch_seat_payload",
]
