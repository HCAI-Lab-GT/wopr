"""Response parsing for Concordia press messages."""

from __future__ import annotations

import json
from typing import Any

from .press_commitment import parse_commitment
from .types import ParsedPressMessage

_DECLINE = "decline"
_SPEAK = "speak"
_WHISPER = "whisper"


def parse_press_response(raw_response: str) -> ParsedPressMessage:
    payload = _json_payload(raw_response)
    if payload is None:
        return ParsedPressMessage()
    action_id = _optional_string(payload, "action_id")
    if action_id == _DECLINE:
        return ParsedPressMessage(declined=True)
    if action_id == _WHISPER:
        return _whisper_from(payload)
    if action_id == _SPEAK:
        return _message_from(payload)
    if action_id is None:
        return _message_from(payload)
    return ParsedPressMessage()


def _json_payload(raw_response: str) -> dict[str, Any] | None:
    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError:
        payload = _first_json_object(raw_response)
    return payload if isinstance(payload, dict) else None


def _first_json_object(raw_response: str) -> Any:
    decoder = json.JSONDecoder()
    for index, char in enumerate(raw_response):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(raw_response[index:])
        except json.JSONDecodeError:
            continue
        return payload
    return None


def _whisper_from(payload: dict[str, Any]) -> ParsedPressMessage:
    recipient = _optional_string(payload, "to")
    if recipient is None:
        return ParsedPressMessage()
    text = _optional_string(payload, "message")
    if text is None:
        return ParsedPressMessage()
    return ParsedPressMessage(
        text=text,
        rationale=_optional_string(payload, "rationale"),
        recipient=recipient,
        commitment=parse_commitment(payload.get("commitment")),
    )


def _message_from(payload: dict[str, Any]) -> ParsedPressMessage:
    text = _optional_string(payload, "message")
    if text is None:
        return ParsedPressMessage()
    return ParsedPressMessage(
        text=text,
        rationale=_optional_string(payload, "rationale"),
        commitment=parse_commitment(payload.get("commitment")),
    )


def _optional_string(payload: dict[str, Any], field: str) -> str | None:
    value = payload.get(field)
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None
