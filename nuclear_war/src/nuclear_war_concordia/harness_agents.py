"""Agent builders for Concordia no-press harness runs."""

from __future__ import annotations

from typing import Any, cast

from nuclear_war_agents import LLMHttpClient

from .agent import (
    ConcordiaDecisionAgent,
    FirstLegalConcordiaClient,
    ScriptedConcordiaClient,
)
from .call_budget import ChannelCallBudget, ChannelScopedConcordiaClient
from .config import ConcordiaNoPressConfig, ConcordiaSeatConfig
from .harness_authority import build_authority_runtime
from .harness_runtime import NATIVE_RUNTIME_PATH
from .harness_seat_runtime import ConcordiaSeatRuntime
from .native import build_native_first_legal_client, build_native_http_client
from .types import ConcordiaClient


def build_seat_runtimes(
    config: ConcordiaNoPressConfig,
    traces: list[dict[str, Any]],
    runtime_path: str,
    call_budget: ChannelCallBudget | None = None,
) -> dict[str, ConcordiaSeatRuntime]:
    return {
        player_id: _single_seat_runtime(
            seat, player_id, traces, runtime_path, call_budget
        )
        for player_id, seat in config.seats.items()
    }


def _single_seat_runtime(
    seat: ConcordiaSeatConfig,
    player_id: str,
    traces: list[dict[str, Any]],
    runtime_path: str,
    call_budget: ChannelCallBudget | None,
) -> ConcordiaSeatRuntime:
    if seat.authority is not None:
        press_factory = (
            (lambda spokesperson: _press_view(spokesperson, call_budget))
            if call_budget
            else None
        )
        return build_authority_runtime(
            seat.authority,
            client_factory=lambda: _client(
                seat, player_id, runtime_path, call_budget, "c2"
            ),
            press_client_factory=press_factory,
            max_retries=seat.max_retries,
        )
    client = _client(seat, player_id, runtime_path, call_budget, "c2")
    press_client = _press_view(client, call_budget) if call_budget else client
    agent = ConcordiaDecisionAgent(
        identity=dict(seat.identity),
        client=client,
        trace_sink=traces,
        max_retries=seat.max_retries,
    )
    return ConcordiaSeatRuntime(
        strategic_agent=agent,
        spokesperson_client=press_client,
        spokesperson_identity=dict(agent.identity),
        memory_recipients=(agent,),
    )


def _client(
    seat: ConcordiaSeatConfig,
    player_id: str,
    runtime_path: str,
    call_budget: ChannelCallBudget | None,
    channel: str,
) -> ConcordiaClient:
    base = _base_client(seat, player_id, runtime_path, call_budget)
    if call_budget is None:
        return base
    return ChannelScopedConcordiaClient(base, call_budget, channel)


def _base_client(
    seat: ConcordiaSeatConfig,
    player_id: str,
    runtime_path: str,
    call_budget: ChannelCallBudget | None,
) -> ConcordiaClient:
    request_guard = call_budget.reserve_transport_active if call_budget else None
    input_guard = call_budget.validate_prompt if call_budget else None
    if seat.agent == "concordia_first_legal":
        return FirstLegalConcordiaClient()
    if seat.agent == "concordia_scripted":
        return ScriptedConcordiaClient(list(seat.scripted_responses))
    if seat.agent == "concordia_http":
        if seat.client is None:
            raise ValueError(f"Concordia seat {player_id} requires client")
        kwargs = {}
        if request_guard is not None:
            kwargs = {"request_guard": request_guard, "input_token_guard": input_guard}
        return cast(ConcordiaClient, LLMHttpClient(seat.client, **kwargs))
    if seat.agent == "concordia_native_first_legal":
        _require_native_runtime(runtime_path)
        return build_native_first_legal_client(seat.identity)
    if seat.agent == "concordia_native_http":
        _require_native_runtime(runtime_path)
        if seat.client is None:
            raise ValueError(f"Concordia seat {player_id} requires client")
        return build_native_http_client(
            seat.identity,
            seat.client,
            request_guard=request_guard,
            input_token_guard=input_guard,
        )
    raise ValueError(f"Unknown Concordia seat agent: {seat.agent}")


def _press_view(
    client: ConcordiaClient,
    call_budget: ChannelCallBudget | None,
) -> ConcordiaClient:
    if call_budget is None:
        return client
    return ChannelScopedConcordiaClient(client, call_budget, "press")


def _require_native_runtime(runtime_path: str) -> None:
    if runtime_path != NATIVE_RUNTIME_PATH:
        raise ValueError("Native Concordia seats require concordia_runtime")


__all__ = ["build_seat_runtimes"]
