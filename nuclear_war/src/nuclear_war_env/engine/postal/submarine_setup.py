"""Submarine setup and reload handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState, PlayerState

VALID_SUBMARINE_WARHEADS = {10, 20}


def apply_submarine_setup(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        submarines = player.pending_orders.setdefault("submarine_states", {})
        events.extend(_launch_orders(state, player.player_id, submarines, player))
        events.extend(_reload_orders(state, player.player_id, submarines, player))
    return events


def _launch_orders(
    state: GameState,
    owner_id: str,
    submarines: dict[str, Any],
    player: PlayerState,
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for order in player.pending_orders.pop("submarine_launch", []):
        submarine_id = order.get("submarine")
        if not submarine_id:
            continue
        events.append(
            _send_or_port(state, owner_id, str(submarine_id), submarines, order)
        )
    return events


def _reload_orders(
    state: GameState,
    owner_id: str,
    submarines: dict[str, Any],
    player: PlayerState,
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for order in player.pending_orders.pop("submarine_reload", []):
        submarine_id = order.get("submarine")
        if not submarine_id:
            continue
        submarine = submarines.get(submarine_id)
        if not isinstance(submarine, dict) or submarine.get("status") != "in_port":
            continue
        event = _send_or_port(state, owner_id, str(submarine_id), submarines, order)
        if event.event_type == "submarine_sent_to_sea":
            event = EngineEvent("submarine_reloaded", owner_id, str(submarine_id))
        events.append(event)
    return events


def _send_or_port(
    state: GameState,
    owner_id: str,
    submarine_id: str,
    submarines: dict[str, Any],
    order: dict[str, Any],
) -> EngineEvent:
    target_id = order.get("target")
    payload = order.get("warhead_yield")
    target = state.players.get(str(target_id))
    if (
        target
        and target.alive
        and type(payload) is int
        and payload in VALID_SUBMARINE_WARHEADS
    ):
        submarines[submarine_id] = {
            "target": target_id,
            "warhead_yield": payload,
            "status": "at_sea",
        }
        return EngineEvent("submarine_sent_to_sea", owner_id, submarine_id)
    submarines[submarine_id] = {"status": "in_port"}
    return EngineEvent("submarine_in_port", owner_id, submarine_id)


__all__ = ["VALID_SUBMARINE_WARHEADS", "apply_submarine_setup"]
