"""Atomic cannon handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.engine.spinner_events import spinner_result_event
from nuclear_war_env.fallout import spin_spinner
from nuclear_war_env.population import remove_population_with_bank
from nuclear_war_env.state import GameState

from .atomic_cannon_setup import apply_atomic_cannon_setup


def apply_atomic_cannon_orders(
    state: GameState, skip_dead_owners: bool = False
) -> list[EngineEvent]:
    events = apply_atomic_cannon_setup(state)
    for player in state.players.values():
        # The equipment phase passes skip_dead_owners=True so an owner eliminated
        # earlier this turn does not fire; the final-strike path keeps the default
        # False because it fires the cannon FOR the (dead) retaliating player.
        if skip_dead_owners and not player.alive:
            continue
        cannons = player.pending_orders.setdefault("atomic_cannons", {})
        orders = player.pending_orders.pop("atomic_cannon", [])
        for order in orders:
            cannon_id = order.get("cannon")
            if not cannon_id:
                continue
            cannon = cannons.get(cannon_id)
            if not isinstance(cannon, dict):
                continue
            events.extend(
                _apply_order(state, player.player_id, cannon_id, cannon, order)
            )
    return events


def _apply_order(
    state: GameState,
    owner_id: str,
    cannon_id: str,
    cannon: dict[str, Any],
    order: dict[str, Any],
) -> list[EngineEvent]:
    action = str(order.get("action", "fire"))
    if action == "reposition":
        return _reposition(state, owner_id, cannon_id, cannon, order.get("target"))
    if action != "fire" or cannon.get("status") != "ready":
        return [_failed(owner_id, cannon_id, "not_ready")]
    warhead_yield = order.get("warhead_yield")
    if type(warhead_yield) is not int or warhead_yield != 10:
        return [_failed(owner_id, cannon_id, "requires_10_megaton_warhead")]
    return _fire(state, owner_id, cannon_id, cannon)


def _reposition(
    state: GameState,
    owner_id: str,
    cannon_id: str,
    cannon: dict[str, Any],
    target_id: object,
) -> list[EngineEvent]:
    if target_id not in state.players:
        return [_failed(owner_id, cannon_id, "unknown_target")]
    if not state.players[str(target_id)].alive:
        return [_failed(owner_id, cannon_id, "target_not_alive")]
    cannon["target"] = target_id
    return [
        EngineEvent(
            "atomic_cannon_repositioned",
            owner_id,
            cannon_id,
            {"target": target_id},
        )
    ]


def _fire(
    state: GameState,
    owner_id: str,
    cannon_id: str,
    cannon: dict[str, Any],
) -> list[EngineEvent]:
    target_id = cannon.get("target")
    if target_id not in state.players:
        return [_failed(owner_id, cannon_id, "unknown_target")]
    if not state.players[str(target_id)].alive:
        return [_failed(owner_id, cannon_id, "target_not_alive")]
    roll, outcome = spin_spinner(state.rng)
    events = [spinner_result_event(owner_id, cannon_id, roll, outcome)]
    if outcome.attacker_backfire:
        cannon["status"] = "destroyed"
        return events + [EngineEvent("atomic_cannon_destroyed", owner_id, cannon_id)]
    effective_yield = max(0, 10 * outcome.yield_multiplier + outcome.target_delta)
    if effective_yield <= 0:
        return events
    target = state.players[str(target_id)]
    loss = remove_population_with_bank(state, str(target_id), effective_yield)
    state.players[owner_id].at_war = True
    target.at_war = True
    state.peace = False
    events.append(
        EngineEvent(
            "atomic_cannon_fired",
            owner_id,
            cannon_id,
            {"target": target_id, "loss": loss, "yield": effective_yield},
        )
    )
    if not target.alive:
        events.extend(schedule_final_retaliation(state, target))
    return events


def _failed(owner_id: str, cannon_id: str, reason: str) -> EngineEvent:
    return EngineEvent(
        "atomic_cannon_failed",
        owner_id,
        cannon_id,
        {"reason": reason},
    )


__all__ = ["apply_atomic_cannon_orders"]
