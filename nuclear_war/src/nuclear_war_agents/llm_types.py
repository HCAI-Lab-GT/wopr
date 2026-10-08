"""Shared types for WOPR-native LLM decision agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class LLMCompletion:
    raw_response: str
    provider_latency_ms: int | None = None
    provider_cost: float | None = None
    provider_usage: dict[str, int | float] | None = None
    provider_label: str | None = None
    provider_model: str | None = None
    # Number of transport-level retries (e.g. HTTP 429/5xx) the client consumed
    # internally before returning this usable completion. Surfaced so those
    # recoverable retries stay observable in the decision trace.
    provider_transport_retries: int = 0


@dataclass(frozen=True)
class ParsedLLMDecision:
    action_id: str | None
    rationale: str | None = None


@dataclass(frozen=True)
class LLMDecisionTrace:
    trace_id: str
    turn: int
    player_id: str
    decision_type: str
    rendered_observation: dict[str, Any]
    prompt: str
    prompts: list[str]
    legal_options: list[dict[str, Any]]
    raw_response: str
    raw_responses: list[str]
    parse_result: dict[str, str | None]
    selected_action_id: str
    retries: int
    validation_errors: list[str]
    stated_rationale: str | None = None
    provider_latency_ms: int | None = None
    provider_cost: float | None = None
    provider_usage: dict[str, int | float] | None = None
    provider_label: str | None = None
    provider_model: str | None = None
    # True when the agent gave up on the model and selected a configured
    # fallback action instead of a model-chosen one (schema v5+). Defaults to
    # False so callers that never fall back stay honest without extra wiring.
    fallback_used: bool = False
    # Count of recoverable provider transport retries (timeout/HTTP error) before
    # a usable completion. Distinct from ``retries`` (model round-trips) and kept
    # out of ``validation_errors`` so transport blips do not inflate invalid-
    # action metrics. Defaults to 0 for agents that do not retry transport.
    recoverable_provider_retries: int = 0

    def to_payload(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "turn": self.turn,
            "player_id": self.player_id,
            "decision_type": self.decision_type,
            "rendered_observation": dict(self.rendered_observation),
            "prompt": self.prompt,
            "prompts": list(self.prompts),
            "legal_options": list(self.legal_options),
            "raw_response": self.raw_response,
            "raw_responses": list(self.raw_responses),
            "parse_result": dict(self.parse_result),
            "selected_action_id": self.selected_action_id,
            "retries": self.retries,
            "validation_errors": list(self.validation_errors),
            "stated_rationale": self.stated_rationale,
            "provider_latency_ms": self.provider_latency_ms,
            "provider_cost": self.provider_cost,
            "provider_usage": self.provider_usage,
            "provider_label": self.provider_label,
            "provider_model": self.provider_model,
            "fallback_used": self.fallback_used,
            "recoverable_provider_retries": self.recoverable_provider_retries,
        }


class LLMModelClient(Protocol):
    def complete(self, prompt: str) -> str | LLMCompletion: ...


@dataclass
class TraceRecorder:
    traces: list[LLMDecisionTrace] = field(default_factory=list)

    def record(self, trace: LLMDecisionTrace) -> None:
        self.traces.append(trace)

    def to_payload(self) -> list[dict[str, Any]]:
        return [trace.to_payload() for trace in self.traces]


__all__ = [
    "LLMCompletion",
    "LLMDecisionTrace",
    "LLMModelClient",
    "ParsedLLMDecision",
    "TraceRecorder",
]
