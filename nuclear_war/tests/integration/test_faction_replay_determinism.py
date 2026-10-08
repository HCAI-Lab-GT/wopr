"""Faction seat replay determinism regression."""

from __future__ import annotations

from nuclear_war_env.llm_harness import (
    LLMSeatConfig,
    NoPressLLMGameConfig,
    run_no_press_llm_game,
)


def _config() -> NoPressLLMGameConfig:
    return NoPressLLMGameConfig(
        players=2,
        seed=7,
        max_turns=3,
        seats={
            "player_0": LLMSeatConfig(
                agent="faction_c2",
                archetype="council",
                archetype_parameters={"threshold": 0.5},
                members=(
                    {"member_id": "advisor_a", "agent": "llm_first_legal"},
                    {"member_id": "advisor_b", "agent": "llm_first_legal"},
                ),
            ),
            "player_1": LLMSeatConfig(agent="heuristic"),
        },
    )


def test_faction_replay_determinism() -> None:
    first = run_no_press_llm_game(_config())
    second = run_no_press_llm_game(_config())

    assert first["replay"] == second["replay"]
    assert first["trace_artifact"] == second["trace_artifact"]
