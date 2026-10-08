"""LLM trace rendered observation validation tests."""

from __future__ import annotations

from typing import cast

import pytest
from tests.unit.test_llm_trace_artifacts import _replay, _replay_reference, _trace

from nuclear_war_env.llm_trace_artifacts import (
    TRACE_SCHEMA_VERSION,
    validate_trace_artifact,
)


def test_trace_artifact_rejects_rendered_observation_player_mismatch() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    _rendered_observation(trace)["player_id"] = "player_1"
    payload = _payload(replay, trace)

    with pytest.raises(ValueError, match="rendered_observation player_id"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_rendered_observation_turn_mismatch() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    _rendered_observation(trace)["turn"] = cast(int, trace["turn"]) + 1
    payload = _payload(replay, trace)

    with pytest.raises(ValueError, match="rendered_observation turn"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_rendered_observation_option_mismatch() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    _rendered_observation(trace)["decision"] = {
        "options": [{"action_id": "different-action"}]
    }
    payload = _payload(replay, trace)

    with pytest.raises(ValueError, match="rendered_observation decision options"):
        validate_trace_artifact(payload, replay)


def _payload(replay: dict[str, object], trace: dict[str, object]) -> dict[str, object]:
    return {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }


def _rendered_observation(trace: dict[str, object]) -> dict[str, object]:
    return cast(dict[str, object], trace["rendered_observation"])
