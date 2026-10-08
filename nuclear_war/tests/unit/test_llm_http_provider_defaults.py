from __future__ import annotations

import json
from typing import Any

from nuclear_war_agents.llm_http_client import HTTPClientConfig, LLMHttpClient
from nuclear_war_agents.llm_http_transport import HTTPResponse


def test_http_client_resolves_known_provider_defaults(monkeypatch) -> None:
    monkeypatch.setenv("TOGETHER_API_KEY", "secret-token")
    monkeypatch.setenv("WOPR_LLM_MODEL", "openai/gpt-oss-20b")
    transport = _Transport(
        {"choices": [{"message": {"content": '{"action_id": "p1:pass"}'}}]}
    )
    client = LLMHttpClient(
        HTTPClientConfig(provider="together"),
        transport=transport,
        monotonic_ms=_Clock(0, 1),
    )

    completion = client.complete("choose one action")

    assert transport.url == "https://api.together.ai/v1/chat/completions"
    assert transport.headers["Authorization"] == "Bearer secret-token"
    assert transport.body["model"] == "openai/gpt-oss-20b"
    assert completion.provider_label == "together"
    assert completion.provider_model == "openai/gpt-oss-20b"


class _Transport:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload
        self.url = ""
        self.headers: dict[str, str] = {}
        self.body: dict[str, Any] = {}

    def __call__(
        self,
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout_seconds: int,
    ) -> HTTPResponse:
        del timeout_seconds
        self.url = url
        self.headers = headers
        self.body = json.loads(body.decode("utf-8"))
        return HTTPResponse(200, json.dumps(self._payload))


class _Clock:
    def __init__(self, *values: int) -> None:
        self._values = list(values)

    def __call__(self) -> int:
        return self._values.pop(0)
