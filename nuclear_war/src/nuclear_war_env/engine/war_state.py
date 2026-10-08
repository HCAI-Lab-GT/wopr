"""War-state transition helpers."""

from __future__ import annotations

from nuclear_war_env.state import GameState, PlayerState

PEACE_RESTORE_PENDING = "peace_restore_pending"


def declare_war(state: GameState) -> None:
    state.peace = False
    for player in state.players.values():
        player.at_war = True


def declare_war_for_launch(state: GameState, order: dict[str, object]) -> None:
    has_target = order.get("target") is not None
    has_equipment_target = isinstance(order.get("equipment_target"), dict)
    if order.get("warheads") and (has_target or has_equipment_target):
        declare_war(state)


def mark_peace_restore_pending(player: PlayerState) -> None:
    player.pending_orders[PEACE_RESTORE_PENDING] = True


def restore_peace(state: GameState) -> None:
    state.peace = True
    for player in state.players.values():
        player.at_war = False


def restore_peace_after_completed_eliminations(state: GameState) -> bool:
    players = [
        player
        for player in state.players.values()
        if player.pending_orders.get(PEACE_RESTORE_PENDING)
    ]
    if not players or any(
        player.pending_orders.get("final_strike") for player in players
    ):
        return False
    # Always clear the satisfied pending flags so they cannot leak across turns.
    for player in players:
        player.pending_orders.pop(PEACE_RESTORE_PENDING, None)
    # Only a kill that actually broke the peace produces a war->peace transition.
    # Non-attack kills (secret effect, space-platform crash) mark peace-restore
    # pending WITHOUT declaring war, so at peace there is nothing to restore and no
    # peace_restored to emit.
    if state.peace:
        return False
    restore_peace(state)
    return True


__all__ = [
    "PEACE_RESTORE_PENDING",
    "declare_war",
    "declare_war_for_launch",
    "mark_peace_restore_pending",
    "restore_peace",
    "restore_peace_after_completed_eliminations",
]
