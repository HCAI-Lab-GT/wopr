"""Replay action payload validation helpers."""

from __future__ import annotations

from typing import Any

from .action_models import ActionType
from .replay_atomic_payload_shapes import (
    validate_cannon_target_payload,
    validate_cannon_warhead_payload,
)
from .replay_equipment_payload_shapes import (
    validate_card_target_warhead_payload,
    validate_missile_payload,
    validate_missile_target_payload,
    validate_platform_target_payload,
    validate_submarine_payload,
    validate_submarine_target_warhead_payload,
)
from .replay_payload_shapes import (
    validate_card_target_payload,
    validate_enqueue_payload,
    validate_final_strike_target_payload,
    validate_intercept_payload,
    validate_modify_deterrent_payload,
    validate_one_target_payload,
    validate_postal_propaganda_payload,
    validate_setup_place_payload,
    validate_strategy_replace_payload,
    validate_target_payload,
)
from .replay_postal_action_payload_shapes import (
    validate_postal_defense_payload,
    validate_postal_sabotage_payload,
    validate_postal_secret_target_payload,
)
from .replay_satellite_payload_shapes import (
    validate_card_payload,
    validate_satellite_attack_payload,
)
from .replay_space_equipment_payload_shapes import (
    validate_card_platform_warheads_payload,
    validate_card_warheads_payload,
)

EMPTY_PAYLOAD_ACTION_TYPES = {
    ActionType.PASS.value,
    ActionType.DRAW.value,
    ActionType.ADVANCE.value,
    ActionType.RESOLVE.value,
    ActionType.POSTAL_VOTE_PEACE.value,
}


def validate_action_payload(action: dict[str, Any], index: int) -> None:
    action_type = action["action_type"]
    if action_type in EMPTY_PAYLOAD_ACTION_TYPES and action["payload"]:
        raise ValueError(f"Replay action {index} {action_type} payload must be empty")
    if action_type == ActionType.ENQUEUE.value:
        validate_enqueue_payload(action["payload"], index)
    if action_type == ActionType.SETUP_PLACE.value:
        validate_setup_place_payload(action["payload"], index)
    if action_type == ActionType.STRATEGY_REPLACE.value:
        validate_strategy_replace_payload(action["payload"], index)
    if action_type == ActionType.TARGET.value:
        validate_target_payload(action["payload"], index)
    if action_type == ActionType.FINAL_STRIKE_TARGET.value:
        validate_final_strike_target_payload(action["payload"], index)
    if action_type == ActionType.SECRET_TARGET.value:
        validate_card_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.PROPAGANDA_TARGET.value:
        validate_card_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.INTERCEPT.value:
        validate_intercept_payload(action["payload"], index)
    if action_type == ActionType.MODIFY_DETERRENT.value:
        validate_modify_deterrent_payload(action["payload"], index)
    if action_type == ActionType.POSTAL_PROPAGANDA.value:
        validate_postal_propaganda_payload(action["payload"], index)
    if action_type == ActionType.POSTAL_SECRET_TARGET.value:
        validate_postal_secret_target_payload(action["payload"], index)
    if action_type == ActionType.POSTAL_STEAL_SECRET.value:
        validate_one_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SUPERVIRUS_PASS.value:
        validate_one_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SUPERVIRUS_START.value:
        validate_card_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_ATOMIC_CANNON_SETUP.value:
        validate_card_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_ATOMIC_CANNON_FIRE.value:
        validate_cannon_warhead_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_ATOMIC_CANNON_REPOSITION.value:
        validate_cannon_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_CRUISE_LAUNCH.value:
        validate_card_target_warhead_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SUBMARINE_LAUNCH.value:
        validate_card_target_warhead_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SPACE_SHUTTLE_ATTACK.value:
        validate_card_target_warhead_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SPACE_PLATFORM_LAUNCH.value:
        validate_card_warheads_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SPACE_SHUTTLE_RELOAD.value:
        validate_card_platform_warheads_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SPACE_PLATFORM_DROP.value:
        validate_platform_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_KILLER_SATELLITE_LAUNCH.value:
        validate_card_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_KILLER_SATELLITE_ATTACK.value:
        validate_satellite_attack_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SUBMARINE_RELOAD.value:
        validate_submarine_target_warhead_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SUBMARINE_FIRE.value:
        validate_submarine_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_SUBMARINE_RETURN.value:
        validate_submarine_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_CRUISE_DROP.value:
        validate_missile_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_CRUISE_MOVE.value:
        validate_missile_target_payload(action["payload"], index, action_type)
    if action_type == ActionType.POSTAL_DEFENSE.value:
        validate_postal_defense_payload(action["payload"], index)
    if action_type == ActionType.POSTAL_SABOTAGE.value:
        validate_postal_sabotage_payload(action["payload"], index)


__all__ = [
    "validate_action_payload",
]
