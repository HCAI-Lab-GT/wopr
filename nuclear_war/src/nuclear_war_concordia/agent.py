"""Strict Concordia-style decision agent."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from nuclear_war_agents import LLMCompletion
from nuclear_war_agents import llm_completion as llm_meta
from nuclear_war_agents.llm_http_transport import provider_attempts_from_error
from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation

from .agent_helpers import (
    FirstLegalConcordiaClient,
    ScriptedConcordiaClient,
    exhaustion_message,
    is_recoverable_client_error,
    validation_error,
)
from .failure import decision_failure
from .response import parse_concordia_response
from .scene import render_concordia_scene
from .trace import append_trace
from .types import ConcordiaClient, ParsedConcordiaDecision

__all__ = [
    "ConcordiaDecisionAgent",
    "FirstLegalConcordiaClient",
    "ScriptedConcordiaClient",
]


@dataclass
class ConcordiaDecisionAgent:
    identity: dict[str, str]
    client: ConcordiaClient
    trace_sink: list[dict[str, Any]] | None = None
    max_retries: int = 1
    trace_index: int = 0
    press_memory: list[dict[str, Any]] | None = None

    def choose(
        self, observation: Observation, options: list[LegalAction]
    ) -> LegalAction:
        if self.max_retries < 0:
            raise ValueError("ConcordiaDecisionAgent max_retries must be non-negative")
        if not options:
            raise ValueError("ConcordiaDecisionAgent requires at least one option")
        legal = {option.action_id: option for option in options}
        # ``attempted_prompts`` records every rendered scene (including transient
        # attempts) for the failure snapshot. ``prompts`` records only scenes that
        # produced a completion, so it stays paired 1:1 with ``raw_responses`` for
        # the decision-trace invariant.
        attempted_prompts: list[str] = []
        prompts: list[str] = []
        raw_responses: list[str] = []
        completions: list[LLMCompletion] = []
        validation_errors: list[str] = []
        parsed = ParsedConcordiaDecision(None)
        last_transient: Exception | None = None
        recoverable_retries = 0
        for _ in range(self.max_retries + 1):
            scene = render_concordia_scene(
                observation,
                options,
                self.identity,
                validation_errors,
                self.press_memory,
            )
            attempted_prompts.append(scene.text)
            try:
                completion = llm_meta.normalize_completion(
                    self.client.complete(scene.text)
                )
            except Exception as exc:
                if getattr(exc, "channel_budget_exceeded", False):
                    raise
                if not is_recoverable_client_error(exc):
                    raise decision_failure(
                        "Concordia decision client failed",
                        identity=self.identity,
                        observation=observation,
                        options=options,
                        scene=scene,
                        prompts=attempted_prompts,
                        raw_responses=raw_responses,
                        completions=completions,
                        validation_errors=validation_errors,
                        parsed=parsed,
                        exception=exc,
                    ) from exc
                # Spec "Recoverable once": a provider timeout or HTTP error is
                # retried within the max_retries budget rather than aborting the
                # run. It is counted on its own transport-retry tally, kept out of
                # validation_errors (reserved for illegal model output) so a
                # network blip never inflates invalid-action metrics.
                last_transient = exc
                recoverable_retries += provider_attempts_from_error(exc)
                continue
            raw_response = completion.raw_response
            prompts.append(scene.text)
            raw_responses.append(raw_response)
            completions.append(completion)
            parsed = parse_concordia_response(raw_response, legal)
            if parsed.action_id in legal:
                selected = legal[parsed.action_id]
                self.trace_index = append_trace(
                    trace_sink=self.trace_sink,
                    trace_index=self.trace_index,
                    identity=self.identity,
                    observation=observation,
                    options=options,
                    scene=scene,
                    prompts=prompts,
                    raw_responses=raw_responses,
                    completions=completions,
                    validation_errors=validation_errors,
                    parsed=parsed,
                    selected=selected,
                    entity_log=getattr(self.client, "last_entity_log", None),
                    # Failed calls preserve their consumed provider attempts;
                    # usable completions preserve their internal retries.
                    recoverable_provider_retries=(
                        recoverable_retries
                        + llm_meta.total_provider_transport_retries(completions)
                    ),
                )
                return selected
            validation_errors.append(validation_error(parsed))
        raise decision_failure(
            exhaustion_message(completions, last_transient),
            identity=self.identity,
            observation=observation,
            options=options,
            scene=scene,
            prompts=attempted_prompts,
            raw_responses=raw_responses,
            completions=completions,
            validation_errors=validation_errors,
            parsed=parsed,
            exception=last_transient,
        )
