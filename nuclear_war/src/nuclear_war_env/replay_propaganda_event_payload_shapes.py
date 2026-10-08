"""Replay propaganda event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int


def validate_propaganda_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type == "postal_propaganda_ordered":
        validate_target_payload(event_type, payload, index)
        return True
    if event_type == "propaganda_effect":
        validate_effect_payload(payload, index)
        return True
    return False


def validate_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")


def validate_effect_payload(payload: dict[str, Any], index: int) -> None:
    event_type = "propaganda_effect"
    if set(payload) != {"target", "migrated"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")
    if not is_strict_int(payload["migrated"]):
        raise ValueError(
            f"Replay event {index} {event_type} migrated must be an integer"
        )


__all__ = [
    "validate_effect_payload",
    "validate_propaganda_event_payload_shape",
    "validate_target_payload",
]
