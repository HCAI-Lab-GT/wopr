"""Experiment summary validation helpers."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .integer_validation import is_strict_int, is_strict_number
from .replay_field_validation import validate_field_set

EXPERIMENT_SUMMARY_FIELDS = (
    "termination_counts",
    "winner_counts",
    "average_turns",
    "total_eliminations",
)


def validate_experiment_summary(summary: Any, results: list[Any]) -> None:
    if not isinstance(summary, dict):
        raise ValueError("Experiment summary must be an object")
    for field in EXPERIMENT_SUMMARY_FIELDS:
        if field not in summary:
            raise ValueError(f"Experiment summary missing required field: {field}")
    validate_field_set(summary, EXPERIMENT_SUMMARY_FIELDS, "Experiment summary")
    _validate_count_map(summary["termination_counts"], "termination_counts")
    _validate_count_map(summary["winner_counts"], "winner_counts")
    if not is_strict_number(summary["average_turns"]):
        raise ValueError("Experiment summary average_turns must be a number")
    if summary["average_turns"] < 0:
        raise ValueError("Experiment summary average_turns must be nonnegative")
    if not is_strict_int(summary["total_eliminations"]):
        raise ValueError("Experiment summary total_eliminations must be an integer")
    if summary["total_eliminations"] < 0:
        raise ValueError("Experiment summary total_eliminations must be nonnegative")
    _validate_summary_value(
        summary,
        "termination_counts",
        _termination_counts(results),
    )
    _validate_summary_value(summary, "winner_counts", _winner_counts(results))
    _validate_summary_value(summary, "average_turns", _average_turns(results))
    _validate_summary_value(
        summary,
        "total_eliminations",
        _total_eliminations(results),
    )


def _validate_summary_value(summary: dict[str, Any], field: str, expected: Any) -> None:
    if summary[field] != expected:
        raise ValueError(f"Experiment summary {field} does not match results")


def _validate_count_map(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"Experiment summary {field} must be an object")
    for key, count in value.items():
        if not isinstance(key, str):
            raise ValueError(f"Experiment summary {field} keys must be strings")
        if not is_strict_int(count):
            raise ValueError(f"Experiment summary {field} values must be integers")
        if count < 0:
            raise ValueError(f"Experiment summary {field} values must be nonnegative")


def _termination_counts(results: list[Any]) -> dict[str, int]:
    return _counts(str(result["termination_reason"]) for result in results)


def _winner_counts(results: list[Any]) -> dict[str, int]:
    return _counts(_winner_key(result["winner"]) for result in results)


def _average_turns(results: list[Any]) -> float:
    return sum(int(result["turns"]) for result in results) / len(results)


def _total_eliminations(results: list[Any]) -> int:
    return sum(len(result["eliminations"]) for result in results)


def _counts(values: Any) -> dict[str, int]:
    return dict(sorted(Counter(values).items()))


def _winner_key(winner: Any) -> str:
    if winner is None:
        return "no_winner"
    return str(winner)


__all__ = ["EXPERIMENT_SUMMARY_FIELDS", "validate_experiment_summary"]
