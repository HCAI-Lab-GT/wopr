"""Provider metadata summaries for no-press LLM harnesses."""

from __future__ import annotations

from typing import Any


def provider_metrics_from_traces(
    traces: list[dict[str, Any]],
) -> dict[str, int | float]:
    metrics: dict[str, int | float] = {}
    latency = _sum_present_int(traces, "provider_latency_ms")
    cost = _sum_present_float(traces, "provider_cost")
    if latency is not None:
        metrics["provider_latency_ms"] = latency
    if cost is not None:
        metrics["provider_cost"] = cost
    return metrics


def provider_totals_from_results(
    results: list[dict[str, Any]],
) -> dict[str, int | float]:
    metrics: dict[str, int | float] = {}
    latency = _sum_present_int(results, "provider_latency_ms")
    cost = _sum_present_float(results, "provider_cost")
    if latency is not None:
        metrics["total_provider_latency_ms"] = latency
    if cost is not None:
        metrics["total_provider_cost"] = cost
    return metrics


def _sum_present_int(items: list[dict[str, Any]], key: str) -> int | None:
    values = [int(item[key]) for item in items if item.get(key) is not None]
    return sum(values) if values else None


def _sum_present_float(items: list[dict[str, Any]], key: str) -> float | None:
    values = [float(item[key]) for item in items if item.get(key) is not None]
    return sum(values) if values else None


__all__ = [
    "provider_metrics_from_traces",
    "provider_totals_from_results",
]
