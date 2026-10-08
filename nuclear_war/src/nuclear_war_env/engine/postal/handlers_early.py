"""Espionage, secrets, final strike, and queue phases."""

from __future__ import annotations

from nuclear_war_env.engine.draw import advance_queue
from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.final_strike import run_final_strike
from nuclear_war_env.engine.launch_helpers import assign_retaliation_targets
from nuclear_war_env.state import GameState, PlayerState

from .secret_effects import apply_secret_effect


def phase_espionage(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            player.pending_orders.pop("steal_secret", None)
            continue
        order = player.pending_orders.pop("steal_secret", None)
        if not order:
            continue
        target_id = order if isinstance(order, str) else order.get("target")
        if not target_id or target_id not in state.players:
            continue
        target = state.players[target_id]
        if not target.alive:
            continue
        if not target.secrets:
            continue
        secret_id = target.secrets.pop(0)
        player.secrets.append(secret_id)
        player.pending_orders.setdefault("secret_cooldown", []).append(secret_id)
        events.append(
            EngineEvent(
                "secret_stolen",
                player.player_id,
                secret_id,
                {"from": target_id},
            )
        )
    return events


def phase_secrets(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            player.pending_orders.pop("secret_targets", None)
            player.pending_orders.pop("secret_cooldown", None)
            continue
        targets = player.pending_orders.pop("secret_targets", {})
        cooldown = set(player.pending_orders.pop("secret_cooldown", []))
        for secret_id, target_id in targets.items():
            if secret_id in cooldown:
                continue
            if secret_id not in player.secrets:
                continue
            if target_id not in state.players:
                continue
            if not state.players[target_id].alive:
                continue
            events.extend(
                apply_secret_effect(state, player.player_id, secret_id, target_id)
            )
            player.secrets.remove(secret_id)
    return events


def phase_final_strike(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        orders = player.pending_orders.get("final_strike")
        if orders or player.final_strike_cards:
            if orders:
                _assign_pure_engine_final_strike_targets(state, player, orders)
            events.extend(
                run_final_strike(
                    state,
                    player,
                    emit_launch_event=False,
                    use_hand_intercept=False,
                )
            )
            player.final_strike_cards.clear()
    return events


def _assign_pure_engine_final_strike_targets(
    state: GameState,
    player: PlayerState,
    orders: list[dict[str, object]],
) -> None:
    """Point pure-engine postal final strikes at a deterministic legal target.

    The decision-loop path assigns targets via FINAL_STRIKE_TARGET actions; the
    pure-engine path (execute_postal_turn -> phase_final_strike) has no such action,
    so a hand-assembled retaliation order (target=None) is otherwise dropped by
    execute_launches, silently voiding the phase-3 final strike. Reuse the shared
    retaliation policy (eliminator-first, else highest-pop). Pooled orders that
    already carry a target are left untouched.
    """
    assign_retaliation_targets(
        state, player.player_id, orders, _final_strike_eliminated_by(orders)
    )


def _final_strike_eliminated_by(orders: list[dict[str, object]]) -> str | None:
    for order in orders:
        eliminated_by = order.get("eliminated_by")
        if isinstance(eliminated_by, str):
            return eliminated_by
    return None


def phase_flip_queue(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        event = advance_queue(state, player)
        if event:
            events.append(event)
    return events


__all__ = [
    "phase_espionage",
    "phase_secrets",
    "phase_final_strike",
    "phase_flip_queue",
]
