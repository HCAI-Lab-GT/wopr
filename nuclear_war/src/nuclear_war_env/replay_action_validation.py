"""Replay action entry validation helpers."""

from __future__ import annotations

from typing import Any

from .action_models import ActionType, payload_suffix
from .replay_action_payload_validation import validate_action_payload
from .result_player_ids import validate_player_reference

POSTAL_ACTION_TYPES = {
    action_type.value
    for action_type in ActionType
    if action_type.value.startswith("postal_")
}

# Table-only decisions the postal engine can never produce: the opening
# commitment auto-commits in postal setup, and the peace-restoration window is
# opened only by the table decision loop. Reject them in postal replays so a
# corrupted log cannot pass validation as if the action were legal.
TABLE_ONLY_ACTION_TYPES = {
    ActionType.SETUP_PLACE.value,
    ActionType.STRATEGY_REPLACE.value,
}


def validate_action_shapes(action: dict[str, Any], index: int, mode: str) -> None:
    if not isinstance(action["player_id"], str):
        raise ValueError(f"Replay action {index} player_id must be a string")
    if not isinstance(action["action_id"], str):
        raise ValueError(f"Replay action {index} action_id must be a string")
    if not isinstance(action["action_type"], str):
        raise ValueError(f"Replay action {index} action_type must be a string")
    _validate_action_type_value(action["action_type"], index)
    _validate_action_mode(action["action_type"], index, mode)
    if not isinstance(action["payload"], dict):
        raise ValueError(f"Replay action {index} payload must be an object")
    validate_action_payload(action, index)


def _validate_action_type_value(action_type: str, index: int) -> None:
    valid_action_types = {item.value for item in ActionType}
    if action_type not in valid_action_types:
        raise ValueError(
            f"Replay action {index} action_type has invalid value: {action_type}"
        )


def _validate_action_mode(action_type: str, index: int, mode: str) -> None:
    if mode == "table" and action_type in POSTAL_ACTION_TYPES:
        raise ValueError(f"Replay action {index} action_type requires postal mode")
    if mode == "postal" and action_type in TABLE_ONLY_ACTION_TYPES:
        raise ValueError(f"Replay action {index} action_type requires table mode")


ACTION_PLAYER_REFERENCE_FIELDS = {
    ActionType.TARGET.value: ("target",),
    ActionType.FINAL_STRIKE_TARGET.value: ("target",),
    ActionType.SECRET_TARGET.value: ("target",),
    ActionType.PROPAGANDA_TARGET.value: ("target",),
    ActionType.POSTAL_PROPAGANDA.value: ("target",),
    ActionType.POSTAL_SECRET_TARGET.value: ("target",),
    ActionType.POSTAL_STEAL_SECRET.value: ("target",),
    ActionType.POSTAL_SABOTAGE.value: ("target",),
    ActionType.POSTAL_DEFENSE.value: ("attacker",),
    ActionType.POSTAL_CRUISE_LAUNCH.value: ("target",),
    ActionType.POSTAL_CRUISE_MOVE.value: ("target",),
    ActionType.POSTAL_SUBMARINE_LAUNCH.value: ("target",),
    ActionType.POSTAL_SUBMARINE_RELOAD.value: ("target",),
    ActionType.POSTAL_SPACE_PLATFORM_DROP.value: ("target",),
    ActionType.POSTAL_SPACE_SHUTTLE_ATTACK.value: ("target",),
    ActionType.POSTAL_KILLER_SATELLITE_ATTACK.value: ("target_player",),
    ActionType.POSTAL_SUPERVIRUS_START.value: ("target",),
    ActionType.POSTAL_SUPERVIRUS_PASS.value: ("target",),
    ActionType.POSTAL_ATOMIC_CANNON_SETUP.value: ("target",),
    ActionType.POSTAL_ATOMIC_CANNON_REPOSITION.value: ("target",),
}


def validate_action_identity(
    action: dict[str, Any], index: int, player_ids: set[str]
) -> None:
    parts = action["action_id"].split(":", 2)
    if len(parts) < 2:
        raise ValueError(f"Replay action {index} action_id must include action type")
    if parts[0] != action["player_id"]:
        raise ValueError(f"Replay action {index} action_id player must match player_id")
    if parts[1] != action["action_type"]:
        raise ValueError(f"Replay action {index} action_id type must match action_type")
    expected = _expected_action_id(action)
    if action["action_id"] != expected:
        raise ValueError(f"Replay action {index} action_id payload must match payload")
    _validate_payload_player_references(action, index, player_ids)


def _expected_action_id(action: dict[str, Any]) -> str:
    return (
        f"{action['player_id']}:{action['action_type']}"
        f"{payload_suffix(action['payload'])}"
    )


def _validate_payload_player_references(
    action: dict[str, Any], index: int, player_ids: set[str]
) -> None:
    action_type = str(action["action_type"])
    fields = ACTION_PLAYER_REFERENCE_FIELDS.get(action_type, ())
    for field in fields:
        if field not in action["payload"]:
            # Some payload shapes carry the reference only in their legacy
            # form (postal_defense conditional orders omit "attacker"); the
            # shape validators decide which field sets are legal.
            continue
        if action["payload"][field] == action["player_id"]:
            raise ValueError(
                f"Replay action {index} {action_type} {field} "
                "must not be the acting player"
            )
        validate_player_reference(
            action["payload"][field],
            player_ids,
            f"Replay action {index} {action_type} {field}",
        )


__all__ = [
    "POSTAL_ACTION_TYPES",
    "TABLE_ONLY_ACTION_TYPES",
    "ACTION_PLAYER_REFERENCE_FIELDS",
    "validate_action_identity",
    "validate_action_shapes",
]
