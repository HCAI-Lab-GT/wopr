"""Sabotage handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState


def apply_sabotage_orders(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            continue
        for order in player.pending_orders.pop("sabotage", []):
            target_id = order.get("target")
            if not target_id or target_id not in state.players:
                continue
            events.extend(_apply_order(state, player.player_id, str(target_id), order))
    return events


def _apply_order(
    state: GameState,
    saboteur_id: str,
    target_id: str,
    order: dict[str, Any],
) -> list[EngineEvent]:
    target_orders = state.players[target_id].pending_orders
    delivery_id = order.get("delivery")
    if delivery_id and _remove_launch(target_orders, delivery_id):
        return [_success(saboteur_id, str(delivery_id), target_id)]
    cannon_id = order.get("atomic_cannon")
    if cannon_id and _remove_order(target_orders, "atomic_cannon", "cannon", cannon_id):
        return [_success(saboteur_id, str(cannon_id), target_id)]
    satellite_id = order.get("satellite")
    if satellite_id and _remove_order(
        target_orders,
        "killer_satellite_launch",
        "satellite",
        satellite_id,
    ):
        return [_success(saboteur_id, str(satellite_id), target_id)]
    shuttle_id = order.get("shuttle")
    if shuttle_id and _remove_order(
        target_orders,
        "space_shuttle_attack",
        "shuttle",
        shuttle_id,
    ):
        return [_success(saboteur_id, str(shuttle_id), target_id)]
    return []


def _remove_launch(target_orders: dict[str, Any], delivery_id: object) -> bool:
    launches = target_orders.get("launches")
    if not launches or delivery_id not in launches:
        return False
    launches.pop(delivery_id, None)
    return True


def _remove_order(
    target_orders: dict[str, Any],
    order_key: str,
    id_key: str,
    item_id: object,
) -> bool:
    orders = target_orders.get(order_key)
    if not isinstance(orders, list):
        return False
    kept = [order for order in orders if order.get(id_key) != item_id]
    if len(kept) == len(orders):
        return False
    if kept:
        target_orders[order_key] = kept
    else:
        target_orders.pop(order_key, None)
    return True


def _success(saboteur_id: str, card_id: str, target_id: str) -> EngineEvent:
    return EngineEvent(
        "sabotage_success",
        saboteur_id,
        card_id,
        {"against": target_id},
    )


__all__ = ["apply_sabotage_orders"]
