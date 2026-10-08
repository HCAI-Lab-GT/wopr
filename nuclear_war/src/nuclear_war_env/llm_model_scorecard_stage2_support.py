"""Shared Stage 2 scorecard helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nuclear_war_agents import LLMCompletion, parse_llm_response


@dataclass(frozen=True)
class Stage2Config:
    players: int = 4
    seed: int = 101
    max_turns: int = 1
    max_retries: int = 0
    fallback: str = "first"


@dataclass(frozen=True)
class Stage2ModelResult:
    model_id: str
    status: str
    direct_smoke_passed: bool
    wopr_one_turn_passed: bool
    trace_count: int
    invalid_action_count: int
    retry_count: int
    selected_action_ids: tuple[str, ...]
    provider_usage: dict[str, int | float] | None
    provider_latency_ms: int | None
    error_type: str | None
    error_message: str | None


@dataclass(frozen=True)
class Stage2SmokeResult:
    error_type: str | None
    error_message: str | None
    provider_usage: dict[str, int | float] | None
    provider_latency_ms: int | None


_SMOKE_PROMPT = 'Respond only with this JSON: {"action_id": "smoke:test"}.'


def _smoke_result(client: Any) -> Stage2SmokeResult:
    completion = _completion(client.complete(_SMOKE_PROMPT))
    if not completion.raw_response:
        return Stage2SmokeResult(
            "empty_final_content",
            "Direct smoke returned empty content",
            completion.provider_usage,
            completion.provider_latency_ms,
        )
    if parse_llm_response(completion.raw_response).action_id != "smoke:test":
        return Stage2SmokeResult(
            "parse_failure",
            "Direct smoke did not return the smoke action",
            completion.provider_usage,
            completion.provider_latency_ms,
        )
    return Stage2SmokeResult(
        None,
        None,
        completion.provider_usage,
        completion.provider_latency_ms,
    )


def _trace_failure(traces: list[dict[str, Any]]) -> tuple[str, str] | None:
    for trace in traces:
        if not trace["raw_response"]:
            return ("empty_final_content", "WOPR trace returned empty content")
        if trace["parse_result"]["action_id"] != trace["selected_action_id"]:
            return ("parse_failure", "WOPR trace did not parse a legal action")
    return None


def _result(
    model_id: str,
    direct_smoke_passed: bool,
    wopr_one_turn_passed: bool,
    selected_action_ids: tuple[str, ...],
    error_type: str | None,
    error_message: str | None,
    smoke: Stage2SmokeResult | None = None,
    traces: list[dict[str, Any]] | None = None,
) -> Stage2ModelResult:
    smoke_usage = None if smoke is None else smoke.provider_usage
    smoke_latency = None if smoke is None else smoke.provider_latency_ms
    trace_count = 0 if traces is None else len(traces)
    invalid_action_count = (
        0
        if traces is None
        else sum(len(trace["validation_errors"]) for trace in traces)
    )
    retry_count = (
        0 if traces is None else sum(int(trace["retries"]) for trace in traces)
    )
    return Stage2ModelResult(
        model_id=model_id,
        status="passed"
        if direct_smoke_passed and wopr_one_turn_passed and error_type is None
        else "failed",
        direct_smoke_passed=direct_smoke_passed,
        wopr_one_turn_passed=wopr_one_turn_passed,
        trace_count=trace_count,
        invalid_action_count=invalid_action_count,
        retry_count=retry_count,
        selected_action_ids=selected_action_ids,
        provider_usage=_sum_usage(smoke_usage, traces or []),
        provider_latency_ms=_sum_int(smoke_latency, traces or []),
        error_type=error_type,
        error_message=error_message,
    )


def _completion(value: str | LLMCompletion) -> LLMCompletion:
    return value if isinstance(value, LLMCompletion) else LLMCompletion(value)


def _sum_usage(
    smoke_usage: dict[str, int | float] | None,
    traces: list[dict[str, Any]],
) -> dict[str, int | float] | None:
    totals: dict[str, int | float] = dict(smoke_usage or {})
    for trace in traces:
        for key, value in (trace.get("provider_usage") or {}).items():
            totals[key] = totals.get(key, 0) + value
    return totals or None


def _sum_int(smoke_value: int | None, traces: list[dict[str, Any]]) -> int | None:
    values = [smoke_value] if smoke_value is not None else []
    values.extend(
        int(trace["provider_latency_ms"])
        for trace in traces
        if trace.get("provider_latency_ms") is not None
    )
    return sum(values) if values else None


__all__ = [
    "Stage2Config",
    "Stage2ModelResult",
    "_completion",
    "_result",
    "_smoke_result",
    "_sum_int",
    "_sum_usage",
    "_trace_failure",
]
