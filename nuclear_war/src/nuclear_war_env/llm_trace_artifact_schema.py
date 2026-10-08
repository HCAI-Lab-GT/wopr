"""Schema constants for separate LLM trace artifacts."""

from __future__ import annotations

from typing import Any

TRACE_SCHEMA_VERSION = 5
SUPPORTED_TRACE_SCHEMA_VERSIONS = (1, 2, 3, 4, 5)
TRACE_FIELDS_V1 = (
    "trace_id",
    "turn",
    "player_id",
    "decision_type",
    "prompt",
    "prompts",
    "legal_options",
    "raw_response",
    "raw_responses",
    "parse_result",
    "selected_action_id",
    "retries",
    "validation_errors",
    "stated_rationale",
)
TRACE_FIELDS_V2 = (
    *TRACE_FIELDS_V1,
    "provider_latency_ms",
    "provider_cost",
)
TRACE_FIELDS = (
    *TRACE_FIELDS_V2,
    "rendered_observation",
)
TRACE_FIELDS_V4 = (
    *TRACE_FIELDS,
    "provider_usage",
    "provider_label",
    "provider_model",
)
TRACE_FIELDS_V5 = (
    *TRACE_FIELDS_V4,
    "fallback_used",
    "recoverable_provider_retries",
)


def trace_fields(schema_version: int) -> set[str]:
    if schema_version == 1:
        return set(TRACE_FIELDS_V1)
    if schema_version == 2:
        return set(TRACE_FIELDS_V2)
    if schema_version == 3:
        return set(TRACE_FIELDS)
    if schema_version == 4:
        return set(TRACE_FIELDS_V4)
    return set(TRACE_FIELDS_V5)


def validate_provider_metadata(trace: dict[str, Any], index: int) -> None:
    _validate_latency(trace["provider_latency_ms"], index)
    _validate_cost(trace["provider_cost"], index)


def validate_trace_schema(
    trace: dict[str, Any],
    index: int,
    schema_version: int,
) -> None:
    if set(trace) != trace_fields(schema_version):
        raise ValueError(f"Trace {index} fields are invalid")
    _validate_string(trace["trace_id"], index, "trace_id")
    _validate_int(trace["turn"], index, "turn")
    _validate_string(trace["player_id"], index, "player_id")
    _validate_string(trace["decision_type"], index, "decision_type")
    if schema_version >= 3:
        _validate_dict(trace["rendered_observation"], index, "rendered_observation")
    _validate_string(trace["prompt"], index, "prompt")
    _validate_string_list(trace["prompts"], index, "prompts")
    _validate_list(trace["legal_options"], index, "legal_options")
    _validate_string(trace["raw_response"], index, "raw_response")
    _validate_string_list(trace["raw_responses"], index, "raw_responses")
    _validate_parse_result(trace["parse_result"], index)
    _validate_string(trace["selected_action_id"], index, "selected_action_id")
    _validate_int(trace["retries"], index, "retries")
    _validate_string_list(trace["validation_errors"], index, "validation_errors")
    _validate_optional_string(trace["stated_rationale"], index, "stated_rationale")
    _validate_attempts(trace, index)
    if schema_version >= 2:
        validate_provider_metadata(trace, index)
    if schema_version >= 4:
        _validate_optional_usage(trace["provider_usage"], index)
        _validate_optional_string(trace["provider_label"], index, "provider_label")
        _validate_optional_string(trace["provider_model"], index, "provider_model")
    if schema_version >= 5:
        _validate_bool(trace["fallback_used"], index, "fallback_used")
        _validate_int(
            trace["recoverable_provider_retries"],
            index,
            "recoverable_provider_retries",
        )


def _validate_attempts(trace: dict[str, Any], index: int) -> None:
    if not trace["prompts"] or not trace["raw_responses"]:
        raise ValueError(f"Trace {index} prompts and raw_responses must be non-empty")
    if len(trace["prompts"]) != len(trace["raw_responses"]):
        raise ValueError(f"Trace {index} prompts must match raw_responses")
    if trace["prompt"] != trace["prompts"][-1]:
        raise ValueError(f"Trace {index} prompt must match final prompt")
    if trace["raw_response"] != trace["raw_responses"][-1]:
        raise ValueError(f"Trace {index} raw_response must match final raw_response")
    if trace["retries"] != len(trace["raw_responses"]) - 1:
        raise ValueError(f"Trace {index} retries must match raw_responses")


def _validate_parse_result(value: Any, index: int) -> None:
    if not isinstance(value, dict) or set(value) != {"action_id", "rationale"}:
        raise ValueError(f"Trace {index} parse_result must be an object")
    _validate_optional_string(value["action_id"], index, "parse_result action_id")
    _validate_optional_string(value["rationale"], index, "parse_result rationale")


def _validate_string(value: Any, index: int, field: str) -> None:
    if not isinstance(value, str):
        raise ValueError(f"Trace {index} {field} must be a string")


def _validate_optional_string(value: Any, index: int, field: str) -> None:
    if value is not None and not isinstance(value, str):
        raise ValueError(f"Trace {index} {field} must be null or string")


def _validate_string_list(value: Any, index: int, field: str) -> None:
    _validate_list(value, index, field)
    if any(not isinstance(item, str) for item in value):
        raise ValueError(f"Trace {index} {field} entries must be strings")


def _validate_list(value: Any, index: int, field: str) -> None:
    if not isinstance(value, list):
        raise ValueError(f"Trace {index} {field} must be a list")


def _validate_dict(value: Any, index: int, field: str) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"Trace {index} {field} must be an object")


def _validate_int(value: Any, index: int, field: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError(f"Trace {index} {field} must be a non-negative integer")


def _validate_bool(value: Any, index: int, field: str) -> None:
    if not isinstance(value, bool):
        raise ValueError(f"Trace {index} {field} must be a boolean")


def _validate_latency(value: Any, index: int) -> None:
    if value is not None and (
        not isinstance(value, int) or isinstance(value, bool) or value < 0
    ):
        raise ValueError(f"Trace {index} provider_latency_ms must be null or integer")


def _validate_cost(value: Any, index: int) -> None:
    if value is not None and (
        not isinstance(value, int | float) or isinstance(value, bool) or value < 0
    ):
        raise ValueError(f"Trace {index} provider_cost must be null or number")


def _validate_optional_usage(value: Any, index: int) -> None:
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValueError(f"Trace {index} provider_usage must be null or object")
    for item in value.values():
        if not isinstance(item, int | float) or isinstance(item, bool) or item < 0:
            raise ValueError(f"Trace {index} provider_usage values must be numbers")


__all__ = [
    "SUPPORTED_TRACE_SCHEMA_VERSIONS",
    "TRACE_FIELDS",
    "TRACE_SCHEMA_VERSION",
    "trace_fields",
    "validate_provider_metadata",
    "validate_trace_schema",
]
