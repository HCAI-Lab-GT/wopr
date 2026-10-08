"""Cruise missile drop handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.engine.spinner_events import spinner_result_event
from nuclear_war_env.engine.war_state import declare_war
from nuclear_war_env.fallout import spin_spinner
from nuclear_war_env.population import remove_population_with_bank
from nuclear_war_env.state import GameState


def apply_cruise_drops(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            continue
        missiles = player.pending_orders.setdefault("cruise_missiles", {})
        for missile_id, missile in list(missiles.items()):
            # Postal rules: a return-to-sender missile drops on its owner the
            # following turn; no new order can recall it.
            if not isinstance(missile, dict) or not missile.get("drop_next_turn"):
                continue
            missiles.pop(missile_id)
            events.extend(_drop(state, player.player_id, str(missile_id), missile))
        for missile_id in player.pending_orders.pop("cruise_drop", []):
            missile = missiles.pop(missile_id, None)
            if not isinstance(missile, dict):
                events.append(_failed(player.player_id, str(missile_id)))
                continue
            events.extend(_drop(state, player.player_id, str(missile_id), missile))
    return events


def _drop(
    state: GameState,
    owner_id: str,
    missile_id: str,
    missile: dict[str, Any],
) -> list[EngineEvent]:
    target_id = missile.get("target")
    payload = missile.get("yield", 0)
    if type(payload) is not int:
        return [_failed(owner_id, missile_id)]
    if target_id not in state.players or payload <= 0:
        return [_failed(owner_id, missile_id)]
    if not state.players[str(target_id)].alive:
        return [_failed(owner_id, missile_id)]
    roll, outcome = spin_spinner(state.rng)
    events = [spinner_result_event(owner_id, missile_id, roll, outcome)]
    declare_war(state)
    effective_yield = max(0, payload * outcome.yield_multiplier + outcome.target_delta)
    if outcome.attacker_backfire or effective_yield <= 0:
        return events + [EngineEvent("cruise_drop_missed", owner_id, missile_id)]
    target = state.players[str(target_id)]
    loss = remove_population_with_bank(state, str(target_id), effective_yield)
    events.append(
        EngineEvent(
            "cruise_dropped",
            owner_id,
            missile_id,
            {"target": target_id, "loss": loss, "yield": effective_yield},
        )
    )
    if not target.alive:
        events.extend(schedule_final_retaliation(state, target))
    return events


def _failed(owner_id: str, missile_id: str) -> EngineEvent:
    return EngineEvent("cruise_drop_failed", owner_id, missile_id)


__all__ = ["apply_cruise_drops"]
