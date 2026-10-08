"""Replay submarine event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int

SUBMARINE_EMPTY_EVENT_TYPES = {
    "postal_submarine_fire_ordered",
    "postal_submarine_return_ordered",
    "submarine_destroyed",
    "submarine_in_port",
    "submarine_reloaded",
    "submarine_returned",
    "submarine_sent_to_sea",
}
SUBMARINE_SETUP_EVENT_TYPES = {
    "postal_submarine_launch_ordered",
    "postal_submarine_reload_ordered",
}


def validate_submarine_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type == "submarine_strike":
        validate_submarine_strike_payload(payload, index)
        return True
    if event_type in SUBMARINE_SETUP_EVENT_TYPES:
        validate_submarine_setup_payload(event_type, payload, index)
        return True
    if event_type in SUBMARINE_EMPTY_EVENT_TYPES:
        validate_submarine_empty_payload(event_type, payload, index)
        return True
    return False


def validate_submarine_strike_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) not in ({"target", "loss"}, {"target", "loss", "yield"}):
        raise ValueError(
            f"Replay event {index} submarine_strike payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(
            f"Replay event {index} submarine_strike target must be a string"
        )
    if not is_strict_int(payload["loss"]):
        raise ValueError(
            f"Replay event {index} submarine_strike loss must be an integer"
        )
    if "yield" in payload and not is_strict_int(payload["yield"]):
        raise ValueError(
            f"Replay event {index} submarine_strike yield must be an integer"
        )


def validate_submarine_setup_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target", "warhead_yield"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")
    if not is_strict_int(payload["warhead_yield"]):
        raise ValueError(
            f"Replay event {index} {event_type} warhead_yield must be an integer"
        )


def validate_submarine_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


__all__ = [
    "validate_submarine_empty_payload",
    "validate_submarine_event_payload_shape",
    "validate_submarine_setup_payload",
    "validate_submarine_strike_payload",
]
