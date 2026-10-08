"""Miscellaneous postal handlers (propaganda, queue, specials)."""

from __future__ import annotations

from nuclear_war_env.engine.draw import set_face_down_cards
from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.population import (
    add_population_from_bank,
    remove_population_with_bank,
)
from nuclear_war_env.state import GameState

from .atomic_cannon import apply_atomic_cannon_orders
from .cruise import apply_cruise_moves
from .killer_satellite import apply_killer_satellite_orders
from .space_platform import apply_space_platform_orders
from .space_shuttle import apply_space_shuttle_orders
from .submarine import apply_submarine_orders
from .supervirus import apply_supervirus_orders


def phase_propaganda(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    if not state.peace:
        for player in state.players.values():
            player.pending_orders.pop("propaganda", None)
            player.pending_orders.pop("propaganda_orders", None)
        return events
    for player in state.players.values():
        if not player.alive:
            player.pending_orders.pop("propaganda", None)
            player.pending_orders.pop("propaganda_orders", None)
            continue
        cards = player.pending_orders.pop("propaganda", [])
        targets = player.pending_orders.pop("propaganda_orders", {})
        for card_id in cards:
            target_id = targets.get(card_id)
            if not target_id or target_id not in state.players:
                continue
            target = state.players[target_id]
            if not target.alive:
                continue
            card = state.card_by_id(card_id)
            amount = card.metadata.get("value_millions")
            if type(amount) is not int or amount <= 0:
                amount = card.metadata.get("influence", 0)
                if type(amount) is not int:
                    amount = 0
            if amount <= 0:
                continue
            target_was_alive = target.alive
            loss = remove_population_with_bank(state, target_id, amount)
            # An inexact-change round-down can make the loss heavier than the
            # card value; the extra stays in the bank instead of migrating.
            migrated = add_population_from_bank(
                state, player.player_id, min(loss, amount)
            )
            events.append(
                EngineEvent(
                    "propaganda_effect",
                    player.player_id,
                    card_id,
                    {"target": target_id, "migrated": migrated},
                )
            )
            if target_was_alive and not target.alive:
                events.append(
                    EngineEvent(
                        "player_eliminated",
                        target_id,
                        None,
                        {"by": player.player_id},
                    )
                )
    return events


def phase_enqueue(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        queue = player.pending_orders.pop("next_face_down", None)
        if queue:
            set_face_down_cards(player, queue)
            events.append(
                EngineEvent(
                    "queue_updated",
                    player.player_id,
                    None,
                    {"cards": list(queue)},
                )
            )
    return events


def phase_submarines(state: GameState) -> list[EngineEvent]:
    events = apply_submarine_orders(state)
    events.extend(apply_atomic_cannon_orders(state, skip_dead_owners=True))
    return events


def phase_space_platforms(state: GameState) -> list[EngineEvent]:
    events = apply_space_shuttle_orders(state)
    events.extend(apply_space_platform_orders(state))
    events.extend(apply_killer_satellite_orders(state))
    return events


def phase_cruise_move(state: GameState) -> list[EngineEvent]:
    events = apply_cruise_moves(state)
    events.extend(apply_supervirus_orders(state))
    return events


def phase_specials(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        specials = player.pending_orders.pop("specials", [])
        for special_id in specials:
            events.append(
                EngineEvent(
                    "special_played",
                    player.player_id,
                    special_id,
                    {},
                )
            )
    return events


__all__ = [
    "phase_propaganda",
    "phase_enqueue",
    "phase_submarines",
    "phase_space_platforms",
    "phase_cruise_move",
    "phase_specials",
]
