"""Known HTTP provider defaults for LLM clients."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HTTPProviderDefaults:
    base_url: str | None
    model_env: str | None
    api_key_env: str | None
    provider_label: str


_PROVIDERS = {
    "openai_compatible": HTTPProviderDefaults(
        base_url=None,
        model_env=None,
        api_key_env=None,
        provider_label="openai_compatible",
    ),
    "together": HTTPProviderDefaults(
        base_url="https://api.together.ai/v1",
        model_env="WOPR_LLM_MODEL",
        api_key_env="TOGETHER_API_KEY",
        provider_label="together",
    ),
}


def http_provider_defaults(provider: str) -> HTTPProviderDefaults:
    try:
        return _PROVIDERS[provider]
    except KeyError as exc:
        allowed = ", ".join(sorted(_PROVIDERS))
        raise ValueError(
            f"Unknown LLM HTTP provider {provider!r}; expected {allowed}"
        ) from exc


def known_http_providers() -> set[str]:
    return set(_PROVIDERS)


__all__ = [
    "HTTPProviderDefaults",
    "http_provider_defaults",
    "known_http_providers",
]
