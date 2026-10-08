"""Tests for the authority smoke provider request budget."""

from __future__ import annotations

import pytest
from tests.authority_smoke_support import _budgeted_transport

from nuclear_war_agents.llm_http_transport import HTTPResponse


def test_provider_request_budget_rejects_next_call() -> None:
    delegated_calls = 0

    def delegate(
        url: str,
        headers: dict[str, str],
        body: bytes,
        timeout_seconds: int,
    ) -> HTTPResponse:
        nonlocal delegated_calls
        delegated_calls += 1
        return HTTPResponse(200, "{}")

    transport, request_count = _budgeted_transport(delegate, 35)
    for _ in range(35):
        assert transport("url", {}, b"{}", 1).status_code == 200

    with pytest.raises(RuntimeError, match="provider request budget exceeded"):
        transport("url", {}, b"{}", 1)

    assert request_count() == 35
    assert delegated_calls == 35
