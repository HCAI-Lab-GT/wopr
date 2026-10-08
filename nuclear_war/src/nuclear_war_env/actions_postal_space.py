"""Postal space equipment legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .actions_postal_space_setup import (
    SPACE_SETUP_TYPES,
    apply_space_setup_action,
    space_setup_actions,
)
from .engine.events import EngineEvent
from .state import GameState


def space_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = space_setup_actions(state, player_id)
    actions.extend(_platform_drop_actions(state, player_id))
    actions.extend(_killer_satellite_actions(state, player_id))
    return actions


def apply_space_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    if action.action_type in SPACE_SETUP_TYPES:
        return apply_space_setup_action(state, action)
    if action.action_type is ActionType.POSTAL_SPACE_PLATFORM_DROP:
        return _queue_platform_drop(state, action)
    if action.action_type is ActionType.POSTAL_KILLER_SATELLITE_ATTACK:
        return _queue_killer_satellite_attack(state, action)
    return []


def _platform_drop_actions(state: GameState, player_id: str) -> list[LegalAction]:
    platforms = state.players[player_id].pending_orders.get("space_platforms", {})
    if not isinstance(platforms, dict):
        return []
    actions: list[LegalAction] = []
    for platform_id, platform in platforms.items():
        if not isinstance(platform, dict) or not platform.get("warheads"):
            continue
        for target_id, target in state.players.items():
            if target_id == player_id or not target.alive:
                continue
            actions.append(
                build_action(
                    player_id,
                    ActionType.POSTAL_SPACE_PLATFORM_DROP,
                    f"Drop from space platform {platform_id}",
                    {"platform": str(platform_id), "target": target_id},
                )
            )
    return actions


def _killer_satellite_actions(state: GameState, player_id: str) -> list[LegalAction]:
    satellites = state.players[player_id].pending_orders.get("killer_satellites", {})
    if not isinstance(satellites, dict):
        return []
    actions: list[LegalAction] = []
    for satellite_id, satellite in satellites.items():
        if not isinstance(satellite, dict) or satellite.get("status") != "orbit":
            continue
        actions.extend(_target_platform_actions(state, player_id, str(satellite_id)))
    return actions


def _target_platform_actions(
    state: GameState, player_id: str, satellite_id: str
) -> list[LegalAction]:
    actions: list[LegalAction] = []
    for target_id, target in state.players.items():
        platforms = target.pending_orders.get("space_platforms", {})
        if (
            target_id == player_id
            or not target.alive
            or not isinstance(platforms, dict)
        ):
            continue
        for platform_id in platforms:
            actions.append(
                build_action(
                    player_id,
                    ActionType.POSTAL_KILLER_SATELLITE_ATTACK,
                    f"Attack space platform {platform_id}",
                    {
                        "satellite": satellite_id,
                        "target_player": target_id,
                        "platform": str(platform_id),
                    },
                )
            )
    return actions


def _queue_platform_drop(state: GameState, action: LegalAction) -> list[EngineEvent]:
    platform_id = str(action.payload["platform"])
    target_id = str(action.payload["target"])
    state.players[action.player_id].pending_orders.setdefault(
        "space_platform_drop", []
    ).append({"platform": platform_id, "target": target_id})
    return [
        EngineEvent(
            "postal_space_platform_drop_ordered",
            action.player_id,
            platform_id,
            {"target": target_id},
        )
    ]


def _queue_killer_satellite_attack(
    state: GameState, action: LegalAction
) -> list[EngineEvent]:
    satellite_id = str(action.payload["satellite"])
    target_id = str(action.payload["target_player"])
    platform_id = str(action.payload["platform"])
    state.players[action.player_id].pending_orders.setdefault(
        "killer_satellite_attack", []
    ).append(
        {
            "satellite": satellite_id,
            "target_player": target_id,
            "platform": platform_id,
        }
    )
    return [
        EngineEvent(
            "postal_killer_satellite_attack_ordered",
            action.player_id,
            satellite_id,
            {"target_player": target_id, "platform": platform_id},
        )
    ]


__all__ = ["apply_space_action", "space_legal_actions"]
