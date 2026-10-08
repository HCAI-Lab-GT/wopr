"""Aggregation rules for faction C2 archetypes.

Each function is pure: votes in, selected action id and rule label out.
The composite FactionDecisionAgent calls the one matching its archetype.
"""

from __future__ import annotations

from math import isclose

from .faction_types import SubordinateVote

_THRESHOLD_ABS_TOLERANCE = 5e-11


def aggregate_council(
    votes: list[SubordinateVote],
    weights: dict[str, float] | None,
    threshold: float,
) -> tuple[str, str]:
    if not votes:
        raise ValueError("council requires at least one vote")
    resolved_weights = _resolve_weights(votes, weights)
    scores: dict[str, float] = {}
    for vote in votes:
        scores[vote.action_id] = (
            scores.get(vote.action_id, 0.0) + resolved_weights[vote.member_id]
        )
    total = sum(resolved_weights[vote.member_id] for vote in votes)
    ordered = [vote.action_id for vote in votes]
    winner = max(
        scores, key=lambda action_id: (scores[action_id], -ordered.index(action_id))
    )
    winning_share = scores[winner] / total
    if winning_share < threshold and not isclose(
        winning_share,
        threshold,
        rel_tol=0.0,
        abs_tol=_THRESHOLD_ABS_TOLERANCE,
    ):
        return ordered[0], "threshold_not_met_default"
    return winner, "weighted_majority"


def _resolve_weights(
    votes: list[SubordinateVote], weights: dict[str, float] | None
) -> dict[str, float]:
    if weights is None:
        member_ids = {vote.member_id for vote in votes}
        equal = 1.0 / len(member_ids) if member_ids else 0.0
        return {member_id: equal for member_id in member_ids}
    missing = [vote.member_id for vote in votes if vote.member_id not in weights]
    if missing:
        raise ValueError(f"council member missing weight: {missing[0]}")
    return weights


def aggregate_sole_authority(
    votes: list[SubordinateVote],
    deference: float,
) -> tuple[str, str]:
    executive = next((v for v in votes if v.member_id == "executive"), None)
    if executive is None:
        raise ValueError("sole_authority requires an 'executive' member")
    staff = [v for v in votes if v.member_id != "executive"]
    if not staff or deference <= 0.0:
        return executive.action_id, "executive_override"
    if deference >= 1.0:
        return staff[0].action_id, "deferred_to_staff"
    return executive.action_id, "executive_override"


def aggregate_distributed(
    votes: list[SubordinateVote],
    quorum: int,
    pass_action_id: str,
) -> tuple[str, str]:
    if not votes:
        raise ValueError("distributed requires at least one vote")
    release_votes = [v for v in votes if v.action_id != pass_action_id]
    if not release_votes:
        return pass_action_id, "quorum_not_met"
    distinct_releases = {v.action_id for v in release_votes}
    if len(distinct_releases) < quorum:
        return pass_action_id, "quorum_not_met"
    return release_votes[0].action_id, "any_holder_release"


def aggregate_automated(policy_action_id: str) -> tuple[str, str]:
    return policy_action_id, "pre_armed_policy"


__all__ = [
    "aggregate_automated",
    "aggregate_council",
    "aggregate_distributed",
    "aggregate_sole_authority",
]
