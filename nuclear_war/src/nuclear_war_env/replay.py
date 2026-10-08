"""Replay log serialization helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .actions import LegalAction
from .engine.events import EngineEvent
from .replay_validation import validate_replay_payload
from .state import GameState


def event_to_dict(event: EngineEvent, turn: int) -> dict[str, Any]:
    return {
        "turn": turn,
        "event_type": event.event_type,
        "player_id": event.player_id,
        "card_id": event.card_id,
        "payload": event.payload,
    }


def action_to_dict(action: LegalAction, turn: int) -> dict[str, Any]:
    return {
        "turn": turn,
        "player_id": action.player_id,
        "action_id": action.action_id,
        "action_type": action.action_type.value,
        "payload": action.payload,
    }


def final_populations(state: GameState) -> dict[str, int]:
    return {
        player_id: sum(player.population) for player_id, player in state.players.items()
    }


def write_replay(path: Path, payload: dict[str, Any]) -> None:
    validate_replay_payload(payload)
    validate_replay_output_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def validate_replay_output_path(path: Path) -> None:
    if path.is_dir():
        raise ValueError(f"Replay path is a directory: {path}")
    if path.parent.exists() and not path.parent.is_dir():
        raise ValueError(f"Replay parent path is not a directory: {path.parent}")


def read_replay(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ValueError(f"Replay file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Replay path is not a file: {path}")
    try:
        payload = json.loads(
            path.read_text(encoding="utf-8"),
            parse_constant=_reject_json_constant,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"Replay file is not valid JSON: {path}") from exc
    validate_replay_payload(payload)
    return payload


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"Invalid JSON constant: {value}")


def summarize_replay(payload: dict[str, Any]) -> dict[str, Any]:
    validate_replay_payload(payload)
    if "results" in payload:
        return {
            "mode": payload["mode"],
            "seed_start": payload["seed_start"],
            "runs": payload["runs"],
            "agent": payload["agent"],
            "summary": payload["summary"],
        }
    return {
        "mode": payload["mode"],
        "active_variant": payload.get("active_variant"),
        "seed": payload["seed"],
        "agent": payload["agent"],
        "winner": payload["winner"],
        "turns": payload["turns"],
        "termination_reason": payload["termination_reason"],
        "final_populations": payload["final_populations"],
        "pending_final_strikes": payload.get("pending_final_strikes", False),
    }


__all__ = [
    "event_to_dict",
    "action_to_dict",
    "final_populations",
    "write_replay",
    "validate_replay_output_path",
    "read_replay",
    "summarize_replay",
]
