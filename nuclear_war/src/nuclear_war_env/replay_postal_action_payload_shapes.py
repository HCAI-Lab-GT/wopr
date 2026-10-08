"""Replay action payload shape validators for postal actions."""

from __future__ import annotations

from typing import Any

from .replay_card_identity import validate_card_id

POSTAL_SECRET_TARGET_PAYLOAD_FIELDS = {"secret", "target"}
# Conditional orders carry only the committed card; the legacy targeted shape
# stays accepted so pre-repair replays keep validating.
POSTAL_DEFENSE_PAYLOAD_FIELDS = (
    {"card"},
    {"card", "attacker", "delivery"},
)
POSTAL_SABOTAGE_PAYLOAD_FIELDS = (
    {"card", "target", "delivery"},
    {"card", "target", "atomic_cannon"},
    {"card", "target", "satellite"},
    {"card", "target", "shuttle"},
)
POSTAL_SABOTAGE_TARGET_LABELS = {
    "delivery": "card",
    "atomic_cannon": "cannon",
    "satellite": "satellite",
    "shuttle": "shuttle",
}


def validate_postal_secret_target_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != POSTAL_SECRET_TARGET_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} postal_secret_target payload fields are invalid"
        )
    _validate_string_fields(
        payload, index, "postal_secret_target", ("secret", "target")
    )
    _validate_identifier(payload, index, "postal_secret_target", "secret", "card")


def validate_postal_defense_payload(payload: dict[str, Any], index: int) -> None:
    fields = set(payload)
    if fields not in POSTAL_DEFENSE_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} postal_defense payload fields are invalid"
        )
    _validate_string_fields(payload, index, "postal_defense", tuple(sorted(fields)))
    _validate_identifier(payload, index, "postal_defense", "card", "card")
    if "delivery" in payload:
        _validate_identifier(payload, index, "postal_defense", "delivery", "card")


def validate_postal_sabotage_payload(payload: dict[str, Any], index: int) -> None:
    fields = set(payload)
    if fields not in POSTAL_SABOTAGE_PAYLOAD_FIELDS:
        raise ValueError(
            f"Replay action {index} postal_sabotage payload fields are invalid"
        )
    _validate_string_fields(payload, index, "postal_sabotage", tuple(sorted(fields)))
    target_field = next(
        field for field in POSTAL_SABOTAGE_TARGET_LABELS if field in payload
    )
    _validate_identifier(
        payload,
        index,
        "postal_sabotage",
        target_field,
        POSTAL_SABOTAGE_TARGET_LABELS[target_field],
    )
    _validate_identifier(payload, index, "postal_sabotage", "card", "card")


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
    "validate_postal_defense_payload",
    "validate_postal_sabotage_payload",
    "validate_postal_secret_target_payload",
]
