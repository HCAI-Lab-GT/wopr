"""HTTP transport primitives for OpenAI-compatible LLM clients."""

from __future__ import annotations

import http.client
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass


class LLMHttpError(RuntimeError):
    """Raised when an HTTP model request cannot produce a usable response.

    Treated as a *recoverable* transient provider fault by decision agents:
    timeouts, connection drops, and provider-side HTTP errors are worth one
    retry. Deliberate misconfiguration raises :class:`LLMConfigError` instead.
    """

    def __init__(self, message: str, *, provider_attempts: int = 1) -> None:
        super().__init__(message)
        self.provider_attempts = provider_attempts


class LLMConfigError(LLMHttpError):
    """Raised when an HTTP model client is misconfigured (missing url/model/key).

    A subclass of :class:`LLMHttpError` so existing ``except LLMHttpError``
    handlers still catch it, but distinct so decision agents can keep config
    faults *fatal* (retrying a missing API key never helps).
    """


@dataclass(frozen=True)
class HTTPResponse:
    status_code: int
    body: str


HTTPTransport = Callable[[str, dict[str, str], bytes, int], HTTPResponse]


def provider_attempts_from_error(error: Exception) -> int:
    attempts = getattr(error, "provider_attempts", 1)
    return attempts if type(attempts) is int and attempts > 0 else 1


def send_http(
    url: str,
    headers: dict[str, str],
    body: bytes,
    timeout_seconds: int,
) -> HTTPResponse:
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            return HTTPResponse(
                int(response.status),
                response.read().decode("utf-8"),
            )
    except urllib.error.HTTPError as exc:
        return HTTPResponse(int(exc.code), exc.read().decode("utf-8"))
    except (OSError, http.client.HTTPException) as exc:
        # OSError covers socket timeouts and connection drops; HTTPException
        # (e.g. BadStatusLine from a non-HTTP responder) is NOT an OSError and
        # must take the same recoverable path instead of escaping as a raw
        # traceback through preflight and decision agents.
        raise LLMHttpError(f"LLM HTTP request failed: {exc}") from exc


__all__ = [
    "HTTPResponse",
    "HTTPTransport",
    "LLMConfigError",
    "LLMHttpError",
    "provider_attempts_from_error",
    "send_http",
]
