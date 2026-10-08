"""Postal execution orchestrator."""

from __future__ import annotations

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState

from .handlers import PHASE_HANDLERS


def execute_postal_turn(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for phase_name, handler in PHASE_HANDLERS:
        phase_events = handler(state)
        events.extend(phase_events)
        events.append(
            EngineEvent(
                "phase_complete",
                None,
                None,
                {"phase": phase_name},
            )
        )
    return events


__all__ = ["execute_postal_turn", "PHASE_HANDLERS"]
