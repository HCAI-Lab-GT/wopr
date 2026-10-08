"""Trace construction for Concordia-backed WOPR decisions."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import LLMCompletion, LLMDecisionTrace
from nuclear_war_agents.llm_prompt import (
    render_legal_options,
    render_observation_payload,
)
from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation

from .provider_metadata import provider_metadata
from .types import ConcordiaScene, ParsedConcordiaDecision


def append_trace(
    *,
    trace_sink: list[dict[str, Any]] | None,
    trace_index: int,
    identity: dict[str, str],
    observation: Observation,
    options: list[LegalAction],
    scene: ConcordiaScene,
    prompts: list[str],
    raw_responses: list[str],
    completions: list[LLMCompletion],
    validation_errors: list[str],
    parsed: ParsedConcordiaDecision,
    selected: LegalAction,
    entity_log: dict[str, Any] | None = None,
    recoverable_provider_retries: int = 0,
) -> int:
    if trace_sink is None:
        return trace_index
    next_index = trace_index + 1
    rendered_observation = render_observation_payload(observation)
    rendered_observation["concordia"] = {
        "identity": dict(identity),
        "scene": dict(scene.payload),
    }
    if entity_log is not None:
        # Native seats: the true model-visible prompt and each context
        # component's contribution, from EntityAgentWithLogging.get_last_log.
        rendered_observation["concordia"]["entity_log"] = entity_log
    trace = LLMDecisionTrace(
        trace_id=f"{observation.player_id}:{observation.turn}:{next_index}",
        turn=observation.turn,
        player_id=observation.player_id,
        decision_type=_decision_type(observation),
        rendered_observation=rendered_observation,
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
        # Concordia has no configured fallback action: a decision either
        # resolves to a model-chosen legal action or the run fails. The flag
        # is emitted explicitly so a future fallback path stays observable.
        fallback_used=False,
        recoverable_provider_retries=recoverable_provider_retries,
        **provider_metadata(completions),
    )
    trace_sink.append(trace.to_payload())
    return next_index


def _decision_type(observation: Observation) -> str:
    if observation.decision is None:
        return "none"
    return observation.decision.decision_type.value
