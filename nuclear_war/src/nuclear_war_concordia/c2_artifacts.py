"""Validated C2 deliberation sidecar artifacts."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any

from nuclear_war_agents import FactionDecisionAgent, FactionDeliberation

from .c2_validation import (
    C2_SCHEMA_VERSION,
    c2_replay_reference,
    validate_c2_artifact,
)
from .harness_seat_runtime import ConcordiaSeatRuntime


def build_c2_artifact(
    replay: dict[str, Any],
    runtimes: Mapping[str, ConcordiaSeatRuntime],
) -> dict[str, Any]:
    payload = {
        "schema_version": C2_SCHEMA_VERSION,
        "replay": c2_replay_reference(replay),
        "authority_players": sorted(
            player_id
            for player_id, runtime in runtimes.items()
            if isinstance(runtime.strategic_agent, FactionDecisionAgent)
        ),
        "deliberations": [
            item
            for player_id, runtime in runtimes.items()
            for item in _runtime_deliberations(player_id, runtime)
        ],
    }
    validate_c2_artifact(payload, replay)
    return payload


def _runtime_deliberations(
    player_id: str,
    runtime: ConcordiaSeatRuntime,
) -> list[dict[str, Any]]:
    agent = runtime.strategic_agent
    if not isinstance(agent, FactionDecisionAgent):
        if runtime.member_traces:
            raise ValueError(f"C2 runtime {player_id} requires a faction agent")
        return []
    _validate_trace_counts(player_id, agent.deliberations, runtime.member_traces)
    return [
        _deliberation_payload(player_id, index, item, runtime.member_traces)
        for index, item in enumerate(agent.deliberations)
    ]


def _validate_trace_counts(
    player_id: str,
    deliberations: list[FactionDeliberation],
    member_traces: Mapping[str, list[dict[str, Any]]],
) -> None:
    if len(member_traces) != 3:
        raise ValueError(
            f"C2 runtime {player_id} requires exactly three member trace sinks"
        )
    trace_member_ids = set(member_traces)
    for deliberation in deliberations:
        vote_member_ids = {vote.member_id for vote in deliberation.member_votes}
        if vote_member_ids != trace_member_ids:
            raise ValueError(f"C2 runtime {player_id} member trace keys mismatch")
    for member_id, traces in member_traces.items():
        if len(traces) != len(deliberations):
            raise ValueError(
                f"C2 runtime {player_id} member {member_id} trace count mismatch"
            )


def _deliberation_payload(
    player_id: str,
    index: int,
    deliberation: FactionDeliberation,
    member_traces: Mapping[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    members = [
        {
            "member_id": vote.member_id,
            "vote_action_id": vote.action_id,
            "trace_ref": f"c2:{player_id}:{index + 1}:{vote.member_id}",
            "trace": deepcopy(member_traces[vote.member_id][index]),
        }
        for vote in deliberation.member_votes
    ]
    return {
        "deliberation_id": f"c2:{player_id}:{index + 1}",
        "player_id": deliberation.player_id,
        "turn": deliberation.turn,
        "decision_type": deliberation.decision_type,
        "archetype": deliberation.archetype,
        "parameters": deepcopy(deliberation.parameters),
        "rule": deliberation.rule,
        "selected_action_id": deliberation.selected_action_id,
        "members": members,
    }


__all__ = [
    "C2_SCHEMA_VERSION",
    "build_c2_artifact",
    "validate_c2_artifact",
]
