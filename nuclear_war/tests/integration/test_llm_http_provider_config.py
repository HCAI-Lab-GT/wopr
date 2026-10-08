"""No-press LLM HTTP provider config tests."""

from __future__ import annotations

from typing import Any

import pytest

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_env.llm_harness_batch import load_no_press_llm_batch_config


def test_llm_batch_config_loads_known_provider_defaults() -> None:
    payload = _config_payload()
    payload["seats"]["player_0"] = {
        "agent": "llm_http",
        "client": {"provider": "together"},
    }

    config = load_no_press_llm_batch_config(payload)
    client = config.seats["player_0"].client

    assert isinstance(client, HTTPClientConfig)
    assert client.provider == "together"
    assert client.base_url == "https://api.together.ai/v1"
    assert client.model_env == "WOPR_LLM_MODEL"
    assert client.api_key_env == "TOGETHER_API_KEY"
    assert client.provider_label == "together"


def test_llm_batch_config_rejects_unknown_provider() -> None:
    payload = _config_payload()
    payload["seats"]["player_0"] = {
        "agent": "llm_http",
        "client": {"provider": "unknown_provider"},
    }

    with pytest.raises(ValueError, match="provider"):
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
