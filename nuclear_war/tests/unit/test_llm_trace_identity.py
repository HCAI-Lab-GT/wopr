"""LLM trace identity validation tests."""

from __future__ import annotations

import pytest
from tests.unit.test_llm_trace_artifacts import _replay, _replay_reference, _trace

from nuclear_war_env.llm_trace_artifacts import (
    TRACE_SCHEMA_VERSION,
    validate_trace_artifact,
)


def test_trace_artifact_rejects_trace_id_context_mismatch() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    trace["trace_id"] = "player_1:1:1"
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    with pytest.raises(ValueError, match="trace_id"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_duplicate_trace_ids() -> None:
    replay = _replay()
    selected_action_id = replay["actions"][0]["action_id"]
    first_trace = _trace(selected_action_id)
    second_trace = _trace(selected_action_id)
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [first_trace, second_trace],
    }

    with pytest.raises(ValueError, match="duplicate trace_id"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_non_numeric_trace_id_index() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    trace["trace_id"] = "player_0:1:not-a-number"
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    with pytest.raises(ValueError, match="trace_id"):
        validate_trace_artifact(payload, replay)


def test_trace_artifact_rejects_zero_trace_id_index() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    trace["trace_id"] = "player_0:1:0"
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    with pytest.raises(ValueError, match="trace_id"):
        validate_trace_artifact(payload, replay)
