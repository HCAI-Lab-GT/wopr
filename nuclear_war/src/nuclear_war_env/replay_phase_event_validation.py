"""Replay phase-complete event validation helpers."""

from __future__ import annotations

from typing import Any

from .engine.postal.handlers import PHASE_HANDLERS

POSTAL_PHASE_NAMES = {phase_name for phase_name, _handler in PHASE_HANDLERS}


def validate_phase_complete_event(event: dict[str, Any], index: int) -> None:
    if event["player_id"] is not None:
        raise ValueError(f"Replay event {index} phase_complete player_id must be null")
    if event["card_id"] is not None:
        raise ValueError(f"Replay event {index} phase_complete card_id must be null")
    payload = event["payload"]
    if set(payload) != {"phase"}:
        raise ValueError(
            f"Replay event {index} phase_complete payload fields are invalid"
        )
    phase = payload.get("phase")
    if not isinstance(phase, str):
        raise ValueError(f"Replay event {index} phase_complete phase must be a string")
    if phase not in POSTAL_PHASE_NAMES:
        raise ValueError(
            f"Replay event {index} phase_complete phase has invalid value: {phase}"
        )


__all__ = ["validate_phase_complete_event"]
