"""Trace-derived decision metrics for no-press LLM harnesses."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

DECISION_METRIC_FIELDS = (
    "trace_count",
    "invalid_action_count",
    "retry_count",
    "invalid_action_rate",
    "retry_rate",
)
DECISION_COUNT_FIELDS = (
    "trace_count",
    "invalid_action_count",
    "retry_count",
)


def player_decision_metrics(
    player_ids: Iterable[str],
    traces: list[dict[str, Any]],
) -> dict[str, dict[str, int | float]]:
    metrics = {str(player_id): _empty_counts() for player_id in player_ids}
    for trace in traces:
        player_id = str(trace["player_id"])
        metrics.setdefault(player_id, _empty_counts())
        metrics[player_id]["trace_count"] += 1
        metrics[player_id]["invalid_action_count"] += len(trace["validation_errors"])
        metrics[player_id]["retry_count"] += int(trace["retries"])
    return _with_rates(metrics)


def agent_decision_metrics(
    results: list[dict[str, Any]],
    seat_config: dict[str, str],
) -> dict[str, dict[str, int | float]]:
    metrics = {agent: _empty_counts() for agent in sorted(set(seat_config.values()))}
    for result in results:
        for player_id, player_metrics in result["player_decision_metrics"].items():
            agent = seat_config[str(player_id)]
            for field in DECISION_COUNT_FIELDS:
                metrics[agent][field] += int(player_metrics[field])
    return _with_rates(metrics)


def _empty_counts() -> dict[str, int]:
    return {field: 0 for field in DECISION_COUNT_FIELDS}


def _with_rates(
    metrics: dict[str, dict[str, int]],
) -> dict[str, dict[str, int | float]]:
    return {key: _metric_rates(values) for key, values in metrics.items()}


def _metric_rates(values: dict[str, int]) -> dict[str, int | float]:
    trace_count = values["trace_count"]
    return {
        **values,
        "invalid_action_rate": _rate(values["invalid_action_count"], trace_count),
        "retry_rate": _rate(values["retry_count"], trace_count),
    }


def _rate(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


__all__ = [
    "agent_decision_metrics",
    "player_decision_metrics",
]
