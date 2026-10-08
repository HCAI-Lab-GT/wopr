from __future__ import annotations

import json

import pytest
from tests.unit.http_client_test_support import Clock, SequenceTransport

from nuclear_war_agents import HTTPClientConfig, HTTPResponse, LLMHttpClient
from nuclear_war_agents import llm_http_client as client_module
from nuclear_war_agents.llm_http_transport import LLMHttpError


def test_http_client_retries_transient_server_errors() -> None:
    transport = SequenceTransport(
        [
            HTTPResponse(500, "{}"),
            HTTPResponse(
                200,
                json.dumps(
                    {"choices": [{"message": {"content": '{"action_id":"ok"}'}}]}
                ),
            ),
        ]
    )
    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=Clock(0, 5),
    )

    completion = client.complete("prompt")

    assert completion.raw_response == '{"action_id":"ok"}'
    assert transport.call_count == 2
    assert completion.provider_transport_retries == 1


def test_http_client_waits_before_retrying_rate_limit(monkeypatch) -> None:
    sleeps: list[float] = []
    monkeypatch.setattr(client_module.time, "sleep", sleeps.append)
    transport = SequenceTransport(
        [
            HTTPResponse(429, '{"error": {"message": "rate limit"}}'),
            HTTPResponse(
                200,
                json.dumps(
                    {"choices": [{"message": {"content": '{"action_id":"ok"}'}}]}
                ),
            ),
        ]
    )
    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=Clock(0, 5),
    )

    completion = client.complete("prompt")

    assert completion.raw_response == '{"action_id":"ok"}'
    assert transport.call_count == 2
    assert sleeps == [1.0]


def test_http_client_retries_empty_successful_completion() -> None:
    transport = SequenceTransport(
        [
            HTTPResponse(200, json.dumps({"choices": [{"message": {}}]})),
            HTTPResponse(
                200,
                json.dumps(
                    {"choices": [{"message": {"content": '{"action_id":"ok"}'}}]}
                ),
            ),
        ]
    )
    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=Clock(0, 5),
    )

    completion = client.complete("prompt")

    assert completion.raw_response == '{"action_id":"ok"}'
    assert transport.call_count == 2
    assert completion.provider_transport_retries == 1


def test_http_client_does_not_retry_client_errors() -> None:
    transport = SequenceTransport(
        [
            HTTPResponse(403, "{}"),
            HTTPResponse(
                200,
                json.dumps(
                    {"choices": [{"message": {"content": '{"action_id":"ok"}'}}]}
                ),
            ),
        ]
    )
    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=Clock(0, 1),
    )

    with pytest.raises(LLMHttpError, match="403"):
        client.complete("prompt")
    assert transport.call_count == 1


def test_http_client_guards_each_provider_attempt() -> None:
    transport = SequenceTransport(
        [
            HTTPResponse(500, "{}"),
            HTTPResponse(
                200,
                json.dumps(
                    {"choices": [{"message": {"content": '{"action_id":"ok"}'}}]}
                ),
            ),
        ]
    )
    calls = 0

    def guard() -> None:
        nonlocal calls
        calls += 1
        if calls > 1:
            raise RuntimeError("request cap")

    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=Clock(0, 5),
        request_guard=guard,
    )

    with pytest.raises(RuntimeError, match="request cap"):
        client.complete("prompt")
    assert calls == 2
    assert transport.call_count == 1
