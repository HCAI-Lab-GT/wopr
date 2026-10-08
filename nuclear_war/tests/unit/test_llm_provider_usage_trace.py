"""Provider usage metadata in LLM decision traces."""

from __future__ import annotations

import json

from tests.unit.test_llm_agent import _observation, _options

from nuclear_war_agents import (
    LLMCompletion,
    LLMDecisionAgent,
    ScriptedLLMClient,
    TraceRecorder,
)


def test_llm_agent_records_provider_usage_label_and_model() -> None:
    options = _options()
    recorder = TraceRecorder()
    completion = LLMCompletion(
        json.dumps({"action_id": options[1].action_id}),
        provider_usage={"prompt_tokens": 7, "completion_tokens": 3},
        provider_label="together",
        provider_model="demo-model",
    )
    agent = LLMDecisionAgent(ScriptedLLMClient([completion]), recorder=recorder)

    agent.choose(_observation(options), options)
    payload = recorder.to_payload()[0]

    assert payload["provider_usage"] == {
        "prompt_tokens": 7,
        "completion_tokens": 3,
    }
    assert payload["provider_label"] == "together"
    assert payload["provider_model"] == "demo-model"
