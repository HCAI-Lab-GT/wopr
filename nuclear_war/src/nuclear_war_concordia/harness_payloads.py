"""Payload builders for Concordia no-press harness results."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import HTTPClientConfig
from nuclear_war_env.llm_harness_decision_metrics import player_decision_metrics
from nuclear_war_env.llm_harness_provider_metrics import provider_metrics_from_traces

from .channel_metrics import build_channel_metrics
from .condition_payloads import authority_snapshot, press_snapshot
from .config import ConcordiaNoPressConfig, ConcordiaSeatConfig
from .config_constants import NATIVE_AGENTS
from .native_entity import NATIVE_CONTEXT_COMPONENTS
from .types import ConcordiaRuntimeStatus

HTTP_CLIENT_SNAPSHOT_FIELDS = (
    "provider base_url base_url_env model model_env api_key_env provider_label "
    "timeout_seconds temperature max_tokens reasoning_effort reasoning_enabled stream"
).split()


def runtime_payload(
    runtime: ConcordiaRuntimeStatus,
    execution_path: str,
) -> dict[str, Any]:
    return {
        "runtime_path": execution_path,
        "detected_runtime_path": runtime.runtime_path,
        "detected_available": runtime.available,
        "detected_detail": runtime.detail,
        "detected_version": runtime.version,
    }


def agent_metadata(config: ConcordiaNoPressConfig) -> dict[str, dict[str, Any]]:
    press = press_snapshot(config.press)
    return {
        player_id: _seat_metadata(seat, press)
        for player_id, seat in config.seats.items()
    }


def _seat_metadata(
    seat: ConcordiaSeatConfig, press: dict[str, object]
) -> dict[str, Any]:
    # Spec artifact contract: identity (which already carries role), plus
    # model/client metadata for HTTP seats and the component list for native
    # seats. The client snapshot records only config fields, including the API
    # key *env var name* (never a resolved secret), matching config_snapshot.
    metadata: dict[str, Any] = {
        "agent": seat.agent,
        "identity": dict(seat.identity),
        "max_retries": seat.max_retries,
        "press": dict(press),
    }
    if seat.client is not None:
        metadata["client"] = _client_snapshot(seat.client)
    if seat.authority is not None:
        metadata["authority"] = authority_snapshot(seat.authority)
    if seat.agent in NATIVE_AGENTS:
        metadata["components"] = list(NATIVE_CONTEXT_COMPONENTS)
    return metadata


def config_snapshot(config: ConcordiaNoPressConfig) -> dict[str, Any]:
    return {
        "players": config.players,
        "seed": config.seed,
        "max_turns": config.max_turns,
        "runtime": config.runtime,
        "variant_id": config.variant_id,
        "press": press_snapshot(config.press),
        "seats": {pid: _seat_snapshot(seat) for pid, seat in config.seats.items()},
    }


def summary(
    replay: dict[str, Any],
    traces: list[dict[str, Any]],
    runtime_path: str,
    press_message_count: int = 0,
    *,
    c2_artifact: dict[str, Any] | None = None,
    press_traces: list[dict[str, Any]] | None = None,
    budget_metrics: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "winner": replay["winner"],
        "turns": replay["turns"],
        "termination_reason": replay["termination_reason"],
        "runtime_path": runtime_path,
        "trace_count": len(traces),
        "invalid_action_count": sum(
            len(trace["validation_errors"]) for trace in traces
        ),
        "retry_count": sum(int(trace["retries"]) for trace in traces),
        "recoverable_provider_retry_count": sum(
            int(trace.get("recoverable_provider_retries", 0)) for trace in traces
        ),
        "fallback_count": sum(1 for trace in traces if trace.get("fallback_used")),
        "press_message_count": press_message_count,
        "channel_metrics": build_channel_metrics(
            traces,
            c2_artifact,
            press_traces or [],
        ),
        "player_decision_metrics": player_decision_metrics(
            replay["final_populations"], traces
        ),
    }
    payload.update(provider_metrics_from_traces(traces))
    if budget_metrics is not None:
        payload["budget_metrics"] = budget_metrics
    return payload


def _seat_snapshot(seat: ConcordiaSeatConfig) -> dict[str, Any]:
    snapshot: dict[str, Any] = {
        "agent": seat.agent,
        "identity": dict(seat.identity),
        "max_retries": seat.max_retries,
        "scripted_responses": list(seat.scripted_responses),
    }
    if seat.client is not None:
        snapshot["client"] = _client_snapshot(seat.client)
    if seat.authority is not None:
        snapshot["authority"] = authority_snapshot(seat.authority)
    return snapshot


def _client_snapshot(client: HTTPClientConfig) -> dict[str, Any]:
    return {field: getattr(client, field) for field in HTTP_CLIENT_SNAPSHOT_FIELDS}
