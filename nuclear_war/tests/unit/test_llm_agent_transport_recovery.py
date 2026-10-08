"""Transport-failure recovery contract for the no-press LLM decision agent.

The pilot runbook promises that a timeout / connection drop / non-retryable
HTTP error at a decision is retried within the ``max_retries`` budget instead
of aborting a whole batch. These tests pin that behavior for the ``llm_http``
seat (pilot 1); the Concordia agent has its own equivalent contract in
``test_concordia_agent_recovery.py``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field

import pytest
from tests.unit.test_llm_agent import _observation, _options

from nuclear_war_agents import LLMDecisionAgent, TraceRecorder
from nuclear_war_agents.llm_http_transport import LLMConfigError, LLMHttpError


@dataclass
class FlakyLLMClient:
    """Scripted client where an Exception entry is raised instead of returned."""

    results: list[str | Exception] = field(default_factory=list)
    calls: int = 0

    def complete(self, prompt: str) -> str:
        del prompt
        result = self.results[self.calls]
        self.calls += 1
        if isinstance(result, Exception):
            raise result
        return result


def _response(action_id: str) -> str:
    return json.dumps({"action_id": action_id})


def test_transport_error_is_retried_then_model_answer_used() -> None:
    options = _options()
    recorder = TraceRecorder()
    client = FlakyLLMClient(
        [
            LLMHttpError("LLM HTTP request failed: Connection refused"),
            _response(options[1].action_id),
        ]
    )
    agent = LLMDecisionAgent(client, recorder=recorder, max_retries=1)

    selected = agent.choose(_observation(options), options)

    assert selected == options[1]
    assert client.calls == 2
    trace = recorder.traces[0]
    assert trace.fallback_used is False
    # A network blip is not illegal model output: it must not inflate
    # validation errors or the reprompt retry count.
    assert trace.validation_errors == []
    assert trace.retries == 0
    assert trace.recoverable_provider_retries == 1


def test_socket_timeout_is_recoverable() -> None:
    options = _options()
    recorder = TraceRecorder()
    client = FlakyLLMClient(
        [TimeoutError("timed out"), _response(options[1].action_id)]
    )
    agent = LLMDecisionAgent(client, recorder=recorder, max_retries=1)

    selected = agent.choose(_observation(options), options)

    assert selected == options[1]
    assert recorder.traces[0].recoverable_provider_retries == 1


def test_all_attempts_transport_fail_raises_without_trace() -> None:
    options = _options()
    recorder = TraceRecorder()
    client = FlakyLLMClient([LLMHttpError("boom"), LLMHttpError("boom again")])
    agent = LLMDecisionAgent(client, recorder=recorder, max_retries=1)

    with pytest.raises(LLMHttpError, match="boom again"):
        agent.choose(_observation(options), options)

    assert client.calls == 2
    assert recorder.traces == []


def test_config_error_is_fatal_and_never_retried() -> None:
    options = _options()
    client = FlakyLLMClient(
        [
            LLMConfigError("LLM HTTP client requires environment variable X"),
            _response(options[1].action_id),
        ]
    )
    agent = LLMDecisionAgent(client, max_retries=1)

    with pytest.raises(LLMConfigError):
        agent.choose(_observation(options), options)

    assert client.calls == 1


def test_unexpected_exception_is_fatal_and_never_retried() -> None:
    options = _options()
    client = FlakyLLMClient(
        [RuntimeError("unexpected bug"), _response(options[1].action_id)]
    )
    agent = LLMDecisionAgent(client, max_retries=1)

    with pytest.raises(RuntimeError, match="unexpected bug"):
        agent.choose(_observation(options), options)

    assert client.calls == 1


def test_illegal_output_then_transport_error_falls_back() -> None:
    options = _options()
    recorder = TraceRecorder()
    client = FlakyLLMClient(["not legal", LLMHttpError("drop")])
    agent = LLMDecisionAgent(client, recorder=recorder, max_retries=1, fallback="first")

    selected = agent.choose(_observation(options), options)

    assert selected == options[0]
    trace = recorder.traces[0]
    assert trace.fallback_used is True
    assert trace.validation_errors == ["No legal action_id parsed"]
    # Trace attempt-pairing invariant: only attempts that produced a
    # completion appear, so retries tracks raw_responses, not transport blips.
    assert trace.raw_responses == ["not legal"]
    assert trace.retries == 0
    assert trace.recoverable_provider_retries == 1
