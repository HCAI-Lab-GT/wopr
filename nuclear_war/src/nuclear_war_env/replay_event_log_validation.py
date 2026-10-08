"""Replay event log validation helpers."""

from __future__ import annotations

from typing import Any

from .replay_event_player_references import validate_event_player_references
from .replay_event_validation import validate_event_shapes
from .replay_turn_validation import validate_log_turn_order, validate_turn
from .result_player_ids import validate_player_reference

REPLAY_EVENT_FIELDS = ("turn", "event_type", "player_id", "card_id", "payload")


def validate_replay_events(
    events: Any,
    turn_limit: int,
    player_ids: set[str],
    mode: str,
    eliminations: set[str],
) -> None:
    if not isinstance(events, list):
        raise ValueError("Replay events must be a list")
    if not events:
        raise ValueError("Replay events must not be empty")
    validate_log_turn_order(events, "event")
    event_eliminations: set[str] = set()
    for index, event in enumerate(events):
        _validate_replay_event(
            event,
            index,
            turn_limit,
            player_ids,
            mode,
            eliminations,
            event_eliminations,
        )
    _validate_eliminations_have_events(eliminations, event_eliminations)


def _validate_replay_event(
    event: Any,
    index: int,
    turn_limit: int,
    player_ids: set[str],
    mode: str,
    eliminations: set[str],
    event_eliminations: set[str],
) -> None:
    if not isinstance(event, dict):
        raise ValueError(f"Replay event {index} must be an object")
    for field in REPLAY_EVENT_FIELDS:
        if field not in event:
            raise ValueError(f"Replay event {index} missing required field: {field}")
    if set(event) != set(REPLAY_EVENT_FIELDS):
        raise ValueError(f"Replay event {index} fields are invalid")
    validate_event_shapes(event, index, mode=mode)
    validate_player_reference(
        event["player_id"],
        player_ids,
        f"Replay event {index} player_id",
        allow_null=True,
    )
    validate_event_player_references(event, index, player_ids)
    _validate_eliminated_event_summary(event, index, eliminations, event_eliminations)
    validate_turn(event["turn"], turn_limit, "event", index)


def _validate_eliminated_event_summary(
    event: dict[str, Any],
    index: int,
    eliminations: set[str],
    event_eliminations: set[str],
) -> None:
    if event["event_type"] != "player_eliminated":
        return
    player_id = event["player_id"]
    if player_id not in eliminations:
        raise ValueError(
            f"Replay event {index} player_eliminated player_id "
            "must be listed in eliminations"
        )
    if player_id in event_eliminations:
        raise ValueError(
            f"Replay event {index} player_eliminated player_id "
            "must not duplicate an earlier elimination event"
        )
    event_eliminations.add(player_id)


def _validate_eliminations_have_events(
    eliminations: set[str], event_eliminations: set[str]
) -> None:
    missing = sorted(eliminations - event_eliminations)
    if missing:
        raise ValueError(
            f"Replay elimination {missing[0]} must have a player_eliminated event"
        )


__all__ = ["REPLAY_EVENT_FIELDS", "validate_replay_events"]
