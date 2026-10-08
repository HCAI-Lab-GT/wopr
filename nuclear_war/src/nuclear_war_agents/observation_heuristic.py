"""Observation-driven table heuristic agent."""

from __future__ import annotations

from dataclasses import dataclass

from nuclear_war_env.action_models import ActionType, LegalAction
from nuclear_war_env.observation import Observation

_TARGET_TYPES = {
    ActionType.TARGET,
    ActionType.SECRET_TARGET,
    ActionType.PROPAGANDA_TARGET,
    ActionType.FINAL_STRIKE_TARGET,
}

_FALLBACK_PRIORITY = [
    ActionType.RESOLVE,
    ActionType.INTERCEPT,
    ActionType.FINAL_STRIKE_TARGET,
    ActionType.TARGET,
    ActionType.SECRET_TARGET,
    ActionType.PROPAGANDA_TARGET,
    ActionType.POSTAL_PROPAGANDA,
    ActionType.ADVANCE,
    ActionType.MODIFY_DETERRENT,
    ActionType.ENQUEUE,
    ActionType.SETUP_PLACE,
    ActionType.STRATEGY_REPLACE,
    ActionType.DRAW,
    ActionType.PASS,
]


@dataclass(frozen=True)
class ObservationHeuristicAgent:
    def choose(
        self,
        observation: Observation,
        options: list[LegalAction],
    ) -> LegalAction:
        if not options:
            raise ValueError("ObservationHeuristicAgent requires at least one option")
        intercept = _intercept_option(options)
        if intercept is not None:
            return intercept
        target = _highest_population_target(observation, options)
        if target is not None:
            return target
        return _priority_option(options)


def _intercept_option(options: list[LegalAction]) -> LegalAction | None:
    intercepts = [
        option for option in options if option.action_type is ActionType.INTERCEPT
    ]
    if not intercepts:
        return None
    for option in intercepts:
        if isinstance(option.payload.get("card"), str):
            return option
    return intercepts[0]


def _highest_population_target(
    observation: Observation,
    options: list[LegalAction],
) -> LegalAction | None:
    best: LegalAction | None = None
    best_population = -1
    for option in options:
        if option.action_type not in _TARGET_TYPES:
            continue
        target_id = option.payload.get("target")
        if not isinstance(target_id, str) or target_id not in observation.players:
            continue
        population = observation.players[target_id].population
        if population > best_population:
            best = option
            best_population = population
    return best


def _priority_option(options: list[LegalAction]) -> LegalAction:
    for action_type in _FALLBACK_PRIORITY:
        for option in options:
            if option.action_type is action_type:
                return option
    return options[0]


__all__ = ["ObservationHeuristicAgent"]
