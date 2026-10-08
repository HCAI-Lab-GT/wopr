"""HTTP LLM client config parsing for no-press harness seats."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_agents.llm_http_providers import http_provider_defaults

from . import llm_harness_batch_config_values as values

CLIENT_FIELDS = {
    "provider",
    "base_url",
    "base_url_env",
    "model",
    "model_env",
    "api_key_env",
    "provider_label",
    "timeout_seconds",
    "temperature",
    "max_tokens",
    "reasoning_effort",
    "reasoning_enabled",
    "stream",
}
REASONING_EFFORTS = {"low", "medium", "high"}


def http_client_config(payload: Any, context: str) -> HTTPClientConfig:
    if not isinstance(payload, dict):
        raise ValueError(f"{context} client must be an object")
    _validate_fields(payload, context)
    provider = values.str_value(
        payload,
        "provider",
        "openai_compatible",
        context,
    )
    defaults = _defaults(provider, context)
    config = HTTPClientConfig(
        provider=provider,
        base_url=_defaulted_str(payload, "base_url", defaults.base_url, context),
        base_url_env=values.optional_str_value(payload, "base_url_env", context),
        model=values.optional_str_value(payload, "model", context),
        model_env=_defaulted_str(payload, "model_env", defaults.model_env, context),
        api_key_env=_defaulted_str(
            payload,
            "api_key_env",
            defaults.api_key_env,
            context,
        ),
        provider_label=_defaulted_str(
            payload,
            "provider_label",
            defaults.provider_label,
            context,
        ),
        timeout_seconds=values.nonnegative_int(
            payload,
            "timeout_seconds",
            60,
            context,
        ),
        temperature=_number_value(payload, "temperature", 0.0, context),
        max_tokens=values.nonnegative_int(payload, "max_tokens", 256, context),
        reasoning_effort=values.optional_str_value(
            payload,
            "reasoning_effort",
            context,
        ),
        reasoning_enabled=values.optional_bool_value(
            payload, "reasoning_enabled", context
        ),
        stream=values.bool_value(payload, "stream", False, context),
    )
    _validate_sources(config, context)
    return config


def _validate_fields(payload: dict[str, Any], context: str) -> None:
    if set(payload) - CLIENT_FIELDS:
        raise ValueError(f"{context} client fields are invalid")


def _validate_sources(config: HTTPClientConfig, context: str) -> None:
    defaults = _defaults(config.provider, context)
    if not (config.base_url or config.base_url_env):
        if defaults.base_url is None:
            raise ValueError(f"{context} client base_url or base_url_env is required")
    if not (config.model or config.model_env):
        raise ValueError(f"{context} client model or model_env is required")
    if config.timeout_seconds < 1:
        raise ValueError(f"{context} client timeout_seconds must be positive")
    if config.max_tokens < 1:
        raise ValueError(f"{context} client max_tokens must be positive")
    if (
        config.reasoning_effort is not None
        and config.reasoning_effort not in REASONING_EFFORTS
    ):
        raise ValueError(f"{context} client reasoning_effort is invalid")


def _number_value(
    payload: dict[str, Any],
    key: str,
    default: float,
    context: str,
) -> float:
    value = payload.get(key, default)
    if not isinstance(value, int | float) or isinstance(value, bool):
        raise ValueError(f"{context} client {key} must be a number")
    return float(value)


def _defaulted_str(
    payload: dict[str, Any],
    key: str,
    default: str | None,
    context: str,
) -> str | None:
    value = values.optional_str_value(payload, key, context)
    return value if value is not None else default


def _defaults(provider: str, context: str):
    try:
        return http_provider_defaults(provider)
    except ValueError as exc:
        raise ValueError(f"{context} client provider is invalid") from exc


__all__ = ["http_client_config"]
