"""Termination reason validation for replay-safe outputs."""

from __future__ import annotations

from typing import Any

VALID_TERMINATION_REASONS = frozenset(
    {
        "max_turns",
        "no_players_remaining",
        "one_player_remaining",
    }
)


def validate_termination_reason(value: Any, context: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"{context} termination_reason must be a string")
    if value not in VALID_TERMINATION_REASONS:
        raise ValueError(f"{context} termination_reason has invalid value: {value}")


__all__ = ["VALID_TERMINATION_REASONS", "validate_termination_reason"]
