"""LLM trace artifact top-level validation tests."""

from __future__ import annotations

import pytest
from tests.unit.test_llm_trace_artifacts import _replay, _replay_reference

from nuclear_war_env.llm_trace_artifacts import (
    TRACE_SCHEMA_VERSION,
    validate_trace_artifact,
)


def test_trace_artifact_rejects_unknown_top_level_fields() -> None:
    replay = _replay()
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": [],
        "transcript": [],
    }

    with pytest.raises(ValueError, match="fields are invalid"):
        validate_trace_artifact(payload, replay)
