"""Postal secret and espionage legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .engine.events import EngineEvent
from .state import GameState


def secret_legal_actions(state: GameState, player_id: str) -> list[LegalAction]:
    actions = _secret_target_actions(state, player_id)
    actions.extend(_secret_theft_actions(state, player_id))
    return actions


def apply_secret_action(state: GameState, action: LegalAction) -> list[EngineEvent]:
    if action.action_type is ActionType.POSTAL_SECRET_TARGET:
        return _queue_secret_target(state, action)
    if action.action_type is ActionType.POSTAL_STEAL_SECRET:
        return _queue_secret_theft(state, action)
    return []


def _secret_target_actions(state: GameState, player_id: str) -> list[LegalAction]:
    player = state.players[player_id]
    result: list[LegalAction] = []
    for secret_id in player.secrets:
        for target_id, target in state.players.items():
            if target_id == player_id or not target.alive:
                continue
            result.append(
                build_action(
                    player_id,
                    ActionType.POSTAL_SECRET_TARGET,
                    f"Target secret at {target_id}",
                    {"secret": secret_id, "target": target_id},
                )
            )
    return result


def _secret_theft_actions(state: GameState, player_id: str) -> list[LegalAction]:
    result: list[LegalAction] = []
    for target_id, target in state.players.items():
        if target_id == player_id or not target.alive or not target.secrets:
            continue
        result.append(
            build_action(
                player_id,
                ActionType.POSTAL_STEAL_SECRET,
                f"Steal secret from {target_id}",
                {"target": target_id},
            )
        )
    return result


def _queue_secret_target(state: GameState, action: LegalAction) -> list[EngineEvent]:
    secret_id = str(action.payload["secret"])
    target_id = str(action.payload["target"])
    state.players[action.player_id].pending_orders.setdefault("secret_targets", {})[
        secret_id
    ] = target_id
    return [
        EngineEvent(
            "postal_secret_targeted",
            action.player_id,
            secret_id,
            {"target": target_id},
        )
    ]


def _queue_secret_theft(state: GameState, action: LegalAction) -> list[EngineEvent]:
    target_id = str(action.payload["target"])
    state.players[action.player_id].pending_orders["steal_secret"] = target_id
    return [
        EngineEvent(
            "postal_secret_theft_ordered",
            action.player_id,
            None,
            {"target": target_id},
        )
    ]


__all__ = ["apply_secret_action", "secret_legal_actions"]
