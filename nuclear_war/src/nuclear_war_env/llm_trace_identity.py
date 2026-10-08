"""Trace identity validation for separate LLM trace artifacts."""

from __future__ import annotations

from typing import Any


def validate_trace_identity(trace: dict[str, Any], index: int) -> None:
    expected_prefix = f"{trace['player_id']}:{trace['turn']}:"
    trace_id = trace["trace_id"]
    if not trace_id.startswith(expected_prefix):
        raise ValueError(f"Trace {index} trace_id does not match trace context")
    _validate_trace_id_index(trace_id.removeprefix(expected_prefix), index)


def _validate_trace_id_index(value: str, index: int) -> None:
    if not value.isdecimal() or int(value) <= 0:
        raise ValueError(f"Trace {index} trace_id index must be positive")


def validate_unique_trace_ids(traces: list[Any]) -> None:
    seen: set[str] = set()
    for index, trace in enumerate(traces):
        if not isinstance(trace, dict):
            continue
        trace_id = trace.get("trace_id")
        if isinstance(trace_id, str) and trace_id in seen:
            raise ValueError(f"Trace {index} duplicate trace_id")
        if isinstance(trace_id, str):
            seen.add(trace_id)


__all__ = ["validate_trace_identity", "validate_unique_trace_ids"]
