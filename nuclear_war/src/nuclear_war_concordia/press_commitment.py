"""Commitment parsing for full-press messages."""

from __future__ import annotations

from typing import Any

_ALLOWED_FIELDS = {"kind", "target_round", "notes"}


def parse_commitment(payload: Any) -> dict[str, Any] | None:
    if payload is None:
        return None
    if not isinstance(payload, dict):
        return None
    if set(payload) - _ALLOWED_FIELDS:
        return None
    kind = _string(payload.get("kind"))
    if kind is None:
        return None
    commitment: dict[str, Any] = {"kind": kind}
    target_round = payload.get("target_round")
    if target_round is not None:
        if isinstance(target_round, bool) or not isinstance(target_round, int):
            return None
        if target_round < 1:
            return None
        commitment["target_round"] = target_round
    notes = _string(payload.get("notes"))
    if notes is not None:
        commitment["notes"] = notes
    return commitment


def _string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None
