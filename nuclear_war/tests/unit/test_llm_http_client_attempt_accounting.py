from __future__ import annotations

import json
from typing import cast

import pytest
from tests.unit.http_client_test_support import Clock, SequenceTransport
from tests.unit.test_concordia_agent_recovery import _observation, _options

from nuclear_war_agents import HTTPClientConfig, HTTPResponse, LLMHttpClient
from nuclear_war_agents.llm_http_transport import LLMHttpError
from nuclear_war_concordia.agent import ConcordiaDecisionAgent
from nuclear_war_concordia.types import ConcordiaClient


def test_exhausted_http_error_preserves_provider_attempts() -> None:
    transport = SequenceTransport([HTTPResponse(500, "{}")])
    client = _client(transport)

    try:
        client.complete("prompt")
    except LLMHttpError as error:
        assert error.provider_attempts == 3
    else:
        raise AssertionError("expected exhausted provider error")

    assert transport.call_count == 3


def test_agent_records_exhausted_provider_attempts_before_recovery() -> None:
    options = _options()
    traces: list[dict[str, object]] = []
    client = cast(
        ConcordiaClient,
        _client(
            SequenceTransport(
                [
                    HTTPResponse(500, "{}"),
                    HTTPResponse(500, "{}"),
                    HTTPResponse(500, "{}"),
                    _legal_response(options[0].action_id),
                ]
            )
        ),
    )
    agent = ConcordiaDecisionAgent(
        identity={"name": "Analyst Zero"},
        client=client,
        trace_sink=traces,
        max_retries=1,
    )

    assert agent.choose(_observation(options), options) == options[0]
    assert traces[0]["recoverable_provider_retries"] == 3


def test_input_token_guard_runs_before_dispatch() -> None:
    transport = SequenceTransport([_legal_response("player_0:pass")])
    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=Clock(0, 5),
        input_token_guard=lambda prompt: _reject_prompt(prompt),
    )

    with pytest.raises(RuntimeError, match="input cap"):
        client.complete("prompt")

    assert transport.call_count == 0


def _client(transport: SequenceTransport) -> LLMHttpClient:
    return LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=Clock(0, 5, 6, 11),
    )


def _legal_response(action_id: str) -> HTTPResponse:
    message = {"content": json.dumps({"action_id": action_id})}
    payload = {"choices": [{"message": message}]}
    return HTTPResponse(
        200,
        json.dumps(payload),
    )


def _reject_prompt(prompt: str) -> None:
    assert prompt == "prompt"
    raise RuntimeError("input cap")
