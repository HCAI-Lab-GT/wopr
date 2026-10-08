"""Restore bounded-run consumption when a cell is resumed."""

from __future__ import annotations

from typing import Any


def restore_initial_metrics(budget: Any) -> None:
    for channel in ("c2", "press"):
        values = (
            budget.initial_metrics.get(channel, {}) if budget.initial_metrics else {}
        )
        if not isinstance(values, dict):
            continue
        budget._set(channel, "calls", _nonnegative(values.get("call_count", 0)))
        budget._set(
            channel,
            "provider_attempts",
            _nonnegative(
                values.get("provider_attempt_count", values.get("call_count", 0))
            ),
        )
    source = budget.initial_metrics or {}
    budget.reserved_cost_usd = _number(source.get("reserved_cost_usd", 0))
    budget.actual_cost_usd = _number(source.get("actual_cost_usd", 0))


def _nonnegative(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("Budget snapshots require nonnegative integer counts")
    return value


def _number(value: Any) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0:
        raise ValueError("Budget snapshots require nonnegative numeric costs")
    return float(value)
