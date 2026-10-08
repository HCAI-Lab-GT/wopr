"""Replay space event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int

SPACE_EMPTY_EVENT_TYPES = {
    "postal_space_platform_launch_ordered",
    "postal_space_shuttle_attack_ordered",
    "postal_space_shuttle_reload_ordered",
    "space_platform_drop_missed",
    "space_platform_launch_failed",
    "space_platform_launched",
    "space_shuttle_attack_failed",
}
SPACE_TARGET_YIELD_EVENT_TYPES = {
    "space_platform_dropped",
    "space_shuttle_attacked",
}


def validate_space_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type in SPACE_TARGET_YIELD_EVENT_TYPES:
        validate_target_yield_payload(event_type, payload, index)
        return True
    if event_type == "space_platform_crashed":
        validate_loss_payload(event_type, payload, index)
        return True
    if event_type == "space_shuttle_reloaded":
        validate_added_payload(payload, index)
        return True
    if event_type == "postal_space_platform_drop_ordered":
        validate_target_payload(event_type, payload, index)
        return True
    if event_type in SPACE_EMPTY_EVENT_TYPES:
        validate_space_empty_payload(event_type, payload, index)
        return True
    return False


def validate_target_yield_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target", "loss", "yield"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_target_field(payload, index, event_type)
    _validate_integer_field(payload, index, event_type, "loss")
    _validate_integer_field(payload, index, event_type, "yield")


def validate_loss_payload(event_type: str, payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"loss"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_integer_field(payload, index, event_type, "loss")


def validate_added_payload(payload: dict[str, Any], index: int) -> None:
    event_type = "space_shuttle_reloaded"
    if set(payload) != {"added"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    added = payload["added"]
    if not isinstance(added, list):
        raise ValueError(f"Replay event {index} {event_type} added must be a list")
    if not all(is_strict_int(item) for item in added):
        raise ValueError(
            f"Replay event {index} {event_type} added must contain integers"
        )


def validate_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_target_field(payload, index, event_type)


def _validate_target_field(
    payload: dict[str, Any], index: int, event_type: str
) -> None:
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")


def validate_space_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


def _validate_integer_field(
    payload: dict[str, Any], index: int, event_type: str, field: str
) -> None:
    if not is_strict_int(payload[field]):
        raise ValueError(
            f"Replay event {index} {event_type} {field} must be an integer"
        )


__all__ = [
    "validate_added_payload",
    "validate_loss_payload",
    "validate_space_empty_payload",
    "validate_space_event_payload_shape",
    "validate_target_payload",
    "validate_target_yield_payload",
]
