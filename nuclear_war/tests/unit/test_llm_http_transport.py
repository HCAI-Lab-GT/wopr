"""``send_http`` failure-classification tests (no network)."""

from __future__ import annotations

import http.client
from typing import Any, NoReturn

import pytest

from nuclear_war_agents.llm_http_transport import LLMHttpError, send_http

_URL = "http://localhost:9/v1/chat/completions"


def _patched_urlopen(monkeypatch: pytest.MonkeyPatch, exc: Exception) -> None:
    def _raise(*args: Any, **kwargs: Any) -> NoReturn:
        del args, kwargs
        raise exc

    monkeypatch.setattr("urllib.request.urlopen", _raise)


def test_send_http_wraps_non_http_reply_as_llm_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # A misconfigured endpoint replying non-HTTP bytes raises
    # http.client.BadStatusLine (an HTTPException, NOT an OSError). It must
    # take the same clean recoverable path as a connection drop so tools like
    # llm-preflight report it instead of crashing with a raw traceback.
    _patched_urlopen(monkeypatch, http.client.BadStatusLine("GARBAGE NOT HTTP"))

    with pytest.raises(LLMHttpError, match="LLM HTTP request failed"):
        send_http(_URL, {}, b"{}", 1)


def test_send_http_wraps_oserror_as_llm_http_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _patched_urlopen(monkeypatch, ConnectionRefusedError("Connection refused"))

    with pytest.raises(LLMHttpError, match="Connection refused"):
        send_http(_URL, {}, b"{}", 1)
