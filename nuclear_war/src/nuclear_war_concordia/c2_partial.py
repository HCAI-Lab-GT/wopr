"""Partial authority state for failed Concordia runs."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from nuclear_war_agents import FactionDecisionAgent, FactionDeliberation

from .harness_seat_runtime import ConcordiaSeatRuntime


def build_c2_partial_state(
    runtimes: Mapping[str, ConcordiaSeatRuntime],
) -> dict[str, Any]:
    seats = {
        player_id: _seat_state(runtime)
        for player_id, runtime in runtimes.items()
        if isinstance(runtime.strategic_agent, FactionDecisionAgent)
    }
    return {
        "authority_players": sorted(seats),
        "seats": seats,
    }


def _seat_state(runtime: ConcordiaSeatRuntime) -> dict[str, Any]:
    agent = runtime.strategic_agent
    if not isinstance(agent, FactionDecisionAgent):
        raise ValueError("Partial C2 state requires a faction agent")
    return {
        "archetype": agent.archetype,
        "parameters": deepcopy(agent.archetype_parameters),
        "completed_deliberations": [
            _deliberation_state(item) for item in agent.deliberations
        ],
        "member_traces": deepcopy(runtime.member_traces),
    }


def _deliberation_state(deliberation: FactionDeliberation) -> dict[str, Any]:
    return {
        "player_id": deliberation.player_id,
        "turn": deliberation.turn,
        "decision_type": deliberation.decision_type,
        "member_votes": [
            {"member_id": vote.member_id, "action_id": vote.action_id}
            for vote in deliberation.member_votes
        ],
        "selected_action_id": deliberation.selected_action_id,
        "rule": deliberation.rule,
    }


__all__ = ["build_c2_partial_state"]
