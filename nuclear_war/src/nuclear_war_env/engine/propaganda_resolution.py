"""Table-mode propaganda resolution.

Propaganda steals population from another player during peace and is discarded with
no effect during war. Table mode has no interactive target step, so the target is the
deterministic ``highest_population_opponent`` (the shared `select_target` seam).
"""

from __future__ import annotations

from collections.abc import Callable

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.population import (
    add_population_from_bank,
    remove_population_with_bank,
)
from nuclear_war_env.state import GameState

from .target_policy import highest_population_opponent

PropagandaTargetSelector = Callable[[GameState, str], "str | None"]


def select_propaganda_target(state: GameState, player_id: str) -> str | None:
    return highest_population_opponent(state, player_id)


def apply_propaganda_steal(
    state: GameState,
    player_id: str,
    card_id: str,
    target_id: str,
) -> list[EngineEvent]:
    """Steal one propaganda card's value from target to player (peace-time effect).

    Emits propaganda_effect; if the steal drops the target to 0 it emits
    player_eliminated with NO final retaliation (per the rules, propaganda kills
    grant none). Returns [] for a non-positive card value.
    """
    amount = _propaganda_value(state.card_by_id(card_id).metadata)
    if amount <= 0:
        return []
    target = state.players[target_id]
    was_alive = target.alive
    loss = remove_population_with_bank(state, target_id, amount)
    # An inexact-change round-down can make the loss heavier than the card
    # value; the extra stays in the bank instead of migrating.
    migrated = add_population_from_bank(state, player_id, min(loss, amount))
    events: list[EngineEvent] = [
        EngineEvent(
            "propaganda_effect",
            player_id,
            card_id,
            {"target": target_id, "migrated": migrated},
        )
    ]
    if was_alive and not target.alive:
        events.append(
            EngineEvent("player_eliminated", target_id, None, {"by": player_id})
        )
    return events


def resolve_propaganda(
    state: GameState,
    player_id: str,
    select_target: PropagandaTargetSelector = select_propaganda_target,
) -> list[EngineEvent]:
    """Resolve every propaganda card pending for ``player_id`` (legacy path).

    During war propaganda is inert and the pending cards are dropped. During peace
    each card steals its ``value_millions`` from the chosen target (re-evaluated per
    card). Retained for the legacy table_turn driver; the decision loop applies
    propaganda one card at a time via apply_propaganda_steal.
    """
    player = state.players[player_id]
    cards = player.pending_orders.pop("propaganda", [])
    if not state.peace or not cards:
        return []
    events: list[EngineEvent] = []
    for card_id in cards:
        if _propaganda_value(state.card_by_id(card_id).metadata) <= 0:
            continue
        target_id = select_target(state, player_id)
        if target_id is None:
            continue
        events.extend(apply_propaganda_steal(state, player_id, card_id, target_id))
    return events


def _propaganda_value(metadata: object) -> int:
    if not isinstance(metadata, dict):
        return 0
    amount = metadata.get("value_millions", 0)
    return amount if type(amount) is int else 0


__all__ = [
    "apply_propaganda_steal",
    "resolve_propaganda",
    "select_propaganda_target",
    "PropagandaTargetSelector",
]
