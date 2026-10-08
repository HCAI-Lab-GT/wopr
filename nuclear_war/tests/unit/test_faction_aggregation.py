"""Faction C2 aggregation rule tests."""

from __future__ import annotations

import pytest

from nuclear_war_agents.faction_aggregation import (
    aggregate_automated,
    aggregate_council,
    aggregate_distributed,
    aggregate_sole_authority,
)
from nuclear_war_agents.faction_types import SubordinateVote


def test_council_picks_majority_action_id() -> None:
    votes = [
        SubordinateVote("a", "p1:pass", "hold"),
        SubordinateVote("b", "p1:pass", "hold"),
        SubordinateVote("c", "p1:target:p3", "strike"),
    ]

    selected, rule = aggregate_council(votes, weights=None, threshold=0.5)

    assert selected == "p1:pass"
    assert rule == "weighted_majority"


def test_council_respects_equal_weights_by_default() -> None:
    votes = [
        SubordinateVote("a", "p1:target:p3", "strike"),
        SubordinateVote("b", "p1:target:p3", "strike"),
        SubordinateVote("c", "p1:pass", "hold"),
    ]

    selected, _ = aggregate_council(votes, weights=None, threshold=0.5)

    assert selected == "p1:target:p3"


def test_council_applies_custom_weights() -> None:
    votes = [
        SubordinateVote("a", "p1:pass", "hold"),
        SubordinateVote("b", "p1:target:p3", "strike"),
    ]
    weights = {"a": 0.2, "b": 0.8}

    selected, _ = aggregate_council(votes, weights=weights, threshold=0.5)

    assert selected == "p1:target:p3"


def test_council_threshold_blocks_minority() -> None:
    votes = [
        SubordinateVote("a", "p1:pass", "hold"),
        SubordinateVote("b", "p1:target:p3", "strike"),
    ]
    weights = {"a": 0.6, "b": 0.4}

    selected, rule = aggregate_council(votes, weights=weights, threshold=0.5)

    assert selected == "p1:pass"
    assert rule == "weighted_majority"


def test_council_threshold_not_met_defaults_to_first_vote() -> None:
    votes = [
        SubordinateVote("a", "p1:pass", "hold"),
        SubordinateVote("b", "p1:target:p2", "strike"),
        SubordinateVote("c", "p1:target:p3", "strike"),
    ]

    selected, rule = aggregate_council(votes, weights=None, threshold=0.5)

    assert selected == "p1:pass"
    assert rule == "threshold_not_met_default"


def test_equal_council_locked_threshold_rejects_a_minority() -> None:
    votes = [
        SubordinateVote("executive", "hold"),
        SubordinateVote("strategic_advisor", "release"),
        SubordinateVote("risk_advisor", "escalate"),
    ]

    selected, rule = aggregate_council(
        votes,
        weights={
            "executive": 1.0,
            "strategic_advisor": 1.0,
            "risk_advisor": 1.0,
        },
        threshold=0.6666666667,
    )

    assert selected == "hold"
    assert rule == "threshold_not_met_default"


def test_council_tie_breaks_to_first_vote() -> None:
    votes = [
        SubordinateVote("a", "p1:pass", "hold"),
        SubordinateVote("b", "p1:target:p3", "strike"),
    ]

    selected, _ = aggregate_council(votes, weights=None, threshold=0.5)

    assert selected == "p1:pass"


def test_council_empty_votes_raises() -> None:
    with pytest.raises(ValueError, match="council requires at least one vote"):
        aggregate_council([], weights=None, threshold=0.5)


def test_council_unknown_member_weight_raises() -> None:
    votes = [SubordinateVote("a", "p1:pass")]
    weights = {"z": 1.0}

    with pytest.raises(ValueError, match="missing weight"):
        aggregate_council(votes, weights=weights, threshold=0.5)


def test_sole_authority_defers_to_first_advisor_when_deference_high() -> None:
    votes = [
        SubordinateVote("executive", "p1:pass", "hold"),
        SubordinateVote("advisor_a", "p1:target:p3", "strike"),
    ]

    selected, rule = aggregate_sole_authority(votes, deference=1.0)

    assert selected == "p1:target:p3"
    assert rule == "deferred_to_staff"


def test_sole_authority_keeps_executive_when_deference_zero() -> None:
    votes = [
        SubordinateVote("executive", "p1:pass", "hold"),
        SubordinateVote("advisor_a", "p1:target:p3", "strike"),
    ]

    selected, rule = aggregate_sole_authority(votes, deference=0.0)

    assert selected == "p1:pass"
    assert rule == "executive_override"


def test_sole_authority_requires_executive_member() -> None:
    votes = [SubordinateVote("advisor_a", "p1:pass")]

    with pytest.raises(ValueError, match="executive"):
        aggregate_sole_authority(votes, deference=0.0)


def test_sole_authority_no_staff_keeps_executive() -> None:
    votes = [SubordinateVote("executive", "p1:pass")]

    selected, _ = aggregate_sole_authority(votes, deference=1.0)

    assert selected == "p1:pass"


def test_distributed_releases_if_any_holder_authorizes() -> None:
    votes = [
        SubordinateVote("holder_a", "p1:pass", "no_release"),
        SubordinateVote("holder_b", "p1:target:p3", "release"),
    ]

    selected, rule = aggregate_distributed(votes, quorum=1, pass_action_id="p1:pass")

    assert selected == "p1:target:p3"
    assert rule == "any_holder_release"


def test_distributed_requires_quorum_for_multi_holder() -> None:
    votes = [
        SubordinateVote("holder_a", "p1:target:p3", "release"),
        SubordinateVote("holder_b", "p1:pass", "no_release"),
        SubordinateVote("holder_c", "p1:pass", "no_release"),
    ]

    selected, rule = aggregate_distributed(votes, quorum=2, pass_action_id="p1:pass")

    assert selected == "p1:pass"
    assert rule == "quorum_not_met"


def test_distributed_empty_votes_raises() -> None:
    with pytest.raises(ValueError, match="distributed requires at least one vote"):
        aggregate_distributed([], quorum=1, pass_action_id="p1:pass")


def test_distributed_convention_release_is_first_release_action() -> None:
    votes = [
        SubordinateVote("holder_a", "p1:target:p3", "release"),
        SubordinateVote("holder_b", "p1:target:p2", "release"),
    ]

    selected, rule = aggregate_distributed(votes, quorum=1, pass_action_id="p1:pass")

    assert selected == "p1:target:p3"
    assert rule == "any_holder_release"


def test_automated_returns_pre_armed_policy_action() -> None:
    selected, rule = aggregate_automated(policy_action_id="p1:target:p3")

    assert selected == "p1:target:p3"
    assert rule == "pre_armed_policy"
