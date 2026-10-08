"""Seat construction for deterministic no-press LLM harness games."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import (
    FactionDecisionAgent,
    FirstLegalLLMClient,
    HeuristicAgent,
    HTTPClientConfig,
    LLMCompletion,
    LLMDecisionAgent,
    LLMHttpClient,
    ObservationHeuristicAgent,
    RandomAgent,
    ScriptedLLMClient,
    ScriptedSubordinateFactory,
    TraceRecorder,
)

from .agent_protocol import DecisionAgent, as_decision_agent
from .rng import SeededRNG

BASELINE_SEATS = {"random", "heuristic", "decision_heuristic"}
LLM_FIRST_LEGAL_SEAT = "llm_first_legal"
LLM_HTTP_SEAT = "llm_http"
LLM_SCRIPTED_SEAT = "llm_scripted"
LLM_SEATS = {LLM_SCRIPTED_SEAT, LLM_FIRST_LEGAL_SEAT, LLM_HTTP_SEAT}
FACTION_C2_SEAT = "faction_c2"


def build_llm_harness_agent(
    seat: Any,
    rng: SeededRNG,
    recorder: TraceRecorder,
) -> DecisionAgent:
    if seat.agent == LLM_FIRST_LEGAL_SEAT:
        return LLMDecisionAgent(
            FirstLegalLLMClient(),
            recorder=recorder,
            max_retries=seat.max_retries,
            fallback=seat.fallback,
        )
    if seat.agent == LLM_SCRIPTED_SEAT:
        return LLMDecisionAgent(
            ScriptedLLMClient(_scripted_completions(seat)),
            recorder=recorder,
            max_retries=seat.max_retries,
            fallback=seat.fallback,
        )
    if seat.agent == LLM_HTTP_SEAT:
        if seat.client is None and seat.client_override is None:
            raise ValueError("llm_http seat requires client config")
        client = seat.client_override
        if client is None:
            client_config = seat.client
            if not isinstance(client_config, HTTPClientConfig):
                raise ValueError("llm_http seat requires client config")
            client = LLMHttpClient(client_config)
        return LLMDecisionAgent(
            client,
            recorder=recorder,
            max_retries=seat.max_retries,
            fallback=seat.fallback,
        )
    if seat.agent == "random":
        return as_decision_agent(RandomAgent(rng))
    if seat.agent == "heuristic":
        return as_decision_agent(HeuristicAgent(rng))
    if seat.agent == "decision_heuristic":
        return ObservationHeuristicAgent()
    if seat.agent == FACTION_C2_SEAT:
        if not seat.archetype:
            raise ValueError("faction_c2 seat requires archetype")
        if not seat.members:
            raise ValueError("faction_c2 seat requires members")
        factory = ScriptedSubordinateFactory(_build_subordinate_clients(seat))
        return FactionDecisionAgent(
            archetype=seat.archetype,
            subordinate_factory=factory,
            archetype_parameters=seat.archetype_parameters or {},
            recorder=recorder,
        )
    raise ValueError(f"Unknown seat agent: {seat.agent}")


def _build_subordinate_clients(
    seat: Any,
) -> list[tuple[str, Any]]:
    members: list[tuple[str, Any]] = []
    for member in seat.members:
        member_id = member.get("member_id")
        if not isinstance(member_id, str):
            raise ValueError("faction_c2 member requires member_id")
        agent_kind = member.get("agent")
        if agent_kind == LLM_SCRIPTED_SEAT:
            client = ScriptedLLMClient(list(member.get("scripted_responses", ())))
        elif agent_kind == LLM_FIRST_LEGAL_SEAT:
            client = FirstLegalLLMClient()
        else:
            raise ValueError(
                f"faction_c2 member {member_id} agent must be "
                f"{LLM_SCRIPTED_SEAT} or {LLM_FIRST_LEGAL_SEAT}"
            )
        members.append((member_id, client))
    return members


def known_llm_harness_seats() -> set[str]:
    return BASELINE_SEATS | LLM_SEATS | {FACTION_C2_SEAT}


def _scripted_completions(seat: Any) -> list[str | LLMCompletion]:
    if not seat.scripted_provider_latency_ms and not seat.scripted_provider_cost:
        return list(seat.scripted_responses)
    return [
        LLMCompletion(
            raw_response=response,
            provider_latency_ms=_optional_item(
                seat.scripted_provider_latency_ms, index
            ),
            provider_cost=_optional_item(seat.scripted_provider_cost, index),
        )
        for index, response in enumerate(seat.scripted_responses)
    ]


def _optional_item(values: tuple[Any, ...], index: int) -> Any | None:
    return values[index] if index < len(values) else None


__all__ = [
    "FACTION_C2_SEAT",
    "LLM_HTTP_SEAT",
    "LLM_SCRIPTED_SEAT",
    "build_llm_harness_agent",
    "known_llm_harness_seats",
]
