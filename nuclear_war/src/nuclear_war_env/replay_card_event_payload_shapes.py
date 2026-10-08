"""Replay card event payload shape validators."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id

PREVIOUS_PAYLOAD_EVENT_TYPES = {
    "card_resolved",
    "defense_prepared",
    "propaganda_ready",
}


def validate_card_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> bool:
    if event_type == "warhead_loaded":
        validate_warhead_loaded_payload(payload, index)
        return True
    if event_type == "warhead_discarded":
        validate_warhead_discarded_payload(payload, index)
        return True
    if event_type in PREVIOUS_PAYLOAD_EVENT_TYPES:
        validate_previous_payload(event_type, payload, index)
        return True
    return False


def validate_warhead_loaded_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"delivery", "previous"}:
        raise ValueError(
            f"Replay event {index} warhead_loaded payload fields are invalid"
        )
    if not isinstance(payload["delivery"], str):
        raise ValueError(
            f"Replay event {index} warhead_loaded delivery must be a string"
        )
    validate_card_id(
        payload["delivery"],
        f"Replay event {index} warhead_loaded delivery must identify a card",
    )
    if payload["previous"] is not None and not isinstance(payload["previous"], str):
        raise ValueError(
            f"Replay event {index} warhead_loaded previous must be a string or null"
        )
    if payload["previous"] is not None:
        validate_card_id(
            payload["previous"],
            f"Replay event {index} warhead_loaded previous must identify a card",
        )


def validate_warhead_discarded_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"reason", "previous"}:
        raise ValueError(
            f"Replay event {index} warhead_discarded payload fields are invalid"
        )
    if not isinstance(payload["reason"], str):
        raise ValueError(
            f"Replay event {index} warhead_discarded reason must be a string"
        )
    if payload["previous"] is not None and not isinstance(payload["previous"], str):
        raise ValueError(
            f"Replay event {index} warhead_discarded previous must be a string or null"
        )
    if payload["previous"] is not None:
        validate_card_id(
            payload["previous"],
            f"Replay event {index} warhead_discarded previous must identify a card",
        )


def validate_previous_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"previous"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    if payload["previous"] is not None and not isinstance(payload["previous"], str):
        raise ValueError(
            f"Replay event {index} {event_type} previous must be a string or null"
        )
    if payload["previous"] is not None:
        validate_card_id(
            payload["previous"],
            f"Replay event {index} {event_type} previous must identify a card",
        )


__all__ = [
    "validate_card_event_payload_shape",
    "validate_previous_payload",
    "validate_warhead_discarded_payload",
    "validate_warhead_loaded_payload",
]
