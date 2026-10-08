"""Trace recording for the WOPR-native decision agent."""

from __future__ import annotations

from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation

from .llm_agent_fallback import decision_type
from .llm_completion import (
    first_provider_label,
    first_provider_model,
    total_provider_cost,
    total_provider_latency,
    total_provider_transport_retries,
    total_provider_usage,
)
from .llm_prompt import render_legal_options, render_observation_payload
from .llm_types import (
    LLMCompletion,
    LLMDecisionTrace,
    ParsedLLMDecision,
    TraceRecorder,
)


def record_decision_trace(
    recorder: TraceRecorder | None,
    trace_index: int,
    observation: Observation,
    options: list[LegalAction],
    prompts: list[str],
    raw_responses: list[str],
    completions: list[LLMCompletion],
    validation_errors: list[str],
    parsed: ParsedLLMDecision,
    selected: LegalAction,
    *,
    fallback_used: bool,
    recoverable_retries: int,
) -> int:
    if recorder is None:
        return trace_index
    trace_index += 1
    recorder.record(
        LLMDecisionTrace(
            trace_id=f"{observation.player_id}:{observation.turn}:{trace_index}",
            turn=observation.turn,
            player_id=observation.player_id,
            decision_type=decision_type(observation),
            rendered_observation=render_observation_payload(observation),
            prompt=prompts[-1],
            prompts=list(prompts),
            legal_options=render_legal_options(options),
            raw_response=raw_responses[-1],
            raw_responses=list(raw_responses),
            parse_result={"action_id": parsed.action_id, "rationale": parsed.rationale},
            selected_action_id=selected.action_id,
            retries=max(0, len(raw_responses) - 1),
            validation_errors=list(validation_errors),
            stated_rationale=parsed.rationale,
            provider_latency_ms=total_provider_latency(completions),
            provider_cost=total_provider_cost(completions),
            provider_usage=total_provider_usage(completions),
            provider_label=first_provider_label(completions),
            provider_model=first_provider_model(completions),
            fallback_used=fallback_used,
            recoverable_provider_retries=(
                recoverable_retries + total_provider_transport_retries(completions)
            ),
        )
    )
    return trace_index


__all__ = ["record_decision_trace"]
