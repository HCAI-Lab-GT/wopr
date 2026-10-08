"""No-press harness tests for HTTP-backed LLM seats."""

from __future__ import annotations

import json

from nuclear_war_agents import HTTPClientConfig, LLMCompletion, LLMHttpClient
from nuclear_war_agents.llm_fake_clients import FirstLegalLLMClient
from nuclear_war_env.llm_harness import (
    LLMSeatConfig,
    NoPressLLMGameConfig,
    run_no_press_llm_game,
)


def test_no_press_harness_runs_http_seat_without_network(monkeypatch) -> None:
    def complete(self: LLMHttpClient, prompt: str) -> LLMCompletion:
        del self
        action_id = json.loads(FirstLegalLLMClient().complete(prompt))["action_id"]
        return LLMCompletion(
            json.dumps({"action_id": action_id}),
            provider_usage={"prompt_tokens": 4, "completion_tokens": 2},
            provider_label="local-test",
            provider_model="demo-model",
        )

    monkeypatch.setattr(LLMHttpClient, "complete", complete)
    result = run_no_press_llm_game(
        NoPressLLMGameConfig(
            players=4,
            seed=31,
            max_turns=1,
            seats={
                "player_0": LLMSeatConfig(
                    "llm_http",
                    client=HTTPClientConfig(
                        base_url="http://localhost:8000/v1",
                        model="demo-model",
                    ),
                ),
                "player_1": LLMSeatConfig("random"),
                "player_2": LLMSeatConfig("heuristic"),
                "player_3": LLMSeatConfig("decision_heuristic"),
            },
        )
    )

    trace = result["trace_artifact"]["traces"][0]
    assert result["seat_config"]["player_0"] == "llm_http"
    assert trace["provider_usage"] == {"prompt_tokens": 4, "completion_tokens": 2}
    assert trace["provider_label"] == "local-test"
    assert trace["provider_model"] == "demo-model"
