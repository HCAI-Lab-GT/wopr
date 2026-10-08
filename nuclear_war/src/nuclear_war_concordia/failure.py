"""Strict failure payloads for Concordia-backed WOPR runs."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

from nuclear_war_agents import LLMCompletion
from nuclear_war_agents.llm_prompt import render_legal_options
from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation

from .config import ConcordiaNoPressConfig
from .provider_metadata import provider_metadata
from .types import ConcordiaScene, ParsedConcordiaDecision, ParsedPressMessage


@dataclass
class ConcordiaDecisionFailure(ValueError):
    message: str
    snapshot: dict[str, Any]

    def __post_init__(self) -> None:
        ValueError.__init__(self, self.message)


@dataclass
class ConcordiaRunFailure(ValueError):
    message: str
    snapshot: dict[str, Any]

    def __post_init__(self) -> None:
        ValueError.__init__(self, self.message)


def decision_failure(
    message: str,
    *,
    identity: dict[str, str],
    observation: Observation,
    options: list[LegalAction],
    scene: ConcordiaScene,
    prompts: list[str],
    raw_responses: list[str],
    completions: list[LLMCompletion],
    validation_errors: list[str],
    parsed: ParsedConcordiaDecision,
    exception: Exception | None = None,
) -> ConcordiaDecisionFailure:
    extra_completion = _exception_completion(exception)
    all_completions = completions + ([extra_completion] if extra_completion else [])
    responses = raw_responses + (
        [extra_completion.raw_response] if extra_completion else []
    )
    return ConcordiaDecisionFailure(
        message,
        {
            "agent_identity": dict(identity),
            "player_id": observation.player_id,
            "turn": observation.turn,
            "decision_type": _decision_type(observation),
            "scene_payload": dict(scene.payload),
            "legal_options": render_legal_options(options),
            "prompts": list(prompts),
            "raw_visible_responses": responses,
            "parse_result": {
                "action_id": parsed.action_id,
                "rationale": parsed.rationale,
            },
            "validation_errors": list(validation_errors),
            "provider_metadata": provider_metadata(all_completions),
            "exception": _exception_payload(exception),
        },
    )


def press_failure(
    message: str,
    *,
    speaker: str,
    round_no: int,
    audience: str,
    pass_no: int,
    prior_messages: list[dict[str, Any]],
    scene: ConcordiaScene,
    prompts: list[str],
    raw_responses: list[str],
    completions: list[LLMCompletion],
    validation_errors: list[str],
    parsed: ParsedPressMessage,
    exception: Exception | None = None,
) -> ConcordiaDecisionFailure:
    extra_completion = _exception_completion(exception)
    all_completions = completions + ([extra_completion] if extra_completion else [])
    responses = raw_responses + (
        [extra_completion.raw_response] if extra_completion else []
    )
    turn = scene.payload.get("turn", round_no)
    return ConcordiaDecisionFailure(
        message,
        {
            "speaker": speaker,
            "turn": turn,
            "round": round_no,
            "audience": audience,
            "pass": pass_no,
            "decision_type": "press",
            "scene_payload": dict(scene.payload),
            "prior_messages": list(prior_messages),
            "prompts": list(prompts),
            "raw_visible_responses": responses,
            "parse_result": {
                "message": parsed.text,
                "rationale": parsed.rationale,
                "declined": parsed.is_decline,
            },
            "validation_errors": list(validation_errors),
            "provider_metadata": provider_metadata(all_completions),
            "exception": _exception_payload(exception),
        },
    )


def run_failure_snapshot(
    *,
    config_snapshot: dict[str, Any],
    runtime: dict[str, Any],
    agent_metadata: dict[str, Any],
    failure: ConcordiaDecisionFailure,
    config: ConcordiaNoPressConfig,
) -> dict[str, Any]:
    payload = {
        "config_snapshot": config_snapshot,
        "runtime_status": runtime,
        "agent_metadata": agent_metadata,
        "decision_failure": failure.snapshot,
    }
    return _redact(payload, _secret_values(config))


def _exception_payload(exception: Exception | None) -> dict[str, str] | None:
    if exception is None:
        return None
    return {
        "type": type(exception).__name__,
        "module": type(exception).__module__,
        "message": str(exception),
    }


def _exception_completion(exception: Exception | None) -> LLMCompletion | None:
    completion = getattr(exception, "completion", None)
    return completion if isinstance(completion, LLMCompletion) else None


def _secret_values(config: ConcordiaNoPressConfig) -> set[str]:
    names = {
        seat.client.api_key_env
        for seat in config.seats.values()
        if seat.client is not None and seat.client.api_key_env
    }
    return {value for name in names if (value := os.environ.get(name))}


def _redact(value: Any, secrets: set[str]) -> Any:
    if isinstance(value, dict):
        return {key: _redact(item, secrets) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, secrets) for item in value]
    if isinstance(value, str):
        redacted = value
        for secret in secrets:
            redacted = redacted.replace(secret, "[redacted]")
        return redacted
    return value


def _decision_type(observation: Observation) -> str:
    if observation.decision is None:
        return "none"
    return observation.decision.decision_type.value
