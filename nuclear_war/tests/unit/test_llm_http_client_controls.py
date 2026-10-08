from __future__ import annotations

import json
from typing import Any

import pytest

from nuclear_war_agents.llm_http_client import HTTPClientConfig, LLMHttpClient
from nuclear_war_agents.llm_http_transport import HTTPResponse, LLMHttpError


def test_http_client_posts_reasoning_and_stream_controls() -> None:
    transport = _Transport(
        'data: {"choices":[{"delta":{"content":"{\\"action_id\\": "}}]}\n\n'
        'data: {"choices":[{"delta":{"content":"\\"smoke:test\\"}"}}]}\n\n'
        "data: [DONE]\n\n"
    )
    client = LLMHttpClient(
        HTTPClientConfig(
            base_url="https://api.together.ai/v1",
            model="demo-model",
            stream=True,
            reasoning_enabled=False,
        ),
        transport=transport,
        monotonic_ms=_Clock(10, 25),
    )

    completion = client.complete("choose")

    assert transport.body["stream"] is True
    assert transport.body["reasoning"] == {"enabled": False}
    assert completion.raw_response == '{"action_id": "smoke:test"}'
    assert completion.provider_latency_ms == 15


def test_http_client_error_includes_provider_message() -> None:
    transport = _JsonTransport(
        {
            "error": {
                "message": "Set stream to true.",
                "type": "invalid_request_error",
            }
        },
        status_code=400,
    )
    client = LLMHttpClient(
        HTTPClientConfig(base_url="https://api.together.ai/v1", model="demo-model"),
        transport=transport,
        monotonic_ms=_Clock(1, 2),
    )

    with pytest.raises(LLMHttpError, match="Set stream to true"):
        client.complete("choose")


class _Transport:
    def __init__(self, body: str) -> None:
        self._body = body
        self.body: dict[str, Any] = {}

    def __call__(
        self,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout_seconds: int,
    ) -> HTTPResponse:
        self.body = json.loads(body.decode("utf-8"))
        return HTTPResponse(200, self._body)


class _JsonTransport:
    def __init__(self, payload: dict[str, Any], status_code: int) -> None:
        self._payload = payload
        self._status_code = status_code

    def __call__(
        self,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout_seconds: int,
    ) -> HTTPResponse:
        return HTTPResponse(self._status_code, json.dumps(self._payload))


class _Clock:
    def __init__(self, *values: int) -> None:
        self._values = list(values)

    def __call__(self) -> int:
        return self._values.pop(0)
