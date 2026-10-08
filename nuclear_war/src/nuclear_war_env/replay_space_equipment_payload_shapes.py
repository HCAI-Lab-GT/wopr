"""Replay action payload shape validators for postal space equipment."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id, validate_card_id_list

CARD_PLATFORM_WARHEADS_PAYLOAD_FIELDS = {"card", "platform", "warheads"}
CARD_WARHEADS_PAYLOAD_FIELDS = {"card", "warheads"}


def validate_card_platform_warheads_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != CARD_PLATFORM_WARHEADS_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("card", "platform"))
    _validate_identifier(payload, "card", index, action_type, "card")
    _validate_identifier(payload, "platform", index, action_type, "platform")
    _validate_warheads(payload, index, action_type)


def validate_card_warheads_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != CARD_WARHEADS_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("card",))
    _validate_identifier(payload, "card", index, action_type, "card")
    _validate_warheads(payload, index, action_type)


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


def _validate_warheads(payload: dict[str, Any], index: int, action_type: str) -> None:
    warheads = payload["warheads"]
    if not isinstance(warheads, list):
        raise ValueError(f"Replay action {index} {action_type} warheads must be a list")
    if not all(isinstance(warhead_id, str) for warhead_id in warheads):
        raise ValueError(
            f"Replay action {index} {action_type} warheads must be strings"
        )
    validate_card_id_list(
        warheads, f"Replay action {index} {action_type} warheads must identify cards"
    )


__all__ = [
    "validate_card_platform_warheads_payload",
    "validate_card_warheads_payload",
]
