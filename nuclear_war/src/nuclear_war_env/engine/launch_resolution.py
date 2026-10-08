"""Post-spinner launch resolution helpers."""

from __future__ import annotations

from nuclear_war_env.fallout import FalloutOutcome
from nuclear_war_env.population import remove_population_with_bank
from nuclear_war_env.state import GameState, PlayerState

from .equipment_targeting import resolve_equipment_target
from .events import EngineEvent
from .launch_helpers import _is_bomber, schedule_final_retaliation
from .war_state import declare_war, mark_peace_restore_pending


def resolve_unblocked_launch(
    state: GameState,
    attacker_id: str,
    target_id: str,
    delivery_id: str,
    order: dict[str, object],
    total_yield: int,
    outcome: FalloutOutcome,
    auto_resolve_final_strike: bool = True,
) -> list[EngineEvent]:
    equipment_events = resolve_equipment_target(
        state,
        attacker_id,
        delivery_id,
        order,
        outcome,
    )
    if equipment_events is not None:
        return equipment_events
    target = state.players[target_id]
    attacker = state.players[attacker_id]
    delivery_is_bomber = _is_bomber(state.card_by_id(delivery_id))
    return _resolve_population_strike(
        state,
        attacker,
        target,
        attacker_id,
        target_id,
        total_yield,
        outcome,
        delivery_is_bomber,
        auto_resolve_final_strike,
        delivery_id,
    )


def _resolve_population_strike(
    state: GameState,
    attacker: PlayerState,
    target: PlayerState,
    attacker_id: str,
    target_id: str,
    total_yield: int,
    outcome: FalloutOutcome,
    delivery_is_bomber: bool = False,
    auto_resolve_final_strike: bool = True,
    delivery_id: str | None = None,
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    declare_war(state)
    effective_yield = total_yield * outcome.yield_multiplier
    if outcome.target_delta:
        effective_yield = max(0, effective_yield + outcome.target_delta)
    if outcome.attacker_backfire and total_yield > 0 and not delivery_is_bomber:
        # A missile booster explodes on the attacker for the warhead's own yield,
        # even though it never reaches the target (yield_multiplier=0 zeroes the
        # target damage). A bomber instead just runs out of fuel: it is discarded
        # with no backfire (handled by skipping this branch for bombers).
        was_alive = attacker.alive
        backfire = remove_population_with_bank(state, attacker_id, total_yield)
        events.append(
            EngineEvent("launch_backfire", attacker_id, None, {"loss": backfire})
        )
        if was_alive and not attacker.alive:
            # Self-inflicted death: log it (attributed to the intended target so the
            # replay's by != eliminated rule holds) and mark peace pending. The rules
            # grant final retaliation for any death by warhead (only a propaganda
            # defeat forfeits it), so a booster accident retaliates too;
            # eliminated_by mirrors the event's `by` attribution.
            mark_peace_restore_pending(attacker)
            events.append(
                EngineEvent("player_eliminated", attacker_id, None, {"by": target_id})
            )
            # The missile and warhead exploded on the launch pad, so drop this
            # launch before scheduling: schedule_final_retaliation pools every
            # remaining launch, and the exploded one would otherwise be fired
            # and discarded a second time. Its cards are discarded by the
            # execute_launches cleanup that follows.
            launches = attacker.pending_orders.get("launches")
            if isinstance(launches, dict) and delivery_id is not None:
                launches.pop(delivery_id, None)
            events.extend(
                schedule_final_retaliation(
                    state,
                    attacker,
                    eliminated_by=target_id,
                    auto_resolve_table=auto_resolve_final_strike,
                )
            )
    if effective_yield <= 0:
        return events
    was_alive = target.alive
    loss = remove_population_with_bank(state, target_id, effective_yield)
    events.append(
        EngineEvent(
            "warhead_detonated",
            attacker_id,
            None,
            {"target": target_id, "yield": effective_yield, "loss": loss},
        )
    )
    if was_alive and not target.alive:
        mark_peace_restore_pending(target)
        events.append(
            EngineEvent("player_eliminated", target_id, None, {"by": attacker_id})
        )
        events.extend(
            schedule_final_retaliation(
                state,
                target,
                eliminated_by=attacker_id,
                auto_resolve_table=auto_resolve_final_strike,
            )
        )
    return events


def trigger_global_loss(
    state: GameState,
    attacker_id: str,
    target_id: str,
) -> list[EngineEvent]:
    """Super Chain Reaction: a 100Mt warhead + stockpile explosion wipes everyone out.

    Every living player is eliminated simultaneously with no winner and no final
    retaliation. Each elimination is attributed to a player other than itself (the
    attacker, or the intended target for the attacker) so replay logs stay valid.
    """
    events: list[EngineEvent] = [EngineEvent("global_loss", None)]
    for player_id, player in state.players.items():
        if not player.alive:
            continue
        remove_population_with_bank(state, player_id, sum(player.population))
        by = target_id if player_id == attacker_id else attacker_id
        events.append(EngineEvent("player_eliminated", player_id, None, {"by": by}))
    return events


__all__ = ["resolve_unblocked_launch", "trigger_global_loss"]
