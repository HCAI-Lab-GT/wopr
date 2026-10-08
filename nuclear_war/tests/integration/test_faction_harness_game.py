"""End-to-end faction_c2 harness game tests."""

from __future__ import annotations

from nuclear_war_env.llm_harness import (
    LLMSeatConfig,
    NoPressLLMGameConfig,
    run_no_press_llm_game,
)
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact


def test_faction_c2_seat_runs_full_game_and_validates_trace() -> None:
    config = NoPressLLMGameConfig(
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

    result = run_no_press_llm_game(config)
    replay = result["replay"]

    assert replay["players"] == 2
    assert result["trace_artifact"]["schema_version"] == 5
    validate_trace_artifact(result["trace_artifact"], replay)
    faction_actions = [a for a in replay["actions"] if a["player_id"] == "player_0"]
    assert len(faction_actions) > 0
    assert replay["winner"] is not None or replay["turns"] == config.max_turns


def test_faction_c2_sole_authority_seat_runs_full_game() -> None:
    config = NoPressLLMGameConfig(
        players=2,
        seed=7,
        max_turns=3,
        seats={
            "player_0": LLMSeatConfig(
                agent="faction_c2",
                archetype="sole_authority",
                archetype_parameters={"deference": 0.0},
                members=(
                    {"member_id": "executive", "agent": "llm_first_legal"},
                    {"member_id": "advisor_a", "agent": "llm_first_legal"},
                ),
            ),
            "player_1": LLMSeatConfig(agent="heuristic"),
        },
    )

    result = run_no_press_llm_game(config)
    replay = result["replay"]

    assert replay["players"] == 2
    assert result["trace_artifact"]["schema_version"] == 5
    validate_trace_artifact(result["trace_artifact"], replay)
    faction_actions = [a for a in replay["actions"] if a["player_id"] == "player_0"]
    assert len(faction_actions) > 0
    assert replay["winner"] is not None or replay["turns"] == config.max_turns


def test_faction_c2_distributed_seat_runs_full_game() -> None:
    config = NoPressLLMGameConfig(
        players=2,
        seed=7,
        max_turns=3,
        seats={
            "player_0": LLMSeatConfig(
                agent="faction_c2",
                archetype="distributed",
                archetype_parameters={"quorum": 1},
                members=(
                    {"member_id": "holder_a", "agent": "llm_first_legal"},
                    {"member_id": "holder_b", "agent": "llm_first_legal"},
                ),
            ),
            "player_1": LLMSeatConfig(agent="heuristic"),
        },
    )

    result = run_no_press_llm_game(config)
    replay = result["replay"]

    assert replay["players"] == 2
    assert result["trace_artifact"]["schema_version"] == 5
    validate_trace_artifact(result["trace_artifact"], replay)
    faction_actions = [a for a in replay["actions"] if a["player_id"] == "player_0"]
    assert len(faction_actions) > 0
    assert replay["winner"] is not None or replay["turns"] == config.max_turns
