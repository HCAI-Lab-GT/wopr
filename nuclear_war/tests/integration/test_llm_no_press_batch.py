"""No-press LLM batch harness tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.cli import main
from nuclear_war_env.llm_harness import LLMSeatConfig
from nuclear_war_env.llm_harness_batch import (
    NoPressLLMBatchConfig,
    run_no_press_llm_batch,
)
from nuclear_war_env.llm_trace_artifacts import (
    read_trace_artifact,
    validate_trace_artifact,
)
from nuclear_war_env.replay import read_replay
from nuclear_war_env.replay_validation import validate_replay_payload


def test_no_press_llm_batch_summarizes_runs_and_trace_counts() -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=2,
            max_turns=1,
            seats=_seat_configs(),
        )
    )

    assert result["summary"]["runs"] == 2
    assert len(result["games"]) == 2
    assert len(result["results"]) == 2
    assert result["summary"]["total_invalid_action_count"] >= 2
    assert result["summary"]["total_retry_count"] >= 2
    assert (
        result["summary"]["agent_decision_metrics"]["llm_scripted"][
            "invalid_action_count"
        ]
        >= 2
    )
    assert result["summary"]["agent_decision_metrics"]["llm_scripted"][
        "invalid_action_rate"
    ] == pytest.approx(
        result["summary"]["agent_decision_metrics"]["llm_scripted"][
            "invalid_action_count"
        ]
        / result["summary"]["agent_decision_metrics"]["llm_scripted"]["trace_count"]
    )
    assert result["summary"]["agent_decision_metrics"]["llm_scripted"][
        "retry_rate"
    ] == pytest.approx(
        result["summary"]["agent_decision_metrics"]["llm_scripted"]["retry_count"]
        / result["summary"]["agent_decision_metrics"]["llm_scripted"]["trace_count"]
    )
    assert result["summary"]["agent_decision_metrics"]["random"]["trace_count"] == 0
    assert (
        result["summary"]["agent_decision_metrics"]["random"]["invalid_action_rate"]
        == 0.0
    )
    assert result["summary"]["agent_decision_metrics"]["random"]["retry_rate"] == 0.0
    for agent in ("llm_scripted", "random", "heuristic", "decision_heuristic"):
        assert sum(result["summary"]["agent_outcomes"][agent].values()) == 2
    assert (
        result["results"][0]["player_decision_metrics"]["player_0"]["retry_count"] >= 1
    )
    assert "provider_cost" not in result["summary"]
    for game in result["games"]:
        validate_replay_payload(game["replay"])
        validate_trace_artifact(game["trace_artifact"], game["replay"])


def test_cli_llm_experiment_writes_summary_replays_and_traces(tmp_path) -> None:
    config_path = tmp_path / "llm_config.json"
    output_dir = tmp_path / "out"
    config_path.write_text(json.dumps(_config_payload()), encoding="utf-8")

    code = main(
        [
            "llm-experiment",
            "--config",
            str(config_path),
            "--out-dir",
            str(output_dir),
        ]
    )

    assert code == 0
    summary = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
    assert summary["summary"]["runs"] == 2
    assert summary["summary"]["total_retry_count"] >= 2
    assert "agent_outcomes" in summary["summary"]
    assert "agent_decision_metrics" in summary["summary"]
    for seed in (31, 32):
        replay_path = output_dir / f"seed-{seed}.replay.json"
        trace_path = output_dir / f"seed-{seed}.replay.traces.json"
        replay = read_replay(replay_path)
        trace = read_trace_artifact(trace_path, replay)
        assert trace["replay"]["seed"] == seed


def _seat_configs() -> dict[str, LLMSeatConfig]:
    return {
        "player_0": LLMSeatConfig(
            "llm_scripted",
            scripted_responses=("not-json", '{"action_id": "player_0:draw"}'),
        ),
        "player_1": LLMSeatConfig("random"),
        "player_2": LLMSeatConfig("heuristic"),
        "player_3": LLMSeatConfig("decision_heuristic"),
    }


def _config_payload() -> dict[str, object]:
    return {
        "players": 4,
        "seed_start": 31,
        "runs": 2,
        "max_turns": 1,
        "seats": {
            player_id: {
                "agent": seat.agent,
                "scripted_responses": list(seat.scripted_responses),
            }
            for player_id, seat in _seat_configs().items()
        },
    }
