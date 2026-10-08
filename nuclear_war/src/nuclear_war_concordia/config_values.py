"""Shared value parsing for Concordia harness configuration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from nuclear_war_env import llm_harness_batch_config_values as values


def load_identity(
    payload: Any,
    context: str,
    *,
    require_nonempty_name: bool = False,
) -> Mapping[str, str]:
    if not isinstance(payload, dict):
        raise ValueError(f"{context} identity must be an object")
    if not all(isinstance(key, str) for key in payload):
        raise ValueError(f"{context} identity keys must be strings")
    if not all(isinstance(value, str) for value in payload.values()):
        raise ValueError(f"{context} identity values must be strings")
    name = payload.get("name")
    if not isinstance(name, str):
        raise ValueError(f"{context} identity name must be a string")
    if require_nonempty_name and not name.strip():
        raise ValueError(f"{context} identity name must not be empty")
    return dict(payload)


def nonempty_str_value(payload: dict[str, Any], key: str, context: str) -> str:
    value = values.str_value(payload, key, context=context)
    if not value.strip():
        raise ValueError(f"{context} {key} must not be empty")
    return value


def validate_fields(
    payload: dict[str, Any], allowed_fields: set[str], context: str
) -> None:
    if set(payload) - allowed_fields:
        raise ValueError(f"{context} fields are invalid")


__all__ = ["load_identity", "nonempty_str_value", "validate_fields"]
