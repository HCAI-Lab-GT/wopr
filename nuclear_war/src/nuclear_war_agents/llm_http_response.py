"""HTTP response parsing for OpenAI-compatible LLM clients."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from .llm_http_transport import LLMHttpError


def response_json(body: str) -> dict[str, Any]:
    if body.lstrip().startswith("data:"):
        return _stream_response_json(body)
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise LLMHttpError("LLM HTTP response is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise LLMHttpError("LLM HTTP response must be an object")
    return payload


def message_content(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise LLMHttpError("LLM HTTP response choices are missing")
    first = choices[0]
    message = first.get("message") if isinstance(first, dict) else None
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content:
        content = first.get("text") if isinstance(first, dict) else None
    if not isinstance(content, str) or not content:
        raise LLMHttpError("LLM HTTP response message content is missing")
    return content


def provider_usage(value: Any) -> dict[str, int | float] | None:
    if not isinstance(value, Mapping):
        return None
    usage = {
        str(key): item
        for key, item in value.items()
        if isinstance(item, int | float) and not isinstance(item, bool)
    }
    return usage or None


def _stream_response_json(body: str) -> dict[str, Any]:
    content_parts: list[str] = []
    reasoning_parts: list[str] = []
    usage: Any = None
    model: Any = None
    finish_reason: Any = None
    for line in body.splitlines():
        if not line.startswith("data:"):
            continue
        item = line.removeprefix("data:").strip()
        if not item or item == "[DONE]":
            continue
        chunk = _stream_chunk(item)
        model = model or chunk.get("model")
        usage = chunk.get("usage") or usage
        choice = _first_choice(chunk)
        if choice is None:
            continue
        finish_reason = choice.get("finish_reason") or finish_reason
        delta = choice.get("delta")
        if isinstance(delta, Mapping):
            _append_str(content_parts, delta.get("content"))
            _append_str(reasoning_parts, delta.get("reasoning"))
    return {
        "choices": [
            {
                "finish_reason": finish_reason,
                "message": {
                    "content": "".join(content_parts),
                    "reasoning": "".join(reasoning_parts),
                },
            }
        ],
        "model": model,
        "usage": usage,
    }


def _stream_chunk(item: str) -> dict[str, Any]:
    try:
        payload = json.loads(item)
    except json.JSONDecodeError as exc:
        raise LLMHttpError("LLM HTTP stream response is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise LLMHttpError("LLM HTTP stream response chunk must be an object")
    return payload


def _first_choice(payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return None
    first = choices[0]
    return first if isinstance(first, Mapping) else None


def _append_str(parts: list[str], value: Any) -> None:
    if isinstance(value, str) and value:
        parts.append(value)


__all__ = ["message_content", "provider_usage", "response_json"]
