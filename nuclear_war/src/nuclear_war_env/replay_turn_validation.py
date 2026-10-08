"""Replay log turn validation helpers."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int


def validate_log_turn_order(entries: list[Any], entry_type: str) -> None:
    previous_turn = 0
    for entry in entries:
        if not isinstance(entry, dict) or not is_strict_int(entry.get("turn")):
            continue
        turn = entry["turn"]
        if turn < previous_turn:
            raise ValueError(f"Replay {entry_type} log turns must be nondecreasing")
        previous_turn = turn


def validate_turn(value: Any, limit: int, entry_type: str, index: int) -> None:
    if not is_strict_int(value) or value < 1 or value > limit:
        raise ValueError(f"Replay {entry_type} {index} has invalid turn: {value}")


__all__ = ["validate_log_turn_order", "validate_turn"]
