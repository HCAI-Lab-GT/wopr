"""LLM decision agent validation tests."""

from __future__ import annotations

import pytest
from tests.unit.test_llm_agent import _observation

from nuclear_war_agents import LLMDecisionAgent, ScriptedLLMClient, TraceRecorder
from nuclear_war_env.action_models import ActionType, build_action


def test_llm_agent_rejects_negative_retry_budget() -> None:
    options = [build_action("p1", ActionType.PASS, "Pass")]
    agent = LLMDecisionAgent(
        ScriptedLLMClient(['{"action_id": "p1:pass"}']),
        recorder=TraceRecorder(),
        max_retries=-1,
    )

    with pytest.raises(ValueError, match="max_retries"):
        agent.choose(_observation(options), options)
