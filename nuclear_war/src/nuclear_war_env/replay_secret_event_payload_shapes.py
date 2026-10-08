"""Replay secret event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int

SECRET_TARGET_EVENT_TYPES = {
    "postal_secret_targeted",
    "postal_secret_theft_ordered",
    "secret_triggered",
}
SECRET_LOSS_EVENT_TYPES = {
    "secret_population_damaged",
    "secret_population_removed",
}
SECRET_EMPTY_EVENT_TYPES = {"secret_population_gained"}


def validate_secret_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type in SECRET_TARGET_EVENT_TYPES:
        validate_target_payload(event_type, payload, index)
        return True
    if event_type == "secret_stolen":
        validate_from_payload(payload, index)
        return True
    if event_type == "secret_population_stolen":
        validate_population_stolen_payload(payload, index)
        return True
    if event_type in SECRET_LOSS_EVENT_TYPES:
        validate_loss_payload(event_type, payload, index)
        return True
    if event_type == "secret_turns_lost":
        validate_turns_lost_payload(payload, index)
        return True
    if event_type in SECRET_EMPTY_EVENT_TYPES:
        validate_secret_empty_payload(event_type, payload, index)
        return True
    return False


def validate_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_string_field(payload, index, event_type, "target")


def validate_from_payload(payload: dict[str, Any], index: int) -> None:
    event_type = "secret_stolen"
    if set(payload) != {"from"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_string_field(payload, index, event_type, "from")


def validate_population_stolen_payload(payload: dict[str, Any], index: int) -> None:
    event_type = "secret_population_stolen"
    if set(payload) != {"target", "migrated"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_string_field(payload, index, event_type, "target")
    _validate_integer_field(payload, index, event_type, "migrated")


def validate_loss_payload(event_type: str, payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"loss"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_integer_field(payload, index, event_type, "loss")


def validate_turns_lost_payload(payload: dict[str, Any], index: int) -> None:
    event_type = "secret_turns_lost"
    if set(payload) != {"target", "turns"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_string_field(payload, index, event_type, "target")
    _validate_integer_field(payload, index, event_type, "turns")


def validate_secret_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


def _validate_string_field(
    payload: dict[str, Any], index: int, event_type: str, field: str
) -> None:
    if not isinstance(payload[field], str):
        raise ValueError(f"Replay event {index} {event_type} {field} must be a string")


def _validate_integer_field(
    payload: dict[str, Any], index: int, event_type: str, field: str
) -> None:
    if not is_strict_int(payload[field]):
        raise ValueError(
            f"Replay event {index} {event_type} {field} must be an integer"
        )


__all__ = [
    "validate_from_payload",
    "validate_loss_payload",
    "validate_population_stolen_payload",
    "validate_secret_empty_payload",
    "validate_secret_event_payload_shape",
    "validate_target_payload",
    "validate_turns_lost_payload",
]
