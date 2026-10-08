"""Space shuttle handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.engine.spinner_events import spinner_result_event
from nuclear_war_env.engine.war_state import declare_war
from nuclear_war_env.fallout import spin_spinner
from nuclear_war_env.population import remove_population_with_bank
from nuclear_war_env.state import GameState


def apply_space_shuttle_orders(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            continue
        platforms = player.pending_orders.setdefault("space_platforms", {})
        for order in player.pending_orders.pop("space_shuttle_reload", []):
            platform_id = order.get("platform")
            platform = platforms.get(platform_id)
            if not isinstance(platform, dict):
                continue
            reload_warheads = order.get("warheads", [])
            if not isinstance(reload_warheads, list) or not all(
                type(value) is int for value in reload_warheads
            ):
                continue
            warheads = platform.setdefault("warheads", [])
            warheads.extend(reload_warheads)
            events.append(
                EngineEvent(
                    "space_shuttle_reloaded",
                    player.player_id,
                    str(platform_id),
                    {"added": list(reload_warheads)},
                )
            )
        events.extend(_attacks(state, player.player_id, player.pending_orders))
    return events


def _attacks(
    state: GameState,
    owner_id: str,
    orders: dict[str, Any],
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for order in orders.pop("space_shuttle_attack", []):
        target_id = order.get("target")
        shuttle_id = order.get("shuttle")
        warheads = order.get("warheads", [])
        if not isinstance(warheads, list) or not all(
            type(value) is int for value in warheads
        ):
            continue
        if not target_id or target_id not in state.players or not shuttle_id:
            continue
        if not state.players[str(target_id)].alive:
            continue
        if not warheads:
            continue
        events.extend(
            _attack(state, owner_id, str(shuttle_id), str(target_id), warheads[0])
        )
    return events


def _attack(
    state: GameState,
    owner_id: str,
    shuttle_id: str,
    target_id: str,
    payload: int,
) -> list[EngineEvent]:
    roll, outcome = spin_spinner(state.rng)
    events = [spinner_result_event(owner_id, shuttle_id, roll, outcome)]
    declare_war(state)
    effective_yield = max(0, payload * outcome.yield_multiplier + outcome.target_delta)
    if outcome.attacker_backfire or effective_yield <= 0:
        return events + [
            EngineEvent("space_shuttle_attack_failed", owner_id, shuttle_id)
        ]
    target = state.players[target_id]
    loss = remove_population_with_bank(state, target_id, effective_yield)
    events.append(
        EngineEvent(
            "space_shuttle_attacked",
            owner_id,
            shuttle_id,
            {"target": target_id, "loss": loss, "yield": effective_yield},
        )
    )
    if not target.alive:
        events.extend(schedule_final_retaliation(state, target))
    return events


__all__ = ["apply_space_shuttle_orders"]
