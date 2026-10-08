"""Final strike legal action helpers."""

from __future__ import annotations

from .action_models import ActionType, LegalAction, build_action
from .engine.events import EngineEvent
from .state import GameState


def final_strike_actions(state: GameState, player_id: str) -> list[LegalAction]:
    if not _has_untargeted_launch_order(state, player_id):
        return []
    return [
        build_action(
            player_id,
            ActionType.FINAL_STRIKE_TARGET,
            f"Target final strike at {target_id}",
            {"target": target_id},
        )
        for target_id, target in state.players.items()
        if target_id != player_id and target.alive
    ]


def apply_final_strike_action(
    state: GameState,
    action: LegalAction,
) -> list[EngineEvent]:
    target_id = str(action.payload["target"])
    if target_id not in state.players or not state.players[target_id].alive:
        return []
    orders = state.players[action.player_id].pending_orders.get("final_strike", [])
    for order in orders:
        if isinstance(order, dict) and "delivery" in order and not order.get("target"):
            order["target"] = target_id
    return [
        EngineEvent(
            "final_strike_targeted",
            action.player_id,
            None,
            {"target": target_id},
        )
    ]


def _has_untargeted_launch_order(state: GameState, player_id: str) -> bool:
    orders = state.players[player_id].pending_orders.get("final_strike", [])
    if not isinstance(orders, list):
        return False
    return any(
        isinstance(order, dict)
        and "delivery" in order
        and order.get("warheads")
        and not order.get("target")
        for order in orders
    )


__all__ = ["apply_final_strike_action", "final_strike_actions"]
