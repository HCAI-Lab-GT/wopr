"""Deterministic no-press LLM research harness."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from nuclear_war_agents import HTTPClientConfig, TraceRecorder

from .agent_protocol import DecisionAgent
from .llm_harness_decision_metrics import player_decision_metrics
from .llm_harness_provider_metrics import provider_metrics_from_traces
from .llm_harness_seats import (
    LLM_SCRIPTED_SEAT,
    build_llm_harness_agent,
    known_llm_harness_seats,
)
from .llm_trace_artifacts import build_trace_artifact
from .players import player_ids
from .rng import SeededRNG
from .simulation import SimulationConfig, run_table_simulation_with_decision_agents
from .variants import ACTIVE_VARIANT_ID


@dataclass(frozen=True)
class LLMSeatConfig:
    agent: str
    scripted_responses: tuple[str, ...] = ()
    scripted_provider_latency_ms: tuple[int, ...] = ()
    scripted_provider_cost: tuple[float, ...] = ()
    max_retries: int = 1
    fallback: str = "first"
    client: HTTPClientConfig | None = None
    client_override: Any | None = None
    archetype: str | None = None
    archetype_parameters: dict[str, Any] | None = None
    members: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class NoPressLLMGameConfig:
    players: int
    seed: int
    seats: Mapping[str, LLMSeatConfig]
    max_turns: int = 50
    variant_id: str = ACTIVE_VARIANT_ID
    # Per-seat LLM/baseline agents drive each seat, so the replay's single-agent
    # label is honestly "mixed_seats" rather than any one seat's policy. The
    # authoritative per-seat mapping is recorded in seat_config.
    replay_agent: str = "mixed_seats"


def run_no_press_llm_game(config: NoPressLLMGameConfig) -> dict[str, Any]:
    agents, recorder = _build_agents(config)
    replay = run_table_simulation_with_decision_agents(
        SimulationConfig(
            mode="table",
            players=config.players,
            seed=config.seed,
            agent=config.replay_agent,
            max_turns=config.max_turns,
            press=False,
            variant_id=config.variant_id,
        ),
        agents,
    )
    traces = recorder.to_payload()
    return {
        "replay": replay,
        "trace_artifact": build_trace_artifact(replay, traces),
        "seat_config": _seat_labels(config),
        "summary": _summary(replay, traces),
    }


def _build_agents(
    config: NoPressLLMGameConfig,
) -> tuple[dict[str, DecisionAgent], TraceRecorder]:
    _validate_seats(config)
    rng = SeededRNG(config.seed)
    recorder = TraceRecorder()
    agents: dict[str, DecisionAgent] = {}
    for player_id in player_ids(config.players):
        seat = config.seats[player_id]
        agents[player_id] = build_llm_harness_agent(seat, rng, recorder)
    return agents, recorder


def _validate_seats(config: NoPressLLMGameConfig) -> None:
    expected = set(player_ids(config.players))
    actual = set(config.seats)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise ValueError(
            f"Seat config must match players: missing={missing}, extra={extra}"
        )
    for player_id, seat in config.seats.items():
        if seat.agent == LLM_SCRIPTED_SEAT and not seat.scripted_responses:
            raise ValueError(f"Seat {player_id} requires scripted_responses")
        if seat.agent not in known_llm_harness_seats():
            raise ValueError(f"Unknown seat agent: {seat.agent}")


def _seat_labels(config: NoPressLLMGameConfig) -> dict[str, str]:
    return {player_id: seat.agent for player_id, seat in config.seats.items()}


def _summary(replay: dict[str, Any], traces: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "winner": replay["winner"],
        "win_loss": _win_loss(replay),
        "elimination_order": list(replay["eliminations"]),
        "turns": replay["turns"],
        "invalid_action_count": sum(
            len(trace["validation_errors"]) for trace in traces
        ),
        "retry_count": sum(int(trace["retries"]) for trace in traces),
        "trace_count": len(traces),
        "player_decision_metrics": player_decision_metrics(
            replay["final_populations"], traces
        ),
    }
    summary.update(provider_metrics_from_traces(traces))
    return summary


def _win_loss(replay: dict[str, Any]) -> dict[str, str]:
    winner = replay["winner"]
    if winner is None:
        return {player_id: "draw" for player_id in replay["final_populations"]}
    return {
        player_id: "win" if player_id == winner else "loss"
        for player_id in replay["final_populations"]
    }


__all__ = ["LLMSeatConfig", "NoPressLLMGameConfig", "run_no_press_llm_game"]
