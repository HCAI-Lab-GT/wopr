"""Configuration and request helpers for the HTTP model client."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass

from nuclear_war_env.local_env import load_local_dotenv

from .llm_http_providers import http_provider_defaults
from .llm_http_transport import LLMConfigError, LLMHttpError


@dataclass(frozen=True)
class HTTPClientConfig:
    provider: str = "openai_compatible"
    base_url: str | None = None
    model: str | None = None
    base_url_env: str | None = None
    model_env: str | None = None
    api_key_env: str | None = None
    provider_label: str | None = None
    timeout_seconds: int = 60
    temperature: float = 0.0
    max_tokens: int = 256
    reasoning_effort: str | None = None
    reasoning_enabled: bool | None = None
    stream: bool = False


def request_body(prompt: str, model: str, config: HTTPClientConfig) -> bytes:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }
    if config.reasoning_effort is not None:
        payload["reasoning_effort"] = config.reasoning_effort
    if config.reasoning_enabled is not None:
        payload["reasoning"] = {"enabled": config.reasoning_enabled}
    if config.stream:
        payload["stream"] = True
    return json.dumps(payload).encode("utf-8")


def headers(api_key_env: str | None) -> dict[str, str]:
    values = {"Content-Type": "application/json", "User-Agent": "WOPR/0.1"}
    if api_key_env is not None:
        values["Authorization"] = f"Bearer {env_value(api_key_env)}"
    return values


def required_config_value(value: str | None, env_name: str | None, field: str) -> str:
    resolved = value or (env_value(env_name) if env_name else None)
    if not resolved:
        raise LLMConfigError(f"LLM HTTP client requires {field}")
    return resolved.rstrip("/") if field == "base_url" else resolved


def env_value(env_name: str) -> str:
    load_local_dotenv()
    value = os.environ.get(env_name)
    if not value:
        raise LLMConfigError(
            f"LLM HTTP client requires environment variable {env_name}"
        )
    return value


def provider_defaults(provider: str):
    try:
        return http_provider_defaults(provider)
    except ValueError as exc:
        raise LLMHttpError(str(exc)) from exc
