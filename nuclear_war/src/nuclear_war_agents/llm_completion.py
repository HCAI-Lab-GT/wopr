"""Completion normalization for WOPR-native LLM clients."""

from __future__ import annotations

from collections.abc import Iterable

from .llm_types import LLMCompletion


def normalize_completion(value: str | LLMCompletion) -> LLMCompletion:
    if isinstance(value, LLMCompletion):
        return value
    return LLMCompletion(raw_response=value)


def total_provider_latency(completions: Iterable[LLMCompletion]) -> int | None:
    values = [
        completion.provider_latency_ms
        for completion in completions
        if completion.provider_latency_ms is not None
    ]
    return sum(values) if values else None


def total_provider_cost(completions: Iterable[LLMCompletion]) -> float | None:
    values = [
        completion.provider_cost
        for completion in completions
        if completion.provider_cost is not None
    ]
    return sum(values) if values else None


def total_provider_usage(
    completions: Iterable[LLMCompletion],
) -> dict[str, int | float] | None:
    totals: dict[str, int | float] = {}
    for completion in completions:
        for key, value in (completion.provider_usage or {}).items():
            totals[key] = totals.get(key, 0) + value
    return totals or None


def first_provider_label(completions: Iterable[LLMCompletion]) -> str | None:
    for completion in completions:
        if completion.provider_label is not None:
            return completion.provider_label
    return None


def first_provider_model(completions: Iterable[LLMCompletion]) -> str | None:
    for completion in completions:
        if completion.provider_model is not None:
            return completion.provider_model
    return None


def total_provider_transport_retries(completions: Iterable[LLMCompletion]) -> int:
    return sum(completion.provider_transport_retries for completion in completions)


__all__ = [
    "first_provider_label",
    "first_provider_model",
    "normalize_completion",
    "total_provider_cost",
    "total_provider_latency",
    "total_provider_transport_retries",
    "total_provider_usage",
]
