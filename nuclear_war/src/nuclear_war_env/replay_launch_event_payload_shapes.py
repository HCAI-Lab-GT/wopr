"""Replay launch event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int
from .replay_card_identity import validate_card_id, validate_card_id_list

TARGET_PAYLOAD_EVENT_TYPES = {"target_declared", "final_strike_targeted"}


def validate_launch_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type in TARGET_PAYLOAD_EVENT_TYPES:
        validate_target_payload(event_type, payload, index)
        return True
    if event_type == "launch_declared":
        validate_launch_declared_payload(payload, index)
        return True
    if event_type == "intercept_success":
        validate_intercept_success_payload(payload, index)
        return True
    return False


def validate_target_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"target"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(f"Replay event {index} {event_type} target must be a string")


def validate_launch_declared_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"target", "warheads", "yield"}:
        raise ValueError(
            f"Replay event {index} launch_declared payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(
            f"Replay event {index} launch_declared target must be a string"
        )
    warheads = payload["warheads"]
    if not isinstance(warheads, list):
        raise ValueError(
            f"Replay event {index} launch_declared warheads must be a list"
        )
    if not all(isinstance(item, str) for item in warheads):
        raise ValueError(
            f"Replay event {index} launch_declared warheads must contain strings"
        )
    validate_card_id_list(
        warheads, f"Replay event {index} launch_declared warheads must identify cards"
    )
    if not is_strict_int(payload["yield"]):
        raise ValueError(
            f"Replay event {index} launch_declared yield must be an integer"
        )


def validate_intercept_success_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"stopped_delivery"}:
        raise ValueError(
            f"Replay event {index} intercept_success payload fields are invalid"
        )
    if not isinstance(payload["stopped_delivery"], str):
        raise ValueError(
            f"Replay event {index} intercept_success stopped_delivery must be a string"
        )
    validate_card_id(
        payload["stopped_delivery"],
        f"Replay event {index} intercept_success stopped_delivery must identify a card",
    )


__all__ = [
    "validate_intercept_success_payload",
    "validate_launch_declared_payload",
    "validate_launch_event_payload_shape",
    "validate_target_payload",
]
