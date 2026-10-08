"""Replay event entry validation helpers."""

from __future__ import annotations

from typing import Any

from .event_types import KNOWN_EVENT_TYPES
from .fallout import (
    RADIOACTIVE_FALLOUT_DIE_TABLE_ID,
    SpinnerEffect,
    is_fallout_cloud,
    resolve_spinner,
)
from .integer_validation import is_strict_int
from .press import PRESS_DEFERRED_MESSAGE
from .replay_event_identity_validation import validate_event_identity
from .replay_event_payload_shapes import validate_event_payload_shape
from .replay_phase_event_validation import validate_phase_complete_event
from .variants import ACTIVE_VARIANT

SPINNER_PAYLOAD_FIELDS = (
    "raw_result",
    "effect",
    "multiplier",
    "target_adjustment",
    "randomizer",
    "source_table_id",
)
FALLOUT_DIE_PAYLOAD_FIELDS = (
    "raw_result",
    "cloud",
    "randomizer",
    "source_table_id",
)
POSTAL_ONLY_EVENT_PREFIXES = (
    "atomic_cannon_",
    "cruise_",
    "killer_satellite_",
    "space_platform_",
    "space_shuttle_",
    "submarine_",
    "supervirus_",
)
POSTAL_ONLY_EVENT_TYPES = {"fallout_die_result", "phase_complete"}


def validate_event_shapes(event: dict[str, Any], index: int, mode: str) -> None:
    if event["player_id"] is not None and not isinstance(event["player_id"], str):
        raise ValueError(f"Replay event {index} player_id must be a string or null")
    if event["card_id"] is not None and not isinstance(event["card_id"], str):
        raise ValueError(f"Replay event {index} card_id must be a string or null")
    if not isinstance(event["event_type"], str):
        raise ValueError(f"Replay event {index} event_type must be a string")
    if event["event_type"] not in KNOWN_EVENT_TYPES:
        raise ValueError(
            f"Replay event {index} event_type has invalid value: {event['event_type']}"
        )
    _validate_event_mode(event["event_type"], index, mode)
    if event["event_type"] == "press_entry":
        raise ValueError(PRESS_DEFERRED_MESSAGE)
    if not isinstance(event["payload"], dict):
        raise ValueError(f"Replay event {index} payload must be an object")
    if event["event_type"] == "phase_complete":
        validate_phase_complete_event(event, index)
    validate_event_identity(event, index)
    if event["event_type"] == "spinner_result":
        _validate_spinner_payload(event["payload"], index)
    if event["event_type"] == "fallout_die_result":
        _validate_fallout_die_payload(event["payload"], index)
    validate_event_payload_shape(event["event_type"], event["payload"], index)


def _validate_event_mode(event_type: str, index: int, mode: str) -> None:
    if mode == "table" and (
        event_type.startswith("postal_")
        or event_type.startswith(POSTAL_ONLY_EVENT_PREFIXES)
        or event_type in POSTAL_ONLY_EVENT_TYPES
    ):
        raise ValueError(f"Replay event {index} event_type requires postal mode")


def _validate_spinner_payload(payload: dict[str, Any], index: int) -> None:
    for field in SPINNER_PAYLOAD_FIELDS:
        if field not in payload:
            raise ValueError(f"Replay event {index} spinner payload missing {field}")
    if set(payload) != set(SPINNER_PAYLOAD_FIELDS):
        raise ValueError(f"Replay event {index} spinner payload fields are invalid")
    if not is_strict_int(payload["raw_result"]):
        raise ValueError(f"Replay event {index} spinner raw_result must be an integer")
    if not 0 <= payload["raw_result"] <= 99:
        raise ValueError(
            f"Replay event {index} spinner raw_result must be between 0 and 99"
        )
    if not isinstance(payload["effect"], str):
        raise ValueError(f"Replay event {index} spinner effect must be a string")
    if payload["effect"] not in {item.value for item in SpinnerEffect}:
        raise ValueError(
            f"Replay event {index} spinner effect has invalid value: "
            f"{payload['effect']}"
        )
    if not is_strict_int(payload["multiplier"]):
        raise ValueError(f"Replay event {index} spinner multiplier must be an integer")
    if not is_strict_int(payload["target_adjustment"]):
        raise ValueError(
            f"Replay event {index} spinner target_adjustment must be an integer"
        )
    if not isinstance(payload["randomizer"], str):
        raise ValueError(f"Replay event {index} spinner randomizer must be a string")
    if payload["randomizer"] != ACTIVE_VARIANT.randomizer:
        raise ValueError(
            f"Replay event {index} spinner randomizer has invalid value: "
            f"{payload['randomizer']}"
        )
    if not isinstance(payload["source_table_id"], str):
        raise ValueError(
            f"Replay event {index} spinner source_table_id must be a string"
        )
    if payload["source_table_id"] != ACTIVE_VARIANT.randomizer:
        raise ValueError(
            f"Replay event {index} spinner source_table_id has invalid value: "
            f"{payload['source_table_id']}"
        )
    _validate_spinner_outcome(payload, index)


def _validate_fallout_die_payload(payload: dict[str, Any], index: int) -> None:
    if set(payload) != set(FALLOUT_DIE_PAYLOAD_FIELDS):
        raise ValueError(f"Replay event {index} fallout_die payload fields are invalid")
    if not is_strict_int(payload["raw_result"]):
        raise ValueError(
            f"Replay event {index} fallout_die raw_result must be an integer"
        )
    if not 1 <= payload["raw_result"] <= 6:
        raise ValueError(
            f"Replay event {index} fallout_die raw_result must be between 1 and 6"
        )
    if not isinstance(payload["cloud"], bool):
        raise ValueError(f"Replay event {index} fallout_die cloud must be a boolean")
    if payload["cloud"] != is_fallout_cloud(payload["raw_result"]):
        raise ValueError(
            f"Replay event {index} fallout_die cloud does not match raw_result"
        )
    if not isinstance(payload["randomizer"], str):
        raise ValueError(
            f"Replay event {index} fallout_die randomizer must be a string"
        )
    if payload["randomizer"] != RADIOACTIVE_FALLOUT_DIE_TABLE_ID:
        raise ValueError(
            f"Replay event {index} fallout_die randomizer has invalid value: "
            f"{payload['randomizer']}"
        )
    if not isinstance(payload["source_table_id"], str):
        raise ValueError(
            f"Replay event {index} fallout_die source_table_id must be a string"
        )
    if payload["source_table_id"] != RADIOACTIVE_FALLOUT_DIE_TABLE_ID:
        raise ValueError(
            f"Replay event {index} fallout_die source_table_id has invalid value: "
            f"{payload['source_table_id']}"
        )


def _validate_spinner_outcome(payload: dict[str, Any], index: int) -> None:
    outcome = resolve_spinner(payload["raw_result"])
    if payload["effect"] != outcome.effect.value:
        raise ValueError(
            f"Replay event {index} spinner effect does not match raw_result"
        )
    if payload["multiplier"] != outcome.yield_multiplier:
        raise ValueError(
            f"Replay event {index} spinner multiplier does not match raw_result"
        )
    if payload["target_adjustment"] != outcome.target_delta:
        raise ValueError(
            f"Replay event {index} spinner target_adjustment does not match raw_result"
        )


__all__ = [
    "SPINNER_PAYLOAD_FIELDS",
    "FALLOUT_DIE_PAYLOAD_FIELDS",
    "validate_event_shapes",
]
