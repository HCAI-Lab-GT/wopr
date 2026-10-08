"""Environment config validation helpers."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int


def validate_max_cycles(max_cycles: Any) -> int:
    if not is_strict_int(max_cycles):
        raise ValueError("Environment max_cycles must be an integer")
    if max_cycles < 1:
        raise ValueError("Environment max_cycles must be positive")
    return max_cycles


__all__ = ["validate_max_cycles"]
