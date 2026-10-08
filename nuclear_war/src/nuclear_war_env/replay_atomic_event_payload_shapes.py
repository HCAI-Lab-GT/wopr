"""Replay atomic cannon event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int

ATOMIC_EMPTY_EVENT_TYPES = {
    "atomic_cannon_destroyed",
    "atomic_cannon_discarded",
    "atomic_cannon_setup",
    "postal_atomic_cannon_fire_ordered",
}
ATOMIC_TARGET_EVENT_TYPES = {
    "atomic_cannon_repositioned",
    "postal_atomic_cannon_reposition_ordered",
    "postal_atomic_cannon_setup_ordered",
}


def validate_atomic_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type == "atomic_cannon_fired":
        validate_atomic_cannon_fired_payload(payload, index)
        return True
    if event_type == "atomic_cannon_failed":
        validate_atomic_cannon_failed_payload(payload, index)
        return True
    if event_type in ATOMIC_TARGET_EVENT_TYPES:
        validate_atomic_target_payload(event_type, payload, index)
        return True
    if event_type in ATOMIC_EMPTY_EVENT_TYPES:
        validate_atomic_empty_payload(event_type, payload, index)
        return True
    return False


def validate_atomic_cannon_fired_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"target", "loss", "yield"}:
        raise ValueError(
            f"Replay event {index} atomic_cannon_fired payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(
            f"Replay event {index} atomic_cannon_fired target must be a string"
        )
    if not is_strict_int(payload["loss"]):
        raise ValueError(
            f"Replay event {index} atomic_cannon_fired loss must be an integer"
        )
    if not is_strict_int(payload["yield"]):
        raise ValueError(
            f"Replay event {index} atomic_cannon_fired yield must be an integer"
        )


def validate_atomic_cannon_failed_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"reason"}:
        raise ValueError(
            f"Replay event {index} atomic_cannon_failed payload fields are invalid"
        )
    if not isinstance(payload["reason"], str):
        raise ValueError(
            f"Replay event {index} atomic_cannon_failed reason must be a string"
        )


def validate_atomic_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")


def validate_atomic_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


__all__ = [
    "validate_atomic_cannon_failed_payload",
    "validate_atomic_cannon_fired_payload",
    "validate_atomic_empty_payload",
    "validate_atomic_event_payload_shape",
    "validate_atomic_target_payload",
]
