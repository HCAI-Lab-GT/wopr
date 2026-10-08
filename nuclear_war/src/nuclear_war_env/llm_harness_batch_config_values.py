"""Primitive value parsing for no-press LLM batch configs."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int, is_strict_number

_MISSING = object()


def int_value(payload: dict[str, Any], key: str, default: Any = _MISSING) -> int:
    value = payload.get(key, default)
    if value is _MISSING or not is_strict_int(value):
        raise ValueError(f"LLM experiment {key} must be an integer")
    return int(value)


def str_value(
    payload: dict[str, Any],
    key: str,
    default: Any = _MISSING,
    context: str = "LLM experiment",
) -> str:
    value = payload.get(key, default)
    if value is _MISSING or not isinstance(value, str):
        raise ValueError(f"{context} {key} must be a string")
    return value


def optional_str_value(
    payload: dict[str, Any],
    key: str,
    context: str,
) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError(f"{context} {key} must be a string")
    return value


def bool_value(
    payload: dict[str, Any],
    key: str,
    default: bool,
    context: str,
) -> bool:
    value = payload.get(key, default)
    if not isinstance(value, bool):
        raise ValueError(f"{context} {key} must be a boolean")
    return value


def optional_bool_value(
    payload: dict[str, Any],
    key: str,
    context: str,
) -> bool | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, bool):
        raise ValueError(f"{context} {key} must be a boolean")
    return value


def str_list(payload: dict[str, Any], key: str, context: str) -> tuple[str, ...]:
    values = _typed_list(payload, key, context, _is_str, "strings")
    return tuple(str(item) for item in values)


def int_list(payload: dict[str, Any], key: str, context: str) -> tuple[int, ...]:
    values = _typed_list(payload, key, context, is_strict_int, "integers")
    return tuple(int(item) for item in values)


def num_list(payload: dict[str, Any], key: str, context: str) -> tuple[float, ...]:
    values = _typed_list(payload, key, context, is_strict_number, "numbers")
    return tuple(float(item) for item in values)


def nonnegative_int(
    payload: dict[str, Any],
    key: str,
    default: int,
    context: str,
) -> int:
    value = payload.get(key, default)
    if not is_strict_int(value):
        raise ValueError(f"{context} {key} must be an integer")
    if value < 0:
        raise ValueError(f"{context} {key} must be non-negative")
    return int(value)


def _typed_list(
    payload: dict[str, Any],
    key: str,
    context: str,
    validator: Any,
    label: str,
) -> list[Any]:
    values = payload.get(key, [])
    if not isinstance(values, list):
        raise ValueError(f"{context} {key} must be a list")
    if not all(validator(item) for item in values):
        raise ValueError(f"{context} {key} entries must be {label}")
    return values


def _is_str(value: Any) -> bool:
    return isinstance(value, str)
