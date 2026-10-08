"""Decision-point types for the agent-driven engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from nuclear_war_env.action_models import LegalAction


class DecisionType(StrEnum):
    SETUP_PLACE = "setup_place"
    STRATEGY_REPLACE = "strategy_replace"
    PLACE = "place"
    LAUNCH_TARGET = "launch_target"
    SECRET_TARGET = "secret_target"
    PROPAGANDA_TARGET = "propaganda_target"
    FINAL_STRIKE_TARGET = "final_strike_target"
    INTERCEPT = "intercept"
    MODIFY_DETERRENT = "modify_deterrent"
    PASS = "pass"


class TurnPhase(StrEnum):
    SETUP = "setup"
    DRAW = "draw"
    SECRETS = "secrets"
    SLIDE = "slide"
    PROPAGANDA = "propaganda"
    DETERRENTS = "deterrents"
    PLACE = "place"
    ATTACK = "attack"
    INTERCEPT = "intercept"
    FINAL_STRIKE = "final_strike"
    END = "end"


@dataclass(frozen=True)
class Decision:
    agent_id: str
    decision_type: DecisionType
    options: list[LegalAction]
    context: dict[str, Any] = field(default_factory=dict)


@dataclass
class DecisionCursor:
    turn_player: str
    phase: TurnPhase
    pending: Decision | None = None
    # Players not yet given a turn in the CURRENT round. Mirrors the `pending` set
    # in simulation_turns.turn_player_ids (which seeds it with *every* player and
    # discards each as it is yielded) so the loop reproduces the exact clockwise /
    # interception turn order: an override (state.next_player_id) is honored only
    # while that player is still pending, and the round ends when the set empties.
    round_pending: set[str] = field(default_factory=set)
    # 1-based round counter (a round is one full clockwise pass of the players).
    # The legacy table runner numbered replay turns by round, so the loop stamps
    # actions/events with this and increments it when a round completes.
    round: int = 1
    resume_phase: TurnPhase | None = None
    # Last peace value the loop observed. A False->True transition means peace
    # was just restored, which opens the strategy-replacement window (each
    # player may replace one or two face-down cards with hand cards).
    peace_seen: bool = True


__all__ = ["DecisionType", "TurnPhase", "Decision", "DecisionCursor"]
