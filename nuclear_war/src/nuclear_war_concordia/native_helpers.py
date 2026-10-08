"""Small parsing and logging helpers for native Concordia clients."""

from __future__ import annotations

import json
from typing import Any


def entity_log(entity: Any) -> dict[str, Any] | None:
    getter = getattr(entity, "get_last_log", None)
    if not callable(getter):
        return None
    log = getter()
    if not isinstance(log, dict):
        return None
    return json.loads(json.dumps(log, default=str))


def scene_payload(scene_text: str) -> dict[str, Any]:
    _, remainder = scene_text.split("Scene JSON:", 1)
    payload, _ = json.JSONDecoder().raw_decode(remainder.lstrip())
    if not isinstance(payload, dict):
        raise ValueError("Concordia scene JSON must be an object")
    return payload


def action_ids(payload: dict[str, Any]) -> tuple[str, ...]:
    legal_options = payload.get("legal_options")
    if not isinstance(legal_options, list) or not legal_options:
        raise ValueError("Concordia scene requires legal options")
    values: list[str] = []
    for option in legal_options:
        if not isinstance(option, dict) or not isinstance(option.get("action_id"), str):
            raise ValueError("Concordia legal options require action_id values")
        values.append(option["action_id"])
    return tuple(values)
