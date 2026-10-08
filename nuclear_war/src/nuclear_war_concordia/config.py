"""Config parsing for Concordia no-press harness runs."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_env import llm_harness_batch_config_values as values
from nuclear_war_env.llm_harness_http_config import http_client_config
from nuclear_war_env.variants import ACTIVE_VARIANT_ID

from .authority_config import load_authority_config
from .config_types import ConcordiaNoPressConfig, ConcordiaSeatConfig
from .config_validation import validate_config
from .config_values import load_identity, validate_fields
from .press_config import load_press_config

CONFIG_FIELDS = {
    "players",
    "seed",
    "max_turns",
    "variant_id",
    "runtime",
    "seats",
    "press",
}
SEAT_FIELDS = {
    "agent",
    "identity",
    "max_retries",
    "scripted_responses",
    "client",
    "authority",
}


def load_concordia_no_press_config(payload: Any) -> ConcordiaNoPressConfig:
    if not isinstance(payload, dict):
        raise ValueError("Concordia config must be an object")
    validate_fields(payload, CONFIG_FIELDS, "Concordia config")
    seats = payload.get("seats")
    if not isinstance(seats, dict):
        raise ValueError("Concordia config seats must be an object")
    config = ConcordiaNoPressConfig(
        players=values.int_value(payload, "players"),
        seed=values.int_value(payload, "seed"),
        max_turns=values.int_value(payload, "max_turns", 50),
        variant_id=values.str_value(payload, "variant_id", ACTIVE_VARIANT_ID),
        runtime=values.str_value(payload, "runtime", "auto"),
        press=load_press_config(payload.get("press")),
        seats={
            _seat_id(player_id): _seat_config(player_id, seat)
            for player_id, seat in seats.items()
        },
    )
    validate_config(config)
    return config


def _seat_id(value: Any) -> str:
    if not isinstance(value, str):
        raise ValueError("Concordia seat ids must be strings")
    return value


def _seat_config(player_id: Any, payload: Any) -> ConcordiaSeatConfig:
    if not isinstance(payload, dict):
        raise ValueError("Concordia seat entries must be objects")
    context = f"Concordia seat {player_id}"
    validate_fields(payload, SEAT_FIELDS, context)
    return ConcordiaSeatConfig(
        agent=values.str_value(payload, "agent", context=context),
        identity=load_identity(payload.get("identity"), context),
        max_retries=values.nonnegative_int(payload, "max_retries", 1, context),
        scripted_responses=values.str_list(payload, "scripted_responses", context),
        client=_optional_http_client_config(payload, context),
        authority=load_authority_config(payload.get("authority"), context),
    )


def _optional_http_client_config(
    payload: dict[str, Any],
    context: str,
) -> HTTPClientConfig | None:
    client = payload.get("client")
    if client is None:
        return None
    return http_client_config(client, context)


__all__ = [
    "ConcordiaNoPressConfig",
    "ConcordiaSeatConfig",
    "load_concordia_no_press_config",
]
