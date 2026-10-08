"""Killer satellite handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.spinner_events import fallout_die_result_event
from nuclear_war_env.fallout import is_fallout_cloud, roll_fallout_die
from nuclear_war_env.state import GameState


def apply_killer_satellite_orders(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            continue
        satellites = player.pending_orders.setdefault("killer_satellites", {})
        events.extend(_launches(player.player_id, satellites, player.pending_orders))
        events.extend(
            _attacks(state, player.player_id, satellites, player.pending_orders)
        )
    return events


def _launches(
    owner_id: str,
    satellites: dict[str, Any],
    orders: dict[str, Any],
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for order in orders.pop("killer_satellite_launch", []):
        satellite_id = order.get("satellite")
        if not satellite_id:
            continue
        satellites[satellite_id] = {"status": "orbit"}
        events.append(
            EngineEvent("killer_satellite_launched", owner_id, str(satellite_id))
        )
    return events


def _attacks(
    state: GameState,
    owner_id: str,
    satellites: dict[str, Any],
    orders: dict[str, Any],
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for order in orders.pop("killer_satellite_attack", []):
        satellite_id = order.get("satellite")
        if not satellite_id or satellite_id not in satellites:
            continue
        events.extend(_attack(state, owner_id, str(satellite_id), satellites, order))
    return events


def _attack(
    state: GameState,
    owner_id: str,
    satellite_id: str,
    satellites: dict[str, Any],
    order: dict[str, Any],
) -> list[EngineEvent]:
    target_id = order.get("target_player")
    platform_id = order.get("platform")
    if not isinstance(platform_id, str):
        return []
    platform = _target_platform(state, target_id, platform_id)
    if platform is None:
        return []
    # The killer satellite attack rolls the Radioactive Fallout die: 2-6
    # destroys the platform, a nuclear cloud (1) discards only the satellite.
    roll = roll_fallout_die(state.rng)
    satellites.pop(satellite_id, None)
    events = [fallout_die_result_event(owner_id, satellite_id, roll)]
    if is_fallout_cloud(roll):
        return events + [EngineEvent("killer_satellite_failed", owner_id, satellite_id)]
    platform.pop(platform_id, None)
    return events + [
        EngineEvent(
            "killer_satellite_destroyed_platform",
            owner_id,
            satellite_id,
            {"target_player": target_id, "platform": platform_id},
        )
    ]


def _target_platform(
    state: GameState,
    target_id: object,
    platform_id: str,
) -> dict[str, Any] | None:
    if target_id not in state.players:
        return None
    target = state.players[str(target_id)]
    if not target.alive:
        return None
    platforms = target.pending_orders.get("space_platforms", {})
    if platform_id not in platforms:
        return None
    return platforms


__all__ = ["apply_killer_satellite_orders"]
