"""faction_c2 harness seat construction tests."""

from __future__ import annotations

import pytest

from nuclear_war_agents import TraceRecorder
from nuclear_war_env.llm_harness import LLMSeatConfig
from nuclear_war_env.llm_harness_seats import (
    FACTION_C2_SEAT,
    build_llm_harness_agent,
    known_llm_harness_seats,
)
from nuclear_war_env.rng import SeededRNG


def test_faction_c2_seat_is_known() -> None:
    assert FACTION_C2_SEAT in known_llm_harness_seats()


def test_faction_c2_seat_builds_faction_agent() -> None:
    seat = LLMSeatConfig(
        agent=FACTION_C2_SEAT,
        archetype="council",
        archetype_parameters={"threshold": 0.5},
        members=(
            {
                "member_id": "advisor_a",
                "agent": "llm_scripted",
                "scripted_responses": ['{"action_id": "p1:pass"}'],
            },
            {
                "member_id": "advisor_b",
                "agent": "llm_scripted",
                "scripted_responses": ['{"action_id": "p1:pass"}'],
            },
            {
                "member_id": "advisor_c",
                "agent": "llm_scripted",
                "scripted_responses": ['{"action_id": "p1:pass"}'],
            },
        ),
    )

    agent = build_llm_harness_agent(seat, SeededRNG(1), TraceRecorder())

    assert agent.__class__.__name__ == "FactionDecisionAgent"


def test_faction_c2_seat_first_legal_members_build() -> None:
    seat = LLMSeatConfig(
        agent=FACTION_C2_SEAT,
        archetype="council",
        archetype_parameters={"threshold": 0.5},
        members=(
            {"member_id": "advisor_a", "agent": "llm_first_legal"},
            {"member_id": "advisor_b", "agent": "llm_first_legal"},
        ),
    )

    agent = build_llm_harness_agent(seat, SeededRNG(1), TraceRecorder())

    assert agent.__class__.__name__ == "FactionDecisionAgent"


def test_faction_c2_seat_rejects_unknown_member_agent() -> None:
    seat = LLMSeatConfig(
        agent=FACTION_C2_SEAT,
        archetype="council",
        members=({"member_id": "advisor_a", "agent": "bogus"},),
    )

    with pytest.raises(ValueError, match="faction_c2 member"):
        build_llm_harness_agent(seat, SeededRNG(1), TraceRecorder())


def test_faction_c2_seat_requires_archetype() -> None:
    seat = LLMSeatConfig(
        agent=FACTION_C2_SEAT,
        archetype=None,
        members=({"member_id": "advisor_a", "agent": "llm_first_legal"},),
    )

    with pytest.raises(ValueError, match="archetype"):
        build_llm_harness_agent(seat, SeededRNG(1), TraceRecorder())
