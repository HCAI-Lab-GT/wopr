"""Replay equipment event payload shape validators."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id

EQUIPMENT_TARGET_EVENT_TYPES = {"equipment_destroyed", "equipment_target_missed"}


def validate_equipment_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type in EQUIPMENT_TARGET_EVENT_TYPES:
        validate_equipment_target_payload(event_type, payload, index)
        return True
    if event_type == "equipment_target_failed":
        validate_equipment_target_failed_payload(payload, index)
        return True
    return False


def validate_equipment_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target_player", "kind", "equipment"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, event_type, ("target_player", "kind"))
    if not isinstance(payload["equipment"], str):
        raise ValueError(
            f"Replay event {index} {event_type} equipment must be a string"
        )
    validate_card_id(
        payload["equipment"],
        f"Replay event {index} {event_type} equipment must identify equipment",
    )


def validate_equipment_target_failed_payload(
    payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"reason"}:
        raise ValueError(
            f"Replay event {index} equipment_target_failed payload fields are invalid"
        )
    if not isinstance(payload["reason"], str):
        raise ValueError(
            f"Replay event {index} equipment_target_failed reason must be a string"
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
    "validate_equipment_event_payload_shape",
    "validate_equipment_target_failed_payload",
    "validate_equipment_target_payload",
]
