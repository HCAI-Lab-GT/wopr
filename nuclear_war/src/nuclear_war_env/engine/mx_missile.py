"""MX missile launch resolution."""

from __future__ import annotations

from nuclear_war_env.fallout import (
    FalloutOutcome,
    SpinnerEffect,
    is_fallout_cloud,
    roll_fallout_die,
)
from nuclear_war_env.state import GameState

from .events import EngineEvent
from .launch_resolution import resolve_unblocked_launch
from .spinner_events import fallout_die_result_event

# The postal rules: each 10 megaton segment "destroys 2 million people, plus
# whatever is rolled on the die." The base loss is added to the die face.
MX_SEGMENT_BASE_DAMAGE = 2

# A successful (non-cloud) segment applies its precomputed 2 + die damage as a
# plain population strike: no yield multiplier, no target adjustment, no
# attacker backfire. The die face, not the fallout chart, sets the damage.
_MX_SEGMENT_OUTCOME = FalloutOutcome(SpinnerEffect.NO_RADIATION)


def resolve_mx_launch(
    state: GameState,
    attacker_id: str,
    target_id: str,
    delivery_id: str,
    order: dict[str, object],
    total_yield: int,
    auto_resolve_final_strike: bool = True,
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for _segment in range(total_yield // 10):
        roll = roll_fallout_die(state.rng)
        events.append(fallout_die_result_event(attacker_id, None, roll))
        if is_fallout_cloud(roll):
            # A cloud is "explodes on launchpad": it cancels only this one 10Mt
            # attack (no damage, no backfire) and does not affect the others.
            continue
        segment_damage = MX_SEGMENT_BASE_DAMAGE + roll
        events.extend(
            resolve_unblocked_launch(
                state,
                attacker_id,
                target_id,
                delivery_id,
                order,
                segment_damage,
                _MX_SEGMENT_OUTCOME,
                auto_resolve_final_strike=auto_resolve_final_strike,
            )
        )
        if not state.players[target_id].alive:
            break
    return events


__all__ = ["resolve_mx_launch"]
