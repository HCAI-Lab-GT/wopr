"""Bounded, environment-gated live HTTP authority smoke test."""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any, cast

import pytest
from tests.authority_smoke_support import (
    _assert_authority_artifacts,
    _budgeted_transport,
    _reload_authority_artifacts,
)

from nuclear_war_agents.llm_http_client import send_http as real_send_http
from nuclear_war_concordia.artifacts import write_concordia_no_press_artifacts
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness import run_concordia_no_press_game
from nuclear_war_env.llm_trace_artifacts import validate_trace_artifact

_LIVE_ENV = ("WOPR_LLM_BASE_URL", "WOPR_LLM_MODEL", "TOGETHER_API_KEY")
_PROVIDER_REQUEST_BUDGET = 35


def test_authority_smoke_control_flow_reaches_press_offline(
    authority_config_payload: dict[str, object],
) -> None:
    config = load_concordia_no_press_config(
        _offline_control_payload(authority_config_payload)
    )
    result = run_concordia_no_press_game(config)

    metrics = result["summary"]["channel_metrics"]
    assert metrics["c2"]["trace_count"] == 30
    assert metrics["press"]["trace_count"] == 4
    assert metrics["c2"]["call_count"] + metrics["press"]["call_count"] == 34


@pytest.mark.skipif(
    not all(os.environ.get(name) for name in _LIVE_ENV),
    reason="requires WOPR_LLM_BASE_URL, WOPR_LLM_MODEL, and TOGETHER_API_KEY",
)
def test_live_http_authority_full_press_writes_validated_artifacts(
    tmp_path: Path,
    authority_config_payload: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    transport, request_count = _budgeted_transport(
        real_send_http, _PROVIDER_REQUEST_BUDGET
    )
    monkeypatch.setattr("nuclear_war_agents.llm_http_client.send_http", transport)
    config = load_concordia_no_press_config(_live_payload(authority_config_payload))
    result = run_concordia_no_press_game(config)

    validate_trace_artifact(result["trace_artifact"], result["replay"])
    paths = write_concordia_no_press_artifacts(tmp_path, result)
    written = _reload_authority_artifacts(paths)
    _assert_authority_artifacts(
        result, paths, written, request_count(), _PROVIDER_REQUEST_BUDGET
    )


def _live_payload(base_payload: dict[str, object]) -> dict[str, object]:
    payload = deepcopy(base_payload)
    payload["max_turns"] = 2
    payload["press"] = {"mode": "full_press", "enabled": True, "passes": 1}
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seat = seats["player_0"]
    client = {
        "base_url_env": "WOPR_LLM_BASE_URL",
        "model_env": "WOPR_LLM_MODEL",
        "api_key_env": "TOGETHER_API_KEY",
        "provider_label": "direct_api",
    }
    seat["agent"] = "concordia_http"
    seat["max_retries"] = 0
    seat["client"] = client
    return payload


def _offline_control_payload(base_payload: dict[str, object]) -> dict[str, object]:
    payload = _live_payload(base_payload)
    seats = cast(dict[str, dict[str, Any]], payload["seats"])
    seat = seats["player_0"]
    seat["agent"] = "concordia_first_legal"
    seat.pop("client")
    return payload
