"""Env-gated live HTTP LLM smoke test."""

from __future__ import annotations

import os

import pytest

from nuclear_war_agents import HTTPClientConfig, LLMHttpClient


@pytest.mark.skipif(
    not all(os.environ.get(name) for name in ("WOPR_LLM_MODEL", "TOGETHER_API_KEY")),
    reason="live LLM smoke requires WOPR_LLM_MODEL and TOGETHER_API_KEY",
)
def test_live_http_client_returns_non_empty_response() -> None:
    client = LLMHttpClient(
        HTTPClientConfig(
            provider="together",
            timeout_seconds=30,
            temperature=0.0,
            max_tokens=256,
        )
    )

    completion = client.complete(
        'Respond only with this JSON: {"action_id": "smoke:test"}'
    )

    assert completion.raw_response
    assert completion.provider_label == "together"
    assert completion.provider_model == os.environ["WOPR_LLM_MODEL"]
