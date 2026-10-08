"""Submarine handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.engine.spinner_events import spinner_result_event
from nuclear_war_env.fallout import spin_spinner
from nuclear_war_env.population import remove_population_with_bank
from nuclear_war_env.state import GameState

from .submarine_setup import apply_submarine_setup


def apply_submarine_orders(state: GameState) -> list[EngineEvent]:
    events = _return_exposed_submarines(state)
    events.extend(apply_submarine_setup(state))
    for player in state.players.values():
        if not player.alive:
            continue
        submarines = player.pending_orders.setdefault("submarine_states", {})
        orders = player.pending_orders.pop("submarines", [])
        for order in orders:
            submarine_id = order.get("submarine")
            if not submarine_id:
                events.extend(_legacy_strike(state, player.player_id, order))
                continue
            submarine = submarines.get(submarine_id)
            if not isinstance(submarine, dict):
                continue
            events.extend(
                _apply_order(state, player.player_id, submarine_id, submarine, order)
            )
    return events


def _return_exposed_submarines(state: GameState) -> list[EngineEvent]:
    # Postal rules: a fired sub is exposed for one turn while it returns to
    # port; making port is automatic unless it was destroyed in the meantime.
    events: list[EngineEvent] = []
    for player in state.players.values():
        submarines = player.pending_orders.get("submarine_states", {})
        if not isinstance(submarines, dict):
            continue
        for submarine_id, submarine in submarines.items():
            if not isinstance(submarine, dict):
                continue
            if submarine.get("status") != "exposed":
                continue
            if not submarine.get("returning_to_port"):
                continue
            events.append(
                _return_to_port(player.player_id, str(submarine_id), submarine)
            )
    return events


def _apply_order(
    state: GameState,
    owner_id: str,
    submarine_id: str,
    submarine: dict[str, Any],
    order: dict[str, Any],
) -> list[EngineEvent]:
    action = str(order.get("action", "fire"))
    if action == "return_to_port":
        return [_return_to_port(owner_id, submarine_id, submarine)]
    if action != "fire" or submarine.get("status") != "at_sea":
        return []
    return _fire(state, owner_id, submarine_id, submarine)


def _fire(
    state: GameState,
    owner_id: str,
    submarine_id: str,
    submarine: dict[str, Any],
) -> list[EngineEvent]:
    target_id = submarine.get("target")
    stored_payload = submarine.get("warhead_yield", 0)
    if type(stored_payload) is not int:
        return []
    payload = stored_payload
    if target_id not in state.players or payload <= 0:
        return []
    if not state.players[str(target_id)].alive:
        return []
    roll, outcome = spin_spinner(state.rng)
    events = [spinner_result_event(owner_id, submarine_id, roll, outcome)]
    _mark_exposed(submarine)
    if outcome.attacker_backfire:
        submarine["status"] = "destroyed"
        return events + [EngineEvent("submarine_destroyed", owner_id, submarine_id)]
    effective_yield = max(0, payload * outcome.yield_multiplier + outcome.target_delta)
    if effective_yield <= 0:
        return events
    target = state.players[str(target_id)]
    loss = remove_population_with_bank(state, str(target_id), effective_yield)
    state.players[owner_id].at_war = True
    target.at_war = True
    state.peace = False
    events.append(
        EngineEvent(
            "submarine_strike",
            owner_id,
            submarine_id,
            {"target": target_id, "loss": loss, "yield": effective_yield},
        )
    )
    if not target.alive:
        events.extend(schedule_final_retaliation(state, target))
    return events


def _return_to_port(
    owner_id: str, submarine_id: str, submarine: dict[str, Any]
) -> EngineEvent:
    submarine["status"] = "in_port"
    submarine.pop("returning_to_port", None)
    return EngineEvent("submarine_returned", owner_id, submarine_id)


def _mark_exposed(submarine: dict[str, Any]) -> None:
    submarine["status"] = "exposed"
    submarine["returning_to_port"] = True


def _legacy_strike(
    state: GameState,
    owner_id: str,
    order: dict[str, Any],
) -> list[EngineEvent]:
    target_id = order.get("target")
    payload = order.get("yield", 0)
    if type(payload) is not int:
        return []
    if not target_id or target_id not in state.players or payload <= 0:
        return []
    target_key = str(target_id)
    loss = remove_population_with_bank(state, target_key, payload)
    return [
        EngineEvent(
            "submarine_strike",
            owner_id,
            None,
            {"target": target_key, "loss": loss},
        )
    ]


__all__ = ["apply_submarine_orders"]
