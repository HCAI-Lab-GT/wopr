"""Replay payload validation helpers."""

from __future__ import annotations

from typing import Any

from .agent_names import REPLAY_AGENT_NAMES, reject_table_only_agent
from .experiment_replay_validation import (
    EXPERIMENT_FIELDS,
    validate_experiment_payload,
)
from .integer_validation import is_strict_int
from .press import reject_press_mode
from .replay_action_validation import validate_action_identity, validate_action_shapes
from .replay_event_log_validation import validate_replay_events
from .replay_field_validation import validate_field_set
from .replay_result_values import validate_replay_result_values
from .replay_turn_validation import validate_log_turn_order, validate_turn
from .result_player_ids import expected_player_ids, validate_player_reference
from .termination_reasons import validate_termination_reason
from .variants import validate_active_variant_payload

REPLAY_FIELDS = (
    "mode",
    "seed",
    "agent",
    "players",
    "winner",
    "turns",
    "termination_reason",
    "eliminations",
    "final_populations",
    "active_variant",
    "actions",
    "events",
)
EXPERIMENT_DISCRIMINATOR_FIELDS = (
    "seed_start",
    "runs",
    "max_turns",
    "results",
    "summary",
)
SINGLE_GAME_DISCRIMINATOR_FIELDS = (
    "seed",
    "winner",
    "turns",
    "termination_reason",
    "eliminations",
    "final_populations",
    "active_variant",
    "actions",
    "events",
)

REPLAY_ACTION_FIELDS = ("turn", "player_id", "action_id", "action_type", "payload")


def validate_replay_payload(payload: Any, in_progress: bool = False) -> None:
    """Validate a replay payload.

    ``in_progress`` marks a live-session artifact captured mid-game: the log
    shapes are validated identically, but empty action/event logs are allowed
    because the opening SETUP_PLACE decision now pauses the loop before any
    action is applied. Completed replays keep the non-empty requirement.
    """
    if not isinstance(payload, dict):
        raise ValueError("Replay payload must be an object")
    is_experiment = _is_experiment_payload(payload)
    fields = EXPERIMENT_FIELDS if is_experiment else REPLAY_FIELDS
    for field in fields:
        if field not in payload:
            raise ValueError(f"Replay file missing required field: {field}")
    context = "Experiment" if is_experiment else "Replay file"
    optional = () if is_experiment else ("pending_final_strikes", "press")
    validate_field_set(payload, fields, context, optional)
    if is_experiment:
        validate_experiment_payload(payload)
    else:
        _validate_replay_metadata(payload)
        turn_limit = _turn_limit(payload["turns"])
        player_ids = expected_player_ids(payload["players"])
        mode = payload["mode"]
        _validate_replay_actions(
            payload["actions"], turn_limit, player_ids, mode, in_progress
        )
        if not (in_progress and payload["events"] == []):
            validate_replay_events(
                payload["events"],
                turn_limit,
                player_ids,
                mode,
                set(payload["eliminations"]),
            )


def _is_experiment_payload(payload: dict[str, Any]) -> bool:
    if any(field in payload for field in SINGLE_GAME_DISCRIMINATOR_FIELDS):
        return False
    return any(field in payload for field in EXPERIMENT_DISCRIMINATOR_FIELDS)


def _validate_replay_metadata(payload: dict[str, Any]) -> None:
    if "press" in payload:
        reject_press_mode(payload["press"])
    if not is_strict_int(payload["seed"]):
        raise ValueError("Replay seed must be an integer")
    if not isinstance(payload["mode"], str):
        raise ValueError("Replay mode must be a string")
    if payload["mode"] not in {"table", "postal"}:
        raise ValueError(f"Replay has invalid mode: {payload['mode']}")
    if not isinstance(payload["agent"], str):
        raise ValueError("Replay agent must be a string")
    if payload["agent"] not in REPLAY_AGENT_NAMES:
        raise ValueError(f"Replay has invalid agent: {payload['agent']}")
    reject_table_only_agent(payload["agent"], payload["mode"], "Replay")
    if not is_strict_int(payload["players"]) or payload["players"] < 2:
        raise ValueError(f"Replay has invalid players: {payload['players']}")
    if payload["winner"] is not None and not isinstance(payload["winner"], str):
        raise ValueError("Replay winner must be a string or null")
    validate_termination_reason(payload["termination_reason"], "Replay")
    validate_active_variant_payload(payload["active_variant"], "Replay")
    validate_replay_result_values(payload)


def _validate_replay_actions(
    actions: Any,
    turn_limit: int,
    player_ids: set[str],
    mode: str,
    in_progress: bool = False,
) -> None:
    if not isinstance(actions, list):
        raise ValueError("Replay actions must be a list")
    if not actions:
        if in_progress:
            return
        raise ValueError("Replay actions must not be empty")
    validate_log_turn_order(actions, "action")
    for index, action in enumerate(actions):
        if not isinstance(action, dict):
            raise ValueError(f"Replay action {index} must be an object")
        for field in REPLAY_ACTION_FIELDS:
            if field not in action:
                raise ValueError(
                    f"Replay action {index} missing required field: {field}"
                )
        if set(action) != set(REPLAY_ACTION_FIELDS):
            raise ValueError(f"Replay action {index} fields are invalid")
        validate_action_shapes(action, index, mode=mode)
        validate_player_reference(
            action["player_id"],
            player_ids,
            f"Replay action {index} player_id",
        )
        validate_action_identity(action, index, player_ids)
        validate_turn(action["turn"], turn_limit, "action", index)


def _turn_limit(value: Any) -> int:
    if not is_strict_int(value) or value < 1:
        raise ValueError(f"Replay has invalid turn count: {value}")
    return value


__all__ = ["validate_replay_payload"]
