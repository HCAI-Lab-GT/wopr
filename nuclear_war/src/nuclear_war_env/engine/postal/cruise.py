"""Cruise missile movement handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState

from .cruise_drop import apply_cruise_drops
from .cruise_launch import apply_cruise_launches


def apply_cruise_moves(state: GameState) -> list[EngineEvent]:
    events = apply_cruise_launches(state)
    events.extend(apply_cruise_drops(state))
    events.extend(_apply_moves(state))
    return events


def _apply_moves(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            continue
        missiles = player.pending_orders.setdefault("cruise_missiles", {})
        orders = player.pending_orders.pop("cruise_move", [])
        ordered = set()
        for order in orders:
            missile_id = order.get("missile")
            target_id = order.get("target")
            if not missile_id:
                continue
            ordered.add(missile_id)
            missile = missiles.get(missile_id)
            if not isinstance(missile, dict):
                events.append(
                    _legacy_event(player.player_id, missile_id, target_id, state)
                )
                continue
            events.append(
                _move_missile(state, player.player_id, missile_id, missile, target_id)
            )
        for missile_id, missile in missiles.items():
            if missile_id not in ordered and isinstance(missile, dict):
                if missile.pop("skip_move_once", False):
                    continue
                events.append(_return_to_sender(player.player_id, missile_id, missile))
    return events


def _move_missile(
    state: GameState,
    owner_id: str,
    missile_id: str,
    missile: dict[str, Any],
    target_id: object,
) -> EngineEvent:
    visited = set(missile.get("visited", []))
    if (
        target_id not in state.players
        or not state.players[str(target_id)].alive
        or target_id in visited
    ):
        return _return_to_sender(owner_id, missile_id, missile)
    missile["target"] = target_id
    missile["visited"] = sorted(visited | {str(target_id)})
    return EngineEvent(
        "cruise_move",
        owner_id,
        missile_id,
        {"target": target_id, "status": "moved"},
    )


def _return_to_sender(
    owner_id: str,
    missile_id: str,
    missile: dict[str, Any],
) -> EngineEvent:
    missile["target"] = owner_id
    missile["drop_next_turn"] = True
    return EngineEvent(
        "cruise_move",
        owner_id,
        missile_id,
        {"target": owner_id, "status": "return_to_sender"},
    )


def _legacy_event(
    owner_id: str,
    missile_id: str,
    target_id: object,
    state: GameState,
) -> EngineEvent:
    status = "scheduled" if target_id in state.players else "failed"
    return EngineEvent(
        "cruise_move",
        owner_id,
        missile_id,
        {"target": target_id if status == "scheduled" else None, "status": status},
    )


__all__ = ["apply_cruise_moves"]
