"""Random and heuristic baseline agents."""

from __future__ import annotations

from dataclasses import dataclass

from nuclear_war_env.actions import ActionType, LegalAction
from nuclear_war_env.rng import SeededRNG


@dataclass
class RandomAgent:
    rng: SeededRNG

    def choose(self, actions: list[LegalAction]) -> LegalAction:
        return self.rng.choose(actions)


@dataclass
class HeuristicAgent:
    rng: SeededRNG

    def choose(self, actions: list[LegalAction]) -> LegalAction:
        priority = [
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
            # Setup/peace-window decisions: options[0] preserves legacy behavior
            # (setup: hand order == old hand[:2]; strategy replace: decline first).
            ActionType.SETUP_PLACE,
            ActionType.STRATEGY_REPLACE,
            ActionType.DRAW,
            ActionType.PASS,
        ]
        for action_type in priority:
            matching = [
                action for action in actions if action.action_type is action_type
            ]
            if matching:
                return matching[0]
        return self.rng.choose(actions)
