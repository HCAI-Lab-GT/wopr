"""Trace artifact schema tests for provider usage metadata."""

from __future__ import annotations

from tests.unit.test_llm_trace_artifacts import _replay, _replay_reference, _trace

from nuclear_war_env.llm_trace_artifacts import (
    TRACE_SCHEMA_VERSION,
    validate_trace_artifact,
)


def test_current_trace_schema_accepts_provider_usage_metadata() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    trace["provider_usage"] = {"prompt_tokens": 7, "completion_tokens": 3}
    trace["provider_label"] = "together"
    trace["provider_model"] = "demo-model"
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    assert TRACE_SCHEMA_VERSION == 5
    validate_trace_artifact(payload, replay)
