"""Cruise missile launch handling for postal play."""

from __future__ import annotations

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.spinner_events import fallout_die_result_event
from nuclear_war_env.fallout import is_fallout_cloud, roll_fallout_die
from nuclear_war_env.state import GameState


def apply_cruise_launches(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            continue
        missiles = player.pending_orders.setdefault("cruise_missiles", {})
        for order in player.pending_orders.pop("cruise_launch", []):
            missile_id = order.get("missile")
            target_id = order.get("target")
            payload = order.get("yield")
            if (
                not missile_id
                or target_id not in state.players
                or type(payload) is not int
                or payload <= 0
            ):
                events.append(EngineEvent("cruise_launch_failed", player.player_id))
                continue
            if not state.players[str(target_id)].alive:
                events.append(EngineEvent("cruise_launch_failed", player.player_id))
                continue
            # A cruise missile launches on the Radioactive Fallout die: 2-6 is a
            # successful launch, a nuclear cloud (1) discards the missile.
            roll = roll_fallout_die(state.rng)
            events.append(
                fallout_die_result_event(player.player_id, str(missile_id), roll)
            )
            if is_fallout_cloud(roll):
                missiles.pop(missile_id, None)
                events.append(
                    EngineEvent("cruise_launch_failed", player.player_id, missile_id)
                )
                continue
            missiles[missile_id] = {
                "target": target_id,
                "yield": payload,
                "visited": [str(target_id)],
                "skip_move_once": True,
            }
            events.append(
                EngineEvent(
                    "cruise_launched",
                    player.player_id,
                    str(missile_id),
                    {"target": target_id},
                )
            )
    return events


__all__ = ["apply_cruise_launches"]
