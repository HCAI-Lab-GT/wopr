"""Composite faction C2 decision agents.

A faction is a DecisionAgent whose choose runs an internal aggregation over
subordinate opinions and returns one LegalAction. The engine sees one action
per decision, identical to a single-agent seat.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.agent_protocol import DecisionAgent
from nuclear_war_env.observation import Observation

from .faction_aggregation import (
    aggregate_automated,
    aggregate_council,
    aggregate_distributed,
    aggregate_sole_authority,
)
from .faction_members import (
    DirectMemberFactory,
    ScriptedSubordinateFactory,
    SubordinateFactory,
)
from .faction_types import FactionDeliberation, SubordinateVote
from .llm_agent_fallback import decision_type
from .llm_types import TraceRecorder


@dataclass
class FactionDecisionAgent:
    archetype: str
    subordinate_factory: SubordinateFactory
    archetype_parameters: dict[str, Any] = field(default_factory=dict)
    # Reserved for a future faction-level consolidated trace; deliberations
    # currently remain on the agent as the latest item and complete history.
    recorder: TraceRecorder | None = None
    last_deliberation: FactionDeliberation | None = None
    deliberations: list[FactionDeliberation] = field(default_factory=list)
    _members: tuple[tuple[str, DecisionAgent], ...] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._members = tuple(self.subordinate_factory.build_members())

    def choose(
        self,
        observation: Observation,
        options: list[LegalAction],
    ) -> LegalAction:
        self.last_deliberation = None
        votes = self._collect_votes(observation, options)
        selected_id, rule = self._aggregate(votes, options)
        legal = {option.action_id: option for option in options}
        if selected_id not in legal:
            # A pre-armed automated policy id (aggregate_automated) may not be
            # legal at every decision, since action ids embed payloads. Fall back
            # to the first legal option and record the fallback in the
            # deliberation rather than crashing the game.
            rule = f"{rule}_illegal_fallback_first"
            selected_id = options[0].action_id
        deliberation = FactionDeliberation(
            player_id=observation.player_id,
            turn=observation.turn,
            decision_type=decision_type(observation),
            archetype=self.archetype,
            member_votes=votes,
            selected_action_id=selected_id,
            rule=rule,
            parameters=dict(self.archetype_parameters),
        )
        self.deliberations.append(deliberation)
        self.last_deliberation = deliberation
        return legal[selected_id]

    def _collect_votes(
        self,
        observation: Observation,
        options: list[LegalAction],
    ) -> list[SubordinateVote]:
        votes: list[SubordinateVote] = []
        for member_id, member in self._members:
            selected = member.choose(observation, options)
            votes.append(
                SubordinateVote(
                    member_id=member_id,
                    action_id=selected.action_id,
                    rationale=None,
                )
            )
        return votes

    def _aggregate(
        self,
        votes: list[SubordinateVote],
        options: list[LegalAction],
    ) -> tuple[str, str]:
        if self.archetype == "council":
            return aggregate_council(
                votes,
                self.archetype_parameters.get("weights"),
                self.archetype_parameters.get("threshold", 0.5),
            )
        if self.archetype == "sole_authority":
            return aggregate_sole_authority(
                votes,
                self.archetype_parameters.get("deference", 0.0),
            )
        if self.archetype == "distributed":
            return aggregate_distributed(
                votes,
                self.archetype_parameters.get("quorum", 1),
                _pass_action_id(options),
            )
        if self.archetype == "automated":
            policy_action_id = self.archetype_parameters.get("policy_action_id")
            if not isinstance(policy_action_id, str) or not policy_action_id:
                raise ValueError(
                    "automated archetype requires a policy_action_id parameter"
                )
            return aggregate_automated(policy_action_id)
        raise ValueError(f"Unknown faction archetype: {self.archetype}")


def _pass_action_id(options: list[LegalAction]) -> str:
    for option in options:
        if option.action_type.value == "pass":
            return option.action_id
    return options[0].action_id


__all__ = [
    "DirectMemberFactory",
    "FactionDecisionAgent",
    "ScriptedSubordinateFactory",
    "SubordinateFactory",
]
