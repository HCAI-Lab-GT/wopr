"""Replay action payload shape validators for postal atomic cannons."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id

CANNON_TARGET_PAYLOAD_FIELDS = {"cannon", "target"}
CANNON_WARHEAD_PAYLOAD_FIELDS = {"cannon", "warhead"}


def validate_cannon_target_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != CANNON_TARGET_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("cannon", "target"))
    validate_card_id(
        payload["cannon"],
        f"Replay action {index} {action_type} cannon must identify a cannon",
    )


def validate_cannon_warhead_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != CANNON_WARHEAD_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("cannon", "warhead"))
    validate_card_id(
        payload["cannon"],
        f"Replay action {index} {action_type} cannon must identify a cannon",
    )
    validate_card_id(
        payload["warhead"],
        f"Replay action {index} {action_type} warhead must identify a card",
    )


def _validate_string_fields(
    payload: dict[str, Any], index: int, action_type: str, fields: tuple[str, ...]
) -> None:
    for field in fields:
        if not isinstance(payload[field], str):
            raise ValueError(
                f"Replay action {index} {action_type} {field} must be a string"
            )


__all__ = [
    "validate_cannon_target_payload",
    "validate_cannon_warhead_payload",
]
