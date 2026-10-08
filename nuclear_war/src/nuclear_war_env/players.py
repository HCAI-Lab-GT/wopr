"""Player id construction helpers."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int


def player_ids(count: Any) -> list[str]:
    if not is_strict_int(count):
        raise ValueError("Player count must be an integer")
    if count < 2:
        raise ValueError("At least two players are required")
    return [f"player_{index}" for index in range(count)]


__all__ = ["player_ids"]
