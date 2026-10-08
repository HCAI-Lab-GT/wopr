"""LLM trace artifact validation and IO tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_env.llm_trace_artifacts import (
    TRACE_SCHEMA_VERSION,
    read_trace_artifact,
    trace_artifact_path,
    validate_trace_artifact,
    write_trace_artifact,
)
from nuclear_war_env.simulation import SimulationConfig, run_simulation


def test_trace_artifact_round_trips_beside_replay(tmp_path) -> None:
    replay = _replay()
    replay_path = tmp_path / "game.json"
    trace = _trace(replay["actions"][0]["action_id"])

    path = write_trace_artifact(replay_path, replay, [trace])
    payload = read_trace_artifact(path, replay)

    assert path == tmp_path / "game.traces.json"
    assert trace_artifact_path(replay_path) == path
    assert payload["schema_version"] == TRACE_SCHEMA_VERSION
    assert payload["replay"]["seed"] == replay["seed"]
    assert payload["traces"][0]["rendered_observation"]["player_id"] == "player_0"
    assert payload["traces"][0]["selected_action_id"] == trace["selected_action_id"]
    assert payload["traces"][0]["provider_latency_ms"] == 12
    assert payload["traces"][0]["provider_cost"] == 0.003


def test_trace_artifact_rejects_unlinked_selected_action() -> None:
    replay = _replay()
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [_trace("missing-action")],
    }

    with pytest.raises(ValueError, match="does not link to replay action"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_accepts_repeated_action_id_with_matching_context() -> None:
    replay = _replay(seed=1, max_turns=3)
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [_trace("player_0:advance")],
    }

    validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_selected_action_for_different_player() -> None:
    replay = _replay()
    selected = next(
        action for action in replay["actions"] if action["player_id"] != "player_0"
    )
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [_trace(selected["action_id"])],
    }

    with pytest.raises(ValueError, match="player_id does not match"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_selected_action_for_different_turn() -> None:
    replay = _replay()
    selected = replay["actions"][0]
    trace = _trace(selected["action_id"])
    trace["turn"] = selected["turn"] + 1
    trace["trace_id"] = f"player_0:{trace['turn']}:1"
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    with pytest.raises(ValueError, match="turn does not match"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_retry_count_mismatch() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    trace["raw_responses"] = ["not-json", trace["raw_response"]]
    trace["prompts"] = ["first prompt", trace["prompt"]]

    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    with pytest.raises(ValueError, match="retries must match raw_responses"):
        validate_trace_artifact(payload, replay)


def _replay(seed: int = 11, max_turns: int = 1) -> dict[str, Any]:
    return run_simulation(
        SimulationConfig(
            mode="table",
            players=3,
            seed=seed,
            agent="decision_heuristic",
            max_turns=max_turns,
        )
    )


def _trace(selected_action_id: str) -> dict[str, object]:
    return {
        "trace_id": "player_0:1:1",
        "turn": 1,
        "player_id": "player_0",
        "decision_type": "draw",
        "rendered_observation": {"player_id": "player_0", "turn": 1},
        "prompt": "prompt",
        "prompts": ["prompt"],
        "legal_options": [{"action_id": selected_action_id}],
        "raw_response": '{"action_id": "player_0:draw"}',
        "raw_responses": ['{"action_id": "player_0:draw"}'],
        "parse_result": {"action_id": selected_action_id, "rationale": None},
        "selected_action_id": selected_action_id,
        "retries": 0,
        "validation_errors": [],
        "stated_rationale": None,
        "provider_latency_ms": 12,
        "provider_cost": 0.003,
        "provider_usage": None,
        "provider_label": None,
        "provider_model": None,
        "fallback_used": False,
        "recoverable_provider_retries": 0,
    }


def _replay_reference(replay: dict[str, Any]) -> dict[str, object]:
    return {
        "mode": replay["mode"],
        "seed": replay["seed"],
        "agent": replay["agent"],
        "players": replay["players"],
        "turns": replay["turns"],
    }
