"""Deterministic V1 target policy shared by table-mode mechanics.

Table mode has no interactive target-selection step, so secrets, propaganda, and
final retaliation pick targets through this single deterministic policy. It is the
seam to swap for a legal-action targeting choice later (so agents choose targets,
mirroring the postal flow) without touching each mechanic.
"""

from __future__ import annotations

from nuclear_war_env.state import GameState


def opponents_by_population(state: GameState, player_id: str) -> list[str]:
    """Living opponents, highest total population first (ties keep player order).

    A stable descending-population sort over players-insertion order makes
    ``result[0]`` equal to ``highest_population_opponent`` exactly (max() returns
    the first maximal element in iteration order). The engine offers options in
    this order so a pick-first heuristic reproduces the V1 target policy.
    """
    opponents = [
        other_id
        for other_id, other in state.players.items()
        if other_id != player_id and other.alive
    ]
    opponents.sort(key=lambda pid: -sum(state.players[pid].population))
    return opponents


def highest_population_opponent(state: GameState, player_id: str) -> str | None:
    """Return the living opponent with the most population, or None if none."""
    ordered = opponents_by_population(state, player_id)
    return ordered[0] if ordered else None


__all__ = ["highest_population_opponent", "opponents_by_population"]
