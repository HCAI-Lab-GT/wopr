"""No-press LLM harness integration tests."""

from __future__ import annotations

import pytest

from nuclear_war_env.llm_harness import (
    LLMSeatConfig,
    NoPressLLMGameConfig,
    run_no_press_llm_game,
)
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact
from nuclear_war_env.replay_validation import validate_replay_payload


def test_no_press_llm_game_runs_mixed_seats_and_summarizes_traces() -> None:
    result = run_no_press_llm_game(
        NoPressLLMGameConfig(
            players=4,
            seed=17,
            max_turns=1,
            seats={
                "player_0": LLMSeatConfig(
                    "llm_scripted",
                    scripted_responses=(
                        "not-json",
                        '{"action_id": "player_0:draw"}',
                    ),
                ),
                "player_1": LLMSeatConfig("random"),
                "player_2": LLMSeatConfig("heuristic"),
                "player_3": LLMSeatConfig("decision_heuristic"),
            },
        )
    )

    validate_replay_payload(result["replay"])
    validate_trace_artifact(result["trace_artifact"], result["replay"])
    summary = result["summary"]
    assert result["seat_config"] == {
        "player_0": "llm_scripted",
        "player_1": "random",
        "player_2": "heuristic",
        "player_3": "decision_heuristic",
    }
    assert summary["winner"] == result["replay"]["winner"]
    assert summary["turns"] == result["replay"]["turns"]
    assert summary["elimination_order"] == result["replay"]["eliminations"]
    assert set(summary["win_loss"]) == {
        "player_0",
        "player_1",
        "player_2",
        "player_3",
    }
    assert summary["invalid_action_count"] >= 1
    assert summary["retry_count"] >= 1
    assert summary["player_decision_metrics"]["player_0"]["trace_count"] >= 1
    assert summary["player_decision_metrics"]["player_0"]["invalid_action_count"] >= 1
    assert summary["player_decision_metrics"]["player_0"]["retry_count"] >= 1
    assert summary["player_decision_metrics"]["player_0"][
        "invalid_action_rate"
    ] == pytest.approx(
        summary["player_decision_metrics"]["player_0"]["invalid_action_count"]
        / summary["player_decision_metrics"]["player_0"]["trace_count"]
    )
    assert summary["player_decision_metrics"]["player_0"][
        "retry_rate"
    ] == pytest.approx(
        summary["player_decision_metrics"]["player_0"]["retry_count"]
        / summary["player_decision_metrics"]["player_0"]["trace_count"]
    )
    assert summary["player_decision_metrics"]["player_1"]["trace_count"] == 0
    assert summary["player_decision_metrics"]["player_1"]["invalid_action_rate"] == 0.0
    assert summary["player_decision_metrics"]["player_1"]["retry_rate"] == 0.0
    assert "provider_cost" not in summary
    assert "provider_latency_ms" not in summary


def test_no_press_llm_game_labels_replay_agent_mixed_seats() -> None:
    result = run_no_press_llm_game(
        NoPressLLMGameConfig(
            players=2,
            seed=7,
            max_turns=2,
            seats={
                "player_0": LLMSeatConfig("llm_first_legal"),
                "player_1": LLMSeatConfig("heuristic"),
            },
        )
    )

    # Per-seat games are honestly labelled "mixed_seats", not the legacy
    # single-agent placeholder "decision_heuristic".
    assert result["replay"]["agent"] == "mixed_seats"
    assert result["trace_artifact"]["replay"]["agent"] == "mixed_seats"
    validate_replay_payload(result["replay"])
    validate_trace_artifact(result["trace_artifact"], result["replay"])


def test_no_press_llm_first_legal_seat_runs_without_scripted_actions() -> None:
    result = run_no_press_llm_game(
        NoPressLLMGameConfig(
            players=4,
            seed=19,
            max_turns=3,
            seats={
                "player_0": LLMSeatConfig("llm_first_legal"),
                "player_1": LLMSeatConfig("random"),
                "player_2": LLMSeatConfig("heuristic"),
                "player_3": LLMSeatConfig("decision_heuristic"),
            },
        )
    )

    validate_replay_payload(result["replay"])
    validate_trace_artifact(result["trace_artifact"], result["replay"])
    assert result["seat_config"]["player_0"] == "llm_first_legal"
    assert result["summary"]["trace_count"] >= 1
    assert result["summary"]["invalid_action_count"] == 0
    assert result["summary"]["retry_count"] == 0
    assert result["summary"]["player_decision_metrics"]["player_0"]["trace_count"] >= 1


def test_no_press_llm_game_summarizes_provider_metadata_when_available() -> None:
    result = run_no_press_llm_game(
        NoPressLLMGameConfig(
            players=4,
            seed=23,
            max_turns=1,
            seats={
                "player_0": LLMSeatConfig(
                    "llm_scripted",
                    scripted_responses=('{"action_id": "player_0:draw"}',),
                    scripted_provider_latency_ms=(19,),
                    scripted_provider_cost=(0.006,),
                ),
                "player_1": LLMSeatConfig("random"),
                "player_2": LLMSeatConfig("heuristic"),
                "player_3": LLMSeatConfig("decision_heuristic"),
            },
        )
    )

    traces = result["trace_artifact"]["traces"]
    assert result["summary"]["provider_latency_ms"] == sum(
        trace["provider_latency_ms"]
        for trace in traces
        if trace["provider_latency_ms"] is not None
    )
    assert result["summary"]["provider_cost"] == pytest.approx(
        sum(
            trace["provider_cost"]
            for trace in traces
            if trace["provider_cost"] is not None
        )
    )
    assert traces[0]["provider_latency_ms"] >= 19
    assert traces[0]["provider_cost"] >= 0.006
