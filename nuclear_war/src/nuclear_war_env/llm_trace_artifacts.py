"""Separate LLM decision trace artifacts for replay inspection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .llm_trace_artifact_schema import (
    SUPPORTED_TRACE_SCHEMA_VERSIONS,
    TRACE_SCHEMA_VERSION,
    validate_trace_schema,
)
from .llm_trace_identity import validate_trace_identity, validate_unique_trace_ids
from .llm_trace_legal_options import validate_trace_legal_options
from .llm_trace_rendered_observation import validate_trace_rendered_observation
from .replay import validate_replay_output_path
from .replay_validation import validate_replay_payload

_TRACE_ARTIFACT_FIELDS = {"schema_version", "replay", "traces"}


def trace_artifact_path(replay_path: Path) -> Path:
    return replay_path.with_name(f"{replay_path.stem}.traces.json")


def build_trace_artifact(
    replay: dict[str, Any],
    traces: list[dict[str, Any]],
) -> dict[str, Any]:
    payload = {
        "schema_version": TRACE_SCHEMA_VERSION,
        "replay": _replay_reference(replay),
        "traces": traces,
    }
    validate_trace_artifact(payload, replay)
    return payload


def write_trace_artifact(
    replay_path: Path,
    replay: dict[str, Any],
    traces: list[dict[str, Any]],
) -> Path:
    path = trace_artifact_path(replay_path)
    payload = build_trace_artifact(replay, traces)
    validate_replay_output_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def read_trace_artifact(path: Path, replay: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Trace artifact not found: {path}")
    if not path.is_file():
        raise ValueError(f"Trace artifact path is not a file: {path}")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Trace artifact is not valid JSON: {path}") from exc
    validate_trace_artifact(payload, replay)
    return payload


def validate_trace_artifact(payload: Any, replay: dict[str, Any]) -> None:
    validate_replay_payload(replay)
    if not isinstance(payload, dict):
        raise ValueError("Trace artifact must be an object")
    if set(payload) != _TRACE_ARTIFACT_FIELDS:
        raise ValueError("Trace artifact fields are invalid")
    schema_version = payload.get("schema_version")
    if schema_version not in SUPPORTED_TRACE_SCHEMA_VERSIONS:
        raise ValueError("Trace artifact schema_version is invalid")
    if payload.get("replay") != _replay_reference(replay):
        raise ValueError("Trace artifact replay reference does not match replay")
    traces = payload.get("traces")
    if not isinstance(traces, list):
        raise ValueError("Trace artifact traces must be a list")
    validate_unique_trace_ids(traces)
    actions_by_id: dict[str, list[dict[str, Any]]] = {}
    for action in replay["actions"]:
        actions_by_id.setdefault(str(action["action_id"]), []).append(action)
    for index, trace in enumerate(traces):
        _validate_trace(trace, index, actions_by_id, int(schema_version))


def _validate_trace(
    trace: Any,
    index: int,
    actions_by_id: dict[str, list[dict[str, Any]]],
    schema_version: int,
) -> None:
    if not isinstance(trace, dict):
        raise ValueError(f"Trace {index} must be an object")
    validate_trace_schema(trace, index, schema_version)
    validate_trace_identity(trace, index)
    if schema_version >= 3:
        validate_trace_rendered_observation(trace, index)
    validate_trace_legal_options(trace, index)
    selected_action_id = trace["selected_action_id"]
    selected_actions = actions_by_id.get(selected_action_id)
    if selected_actions is None:
        raise ValueError(
            f"Trace {index} selected_action_id does not link to replay action"
        )
    _validate_trace_action_context(trace, selected_actions, index)


def _validate_trace_action_context(
    trace: dict[str, Any],
    actions: list[dict[str, Any]],
    index: int,
) -> None:
    player_actions = [
        action for action in actions if trace["player_id"] == action["player_id"]
    ]
    if not player_actions:
        raise ValueError(f"Trace {index} player_id does not match replay action")
    if not any(trace["turn"] == action["turn"] for action in player_actions):
        raise ValueError(f"Trace {index} turn does not match replay action")


def _replay_reference(replay: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": replay["mode"],
        "seed": replay["seed"],
        "agent": replay["agent"],
        "players": replay["players"],
        "turns": replay["turns"],
    }


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


__all__ = [
    "TRACE_SCHEMA_VERSION",
    "SUPPORTED_TRACE_SCHEMA_VERSIONS",
    "build_trace_artifact",
    "read_trace_artifact",
    "trace_artifact_path",
    "validate_trace_artifact",
    "write_trace_artifact",
]
