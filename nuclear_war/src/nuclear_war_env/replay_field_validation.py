"""Replay field-set validation helpers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any


def validate_field_set(
    payload: dict[str, Any],
    required_fields: Iterable[str],
    context: str,
    optional_fields: Iterable[str] = (),
) -> None:
    allowed = set(required_fields) | set(optional_fields)
    if set(payload) != allowed and set(payload) - allowed:
        raise ValueError(f"{context} fields are invalid")


__all__ = ["validate_field_set"]
