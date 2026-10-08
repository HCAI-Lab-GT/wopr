"""No-press LLM HTTP seat config tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config
from nuclear_war_env.llm_harness_batch_config_snapshot import batch_config_snapshot


def test_llm_batch_config_loads_http_client_fields() -> None:
    payload = _config_payload()
    payload["seats"]["player_0"] = {
        "agent": "llm_http",
        "max_retries": 2,
        "fallback": "pass",
        "client": {
            "base_url_env": "NW_LLM_BASE_URL",
            "model": "demo-model",
            "api_key_env": "NW_LLM_KEY",
            "provider_label": "together",
            "timeout_seconds": 7,
            "temperature": 0.2,
            "max_tokens": 64,
            "reasoning_effort": "low",
            "reasoning_enabled": False,
            "stream": True,
        },
    }

    config = load_no_press_llm_batch_config(payload)
    seat = config.seats["player_0"]

    assert seat.agent == "llm_http"
    assert isinstance(seat.client, HTTPClientConfig)
    assert seat.client.base_url_env == "NW_LLM_BASE_URL"
    assert seat.client.model == "demo-model"
    assert seat.client.api_key_env == "NW_LLM_KEY"
    assert seat.client.provider_label == "together"
    assert seat.client.timeout_seconds == 7
    assert seat.client.temperature == 0.2
    assert seat.client.max_tokens == 64
    assert seat.client.reasoning_effort == "low"
    assert seat.client.reasoning_enabled is False
    assert seat.client.stream is True


def test_llm_batch_config_snapshot_keeps_http_client_env_names() -> None:
    payload = _config_payload()
    payload["seats"]["player_0"] = {
        "agent": "llm_http",
        "client": {
            "base_url_env": "NW_LLM_BASE_URL",
            "model_env": "NW_LLM_MODEL",
            "api_key_env": "NW_LLM_KEY",
        },
    }

    snapshot = batch_config_snapshot(load_no_press_llm_batch_config(payload))

    assert snapshot["seats"]["player_0"]["client"] == {
        "provider": "openai_compatible",
        "base_url": None,
        "base_url_env": "NW_LLM_BASE_URL",
        "model": None,
        "model_env": "NW_LLM_MODEL",
        "api_key_env": "NW_LLM_KEY",
        "provider_label": "openai_compatible",
        "timeout_seconds": 60,
        "temperature": 0.0,
        "max_tokens": 256,
        "reasoning_effort": None,
        "reasoning_enabled": None,
        "stream": False,
    }


def test_llm_batch_config_rejects_http_seat_without_client() -> None:
    payload = _config_payload()
    payload["seats"]["player_0"] = {"agent": "llm_http"}

    with pytest.raises(ValueError, match="client requires llm_http config"):
        load_no_press_llm_batch_config(payload)


def test_llm_batch_config_rejects_client_for_non_http_seat() -> None:
    payload = _config_payload()
    payload["seats"]["player_1"]["client"] = {"model": "ignored"}

    with pytest.raises(ValueError, match="client requires llm_http agent"):
        load_no_press_llm_batch_config(payload)


def test_llm_batch_config_rejects_http_client_without_model_source() -> None:
    payload = _config_payload()
    payload["seats"]["player_0"] = {
        "agent": "llm_http",
        "client": {"base_url": "http://localhost:8000/v1"},
    }

    with pytest.raises(ValueError, match="client model or model_env"):
        load_no_press_llm_batch_config(payload)


def test_llm_batch_config_rejects_invalid_reasoning_effort() -> None:
    payload = _config_payload()
    payload["seats"]["player_0"] = {
        "agent": "llm_http",
        "client": {
            "base_url": "http://localhost:8000/v1",
            "model": "demo-model",
            "reasoning_effort": "maximum",
        },
    }

    with pytest.raises(ValueError, match="reasoning_effort"):
        load_no_press_llm_batch_config(payload)


def _config_payload() -> dict[str, Any]:
    return {
        "players": 4,
        "seed_start": 31,
        "runs": 1,
        "max_turns": 1,
        "seats": {
            "player_0": {
                "agent": "llm_scripted",
                "scripted_responses": ['{"action_id": "player_0:draw"}'],
            },
            "player_1": {"agent": "random"},
            "player_2": {"agent": "heuristic"},
            "player_3": {"agent": "decision_heuristic"},
        },
    }
