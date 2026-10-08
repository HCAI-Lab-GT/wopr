"""Replay killer satellite event payload shape validators."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id

SATELLITE_EMPTY_EVENT_TYPES = {
    "killer_satellite_failed",
    "killer_satellite_launched",
    "postal_killer_satellite_launch_ordered",
}
SATELLITE_TARGET_EVENT_TYPES = {
    "killer_satellite_destroyed_platform",
    "postal_killer_satellite_attack_ordered",
}


def validate_satellite_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type in SATELLITE_TARGET_EVENT_TYPES:
        validate_satellite_target_payload(event_type, payload, index)
        return True
    if event_type in SATELLITE_EMPTY_EVENT_TYPES:
        validate_satellite_empty_payload(event_type, payload, index)
        return True
    return False


def validate_satellite_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target_player", "platform"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, event_type, ("target_player", "platform"))
    validate_card_id(
        payload["platform"],
        f"Replay event {index} {event_type} platform must identify a platform",
    )


def validate_satellite_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


def _validate_string_fields(
    payload: dict[str, Any], index: int, event_type: str, fields: tuple[str, ...]
) -> None:
    for field in fields:
        if not isinstance(payload[field], str):
            raise ValueError(
                f"Replay event {index} {event_type} {field} must be a string"
            )


__all__ = [
    "validate_satellite_empty_payload",
    "validate_satellite_event_payload_shape",
    "validate_satellite_target_payload",
]
