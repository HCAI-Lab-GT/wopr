"""Replay cruise event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int

CRUISE_EMPTY_EVENT_TYPES = {
    "cruise_drop_failed",
    "cruise_drop_missed",
    "cruise_launch_failed",
    "postal_cruise_drop_ordered",
}


def validate_cruise_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type == "cruise_launched":
        validate_cruise_launched_payload(payload, index)
        return True
    if event_type == "cruise_move":
        validate_cruise_move_payload(payload, index)
        return True
    if event_type == "cruise_dropped":
        validate_cruise_dropped_payload(payload, index)
        return True
    if event_type == "postal_cruise_launch_ordered":
        validate_postal_cruise_launch_payload(payload, index)
        return True
    if event_type == "postal_cruise_move_ordered":
        validate_target_payload(event_type, payload, index)
        return True
    if event_type in CRUISE_EMPTY_EVENT_TYPES:
        validate_cruise_empty_payload(event_type, payload, index)
        return True
    return False


def validate_cruise_launched_payload(payload: dict[str, Any], index: int) -> None:
    validate_target_payload("cruise_launched", payload, index)


def validate_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")


def validate_cruise_move_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"target", "status"}:
        raise ValueError(f"Replay event {index} cruise_move payload fields are invalid")
    if payload["target"] is not None and not isinstance(payload["target"], str):
        raise ValueError(
            f"Replay event {index} cruise_move target must be a string or null"
        )
    if not isinstance(payload["status"], str):
        raise ValueError(f"Replay event {index} cruise_move status must be a string")


def validate_cruise_dropped_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"target", "loss", "yield"}:
        raise ValueError(
            f"Replay event {index} cruise_dropped payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} cruise_dropped target must be a string")
    if not is_strict_int(payload["loss"]):
        raise ValueError(f"Replay event {index} cruise_dropped loss must be an integer")
    if not is_strict_int(payload["yield"]):
        raise ValueError(
            f"Replay event {index} cruise_dropped yield must be an integer"
        )


def validate_postal_cruise_launch_payload(payload: dict[str, Any], index: int) -> None:
    event_type = "postal_cruise_launch_ordered"
    if set(payload) != {"target", "yield"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")
    if not is_strict_int(payload["yield"]):
        raise ValueError(f"Replay event {index} {event_type} yield must be an integer")


def validate_cruise_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


__all__ = [
    "validate_cruise_dropped_payload",
    "validate_cruise_empty_payload",
    "validate_cruise_event_payload_shape",
    "validate_cruise_launched_payload",
    "validate_cruise_move_payload",
    "validate_postal_cruise_launch_payload",
    "validate_target_payload",
]
