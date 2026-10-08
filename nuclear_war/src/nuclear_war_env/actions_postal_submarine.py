"""Postal submarine legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .actions_postal_submarine_setup import (
    apply_submarine_setup_action,
    submarine_setup_actions,
)
from .engine.events import EngineEvent
from .state import GameState


def submarine_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = submarine_setup_actions(state, player_id)
    submarines = state.players[player_id].pending_orders.get("submarine_states", {})
    if not isinstance(submarines, dict):
        return actions
    for submarine_id, submarine in submarines.items():
        if not isinstance(submarine, dict) or submarine.get("status") != "at_sea":
            continue
        actions.extend(_at_sea_actions(player_id, str(submarine_id)))
    return actions


def apply_submarine_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    if action.action_type in {
        ActionType.POSTAL_SUBMARINE_LAUNCH,
        ActionType.POSTAL_SUBMARINE_RELOAD,
    }:
        return apply_submarine_setup_action(state, action)
    if action.action_type is ActionType.POSTAL_SUBMARINE_FIRE:
        return _queue_order(state, action, "fire", "postal_submarine_fire_ordered")
    if action.action_type is ActionType.POSTAL_SUBMARINE_RETURN:
        return _queue_order(
            state,
            action,
            "return_to_port",
            "postal_submarine_return_ordered",
        )
    return []


def _at_sea_actions(player_id: str, submarine_id: str) -> list[LegalAction]:
    payload = {"submarine": submarine_id}
    return [
        build_action(
            player_id,
            ActionType.POSTAL_SUBMARINE_FIRE,
            f"Fire submarine {submarine_id}",
            payload,
        ),
        build_action(
            player_id,
            ActionType.POSTAL_SUBMARINE_RETURN,
            f"Return submarine {submarine_id}",
            payload,
        ),
    ]


def _queue_order(
    state: GameState, action: LegalAction, order: str, event_type: str
) -> list[EngineEvent]:
    submarine_id = str(action.payload["submarine"])
    state.players[action.player_id].pending_orders.setdefault("submarines", []).append(
        {"submarine": submarine_id, "action": order}
    )
    return [EngineEvent(event_type, action.player_id, submarine_id)]


__all__ = ["apply_submarine_action", "submarine_legal_actions"]
