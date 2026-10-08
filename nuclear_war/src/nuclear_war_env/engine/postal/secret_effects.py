"""Secret and top-secret card effect resolution."""

from __future__ import annotations

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.engine.war_state import mark_peace_restore_pending
from nuclear_war_env.population import (
    add_population_from_bank,
    remove_population_with_bank,
)
from nuclear_war_env.state import GameState, PlayerState
from nuclear_war_env.turn_effects import add_skip_turns

SUPPORTED_EFFECT_KEYS = {
    "damage_population_millions",
    "gain_from_bank_millions",
    "remove_to_bank_millions",
    "steal_population_millions",
    "target_loses_turns",
}


def apply_secret_effect(
    state: GameState,
    player_id: str,
    card_id: str,
    target_id: str,
    auto_resolve_table: bool = True,
) -> list[EngineEvent]:
    target = state.players[target_id]
    metadata = state.card_by_id(card_id).metadata
    target_was_alive = target.alive
    events: list[EngineEvent] = []
    # A secret only "triggers against" a target when it acts on another player.
    # Self-benefiting secrets (e.g. gain-from-bank) have no opponent target, and
    # replay logs reject a secret_triggered whose target is the acting player.
    if target_id != player_id:
        events.append(
            EngineEvent(
                "secret_triggered",
                player_id,
                card_id,
                {"target": target_id},
            )
        )
    events.extend(_move_population(state, player_id, target_id, card_id, metadata))
    events.extend(_damage_population(state, target_id, card_id, metadata))
    events.extend(_skip_turn(target, player_id, card_id, metadata))
    # Any effect that drains a target to zero (steal or damage) is an elimination
    # and must be logged like a warhead kill, then routed to final retaliation.
    if target_was_alive and not target.alive and target_id != player_id:
        mark_peace_restore_pending(target)
        events.append(
            EngineEvent("player_eliminated", target_id, None, {"by": player_id})
        )
        events.extend(
            schedule_final_retaliation(
                state,
                target,
                eliminated_by=player_id,
                auto_resolve_table=auto_resolve_table,
            )
        )
    return events


def _move_population(
    state: GameState,
    player_id: str,
    target_id: str,
    card_id: str,
    metadata: object,
) -> list[EngineEvent]:
    player = state.players[player_id]
    target = state.players[target_id]
    if not isinstance(metadata, dict):
        return []
    amount = metadata.get("steal_population_millions", 0)
    if type(amount) is not int:
        amount = 0
    if amount <= 0:
        amount = metadata.get("gain_from_bank_millions", 0)
        if type(amount) is not int:
            amount = 0
        if amount <= 0:
            return []
        add_population_from_bank(state, player_id, amount)
        return [EngineEvent("secret_population_gained", player.player_id, card_id)]
    loss = remove_population_with_bank(state, target_id, amount)
    # An inexact-change round-down can make the loss heavier than the card
    # value; the extra stays in the bank instead of migrating.
    migrated = add_population_from_bank(state, player_id, min(loss, amount))
    return [
        EngineEvent(
            "secret_population_stolen",
            player.player_id,
            card_id,
            {"target": target.player_id, "migrated": migrated},
        )
    ]


def _damage_population(
    state: GameState,
    target_id: str,
    card_id: str,
    metadata: object,
) -> list[EngineEvent]:
    target = state.players[target_id]
    if not isinstance(metadata, dict):
        return []
    amount = metadata.get("damage_population_millions", 0)
    if type(amount) is not int:
        amount = 0
    event_type = "secret_population_damaged"
    if amount <= 0:
        amount = metadata.get("remove_to_bank_millions", 0)
        if type(amount) is not int:
            amount = 0
        event_type = "secret_population_removed"
    if amount <= 0:
        return []
    loss = remove_population_with_bank(state, target_id, amount)
    return [EngineEvent(event_type, target.player_id, card_id, {"loss": loss})]


def _skip_turn(
    target: PlayerState,
    player_id: str,
    card_id: str,
    metadata: object,
) -> list[EngineEvent]:
    if not isinstance(metadata, dict):
        return []
    turns = metadata.get("target_loses_turns", 0)
    if type(turns) is not int:
        turns = 0
    if turns <= 0:
        return []
    add_skip_turns(target, turns)
    return [
        EngineEvent(
            "secret_turns_lost",
            player_id,
            card_id,
            {"target": target.player_id, "turns": turns},
        )
    ]


__all__ = ["SUPPORTED_EFFECT_KEYS", "apply_secret_effect"]
