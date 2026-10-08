"""Trace schema v5: per-decision ``fallback_used`` flag.

The Concordia harness design spec (docs/specs/2026-06-22-concordia-agent-
harness-design.md) promises each decision trace carries a "fallback used flag".
This exercises the additive, versioned schema bump that makes fallback visible.
"""

from __future__ import annotations

from typing import Any

import pytest
from tests.unit.test_llm_trace_artifacts import _replay, _replay_reference, _trace

from nuclear_war_agents import LLMDecisionTrace
from nuclear_war_env.llm_trace_artifact_schema import trace_fields
from nuclear_war_env.llm_trace_artifacts import (
    TRACE_SCHEMA_VERSION,
    validate_trace_artifact,
)


def test_schema_version_is_v5_and_defines_fallback_used() -> None:
    assert TRACE_SCHEMA_VERSION == 5
    assert "fallback_used" in trace_fields(5)
    assert "fallback_used" not in trace_fields(4)


def test_trace_payload_defaults_fallback_used_to_false() -> None:
    payload = _decision_trace().to_payload()
    assert payload["fallback_used"] is False


def test_trace_payload_records_fallback_used_true() -> None:
    payload = _decision_trace(fallback_used=True).to_payload()
    assert payload["fallback_used"] is True


def test_v5_artifact_accepts_fallback_used_flag() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    trace["fallback_used"] = True
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    validate_trace_artifact(payload, replay)


def test_v5_artifact_requires_fallback_used_field() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    del trace["fallback_used"]
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    with pytest.raises(ValueError, match="fields are invalid"):
        validate_trace_artifact(payload, replay)


def test_v5_artifact_rejects_non_bool_fallback_used() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    trace["fallback_used"] = "yes"
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    with pytest.raises(ValueError, match="fallback_used must be a boolean"):
        validate_trace_artifact(payload, replay)


def test_v4_artifact_still_validates_without_fallback_used() -> None:
    replay = _replay()
    trace = _trace(replay["actions"][0]["action_id"])
    del trace["fallback_used"]
    del trace["recoverable_provider_retries"]
    payload = {
        "schema_version": 4,
        "replay": _replay_reference(replay),
        "traces": [trace],
    }

    validate_trace_artifact(payload, replay)


def _decision_trace(*, fallback_used: bool = False) -> LLMDecisionTrace:
    return LLMDecisionTrace(
        trace_id="player_0:1:1",
        turn=1,
        player_id="player_0",
        decision_type="draw",
        rendered_observation={"player_id": "player_0", "turn": 1},
        prompt="prompt",
        prompts=["prompt"],
        legal_options=[{"action_id": "player_0:draw"}],
        raw_response='{"action_id": "player_0:draw"}',
        raw_responses=['{"action_id": "player_0:draw"}'],
        parse_result={"action_id": "player_0:draw", "rationale": None},
        selected_action_id="player_0:draw",
        retries=0,
        validation_errors=[],
        fallback_used=fallback_used,
    )


_: Any = None
