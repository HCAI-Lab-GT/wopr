"""Space platform handling for postal play."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.engine.events import EngineEvent
from nuclear_war_env.engine.launch_helpers import schedule_final_retaliation
from nuclear_war_env.engine.spinner_events import (
    fallout_die_result_event,
    spinner_result_event,
)
from nuclear_war_env.engine.target_policy import highest_population_opponent
from nuclear_war_env.engine.war_state import declare_war, mark_peace_restore_pending
from nuclear_war_env.fallout import (
    FalloutOutcome,
    is_fallout_cloud,
    roll_fallout_die,
    spin_spinner,
)
from nuclear_war_env.population import remove_population_with_bank
from nuclear_war_env.state import GameState, PlayerState

MAX_PLATFORM_WARHEADS = 7


def apply_space_platform_orders(state: GameState) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for player in state.players.values():
        if not player.alive:
            continue
        platforms = player.pending_orders.setdefault("space_platforms", {})
        events.extend(
            _launches(state, player.player_id, platforms, player.pending_orders)
        )
        # A double-cloud crash in _launches can eliminate the owner; a corpse must
        # not go on to spin, declare war, and drop on a target.
        if not player.alive:
            continue
        events.extend(_drops(state, player.player_id, platforms, player.pending_orders))
    return events


def _launches(
    state: GameState,
    owner_id: str,
    platforms: dict[str, Any],
    orders: dict[str, Any],
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for order in orders.pop("space_platform_launch", []):
        platform_id = order.get("platform")
        warheads = order.get("warheads", [])
        if not isinstance(warheads, list) or not all(
            type(value) is int for value in warheads
        ):
            continue
        if not platform_id or not warheads:
            continue
        events.extend(
            _launch_platform(state, owner_id, str(platform_id), warheads, platforms)
        )
    return events


def _launch_platform(
    state: GameState,
    owner_id: str,
    platform_id: str,
    warheads: list[int],
    platforms: dict[str, Any],
) -> list[EngineEvent]:
    # The postal rules launch a space platform with the 6-sided Radioactive
    # Fallout die: 2 through 6 launches it, a nuclear cloud (1) is a failure.
    roll = roll_fallout_die(state.rng)
    events = [fallout_die_result_event(owner_id, platform_id, roll)]
    if not is_fallout_cloud(roll):
        platforms[platform_id] = {"warheads": warheads[:MAX_PLATFORM_WARHEADS]}
        return events + [EngineEvent("space_platform_launched", owner_id, platform_id)]
    # A cloud loses the platform and its warheads; the die is rolled again and a
    # second cloud crashes the platform into the owner for 10 million.
    second = roll_fallout_die(state.rng)
    events.append(fallout_die_result_event(owner_id, platform_id, second))
    if is_fallout_cloud(second):
        owner = state.players[owner_id]
        was_alive = owner.alive
        loss = remove_population_with_bank(state, owner_id, 10)
        events.append(
            EngineEvent("space_platform_crashed", owner_id, platform_id, {"loss": loss})
        )
        if was_alive and not owner.alive:
            events.extend(_resolve_crash_self_kill(state, owner_id, owner))
        return events
    return events + [EngineEvent("space_platform_launch_failed", owner_id, platform_id)]


def _resolve_crash_self_kill(
    state: GameState,
    owner_id: str,
    owner: PlayerState,
) -> list[EngineEvent]:
    """Log and route a launch-pad crash that destroys the owner's own population.

    The postal rules grant a final strike to any player whose population is
    destroyed except by propaganda, so a crash-kill retaliates like a warhead
    death: emit ``player_eliminated``, mark peace pending, and pool the owner's
    remaining launch cards into a final strike. This mirrors the missile-booster
    self-kill (``launch_resolution.py``); the crash branch was the lone kill site
    that skipped it, leaving a dead owner with no elimination event and breaking
    the replay's ``_validate_eliminations_have_events`` invariant.
    """
    eliminated_by = _crash_attribution(state, owner_id)
    mark_peace_restore_pending(owner)
    events = [EngineEvent("player_eliminated", owner_id, None, {"by": eliminated_by})]
    events.extend(schedule_final_retaliation(state, owner, eliminated_by=eliminated_by))
    return events


def _crash_attribution(state: GameState, owner_id: str) -> str:
    """Return a deterministic, replay-legal ``by`` for a targetless self-crash.

    A space-platform *launch* has no target, yet the replay schema forbids both a
    self and a null ``by``. V1 attributes the death to the top living opponent --
    the same country the pooled final strike targets, keeping ``by`` consistent
    with ``eliminated_by``. When the crash makes the owner the final casualty
    (no living opponent), it falls back to the first other seat so the event still
    carries a known, non-self attribution. See docs/rule_fidelity_matrix.md.
    """
    eliminator = highest_population_opponent(state, owner_id)
    if eliminator is not None:
        return eliminator
    return next(player_id for player_id in state.players if player_id != owner_id)


def _drops(
    state: GameState,
    owner_id: str,
    platforms: dict[str, Any],
    orders: dict[str, Any],
) -> list[EngineEvent]:
    events: list[EngineEvent] = []
    for order in orders.pop("space_platform_drop", []):
        platform_id = order.get("platform")
        target_id = order.get("target")
        platform = platforms.get(platform_id)
        if not isinstance(platform, dict) or target_id not in state.players:
            continue
        if not state.players[str(target_id)].alive:
            continue
        events.extend(_drop(state, owner_id, str(platform_id), target_id, platform))
        if not platform.get("warheads"):
            platforms.pop(platform_id, None)
    return events


def _drop(
    state: GameState,
    owner_id: str,
    platform_id: str,
    target_id: object,
    platform: dict[str, Any],
) -> list[EngineEvent]:
    warheads = platform.setdefault("warheads", [])
    if not warheads:
        return []
    payload = warheads[0]
    if type(payload) is not int:
        return []
    warheads.pop(0)
    roll, outcome = spin_spinner(state.rng)
    events = [_spinner_event(owner_id, platform_id, roll, outcome)]
    declare_war(state)
    effective_yield = max(0, payload * outcome.yield_multiplier + outcome.target_delta)
    if outcome.attacker_backfire or effective_yield <= 0:
        return events + [
            EngineEvent("space_platform_drop_missed", owner_id, platform_id)
        ]
    target = state.players[str(target_id)]
    loss = remove_population_with_bank(state, str(target_id), effective_yield)
    events.append(
        EngineEvent(
            "space_platform_dropped",
            owner_id,
            platform_id,
            {"target": target_id, "loss": loss, "yield": effective_yield},
        )
    )
    if not target.alive:
        events.extend(schedule_final_retaliation(state, target))
    return events


def _spinner_event(
    owner_id: str,
    platform_id: str,
    roll: int,
    outcome: FalloutOutcome,
) -> EngineEvent:
    return spinner_result_event(owner_id, platform_id, roll, outcome)


__all__ = ["apply_space_platform_orders"]
