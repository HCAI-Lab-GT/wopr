"""Replay action payload shape validators."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id, validate_card_id_list
from .state import DETERRENT_SLOTS, FACE_DOWN_SLOTS

TARGET_PAYLOAD_FIELDS = {"delivery", "target"}
FINAL_STRIKE_TARGET_PAYLOAD_FIELDS = {"target"}
ENQUEUE_PAYLOAD_FIELDS = {"cards"}
CARD_TARGET_PAYLOAD_FIELDS = {"card", "target"}
ONE_TARGET_PAYLOAD_FIELDS = {"target"}
MODIFY_DETERRENT_TO_SLOT_FIELDS = {"card", "to_slot"}
MODIFY_DETERRENT_FROM_SLOT_FIELDS = {"from_slot"}


def validate_target_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != TARGET_PAYLOAD_FIELDS:
        raise ValueError(f"Replay action {index} target payload fields are invalid")
    _validate_string_fields(payload, index, "target", ("delivery", "target"))
    _validate_card_field(payload, index, "target", "delivery")


def validate_final_strike_target_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != FINAL_STRIKE_TARGET_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} final_strike_target payload fields are invalid"
        )
    _validate_string_fields(payload, index, "final_strike_target", ("target",))


def validate_enqueue_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != ENQUEUE_PAYLOAD_FIELDS:
        raise ValueError(f"Replay action {index} enqueue payload fields are invalid")
    cards = payload["cards"]
    if not isinstance(cards, list):
        raise ValueError(f"Replay action {index} enqueue cards must be a list")
    if not all(isinstance(card_id, str) for card_id in cards):
        raise ValueError(f"Replay action {index} enqueue cards must be strings")
    validate_card_id_list(
        cards, f"Replay action {index} enqueue cards must identify cards"
    )


def validate_setup_place_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != ENQUEUE_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} setup_place payload fields are invalid"
        )
    cards = payload["cards"]
    if not isinstance(cards, list) or len(cards) != 1:
        raise ValueError(
            f"Replay action {index} setup_place cards must be a one-card list"
        )
    if not all(isinstance(card_id, str) for card_id in cards):
        raise ValueError(f"Replay action {index} setup_place cards must be strings")
    validate_card_id_list(
        cards, f"Replay action {index} setup_place cards must identify cards"
    )


def validate_strategy_replace_payload(payload: dict[str, Any], index: int) -> None:
    # A decline is an empty payload; a replacement is {"card": ..., "slot": int}.
    if not payload:
        return
    if set(payload) != {"card", "slot"}:
        raise ValueError(
            f"Replay action {index} strategy_replace payload fields are invalid"
        )
    _validate_string_fields(payload, index, "strategy_replace", ("card",))
    _validate_card_field(payload, index, "strategy_replace", "card")
    slot = payload["slot"]
    if type(slot) is not int:
        raise ValueError(f"Replay action {index} strategy_replace slot must be an int")
    if slot < 0 or slot >= FACE_DOWN_SLOTS:
        raise ValueError(f"Replay action {index} strategy_replace slot is out of range")


def validate_postal_propaganda_payload(payload: dict[str, Any], index: int) -> None:
    validate_card_target_payload(payload, index, "postal_propaganda")


def validate_card_target_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != CARD_TARGET_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("card", "target"))
    _validate_card_field(payload, index, action_type, "card")


def validate_one_target_payload(
    payload: dict[str, Any], index: int, action_type: str
) -> None:
    if set(payload) != ONE_TARGET_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} {action_type} payload fields are invalid"
        )
    _validate_string_fields(payload, index, action_type, ("target",))


def validate_intercept_payload(payload: dict[str, Any], index: int) -> None:
    # A decline is an empty payload; a play is {"card": <antimissile card id>}.
    if not payload:
        return
    if set(payload) != {"card"}:
        raise ValueError(f"Replay action {index} intercept payload fields are invalid")
    _validate_string_fields(payload, index, "intercept", ("card",))
    _validate_card_field(payload, index, "intercept", "card")


def validate_modify_deterrent_payload(payload: dict[str, Any], index: int) -> None:
    if not payload:
        return
    fields = set(payload)
    if fields == MODIFY_DETERRENT_TO_SLOT_FIELDS:
        _validate_string_fields(payload, index, "modify_deterrent", ("card",))
        _validate_card_field(payload, index, "modify_deterrent", "card")
        _validate_slot(payload["to_slot"], index, "to_slot")
        return
    if fields == MODIFY_DETERRENT_FROM_SLOT_FIELDS:
        _validate_slot(payload["from_slot"], index, "from_slot")
        return
    raise ValueError(
        f"Replay action {index} modify_deterrent payload fields are invalid"
    )


def _validate_slot(value: object, index: int, field: str) -> None:
    if type(value) is not int:
        raise ValueError(
            f"Replay action {index} modify_deterrent {field} must be an int"
        )
    if value < 0 or value >= DETERRENT_SLOTS:
        raise ValueError(
            f"Replay action {index} modify_deterrent {field} is out of range"
        )


def _validate_card_field(
    payload: dict[str, Any], index: int, action_type: str, field: str
) -> None:
    _validate_identifier(payload, index, action_type, field, "card")


def _validate_identifier(
    payload: dict[str, Any], index: int, action_type: str, field: str, label: str
) -> None:
    validate_card_id(
        payload[field],
        f"Replay action {index} {action_type} {field} must identify a {label}",
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
    "validate_card_target_payload",
    "validate_enqueue_payload",
    "validate_final_strike_target_payload",
    "validate_intercept_payload",
    "validate_modify_deterrent_payload",
    "validate_one_target_payload",
    "validate_postal_propaganda_payload",
    "validate_setup_place_payload",
    "validate_strategy_replace_payload",
    "validate_target_payload",
]
