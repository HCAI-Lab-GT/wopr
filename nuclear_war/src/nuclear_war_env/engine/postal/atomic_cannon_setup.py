"""Atomic cannon setup handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState


def apply_atomic_cannon_setup(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        cannons = player.pending_orders.setdefault("atomic_cannons", {})
        orders = player.pending_orders.pop("atomic_cannon_setup", [])
        if isinstance(orders, dict):
            orders = [orders]
        for order in orders:
            cannon_id = order.get("cannon")
            target_id = order.get("target")
            if not cannon_id or target_id not in state.players:
                continue
            if not state.players[str(target_id)].alive:
                events.append(
                    EngineEvent(
                        "atomic_cannon_failed",
                        player.player_id,
                        str(cannon_id),
                        {"reason": "target_not_alive"},
                    )
                )
                continue
            if _has_ready_cannon(cannons):
                events.append(
                    EngineEvent(
                        "atomic_cannon_discarded",
                        player.player_id,
                        str(cannon_id),
                    )
                )
                continue
            cannons[cannon_id] = {"target": target_id, "status": "ready"}
            events.append(
                EngineEvent("atomic_cannon_setup", player.player_id, str(cannon_id))
            )
    return events


def _has_ready_cannon(cannons: dict[str, Any]) -> bool:
    return any(
        isinstance(cannon, dict) and cannon.get("status") != "destroyed"
        for cannon in cannons.values()
    )


__all__ = ["apply_atomic_cannon_setup"]
