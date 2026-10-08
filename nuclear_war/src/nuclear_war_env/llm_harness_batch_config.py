"""Config parsing for deterministic no-press LLM harness batches."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from . import llm_harness_batch_config_validation as config_validation
from . import llm_harness_batch_config_values as values
from .llm_harness import LLMSeatConfig
from .llm_harness_http_config import http_client_config
from .variants import ACTIVE_VARIANT_ID

FALLBACK_POLICIES = {"first", "pass"}


@dataclass(frozen=True)
class NoPressLLMBatchConfig:
    players: int
    seed_start: int
    runs: int
    seats: Mapping[str, LLMSeatConfig]
    max_turns: int = 50
    variant_id: str = ACTIVE_VARIANT_ID


def load_no_press_llm_batch_config(payload: Any) -> NoPressLLMBatchConfig:
    if not isinstance(payload, dict):
        raise ValueError("LLM experiment config must be an object")
    config_validation.validate_no_press_llm_batch_payload(payload)
    seats = payload.get("seats")
    if not isinstance(seats, dict):
        raise ValueError("LLM experiment seats must be an object")
    config = NoPressLLMBatchConfig(
        players=values.int_value(payload, "players"),
        seed_start=values.int_value(payload, "seed_start"),
        runs=values.int_value(payload, "runs"),
        max_turns=values.int_value(payload, "max_turns", 50),
        variant_id=values.str_value(payload, "variant_id", ACTIVE_VARIANT_ID),
        seats={
            _seat_id(player_id): _seat_config(player_id, seat)
            for player_id, seat in seats.items()
        },
    )
    config_validation.validate_no_press_llm_batch_config(config)
    return config


def _seat_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("LLM experiment seat ids must be strings")
    return value


def _seat_config(player_id: Any, payload: Any) -> LLMSeatConfig:
    if not isinstance(payload, dict):
        raise ValueError("LLM experiment seat entries must be objects")
    context = f"LLM experiment seat {player_id}"
    config_validation.validate_no_press_llm_batch_seat_payload(payload, context)
    fallback = values.str_value(payload, "fallback", "first", context)
    if fallback not in FALLBACK_POLICIES:
        allowed = sorted(FALLBACK_POLICIES)
        raise ValueError(f"{context} fallback must be one of {allowed}")
    return LLMSeatConfig(
        agent=values.str_value(payload, "agent", context=context),
        scripted_responses=values.str_list(payload, "scripted_responses", context),
        scripted_provider_latency_ms=values.int_list(
            payload,
            "scripted_provider_latency_ms",
            context,
        ),
        scripted_provider_cost=values.num_list(
            payload,
            "scripted_provider_cost",
            context,
        ),
        max_retries=values.nonnegative_int(payload, "max_retries", 1, context),
        fallback=fallback,
        client=_optional_http_client_config(payload, context),
        archetype=_optional_payload_value(payload, "archetype"),
        archetype_parameters=_optional_payload_value(payload, "archetype_parameters"),
        members=tuple(payload.get("members") or ()),
    )


def _optional_http_client_config(payload: dict[str, Any], context: str) -> Any:
    client = payload.get("client")
    if client is None:
        return None
    return http_client_config(client, context)


def _optional_payload_value(payload: dict[str, Any], key: str) -> Any:
    value = payload.get(key)
    return None if value is None else value


__all__ = ["NoPressLLMBatchConfig", "load_no_press_llm_batch_config"]
