from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from . import llm_http_completion as http_completion
from .llm_http_config import (
    HTTPClientConfig,
    headers,
    provider_defaults,
    request_body,
    required_config_value,
)
from .llm_http_transport import HTTPTransport, LLMHttpError, send_http
from .llm_types import LLMCompletion

MAX_HTTP_ATTEMPTS, RETRYABLE_STATUS_CODES = 3, {429}


@dataclass(frozen=True)
class LLMHttpClient:
    config: HTTPClientConfig
    transport: HTTPTransport | None = None
    monotonic_ms: Callable[[], int] | None = None
    request_guard: Callable[[], None] | None = None
    input_token_guard: Callable[[str], None] | None = None

    def complete(self, prompt: str) -> LLMCompletion:
        defaults = provider_defaults(self.config.provider)
        base_url = required_config_value(
            self.config.base_url or defaults.base_url,
            self.config.base_url_env,
            "base_url",
        )
        model = required_config_value(
            self.config.model,
            self.config.model_env or defaults.model_env,
            "model",
        )
        request_headers = headers(self.config.api_key_env or defaults.api_key_env)
        clock = self.monotonic_ms or _monotonic_ms
        start_ms = clock()
        transport = self.transport or send_http
        url = f"{base_url.rstrip('/')}/chat/completions"
        if self.input_token_guard is not None:
            self.input_token_guard(prompt)
        body = request_body(prompt, model, self.config)
        parsed = None
        transport_retries = 0
        for attempt in range(MAX_HTTP_ATTEMPTS):
            if self.request_guard is not None:
                self.request_guard()
            response = transport(
                url, request_headers, body, self.config.timeout_seconds
            )
            retryable = (
                response.status_code in RETRYABLE_STATUS_CODES
                or response.status_code >= 500
            )
            if response.status_code < 400:
                try:
                    parsed = http_completion.parsed_http_completion(response)
                except LLMHttpError as exc:
                    if not http_completion.retryable_empty_completion(
                        exc, attempt, MAX_HTTP_ATTEMPTS
                    ):
                        raise _with_provider_attempts(exc, attempt + 1) from exc
                    transport_retries += 1
                    continue
                break
            if not retryable:
                break
            if attempt == MAX_HTTP_ATTEMPTS - 1:
                break
            transport_retries += 1
            _sleep_before_retry(response.status_code)
        latency_ms = max(0, clock() - start_ms)
        if response.status_code >= 400:
            raise LLMHttpError(
                http_completion.http_error_message(response),
                provider_attempts=attempt + 1,
            )
        if parsed is None:
            try:
                parsed = http_completion.parsed_http_completion(response)
            except LLMHttpError as exc:
                raise _with_provider_attempts(exc, attempt + 1) from exc
        return LLMCompletion(
            raw_response=parsed.raw_response,
            provider_latency_ms=latency_ms,
            provider_usage=parsed.provider_usage,
            provider_label=self.config.provider_label or defaults.provider_label,
            provider_model=model,
            provider_transport_retries=transport_retries,
        )


def _sleep_before_retry(status_code: int) -> None:
    if status_code == 429:
        time.sleep(1.0)


def _monotonic_ms() -> int:
    return time.monotonic_ns() // 1_000_000


def _with_provider_attempts(error: LLMHttpError, attempts: int) -> LLMHttpError:
    error.provider_attempts = attempts
    return error
