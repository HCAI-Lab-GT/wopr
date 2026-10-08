"""Replay action payload shape validators for postal equipment."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id

CARD_TARGET_WARHEAD_PAYLOAD_FIELDS = {"card", "target", "warhead"}
MISSILE_PAYLOAD_FIELDS = {"missile"}
MISSILE_TARGET_PAYLOAD_FIELDS = {"missile", "target"}
PLATFORM_TARGET_PAYLOAD_FIELDS = {"platform", "target"}
SUBMARINE_PAYLOAD_FIELDS = {"submarine"}
SUBMARINE_TARGET_WARHEAD_PAYLOAD_FIELDS = {"submarine", "target", "warhead"}


def validate_card_target_warhead_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != CARD_TARGET_WARHEAD_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("card", "target", "warhead"))
    _validate_identifier(payload, "card", index, action_type, "card")
    _validate_identifier(payload, "warhead", index, action_type, "card")


def validate_missile_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != MISSILE_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("missile",))
    _validate_identifier(payload, "missile", index, action_type, "missile")


def validate_missile_target_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != MISSILE_TARGET_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("missile", "target"))
    _validate_identifier(payload, "missile", index, action_type, "missile")


def validate_platform_target_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != PLATFORM_TARGET_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("platform", "target"))
    _validate_identifier(payload, "platform", index, action_type, "platform")


def validate_submarine_target_warhead_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != SUBMARINE_TARGET_WARHEAD_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(
        payload, index, action_type, ("submarine", "target", "warhead")
    )
    _validate_identifier(payload, "submarine", index, action_type, "submarine")
    _validate_identifier(payload, "warhead", index, action_type, "card")


def validate_submarine_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != SUBMARINE_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("submarine",))
    _validate_identifier(payload, "submarine", index, action_type, "submarine")


def _validate_string_fields(
    payload: dict[str, Any], index: int, action_type: str, fields: tuple[str, ...]
) -> None:
    for field in fields:
        if not isinstance(payload[field], str):
            raise ValueError(
                f"Replay action {index} {action_type} {field} must be a string"
            )


def _validate_identifier(
    payload: dict[str, Any], field: str, index: int, action_type: str, label: str
) -> None:
    validate_card_id(
        payload[field],
        f"Replay action {index} {action_type} {field} must identify a {label}",
    )


__all__ = [
    "validate_card_target_warhead_payload",
    "validate_missile_payload",
    "validate_missile_target_payload",
    "validate_platform_target_payload",
    "validate_submarine_payload",
    "validate_submarine_target_warhead_payload",
]
