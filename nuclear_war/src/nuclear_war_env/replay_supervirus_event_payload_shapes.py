"""Replay supervirus event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int

SUPERVIRUS_EMPTY_EVENT_TYPES = {
    "supervirus_cured",
    "supervirus_immunity",
    "supervirus_wiped_out",
}
SUPERVIRUS_TARGET_EVENT_TYPES = {
    "postal_supervirus_pass_ordered",
    "postal_supervirus_start_ordered",
    "supervirus_pass_failed",
}
SUPERVIRUS_TARGET_LOSS_EVENT_TYPES = {
    "supervirus_passed",
    "supervirus_started",
}


def validate_supervirus_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type in SUPERVIRUS_TARGET_LOSS_EVENT_TYPES:
        validate_target_loss_payload(event_type, payload, index)
        return True
    if event_type in SUPERVIRUS_TARGET_EVENT_TYPES:
        validate_target_payload(event_type, payload, index)
        return True
    if event_type == "supervirus_retained":
        validate_turns_held_payload(payload, index)
        return True
    if event_type in SUPERVIRUS_EMPTY_EVENT_TYPES:
        validate_supervirus_empty_payload(event_type, payload, index)
        return True
    return False


def validate_target_loss_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target", "loss"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_target_field(payload, index, event_type)
    if not is_strict_int(payload["loss"]):
        raise ValueError(f"Replay event {index} {event_type} loss must be an integer")


def validate_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_target_field(payload, index, event_type)


def validate_turns_held_payload(payload: dict[str, Any], index: int) -> None:
    event_type = "supervirus_retained"
    if set(payload) != {"turns_held"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not is_strict_int(payload["turns_held"]):
        raise ValueError(
            f"Replay event {index} {event_type} turns_held must be an integer"
        )


def validate_supervirus_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


def _validate_target_field(
    payload: dict[str, Any], index: int, event_type: str
) -> None:
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")


__all__ = [
    "validate_supervirus_empty_payload",
    "validate_supervirus_event_payload_shape",
    "validate_target_loss_payload",
    "validate_target_payload",
    "validate_turns_held_payload",
]
