"""Postal cruise missile legal action helpers."""

from __future__ import annotations

from typing import Any

from .action_models import ActionType, LegalAction, build_action
from .actions_postal_cruise_launch import (
    apply_cruise_launch_action,
    cruise_launch_actions,
)
from .engine.events import EngineEvent
from .state import GameState


def cruise_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = cruise_launch_actions(state, player_id)
    missiles = state.players[player_id].pending_orders.get("cruise_missiles", {})
    if not isinstance(missiles, dict):
        return actions
    for missile_id, missile in missiles.items():
        if not isinstance(missile, dict):
            continue
        actions.extend(_missile_actions(state, player_id, str(missile_id), missile))
    return actions


def apply_cruise_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    if action.action_type is ActionType.POSTAL_CRUISE_LAUNCH:
        return apply_cruise_launch_action(state, action)
    if action.action_type is ActionType.POSTAL_CRUISE_DROP:
        return _queue_drop(state, action)
    if action.action_type is ActionType.POSTAL_CRUISE_MOVE:
        return _queue_move(state, action)
    return []


def _missile_actions(
    state: GameState, player_id: str, missile_id: str, missile: dict[str, Any]
) -> list[LegalAction]:
    if missile.get("drop_next_turn"):
        # A return-to-sender missile force-drops on its owner; nothing to order.
        return []
    actions = [
        build_action(
            player_id,
            ActionType.POSTAL_CRUISE_DROP,
            f"Drop cruise missile {missile_id}",
            {"missile": missile_id},
        )
    ]
    visited = set(missile.get("visited", []))
    for target_id, target in state.players.items():
        if target_id == player_id or not target.alive or target_id in visited:
            continue
        actions.append(
            build_action(
                player_id,
                ActionType.POSTAL_CRUISE_MOVE,
                f"Move cruise missile {missile_id} to {target_id}",
                {"missile": missile_id, "target": target_id},
            )
        )
    return actions


def _queue_drop(state: GameState, action: LegalAction) -> list[EngineEvent]:
    missile_id = str(action.payload["missile"])
    state.players[action.player_id].pending_orders.setdefault("cruise_drop", []).append(
        missile_id
    )
    return [EngineEvent("postal_cruise_drop_ordered", action.player_id, missile_id)]


def _queue_move(state: GameState, action: LegalAction) -> list[EngineEvent]:
    missile_id = str(action.payload["missile"])
    target_id = str(action.payload["target"])
    state.players[action.player_id].pending_orders.setdefault("cruise_move", []).append(
        {"missile": missile_id, "target": target_id}
    )
    return [
        EngineEvent(
            "postal_cruise_move_ordered",
            action.player_id,
            missile_id,
            {"target": target_id},
        )
    ]


__all__ = ["apply_cruise_action", "cruise_legal_actions"]
