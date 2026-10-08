"""Support phases and utilities for postal execution."""

from __future__ import annotations

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.war_state import (
    restore_peace,
    restore_peace_after_completed_eliminations,
)
from nuclear_war_env.state import GameState


def phase_peace(state: GameState) -> list[EngineEvent]:
    if restore_peace_after_completed_eliminations(state):
        return [EngineEvent("peace_restored", None)]
    votes = []
    for player in state.players.values():
        vote = player.pending_orders.pop("vote_peace", False)
        if player.alive:
            votes.append(vote)
    if votes and all(votes):
        restore_peace(state)
        return [EngineEvent("peace_restored", None)]
    return []


def phase_press(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        for message in player.pending_orders.pop("press", []):
            if not state.press_enabled:
                continue
            events.append(
                EngineEvent(
                    "press_entry",
                    player.player_id,
                    None,
                    {"message": message},
                )
            )
    return events


def phase_empty(_: GameState) -> list[EngineEvent]:
    return []


__all__ = ["phase_peace", "phase_press", "phase_empty"]
