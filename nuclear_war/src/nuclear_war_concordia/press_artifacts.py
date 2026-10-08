"""Press trace sidecar artifacts for Concordia press-light runs."""

from __future__ import annotations

from typing import Any

from nuclear_war_env.replay_validation import validate_replay_payload

PRESS_SCHEMA_VERSION = 1
SUPPORTED_PRESS_SCHEMA_VERSIONS = {1}
PRESS_MODES = {"press_light", "multi_turn_public", "full_press"}
_PUBLIC_ONLY_MODES = {"press_light", "multi_turn_public"}
_PRESS_FIELDS = {"schema_version", "press_mode", "replay", "messages"}

_REQUIRED_MESSAGE_FIELDS = {
    "message_id",
    "turn",
    "round",
    "speaker",
    "audience",
    "visibility",
    "pass",
    "decision_type",
    "text",
    "prompts",
    "raw_responses",
    "prior_messages",
    "retries",
    "parse_result",
    "validation_errors",
    "linked_decision_traces",
}
_LIST_MESSAGE_FIELDS = ("prompts", "raw_responses", "prior_messages")


def build_press_artifact(
    replay: dict[str, Any],
    messages: list[dict[str, Any]],
    press_mode: str,
) -> dict[str, Any]:
    payload = {
        "schema_version": PRESS_SCHEMA_VERSION,
        "press_mode": press_mode,
        "replay": _replay_reference(replay),
        "messages": messages,
    }
    validate_press_artifact(payload, replay)
    return payload


def validate_press_artifact(payload: Any, replay: dict[str, Any]) -> None:
    validate_replay_payload(replay)
    if not isinstance(payload, dict):
        raise ValueError("Press artifact must be an object")
    if set(payload) != _PRESS_FIELDS:
        raise ValueError("Press artifact fields are invalid")
    if payload["schema_version"] not in SUPPORTED_PRESS_SCHEMA_VERSIONS:
        raise ValueError("Press artifact schema_version is invalid")
    if payload["press_mode"] not in PRESS_MODES:
        raise ValueError("Press artifact press_mode is invalid")
    if payload["replay"] != _replay_reference(replay):
        raise ValueError("Press artifact replay reference does not match replay")
    messages = payload["messages"]
    if not isinstance(messages, list):
        raise ValueError("Press artifact messages must be a list")
    press_mode = payload["press_mode"]
    seen_ids: set[str] = set()
    for index, message in enumerate(messages):
        _validate_message(message, index, seen_ids, press_mode)


def _validate_message(
    message: Any,
    index: int,
    seen_ids: set[str],
    press_mode: str,
) -> None:
    if not isinstance(message, dict):
        raise ValueError(f"Press message {index} must be an object")
    missing = _REQUIRED_MESSAGE_FIELDS - set(message)
    if missing:
        raise ValueError(f"Press message {index} missing fields: {sorted(missing)}")
    message_id = message["message_id"]
    if not isinstance(message_id, str) or message_id in seen_ids:
        raise ValueError(f"Press message {index} has invalid or duplicate message_id")
    seen_ids.add(message_id)
    if "selected_action_id" in message:
        raise ValueError(f"Press message {index} must not carry selected_action_id")
    if message["decision_type"] != "press":
        raise ValueError(f"Press message {index} decision_type must be press")
    _validate_trace_fields(message, index)
    _validate_visibility(message, index, press_mode)


def _validate_trace_fields(message: dict[str, Any], index: int) -> None:
    pass_no = message["pass"]
    if isinstance(pass_no, bool) or not isinstance(pass_no, int) or pass_no < 1:
        raise ValueError(f"Press message {index} pass must be a positive integer")
    retries = message["retries"]
    if isinstance(retries, bool) or not isinstance(retries, int) or retries < 0:
        raise ValueError(
            f"Press message {index} retries must be a non-negative integer"
        )
    for field in _LIST_MESSAGE_FIELDS:
        if not isinstance(message[field], list):
            raise ValueError(f"Press message {index} {field} must be a list")


def _validate_visibility(message: dict[str, Any], index: int, press_mode: str) -> None:
    visibility = message["visibility"]
    recipient = message.get("recipient")
    if press_mode in _PUBLIC_ONLY_MODES and visibility == "private":
        raise ValueError(
            f"Press message {index} private visibility is not allowed in {press_mode}"
        )
    if visibility == "private":
        if not isinstance(recipient, str) or not recipient:
            raise ValueError(
                f"Press message {index} private visibility requires recipient"
            )
    elif recipient is not None:
        raise ValueError(
            f"Press message {index} public visibility must not carry recipient"
        )
    commitment = message.get("commitment")
    if commitment is not None:
        _validate_commitment(commitment, index)


def _validate_commitment(commitment: Any, index: int) -> None:
    if not isinstance(commitment, dict):
        raise ValueError(f"Press message {index} commitment must be an object")
    allowed = {"kind", "target_round", "notes"}
    if set(commitment) - allowed:
        raise ValueError(f"Press message {index} commitment has invalid fields")
    kind = commitment.get("kind")
    if not isinstance(kind, str) or not kind:
        raise ValueError(f"Press message {index} commitment kind is required")
    target_round = commitment.get("target_round")
    if target_round is not None and (
        isinstance(target_round, bool)
        or not isinstance(target_round, int)
        or target_round < 1
    ):
        raise ValueError(
            f"Press message {index} commitment target_round must be a positive int"
        )


def _replay_reference(replay: dict[str, Any]) -> dict[str, Any]:
    return {
        "mode": replay["mode"],
        "seed": replay["seed"],
        "agent": replay["agent"],
        "players": replay["players"],
        "turns": replay["turns"],
    }
