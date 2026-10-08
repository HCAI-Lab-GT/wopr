"""Replay action payload shape validators for postal satellites."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id

CARD_PAYLOAD_FIELDS = {"card"}
SATELLITE_ATTACK_PAYLOAD_FIELDS = {"satellite", "target_player", "platform"}


def validate_card_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != CARD_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("card",))
    validate_card_id(
        payload["card"],
        f"Replay action {index} {action_type} card must identify a card",
    )


def validate_satellite_attack_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != SATELLITE_ATTACK_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(
        payload, index, action_type, ("satellite", "target_player", "platform")
    )
    validate_card_id(
        payload["satellite"],
        f"Replay action {index} {action_type} satellite must identify a satellite",
    )
    validate_card_id(
        payload["platform"],
        f"Replay action {index} {action_type} platform must identify a platform",
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
    "validate_card_payload",
    "validate_satellite_attack_payload",
]
