"""No-press WOPR-native LLM decision agent."""

from __future__ import annotations

from dataclasses import dataclass

from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation

from .llm_agent_fallback import fallback_option, validation_error
from .llm_agent_trace import record_decision_trace
from .llm_completion import normalize_completion
from .llm_http_transport import (
    LLMConfigError,
    LLMHttpError,
    provider_attempts_from_error,
)
from .llm_prompt import (
    render_llm_prompt,
)
from .llm_response import parse_llm_response
from .llm_types import (
    LLMCompletion,
    LLMModelClient,
    ParsedLLMDecision,
    TraceRecorder,
)


@dataclass
class LLMDecisionAgent:
    client: LLMModelClient
    recorder: TraceRecorder | None = None
    max_retries: int = 1
    fallback: str = "first"
    trace_index: int = 0

    def choose(
        self,
        observation: Observation,
        options: list[LegalAction],
    ) -> LegalAction:
        if self.max_retries < 0:
            raise ValueError("LLMDecisionAgent max_retries must be non-negative")
        if not options:
            raise ValueError("LLMDecisionAgent requires at least one option")
        legal = {option.action_id: option for option in options}
        prompts: list[str] = []
        raw_responses: list[str] = []
        completions: list[LLMCompletion] = []
        validation_errors: list[str] = []
        parsed = ParsedLLMDecision(None)
        recoverable_retries = 0
        last_transport_error: Exception | None = None
        for _ in range(self.max_retries + 1):
            prompt = render_llm_prompt(observation, options, validation_errors)
            try:
                completion = normalize_completion(self.client.complete(prompt))
            except (LLMHttpError, OSError) as exc:
                if isinstance(exc, LLMConfigError):
                    raise
                # Recoverable transport fault (timeout, connection drop,
                # non-retryable HTTP error): re-issue the call within the
                # max_retries budget instead of aborting the whole batch. It is
                # tallied separately and kept out of validation_errors, which
                # are reserved for illegal model output.
                recoverable_retries += provider_attempts_from_error(exc)
                last_transport_error = exc
                continue
            raw_response = completion.raw_response
            prompts.append(prompt)
            raw_responses.append(raw_response)
            completions.append(completion)
            parsed = parse_llm_response(raw_response, legal)
            if parsed.action_id in legal:
                selected = legal[parsed.action_id]
                self.trace_index = record_decision_trace(
                    self.recorder,
                    self.trace_index,
                    observation,
                    options,
                    prompts,
                    raw_responses,
                    completions,
                    validation_errors,
                    parsed,
                    selected,
                    fallback_used=False,
                    recoverable_retries=recoverable_retries,
                )
                return selected
            validation_errors.append(validation_error(parsed))
        if not completions and last_transport_error is not None:
            # Every attempt died on provider transport: there is no model
            # output to fall back from and no completion to trace. Surface the
            # fault so the harness can write its failure artifacts.
            raise last_transport_error
        selected = fallback_option(options, self.fallback)
        self.trace_index = record_decision_trace(
            self.recorder,
            self.trace_index,
            observation,
            options,
            prompts,
            raw_responses,
            completions,
            validation_errors,
            parsed,
            selected,
            fallback_used=True,
            recoverable_retries=recoverable_retries,
        )
        return selected


__all__ = ["LLMDecisionAgent"]
