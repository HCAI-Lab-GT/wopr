"""Replay event payload shape validators."""

from __future__ import annotations

from typing import Any

from .integer_validation import is_strict_int
from .replay_atomic_event_payload_shapes import validate_atomic_event_payload_shape
from .replay_card_event_payload_shapes import validate_card_event_payload_shape
from .replay_card_identity import validate_card_id_list
from .replay_cruise_event_payload_shapes import validate_cruise_event_payload_shape
from .replay_delivery_event_payload_shapes import validate_delivery_ready_payload
from .replay_equipment_event_payload_shapes import (
    validate_equipment_event_payload_shape,
)
from .replay_launch_event_payload_shapes import validate_launch_event_payload_shape
from .replay_propaganda_event_payload_shapes import (
    validate_propaganda_event_payload_shape,
)
from .replay_sabotage_event_payload_shapes import validate_sabotage_event_payload_shape
from .replay_satellite_event_payload_shapes import (
    validate_satellite_event_payload_shape,
)
from .replay_secret_event_payload_shapes import validate_secret_event_payload_shape
from .replay_space_event_payload_shapes import validate_space_event_payload_shape
from .replay_submarine_event_payload_shapes import (
    validate_submarine_event_payload_shape,
)
from .replay_supervirus_event_payload_shapes import (
    validate_supervirus_event_payload_shape,
)

EMPTY_PAYLOAD_EVENT_TYPES = {
    "action_passed",
    "card_drawn",
    "final_strike_executed",
    "peace_restored",
    "postal_defense_ordered",
    "postal_peace_voted",
    "secret_queued",
    "special_played",
    "turn_skipped",
}
EVENT_PAYLOAD_SHAPE_VALIDATORS = (
    validate_atomic_event_payload_shape,
    validate_launch_event_payload_shape,
    validate_equipment_event_payload_shape,
    validate_cruise_event_payload_shape,
    validate_submarine_event_payload_shape,
    validate_satellite_event_payload_shape,
    validate_space_event_payload_shape,
    validate_supervirus_event_payload_shape,
    validate_secret_event_payload_shape,
    validate_sabotage_event_payload_shape,
    validate_propaganda_event_payload_shape,
)


def validate_event_payload_shape(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    for validator in EVENT_PAYLOAD_SHAPE_VALIDATORS:
        if validator(event_type, payload, index):
            return
    if event_type == "delivery_ready":
        validate_delivery_ready_payload(payload, index)
    if validate_card_event_payload_shape(event_type, payload, index):
        return
    if event_type == "warhead_detonated":
        validate_warhead_detonated_payload(payload, index)
    if event_type == "player_eliminated":
        _validate_player_eliminated_payload(payload, index)
    if event_type == "launch_backfire":
        _validate_launch_backfire_payload(payload, index)
    if event_type in {"cards_enqueued", "queue_updated"}:
        _validate_cards_payload(event_type, payload, index)
    if event_type in EMPTY_PAYLOAD_EVENT_TYPES:
        _validate_empty_payload(event_type, payload, index)


def validate_warhead_detonated_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"target", "yield", "loss"}:
        raise ValueError(
            f"Replay event {index} warhead_detonated payload fields are invalid"
        )
    if not isinstance(payload["target"], str):
        raise ValueError(
            f"Replay event {index} warhead_detonated target must be a string"
        )
    if not is_strict_int(payload["yield"]):
        raise ValueError(
            f"Replay event {index} warhead_detonated yield must be an integer"
        )
    if not is_strict_int(payload["loss"]):
        raise ValueError(
            f"Replay event {index} warhead_detonated loss must be an integer"
        )


def _validate_player_eliminated_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"by"}:
        raise ValueError(
            f"Replay event {index} player_eliminated payload fields are invalid"
        )
    if not isinstance(payload["by"], str):
        raise ValueError(f"Replay event {index} player_eliminated by must be a string")


def _validate_launch_backfire_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != {"loss"}:
        raise ValueError(
            f"Replay event {index} launch_backfire payload fields are invalid"
        )
    if not is_strict_int(payload["loss"]):
        raise ValueError(
            f"Replay event {index} launch_backfire loss must be an integer"
        )


def _validate_cards_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if set(payload) != {"cards"}:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )
    cards = payload["cards"]
    if not isinstance(cards, list):
        raise ValueError(f"Replay event {index} {event_type} cards must be a list")
    if not all(isinstance(item, str) for item in cards):
        raise ValueError(
            f"Replay event {index} {event_type} cards must contain strings"
        )
    validate_card_id_list(
        cards, f"Replay event {index} {event_type} cards must identify cards"
    )


def _validate_empty_payload(
    event_type: str, payload: dict[str, Any], index: int
) -> None:
    if payload:
        raise ValueError(
            f"Replay event {index} {event_type} payload fields are invalid"
        )


__all__ = ["validate_event_payload_shape"]
