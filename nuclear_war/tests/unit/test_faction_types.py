"""Faction C2 shared type tests."""

from __future__ import annotations

from nuclear_war_agents.faction_types import (
    FactionConfig,
    FactionDeliberation,
    SubordinateVote,
)


def test_subordinate_vote_holds_action_id_and_rationale() -> None:
    vote = SubordinateVote(
        member_id="advisor_a",
        action_id="p1:pass",
        rationale="hold",
    )

    assert vote.member_id == "advisor_a"
    assert vote.action_id == "p1:pass"
    assert vote.rationale == "hold"


def test_faction_deliberation_records_members_and_selected() -> None:
    votes = [
        SubordinateVote("advisor_a", "p1:pass", "hold"),
        SubordinateVote("advisor_b", "p1:target:p3", "strike"),
    ]
    deliberation = FactionDeliberation(
        player_id="p1",
        turn=3,
        decision_type="launch_target",
        archetype="council",
        member_votes=votes,
        selected_action_id="p1:target:p3",
        rule="weighted_majority",
    )

    assert deliberation.player_id == "p1"
    assert deliberation.turn == 3
    assert deliberation.decision_type == "launch_target"
    assert deliberation.archetype == "council"
    assert len(deliberation.member_votes) == 2
    assert deliberation.selected_action_id == "p1:target:p3"
    assert deliberation.rule == "weighted_majority"


def test_faction_deliberation_legacy_constructor_defaults_context() -> None:
    deliberation = FactionDeliberation(
        "council",
        [SubordinateVote("advisor", "p1:pass")],
        "p1:pass",
        "weighted_majority",
    )

    assert deliberation.player_id == ""
    assert deliberation.turn == 0
    assert deliberation.decision_type == "none"


def test_faction_config_carries_archetype_and_parameters() -> None:
    config = FactionConfig(archetype="council", parameters={"threshold": 0.5})

    assert config.archetype == "council"
    assert config.parameters == {"threshold": 0.5}
