"""No-press LLM batch artifact validation edge cases."""

from __future__ import annotations

import json

import pytest

from nuclear_war_env.llm_harness import LLMSeatConfig
from nuclear_war_env.llm_harness_batch import (
    NoPressLLMBatchConfig,
    run_no_press_llm_batch,
)
from nuclear_war_env.llm_harness_batch_io import (
    read_no_press_llm_batch,
    write_no_press_llm_batch,
)
from nuclear_war_env.llm_harness_batch_summary import summarize_no_press_llm_results


def test_read_no_press_llm_batch_rejects_win_loss_mismatch(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=1,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload["results"][0]["win_loss"] = {
        player_id: "win" for player_id in payload["results"][0]["win_loss"]
    }
    payload["summary"] = summarize_no_press_llm_results(
        payload["results"],
        payload["seat_config"],
    )
    summary_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="win_loss does not match files"):
        read_no_press_llm_batch(summary_path)


def test_read_no_press_llm_batch_rejects_player_count_mismatch(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=1,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload["players"] = 5
    payload["config"]["players"] = 5
    payload["config"]["seats"]["player_4"] = _random_seat_snapshot()
    payload["seat_config"]["player_4"] = "random"
    summary_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="players does not match replay"):
        read_no_press_llm_batch(summary_path)


def test_read_no_press_llm_batch_rejects_max_turns_below_replay(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=3,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload["max_turns"] = 2
    payload["config"]["max_turns"] = 2
    summary_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="turns exceeds max_turns"):
        read_no_press_llm_batch(summary_path)


def test_read_no_press_llm_batch_rejects_variant_mismatch(tmp_path) -> None:
    result = run_no_press_llm_batch(
        NoPressLLMBatchConfig(
            players=4,
            seed_start=31,
            runs=1,
            max_turns=1,
            seats=_seat_configs(),
        )
    )
    summary_path = write_no_press_llm_batch(tmp_path / "out", result)
    payload = json.loads(summary_path.read_text(encoding="utf-8"))
    payload["config"]["variant_id"] = "tampered_variant"
    summary_path.write_text(json.dumps(payload), encoding="utf-8")

    with pytest.raises(ValueError, match="variant_id does not match replay"):
        read_no_press_llm_batch(summary_path)


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


def _random_seat_snapshot() -> dict[str, object]:
    return {
        "agent": "random",
        "scripted_responses": [],
        "scripted_provider_latency_ms": [],
        "scripted_provider_cost": [],
        "max_retries": 1,
        "fallback": "first",
    }
