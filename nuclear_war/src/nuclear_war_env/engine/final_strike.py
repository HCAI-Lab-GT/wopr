"""Shared helpers for final retaliation sequencing."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState, PlayerState


def run_final_strike(
    state: GameState,
    player: PlayerState,
    emit_launch_event: bool,
    auto_resolve_final_strike: bool = True,
    use_hand_intercept: bool = True,
) -> list[EngineEvent]:
    orders = player.pending_orders.pop("final_strike", [])
    if not orders:
        return []
    launch_orders = [order for order in orders if "delivery" in order]
    cannon_orders = [order for order in orders if "atomic_cannon" in order]
    events = _run_launch_orders(
        state,
        player,
        launch_orders,
        emit_launch_event,
        auto_resolve_final_strike,
        use_hand_intercept,
    )
    events.extend(_run_atomic_cannon_orders(state, player, cannon_orders))
    events.insert(0, EngineEvent("final_strike_executed", player.player_id))
    return events


def begin_final_strike_launches(
    state: GameState,
    player: PlayerState,
) -> list[EngineEvent]:
    orders = player.pending_orders.pop("final_strike", [])
    if not orders:
        return []
    launch_orders = [order for order in orders if "delivery" in order]
    cannon_orders = [order for order in orders if "atomic_cannon" in order]
    _queue_launch_orders(state, player, launch_orders)
    events = [EngineEvent("final_strike_executed", player.player_id)]
    events.extend(_run_atomic_cannon_orders(state, player, cannon_orders))
    return events


def _queue_launch_orders(
    state: GameState,
    player: PlayerState,
    orders: list[dict[str, Any]],
) -> None:
    if not orders:
        return
    launches = player.pending_orders.setdefault("launches", {})
    if not isinstance(launches, dict):
        launches = {}
        player.pending_orders["launches"] = launches
    for order in orders:
        delivery_id = order["delivery"]
        target_id = order.get("target")
        if not isinstance(target_id, str):
            continue
        target = state.players.get(target_id)
        if target is None or not target.alive:
            continue
        launches[delivery_id] = {
            "delivery": delivery_id,
            "capacity": len(order.get("warheads", [])),
            "warheads": list(order.get("warheads", [])),
            "target": target_id,
            "_final_strike": True,
        }


def _run_launch_orders(
    state: GameState,
    player: PlayerState,
    orders: list[dict[str, Any]],
    emit_launch_event: bool,
    auto_resolve_final_strike: bool,
    use_hand_intercept: bool = True,
) -> list[EngineEvent]:
    from nuclear_war_env.engine.launch import execute_launches

    if not orders:
        return []
    original_launches = player.pending_orders.get("launches")
    temp: dict[str, dict[str, object]] = {}
    for order in orders:
        delivery_id = order["delivery"]
        temp[delivery_id] = {
            "delivery": delivery_id,
            "capacity": len(order.get("warheads", [])),
            "warheads": list(order.get("warheads", [])),
            "target": order.get("target"),
        }
    player.pending_orders["launches"] = temp
    events = execute_launches(
        state,
        emit_launch_event=emit_launch_event,
        use_hand_intercept=use_hand_intercept,
        auto_resolve_final_strike=auto_resolve_final_strike,
    )
    if original_launches is not None:
        remaining = player.pending_orders.get("launches")
        if remaining:
            original_launches.update(remaining)
        player.pending_orders["launches"] = original_launches
    else:
        player.pending_orders.pop("launches", None)
    return events


def _run_atomic_cannon_orders(
    state: GameState,
    player: PlayerState,
    orders: list[dict[str, Any]],
) -> list[EngineEvent]:
    from nuclear_war_env.engine.postal.atomic_cannon import apply_atomic_cannon_orders

    if not orders:
        return []
    player.pending_orders.setdefault("atomic_cannon", []).extend(
        {
            "cannon": order["atomic_cannon"],
            "action": "fire",
            "warhead_yield": order.get("warhead_yield", 10),
        }
        for order in orders
    )
    return apply_atomic_cannon_orders(state)


__all__ = ["begin_final_strike_launches", "run_final_strike"]
