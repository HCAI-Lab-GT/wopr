"""Validation for no-press LLM batch artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .integer_validation import is_strict_int, is_strict_number
from .llm_harness_batch_config_snapshot import validate_batch_config_snapshot
from .llm_harness_batch_result_values import expected_no_press_llm_result_values
from .llm_harness_batch_schema import (
    BATCH_FIELDS,
    OPTIONAL_RESULT_FIELDS,
    OPTIONAL_SUMMARY_FIELDS,
    RESULT_FIELDS,
    RESULT_INT_FIELDS,
    SUMMARY_FIELDS,
    SUMMARY_INT_FIELDS,
)
from .llm_harness_batch_summary import summarize_no_press_llm_results
from .llm_trace_artifacts import read_trace_artifact
from .replay import read_replay


def validate_no_press_llm_batch(payload: Any, base_dir: Path) -> None:
    if not isinstance(payload, dict):
        raise ValueError("LLM experiment summary must be an object")
    _require_fields(payload, BATCH_FIELDS, "LLM experiment summary")
    if payload["mode"] != "table":
        raise ValueError("LLM experiment mode must be table")
    for field in ("players", "seed_start", "runs", "max_turns"):
        _validate_int(payload, field)
    if not isinstance(payload["seat_config"], dict):
        raise ValueError("LLM experiment seat_config must be an object")
    validate_batch_config_snapshot(payload["config"], payload)
    results = payload["results"]
    if not isinstance(results, list):
        raise ValueError("LLM experiment results must be a list")
    if len(results) != payload["runs"]:
        raise ValueError("LLM experiment results length must match runs")
    for index, result in enumerate(results):
        _validate_result(result, index, base_dir, payload)
    _validate_summary(payload["summary"], results, payload["seat_config"])


def _validate_result(
    result: Any,
    index: int,
    base_dir: Path,
    metadata: dict[str, Any],
) -> None:
    if not isinstance(result, dict):
        raise ValueError(f"LLM experiment result {index} must be an object")
    context = f"LLM experiment result {index}"
    _require_fields(result, RESULT_FIELDS, context, OPTIONAL_RESULT_FIELDS)
    for field in RESULT_INT_FIELDS:
        _validate_int(result, field)
    _validate_result_shapes(result, context)
    if result["seed"] != metadata["seed_start"] + index:
        raise ValueError(f"{context} seed does not match seed_start")
    replay = read_replay(_linked_path(base_dir, result["replay_path"], "replay_path"))
    if replay["players"] != metadata["players"]:
        raise ValueError(f"{context} players does not match replay")
    if replay["turns"] > metadata["max_turns"]:
        raise ValueError(f"{context} turns exceeds max_turns")
    if replay["active_variant"]["variant_id"] != metadata["config"]["variant_id"]:
        raise ValueError(f"{context} variant_id does not match replay")
    trace = read_trace_artifact(
        _linked_path(base_dir, result["trace_path"], "trace_path"),
        replay,
    )
    _validate_result_links(result, replay, trace, index)


def _validate_result_shapes(result: dict[str, Any], context: str) -> None:
    if not isinstance(result["termination_reason"], str):
        raise ValueError(f"{context} termination_reason must be a string")
    if not isinstance(result["elimination_order"], list):
        raise ValueError(f"{context} elimination_order must be a list")
    if not isinstance(result["win_loss"], dict):
        raise ValueError(f"{context} win_loss must be an object")


def _validate_summary(
    summary: Any,
    results: list[dict[str, Any]],
    seat_config: dict[str, str],
) -> None:
    if not isinstance(summary, dict):
        raise ValueError("LLM experiment aggregate summary must be an object")
    _require_fields(
        summary,
        SUMMARY_FIELDS,
        "LLM experiment aggregate summary",
        OPTIONAL_SUMMARY_FIELDS,
    )
    if summary != summarize_no_press_llm_results(results, seat_config):
        raise ValueError("LLM experiment aggregate summary does not match results")
    if not is_strict_number(summary["average_turns"]):
        raise ValueError("LLM experiment aggregate average_turns must be a number")
    for field in SUMMARY_INT_FIELDS:
        _validate_int(summary, field)


def _validate_result_links(
    result: dict[str, Any],
    replay: dict[str, Any],
    trace: dict[str, Any],
    index: int,
) -> None:
    expected = expected_no_press_llm_result_values(replay, trace)
    for field, value in expected.items():
        if result[field] != value:
            raise ValueError(
                f"LLM experiment result {index} {field} does not match files"
            )


def _linked_path(base_dir: Path, value: Any, field: str) -> Path:
    if not isinstance(value, str) or not value:
        raise ValueError(f"LLM experiment {field} must be a string")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"LLM experiment {field} must be relative to summary")
    return base_dir / path


def _require_fields(
    payload: dict[str, Any],
    fields: tuple[str, ...],
    context: str,
    optional_fields: tuple[str, ...] = (),
) -> None:
    missing = sorted(set(fields) - set(payload))
    if missing:
        raise ValueError(f"{context} missing required field: {missing[0]}")
    if set(payload) - set(fields) - set(optional_fields):
        raise ValueError(f"{context} fields are invalid")


def _validate_int(payload: dict[str, Any], field: str) -> None:
    if not is_strict_int(payload[field]):
        raise ValueError(f"LLM experiment {field} must be an integer")
