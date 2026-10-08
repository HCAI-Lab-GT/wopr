"""Strict integer validation helpers."""

from __future__ import annotations

from typing import Any


def is_strict_int(value: Any) -> bool:
    return type(value) is int


def is_strict_number(value: Any) -> bool:
    return type(value) in {float, int}


def positive_int_or_zero(value: object) -> int:
    return value if type(value) is int and value > 0 else 0


__all__ = ["is_strict_int", "is_strict_number", "positive_int_or_zero"]
