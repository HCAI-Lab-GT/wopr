"""Config snapshots for no-press LLM batch artifacts."""

from __future__ import annotations

from typing import Any

from .llm_harness import LLMSeatConfig
from .llm_harness_batch_config import (
    NoPressLLMBatchConfig,
    load_no_press_llm_batch_config,
)


def batch_config_snapshot(config: NoPressLLMBatchConfig) -> dict[str, Any]:
    return {
        "players": config.players,
        "seed_start": config.seed_start,
        "runs": config.runs,
        "max_turns": config.max_turns,
        "variant_id": config.variant_id,
        "seats": {
            player_id: _seat_snapshot(seat) for player_id, seat in config.seats.items()
        },
    }


def validate_batch_config_snapshot(
    config_payload: Any,
    summary: dict[str, Any],
) -> None:
    config = load_no_press_llm_batch_config(config_payload)
    if config_payload != batch_config_snapshot(config):
        raise ValueError("LLM experiment config does not match strict snapshot")
    _validate_top_level(config, summary)
    if _seat_labels(config) != summary["seat_config"]:
        raise ValueError("LLM experiment config seats do not match seat_config")


def _seat_snapshot(seat: LLMSeatConfig) -> dict[str, Any]:
    snapshot = {
        "agent": seat.agent,
        "scripted_responses": list(seat.scripted_responses),
        "scripted_provider_latency_ms": list(seat.scripted_provider_latency_ms),
        "scripted_provider_cost": list(seat.scripted_provider_cost),
        "max_retries": seat.max_retries,
        "fallback": seat.fallback,
    }
    if seat.client is not None:
        snapshot["client"] = _client_snapshot(seat)
    # Faction (faction_c2) seats carry archetype/members that the seat parser
    # requires. Omitting them made the snapshot fail its own round-trip load
    # ("archetype requires faction_c2 agent"), invalidating every faction batch's
    # summary.json. Emit them only when present so non-faction snapshots are byte
    # identical to before.
    if seat.archetype is not None:
        snapshot["archetype"] = seat.archetype
    if seat.archetype_parameters is not None:
        snapshot["archetype_parameters"] = dict(seat.archetype_parameters)
    if seat.members:
        snapshot["members"] = [dict(member) for member in seat.members]
    return snapshot


def _client_snapshot(seat: LLMSeatConfig) -> dict[str, Any]:
    client = seat.client
    if client is None:
        raise ValueError("HTTP client snapshot requires client config")
    return {
        "provider": client.provider,
        "base_url": client.base_url,
        "base_url_env": client.base_url_env,
        "model": client.model,
        "model_env": client.model_env,
        "api_key_env": client.api_key_env,
        "provider_label": client.provider_label,
        "timeout_seconds": client.timeout_seconds,
        "temperature": client.temperature,
        "max_tokens": client.max_tokens,
        "reasoning_effort": client.reasoning_effort,
        "reasoning_enabled": client.reasoning_enabled,
        "stream": client.stream,
    }


def _validate_top_level(
    config: NoPressLLMBatchConfig,
    summary: dict[str, Any],
) -> None:
    for field, value in _top_level_values(config).items():
        if summary[field] != value:
            raise ValueError(f"LLM experiment config {field} does not match summary")


def _top_level_values(config: NoPressLLMBatchConfig) -> dict[str, int]:
    return {
        "players": config.players,
        "seed_start": config.seed_start,
        "runs": config.runs,
        "max_turns": config.max_turns,
    }


def _seat_labels(config: NoPressLLMBatchConfig) -> dict[str, str]:
    return {player_id: seat.agent for player_id, seat in config.seats.items()}


__all__ = ["batch_config_snapshot", "validate_batch_config_snapshot"]
