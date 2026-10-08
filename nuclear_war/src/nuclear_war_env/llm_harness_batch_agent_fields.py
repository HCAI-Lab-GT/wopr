"""Agent-specific no-press LLM batch config validation."""

from __future__ import annotations

from typing import Any

from .llm_harness_seats import (
    BASELINE_SEATS,
    FACTION_C2_SEAT,
    LLM_HTTP_SEAT,
    LLM_SCRIPTED_SEAT,
    known_llm_harness_seats,
)

_SCRIPTED_ONLY_FIELDS = {
    "scripted_responses",
    "scripted_provider_latency_ms",
    "scripted_provider_cost",
}


def validate_agent_specific_fields(payload: dict[str, Any], context: str) -> None:
    agent = payload.get("agent")
    if not isinstance(agent, str) or agent not in known_llm_harness_seats():
        return
    if agent == LLM_SCRIPTED_SEAT:
        _reject_client(payload, context)
        return
    if agent == LLM_HTTP_SEAT:
        _reject_scripted_fields(payload, context)
        if "client" not in payload:
            raise ValueError(f"{context} client requires llm_http config")
        return
    if agent == FACTION_C2_SEAT:
        _reject_scripted_fields(payload, context)
        _reject_client(payload, context)
        if "archetype" not in payload:
            raise ValueError(f"{context} archetype requires faction_c2 agent")
        if "members" not in payload:
            raise ValueError(f"{context} members requires faction_c2 agent")
        _validate_automated_archetype_parameters(payload, context)
        return
    _reject_scripted_fields(payload, context)
    _reject_client(payload, context)
    if agent in BASELINE_SEATS:
        _reject_llm_controls(payload, context)


def _validate_automated_archetype_parameters(
    payload: dict[str, Any], context: str
) -> None:
    # The "automated" archetype consumes archetype_parameters.policy_action_id as
    # a pre-armed policy (aggregate_automated). No other archetype reads a
    # required parameter, so validate this one at config time rather than crashing
    # mid-run with a KeyError.
    if payload.get("archetype") != "automated":
        return
    parameters = payload.get("archetype_parameters")
    policy_action_id = (
        parameters.get("policy_action_id") if isinstance(parameters, dict) else None
    )
    if not isinstance(policy_action_id, str) or not policy_action_id:
        raise ValueError(
            f"{context} automated archetype requires "
            "archetype_parameters.policy_action_id"
        )


def _reject_scripted_fields(payload: dict[str, Any], context: str) -> None:
    for field in _SCRIPTED_ONLY_FIELDS:
        if payload.get(field):
            raise ValueError(f"{context} {field} requires llm_scripted agent")


def _reject_client(payload: dict[str, Any], context: str) -> None:
    if payload.get("client"):
        raise ValueError(f"{context} client requires llm_http agent")


def _reject_llm_controls(payload: dict[str, Any], context: str) -> None:
    if payload.get("max_retries", 1) != 1:
        raise ValueError(f"{context} max_retries requires LLM seat")
    if payload.get("fallback", "first") != "first":
        raise ValueError(f"{context} fallback requires LLM seat")


__all__ = ["validate_agent_specific_fields"]
