"""Replay delivery event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int
from .replay_card_identity import validate_card_id


def validate_delivery_ready_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"capacity", "previous"}:
        raise ValueError(
            f"Replay event {index} delivery_ready payload fields are invalid"
        )
    if not is_strict_int(payload["capacity"]):
        raise ValueError(
            f"Replay event {index} delivery_ready capacity must be an integer"
        )
    if payload["previous"] is not None and not isinstance(payload["previous"], str):
        raise ValueError(
            f"Replay event {index} delivery_ready previous must be a string or null"
        )
    if payload["previous"] is not None:
        validate_card_id(
            payload["previous"],
            f"Replay event {index} delivery_ready previous must identify a card",
        )


__all__ = ["validate_delivery_ready_payload"]
