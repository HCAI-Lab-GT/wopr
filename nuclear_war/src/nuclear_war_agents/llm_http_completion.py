"""HTTP completion extraction helpers for LLM clients."""

from __future__ import annotations

from dataclasses import dataclass

from .llm_http_response import message_content, provider_usage, response_json
from .llm_http_transport import HTTPResponse, LLMHttpError

_MISSING_MESSAGE_CONTENT = "LLM HTTP response message content is missing"


@dataclass(frozen=True)
class ParsedHTTPCompletion:
    raw_response: str
    provider_usage: dict[str, int | float] | None


def parsed_http_completion(response: HTTPResponse) -> ParsedHTTPCompletion:
    payload = response_json(response.body)
    return ParsedHTTPCompletion(
        message_content(payload),
        provider_usage(payload.get("usage")),
    )


def http_error_message(response: HTTPResponse) -> str:
    message = f"LLM HTTP request failed with {response.status_code}"
    try:
        payload = response_json(response.body)
    except LLMHttpError:
        return message
    error = payload.get("error")
    detail = error.get("message") if isinstance(error, dict) else None
    return f"{message}: {detail}" if isinstance(detail, str) and detail else message


def retryable_empty_completion(
    exc: LLMHttpError,
    attempt: int,
    max_attempts: int,
) -> bool:
    return str(exc) == _MISSING_MESSAGE_CONTENT and attempt < max_attempts - 1
