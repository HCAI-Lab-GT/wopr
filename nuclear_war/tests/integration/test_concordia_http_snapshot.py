"""Concordia HTTP config snapshot tests."""

from __future__ import annotations

import json

import pytest

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_concordia.agent import FirstLegalConcordiaClient
from nuclear_war_concordia.config import ConcordiaNoPressConfig, ConcordiaSeatConfig
from nuclear_war_concordia.harness import run_concordia_no_press_game


def test_concordia_no_press_http_snapshot_uses_allowlisted_config(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class FakeHTTPClient:
        def __init__(self, config: HTTPClientConfig) -> None:
            del config

        def complete(self, scene_text: str) -> str:
            return FirstLegalConcordiaClient().complete(scene_text)

    target = "nuclear_war_concordia.harness_agents.LLMHttpClient"
    monkeypatch.setattr(target, FakeHTTPClient)
    monkeypatch.setenv("TOGETHER_API_KEY", "secret-value")

    result = run_concordia_no_press_game(_config(_http_seats()))

    snapshot = result["config_snapshot"]["seats"]["player_0"]
    client_snapshot = snapshot["client"]
    assert snapshot["scripted_responses"] == []
    assert set(client_snapshot) == set(
        "provider base_url base_url_env model model_env api_key_env provider_label "
        "timeout_seconds temperature max_tokens reasoning_effort reasoning_enabled "
        "stream".split()
    )
    assert client_snapshot["api_key_env"] == "TOGETHER_API_KEY"
    assert "secret-value" not in json.dumps(result["config_snapshot"])


def _config(seats: dict[str, ConcordiaSeatConfig]) -> ConcordiaNoPressConfig:
    return ConcordiaNoPressConfig(players=4, seed=61, max_turns=1, seats=seats)


def _http_seats() -> dict[str, ConcordiaSeatConfig]:
    return {
        f"player_{index}": ConcordiaSeatConfig(
            agent="concordia_http",
            identity={"name": f"Commander {index}", "role": "strategic actor"},
            client=HTTPClientConfig(
                base_url="http://localhost:8000/v1",
                model="demo-model",
                api_key_env="TOGETHER_API_KEY",
            ),
        )
        for index in range(4)
    }
