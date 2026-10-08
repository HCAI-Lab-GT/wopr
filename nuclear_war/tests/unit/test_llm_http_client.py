from __future__ import annotations

import json
from typing import Any

import pytest

from nuclear_war_agents.llm_http_client import (
    HTTPClientConfig,
    LLMHttpClient,
    LLMHttpError,
)
from nuclear_war_agents.llm_http_transport import HTTPResponse


def test_http_client_posts_chat_request_and_records_usage(monkeypatch) -> None:
    monkeypatch.setenv("NW_LLM_KEY", "secret-token")
    transport = _Transport(
        {
            "choices": [{"message": {"content": '{"action_id": "p1:pass"}'}}],
            "usage": {"prompt_tokens": 8, "completion_tokens": 4, "total_tokens": 12},
        }
    )
    client = LLMHttpClient(
        HTTPClientConfig(
            base_url="https://api.together.ai/v1/",
            model="demo-model",
            api_key_env="NW_LLM_KEY",
            provider_label="together",
            timeout_seconds=7,
            temperature=0.2,
            max_tokens=64,
            reasoning_effort="low",
        ),
        transport=transport,
        monotonic_ms=_Clock(1000, 1250),
    )

    completion = client.complete("choose one action")

    assert transport.url == "https://api.together.ai/v1/chat/completions"
    assert transport.timeout_seconds == 7
    assert transport.headers["Authorization"] == "Bearer secret-token"
    assert transport.headers["Content-Type"] == "application/json"
    assert transport.headers["User-Agent"] == "WOPR/0.1"
    assert transport.body["model"] == "demo-model"
    assert transport.body["temperature"] == 0.2
    assert transport.body["max_tokens"] == 64
    assert transport.body["reasoning_effort"] == "low"
    assert transport.body["messages"] == [
        {"role": "user", "content": "choose one action"}
    ]
    assert completion.raw_response == '{"action_id": "p1:pass"}'
    assert completion.provider_latency_ms == 250
    assert completion.provider_usage == {
        "prompt_tokens": 8,
        "completion_tokens": 4,
        "total_tokens": 12,
    }


def test_http_client_omits_authorization_without_api_key() -> None:
    transport = _Transport({"choices": [{"message": {"content": "action_id: x"}}]})
    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=transport,
        monotonic_ms=_Clock(0, 1),
    )

    client.complete("prompt")

    assert "Authorization" not in transport.headers


def test_http_client_rejects_missing_required_env(monkeypatch) -> None:
    monkeypatch.delenv("NW_MISSING_KEY", raising=False)
    client = LLMHttpClient(
        HTTPClientConfig(
            base_url="https://api.together.ai/v1",
            model="demo-model",
            api_key_env="NW_MISSING_KEY",
        ),
        transport=_Transport({}),
        monotonic_ms=_Clock(0, 1),
    )

    with pytest.raises(LLMHttpError, match="NW_MISSING_KEY"):
        client.complete("prompt")


def test_http_client_error_does_not_include_secret(monkeypatch) -> None:
    monkeypatch.setenv("NW_LLM_KEY", "secret-token")
    client = LLMHttpClient(
        HTTPClientConfig(
            base_url="https://api.together.ai/v1",
            model="demo-model",
            api_key_env="NW_LLM_KEY",
        ),
        transport=_Transport({"error": "bad"}, status_code=401),
        monotonic_ms=_Clock(0, 1),
    )

    with pytest.raises(LLMHttpError) as exc_info:
        client.complete("prompt")

    assert "401" in str(exc_info.value)
    assert "secret-token" not in str(exc_info.value)


def test_http_client_rejects_missing_message_content() -> None:
    client = LLMHttpClient(
        HTTPClientConfig(base_url="http://localhost:8000/v1", model="local-model"),
        transport=_Transport({"choices": [{"message": {}}]}),
        monotonic_ms=_Clock(0, 1),
    )

    with pytest.raises(LLMHttpError, match="message content"):
        client.complete("prompt")


class _Transport:
    def __init__(self, payload: dict[str, Any], status_code: int = 200) -> None:
        self._payload = payload
        self._status_code = status_code
        self.url = ""
        self.headers: dict[str, str] = {}
        self.body: dict[str, Any] = {}
        self.timeout_seconds = 0

    def __call__(
        self,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout_seconds: int,
    ) -> HTTPResponse:
        self.url = url
        self.headers = headers
        self.body = json.loads(body.decode("utf-8"))
        self.timeout_seconds = timeout_seconds
        return HTTPResponse(self._status_code, json.dumps(self._payload))


class _Clock:
    def __init__(self, *values: int) -> None:
        self._values = list(values)

    def __call__(self) -> int:
        return self._values.pop(0)
