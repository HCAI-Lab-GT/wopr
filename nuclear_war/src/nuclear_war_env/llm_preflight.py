"""One-call live endpoint preflight for pilot LLM experiment configs.

Loads a pilot config (no-press ``llm_http`` batch or Concordia
``concordia_http`` game), resolves the first HTTP seat's client settings
(including env vars), and makes ONE cheap completion call. The report never
contains the API key; only the name of the env var that supplies it.
"""

from __future__ import annotations

import os
from typing import Any

from nuclear_war_agents import HTTPClientConfig, LLMHttpClient, LLMHttpError
from nuclear_war_agents.llm_http_transport import HTTPTransport
from nuclear_war_concordia.condition_payloads import authority_snapshot, press_snapshot
from nuclear_war_concordia.config import load_concordia_no_press_config
from nuclear_war_concordia.harness_payloads import HTTP_CLIENT_SNAPSHOT_FIELDS

from .llm_harness_batch_config import load_no_press_llm_batch_config

PREFLIGHT_PROMPT = (
    'Reply with exactly this JSON and nothing else: {"action_id": "preflight:ok"}'
)


def run_llm_preflight(
    payload: Any,
    transport: HTTPTransport | None = None,
) -> dict[str, Any]:
    config_kind, seat_id, client_config = _resolve_client(payload)
    client = LLMHttpClient(_cheap_variant(client_config), transport=transport)
    try:
        base_url = _resolved(client_config.base_url, client_config.base_url_env)
        completion = client.complete(PREFLIGHT_PROMPT)
    except LLMHttpError as exc:
        raise ValueError(f"LLM preflight request failed: {exc}") from exc
    return {
        "ok": True,
        "config_kind": config_kind,
        "seat": seat_id,
        "endpoint": f"{base_url.rstrip('/')}/chat/completions",
        "provider_label": client_config.provider_label,
        "model": completion.provider_model,
        "api_key_env": client_config.api_key_env,
        "latency_ms": completion.provider_latency_ms,
        "transport_retries": completion.provider_transport_retries,
        "response_snippet_chars": len(completion.raw_response),
    }


def resolve_llm_preflight_config(payload: Any) -> dict[str, Any]:
    """Resolve a pilot config without constructing a client or making a call."""
    config_kind, seat_id, client_config = _resolve_client(payload)
    report: dict[str, Any] = {
        "config_kind": config_kind,
        "seat": seat_id,
        "client": _client_snapshot(client_config),
    }
    if config_kind == "concordia":
        config = load_concordia_no_press_config(payload)
        seat = config.seats[seat_id]
        if seat.authority is not None:
            report["authority"] = authority_snapshot(seat.authority)
            report["press"] = press_snapshot(config.press)
    return report


def _resolve_client(payload: Any) -> tuple[str, str, HTTPClientConfig]:
    errors: list[str] = []
    try:
        config = load_no_press_llm_batch_config(payload)
    except ValueError as exc:
        errors.append(f"no-press llm_http parser: {exc}")
    else:
        return ("no_press_llm_http", *_first_http_seat(config.seats))
    try:
        concordia = load_concordia_no_press_config(payload)
    except ValueError as exc:
        errors.append(f"concordia parser: {exc}")
    else:
        return ("concordia", *_first_http_seat(concordia.seats))
    details = "; ".join(errors)
    raise ValueError(f"Config is not a recognized pilot experiment config: {details}")


def _first_http_seat(seats: Any) -> tuple[str, HTTPClientConfig]:
    for seat_id in sorted(seats):
        client = seats[seat_id].client
        if client is not None:
            return seat_id, client
    raise ValueError("Config has no HTTP-client seat to preflight")


def _cheap_variant(config: HTTPClientConfig) -> HTTPClientConfig:
    # One tiny deterministic completion is enough to prove the endpoint,
    # model id, and credentials work; do not spend the seat's real budget.
    return HTTPClientConfig(
        base_url=config.base_url,
        model=config.model,
        base_url_env=config.base_url_env,
        model_env=config.model_env,
        api_key_env=config.api_key_env,
        provider_label=config.provider_label,
        timeout_seconds=config.timeout_seconds,
        temperature=0.0,
        max_tokens=32,
        reasoning_effort=config.reasoning_effort,
    )


def _client_snapshot(config: HTTPClientConfig) -> dict[str, Any]:
    return {field: getattr(config, field) for field in HTTP_CLIENT_SNAPSHOT_FIELDS}


def _resolved(value: str | None, env_name: str | None) -> str:
    resolved = value or (os.environ.get(env_name) if env_name else None)
    if not resolved:
        raise ValueError(
            f"LLM preflight requires environment variable {env_name}"
            if env_name
            else "LLM preflight client is missing base_url"
        )
    return resolved


__all__ = [
    "PREFLIGHT_PROMPT",
    "resolve_llm_preflight_config",
    "run_llm_preflight",
]
