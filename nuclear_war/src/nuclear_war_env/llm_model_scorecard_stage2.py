"""Stage 2 calibration runner for serverless chat models."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from nuclear_war_agents import HTTPClientConfig, LLMHttpError

from .llm_harness import LLMSeatConfig, NoPressLLMGameConfig, run_no_press_llm_game
from .llm_model_scorecard_stage2_support import (
    Stage2Config,
    Stage2ModelResult,
    _result,
    _smoke_result,
    _trace_failure,
)


def run_stage2_model(
    config: Stage2Config,
    model_id: str,
    client_factory: Callable[[str], Any],
) -> Stage2ModelResult:
    client = client_factory(model_id)
    try:
        smoke = _smoke_result(client)
    except LLMHttpError as exc:
        return _result(model_id, False, False, (), "http_error", str(exc))
    if smoke.error_type is not None:
        return _result(
            model_id,
            False,
            False,
            (),
            smoke.error_type,
            smoke.error_message,
            smoke,
        )
    try:
        replay, traces = _run_wopr_one_turn(config, client)
    except LLMHttpError as exc:
        return _result(model_id, True, False, (), "http_error", str(exc), smoke)
    except ValueError as exc:
        return _result(
            model_id,
            True,
            False,
            (),
            "trace_validation_error",
            str(exc),
            smoke,
        )
    wopr_error = _trace_failure(traces)
    selected_action_ids = tuple(trace["selected_action_id"] for trace in traces)
    return _result(
        model_id,
        True,
        wopr_error is None,
        selected_action_ids,
        None if wopr_error is None else wopr_error[0],
        None if wopr_error is None else wopr_error[1],
        smoke,
        traces,
    )


def _run_wopr_one_turn(
    config: Stage2Config,
    client: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    result = run_no_press_llm_game(
        NoPressLLMGameConfig(
            players=config.players,
            seed=config.seed,
            max_turns=config.max_turns,
            seats={
                "player_0": LLMSeatConfig(
                    "llm_http",
                    client=HTTPClientConfig(
                        model="stage2-model",
                        base_url="http://stage2.local/v1",
                    ),
                    client_override=client,
                    max_retries=config.max_retries,
                    fallback=config.fallback,
                ),
                "player_1": LLMSeatConfig("random"),
                "player_2": LLMSeatConfig("heuristic"),
                "player_3": LLMSeatConfig("decision_heuristic"),
            },
        )
    )
    traces = result["trace_artifact"]["traces"]
    return result["replay"], traces


__all__ = ["Stage2Config", "Stage2ModelResult", "run_stage2_model"]
