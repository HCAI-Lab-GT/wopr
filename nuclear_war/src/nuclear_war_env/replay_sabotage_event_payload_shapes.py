"""Replay sabotage event payload shape validators."""

from __future__ import annotations

from typing import Any


def validate_sabotage_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type == "postal_sabotage_ordered":
        validate_string_payload(event_type, payload, index, "target")
        return True
    if event_type == "sabotage_success":
        validate_string_payload(event_type, payload, index, "against")
        return True
    return False


def validate_string_payload(
    event_type: str, payload: dict[str, Any], index: int, field: str
) -> None:
    if set(payload) != {field}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload[field], str):
        raise ValueError(f"Replay event {index} {event_type} {field} must be a string")


__all__ = [
    "validate_sabotage_event_payload_shape",
    "validate_string_payload",
]
