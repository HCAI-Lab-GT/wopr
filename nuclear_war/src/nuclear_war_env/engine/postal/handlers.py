"""Aggregates postal phase handlers."""

from __future__ import annotations

from collections.abc import Callable

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.state import GameState

from .handlers_early import (
    phase_espionage,
    phase_final_strike,
    phase_flip_queue,
    phase_secrets,
)
from .handlers_launch import (
    phase_declare_targets,
    phase_intercept,
    phase_launch,
    phase_nuking,
    phase_sabotage,
)
from .handlers_misc import (
    phase_cruise_move,
    phase_enqueue,
    phase_propaganda,
    phase_space_platforms,
    phase_specials,
    phase_submarines,
)
from .handlers_support import phase_peace, phase_press

PostalHandler = Callable[[GameState], list[EngineEvent]]

PHASE_HANDLERS: list[tuple[str, PostalHandler]] = [
    ("espionage", phase_espionage),
    ("secrets", phase_secrets),
    ("final_strike", phase_final_strike),
    ("flip_queue", phase_flip_queue),
    ("declare_targets", phase_declare_targets),
    ("sabotage", phase_sabotage),
    ("launch", phase_launch),
    ("intercept", phase_intercept),
    ("nuking", phase_nuking),
    ("space_platforms", phase_space_platforms),
    ("submarines", phase_submarines),
    ("cruise_move", phase_cruise_move),
    ("propaganda", phase_propaganda),
    ("specials", phase_specials),
    ("peace", phase_peace),
    ("enqueue", phase_enqueue),
    ("press", phase_press),
]


__all__ = ["PHASE_HANDLERS"]
