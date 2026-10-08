"""Action model helpers shared by engine adapters."""

from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ActionType(StrEnum):
    PASS = "pass"
    DRAW = "draw"
    ENQUEUE = "enqueue"
    SETUP_PLACE = "setup_place"
    STRATEGY_REPLACE = "strategy_replace"
    ADVANCE = "advance"
    TARGET = "target"
    RESOLVE = "resolve"
    FINAL_STRIKE_TARGET = "final_strike_target"
    SECRET_TARGET = "secret_target"
    PROPAGANDA_TARGET = "propaganda_target"
    INTERCEPT = "intercept"
    MODIFY_DETERRENT = "modify_deterrent"
    POSTAL_PROPAGANDA = "postal_propaganda"
    POSTAL_VOTE_PEACE = "postal_vote_peace"
    POSTAL_SECRET_TARGET = "postal_secret_target"
    POSTAL_STEAL_SECRET = "postal_steal_secret"
    POSTAL_SABOTAGE = "postal_sabotage"
    POSTAL_DEFENSE = "postal_defense"
    POSTAL_CRUISE_LAUNCH = "postal_cruise_launch"
    POSTAL_CRUISE_DROP = "postal_cruise_drop"
    POSTAL_CRUISE_MOVE = "postal_cruise_move"
    POSTAL_SUBMARINE_LAUNCH = "postal_submarine_launch"
    POSTAL_SUBMARINE_RELOAD = "postal_submarine_reload"
    POSTAL_SUBMARINE_FIRE = "postal_submarine_fire"
    POSTAL_SUBMARINE_RETURN = "postal_submarine_return"
    POSTAL_SPACE_PLATFORM_LAUNCH = "postal_space_platform_launch"
    POSTAL_SPACE_PLATFORM_DROP = "postal_space_platform_drop"
    POSTAL_SPACE_SHUTTLE_RELOAD = "postal_space_shuttle_reload"
    POSTAL_SPACE_SHUTTLE_ATTACK = "postal_space_shuttle_attack"
    POSTAL_KILLER_SATELLITE_LAUNCH = "postal_killer_satellite_launch"
    POSTAL_KILLER_SATELLITE_ATTACK = "postal_killer_satellite_attack"
    POSTAL_SUPERVIRUS_START = "postal_supervirus_start"
    POSTAL_SUPERVIRUS_PASS = "postal_supervirus_pass"
    POSTAL_ATOMIC_CANNON_SETUP = "postal_atomic_cannon_setup"
    POSTAL_ATOMIC_CANNON_FIRE = "postal_atomic_cannon_fire"
    POSTAL_ATOMIC_CANNON_REPOSITION = "postal_atomic_cannon_reposition"


@dataclass(frozen=True)
class LegalAction:
    action_id: str
    player_id: str
    action_type: ActionType
    label: str
    payload: dict[str, Any] = field(default_factory=dict)


def build_action(
    player_id: str,
    action_type: ActionType,
    label: str,
    payload: dict[str, Any] | None = None,
) -> LegalAction:
    payload = deepcopy(payload) if payload else {}
    return LegalAction(
        action_id=f"{player_id}:{action_type.value}{payload_suffix(payload)}",
        player_id=player_id,
        action_type=action_type,
        label=label,
        payload=payload,
    )


def payload_suffix(payload: dict[str, Any]) -> str:
    if not payload:
        return ""
    encoded = json.dumps(
        payload,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return f":{encoded}"


def dedupe_actions(actions: list[LegalAction]) -> list[LegalAction]:
    seen: set[str] = set()
    result: list[LegalAction] = []
    for action in actions:
        if action.action_id in seen:
            continue
        seen.add(action.action_id)
        result.append(action)
    return result


__all__ = [
    "ActionType",
    "LegalAction",
    "build_action",
    "dedupe_actions",
    "payload_suffix",
]
