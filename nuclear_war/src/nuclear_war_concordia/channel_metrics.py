"""Call and provider-usage metrics separated by Concordia channel."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.llm_harness_provider_metrics import provider_metrics_from_traces


def build_channel_metrics(
    strategic_traces: list[dict[str, Any]],
    c2_artifact: dict[str, Any] | None,
    press_traces: list[dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    return {
        "strategic": _trace_metrics(strategic_traces),
        "c2": _trace_metrics(_c2_traces(c2_artifact)),
        "press": _trace_metrics(press_traces),
    }


def _c2_traces(c2_artifact: dict[str, Any] | None) -> list[dict[str, Any]]:
    if c2_artifact is None:
        return []
    return [
        member["trace"]
        for deliberation in c2_artifact["deliberations"]
        for member in deliberation["members"]
    ]


def _trace_metrics(traces: list[dict[str, Any]]) -> dict[str, Any]:
    provider_retries = sum(
        int(trace.get("recoverable_provider_retries", 0)) for trace in traces
    )
    metrics = {
        "trace_count": len(traces),
        "call_count": sum(_completion_count(trace) for trace in traces)
        + provider_retries,
        "retry_count": sum(int(trace.get("retries", 0)) for trace in traces),
        "recoverable_provider_retry_count": provider_retries,
        "provider_usage": _provider_usage(traces),
    }
    metrics.update(provider_metrics_from_traces(traces))
    return metrics


def _completion_count(trace: dict[str, Any]) -> int:
    responses = trace.get("raw_responses")
    return len(responses) if isinstance(responses, list) else 1


def _provider_usage(traces: list[dict[str, Any]]) -> dict[str, int | float]:
    totals: dict[str, int | float] = {}
    for trace in traces:
        usage = trace.get("provider_usage")
        if not isinstance(usage, dict):
            continue
        for key, value in usage.items():
            if isinstance(value, int | float) and not isinstance(value, bool):
                totals[key] = totals.get(key, 0) + value
    return totals


__all__ = ["build_channel_metrics"]
