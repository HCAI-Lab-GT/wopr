"""Pure aggregation replay for C2 deliberation sidecars."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, cast

from nuclear_war_agents import (
    SubordinateVote,
    aggregate_council,
    aggregate_sole_authority,
)

from .authority_parameters import normalized_authority_parameters


def validate_c2_aggregation(deliberation: dict[str, Any], index: int) -> None:
    members = deliberation["members"]
    member_ids = [member["member_id"] for member in members]
    votes = [
        SubordinateVote(
            member_id=member["member_id"],
            action_id=member["vote_action_id"],
        )
        for member in members
    ]
    archetype = deliberation["archetype"]
    parameters = deliberation["parameters"]
    if not isinstance(archetype, str) or not isinstance(parameters, Mapping):
        raise ValueError(f"C2 deliberation {index} authority fields are invalid")
    normalized = normalized_authority_parameters(
        archetype,
        parameters,
        member_ids,
        f"C2 deliberation {index}",
    )
    selected_action_id, rule = _aggregate(archetype, votes, normalized)
    if (selected_action_id, rule) != (
        deliberation["selected_action_id"],
        deliberation["rule"],
    ):
        raise ValueError(
            f"C2 deliberation {index} aggregation does not reproduce selection"
        )


def _aggregate(
    archetype: str,
    votes: list[SubordinateVote],
    parameters: dict[str, object],
) -> tuple[str, str]:
    if archetype == "sole_authority":
        return aggregate_sole_authority(votes, cast(float, parameters["deference"]))
    if archetype == "council":
        return aggregate_council(
            votes,
            cast(dict[str, float], parameters["weights"]),
            cast(float, parameters["threshold"]),
        )
    raise ValueError(f"C2 artifact authority archetype is invalid: {archetype}")


__all__ = ["validate_c2_aggregation"]
