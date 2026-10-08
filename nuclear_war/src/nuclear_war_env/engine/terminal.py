"""Engine-owned game-over predicate shared by every interface layer.

A game is over when at most one player is alive AND no eliminated player
still has an unresolved final strike (pending orders or in-flight
final-strike launches). Environments must call this instead of re-deriving
their own terminal condition.
"""

from __future__ import annotations

from nuclear_war_env.state import GameState, PlayerState


def player_final_strike_pending(player: PlayerState) -> bool:
    """True while the player still has final-strike orders or launches in flight."""
    launches = player.pending_orders.get("launches", {})
    return bool(player.pending_orders.get("final_strike")) or (
        isinstance(launches, dict)
        and any(
            isinstance(order, dict) and order.get("_final_strike")
            for order in launches.values()
        )
    )


def final_strikes_pending(state: GameState) -> bool:
    return any(player_final_strike_pending(p) for p in state.players.values())


def game_over(state: GameState) -> bool:
    if final_strikes_pending(state):
        return False
    return sum(1 for player in state.players.values() if player.alive) <= 1


__all__ = ["player_final_strike_pending", "final_strikes_pending", "game_over"]
