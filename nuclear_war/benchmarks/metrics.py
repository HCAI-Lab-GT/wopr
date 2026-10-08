"""Benchmark metric comparison helpers."""

from __future__ import annotations

from statistics import median

GUARDRAIL_METRICS = ("guardrail_main_ms", "phase0_main_ms")
REGRESSION_METRICS = ("table_simulation_ms", "postal_simulation_ms")
GUARDRAIL_ABSOLUTE_TOLERANCE_MS = 0.25
MICRO_BENCH_ABSOLUTE_TOLERANCE_MS = 2.0


def compare_metrics(
    current: dict[str, object], baseline: dict[str, object], threshold: float
) -> bool:
    baseline_metrics = baseline.get("metrics") if isinstance(baseline, dict) else None
    current_metrics = current.get("metrics") if isinstance(current, dict) else None
    if not isinstance(baseline_metrics, dict) or not isinstance(current_metrics, dict):
        return False
    baseline_value = _guardrail_metric_value(baseline_metrics)
    current_value = _guardrail_compare_value(current, current_metrics)
    if baseline_value is None or current_value is None:
        return False
    allowed = _guardrail_allowed(baseline_value, threshold)
    if current_value > allowed:
        return False
    return _simulation_metrics_ok(current_metrics, baseline_metrics, threshold)


def _guardrail_metric_value(metrics: dict[object, object]) -> float | None:
    for metric in GUARDRAIL_METRICS:
        value = metrics.get(metric)
        if isinstance(value, int | float):
            return float(value)
    return None


def _guardrail_compare_value(
    current: dict[str, object], current_metrics: dict[object, object]
) -> float | None:
    timeline = current.get("timeline")
    if isinstance(timeline, list):
        samples: list[float] = []
        for item in timeline:
            if not isinstance(item, dict):
                continue
            elapsed = item.get("elapsed_ms")
            if isinstance(elapsed, int | float):
                samples.append(float(elapsed))
        if samples:
            return float(median(samples))
    return _guardrail_metric_value(current_metrics)


def _simulation_metrics_ok(
    current_metrics: dict[object, object],
    baseline_metrics: dict[object, object],
    threshold: float,
) -> bool:
    for metric in REGRESSION_METRICS:
        baseline_value = baseline_metrics.get(metric)
        if baseline_value is None:
            continue
        current_value = current_metrics.get(metric)
        if not isinstance(baseline_value, int | float):
            return False
        if not isinstance(current_value, int | float):
            return False
        if float(current_value) > _metric_allowed(float(baseline_value), threshold):
            return False
    return True


def _guardrail_allowed(baseline_value: float, threshold: float) -> float:
    relative_allowed = baseline_value / threshold
    absolute_allowed = baseline_value + GUARDRAIL_ABSOLUTE_TOLERANCE_MS
    return max(relative_allowed, absolute_allowed)


def _metric_allowed(baseline_value: float, threshold: float) -> float:
    relative_allowed = baseline_value / threshold
    absolute_allowed = baseline_value + MICRO_BENCH_ABSOLUTE_TOLERANCE_MS
    return max(relative_allowed, absolute_allowed)


__all__ = ["compare_metrics"]
