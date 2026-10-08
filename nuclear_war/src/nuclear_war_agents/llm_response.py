"""Response parsing for WOPR-native LLM decision agents."""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from typing import Any

from .llm_types import ParsedLLMDecision

_ACTION_LINE = re.compile(r"^\s*action_id\s*:\s*(?P<value>\S+)\s*$", re.I | re.M)
_RATIONALE_LINE = re.compile(r"^\s*rationale\s*:\s*(?P<value>.+?)\s*$", re.I | re.M)
_QUOTED_ACTION = re.compile(
    r'"action_id"\s*:\s*"(?P<value>(?:\\.|[^"\\])*)"', re.I | re.S
)
_QUOTED_RATIONALE = re.compile(
    r'"rationale"\s*:\s*"(?P<value>(?:\\.|[^"\\])*)"', re.I | re.S
)


def parse_llm_response(
    raw_response: str,
    legal_action_ids: Iterable[str] = (),
) -> ParsedLLMDecision:
    legal = tuple(legal_action_ids)
    parsed_json = _parse_json_response(raw_response)
    if _is_usable(parsed_json, legal):
        return parsed_json
    legal_match = _parse_legal_action(raw_response, legal, parsed_json.rationale)
    if legal_match.action_id is not None:
        return legal_match
    if parsed_json.action_id is not None:
        return parsed_json
    quoted = _parse_quoted_fields(raw_response)
    if _is_usable(quoted, legal):
        return quoted
    legal_match = _parse_legal_action(raw_response, legal, quoted.rationale)
    if legal_match.action_id is not None:
        return legal_match
    if quoted.action_id is not None:
        return quoted
    action = _ACTION_LINE.search(raw_response)
    if action is None:
        return ParsedLLMDecision(None)
    rationale = _RATIONALE_LINE.search(raw_response)
    return ParsedLLMDecision(
        action.group("value"),
        rationale.group("value") if rationale is not None else None,
    )


def _parse_json_response(raw_response: str) -> ParsedLLMDecision:
    try:
        payload = json.loads(raw_response)
    except json.JSONDecodeError:
        return ParsedLLMDecision(None)
    if not isinstance(payload, dict):
        return ParsedLLMDecision(None)
    action_id = _optional_string(payload, "action_id")
    return ParsedLLMDecision(
        action_id,
        _optional_string(payload, "rationale"),
    )


def _optional_string(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    return value if isinstance(value, str) and value else None


def _is_usable(parsed: ParsedLLMDecision, legal: tuple[str, ...]) -> bool:
    if parsed.action_id is None:
        return False
    return not legal or parsed.action_id in legal


def _parse_legal_action(
    raw_response: str,
    legal: tuple[str, ...],
    rationale: str | None,
) -> ParsedLLMDecision:
    matches = [action_id for action_id in legal if action_id in raw_response]
    if not matches:
        return ParsedLLMDecision(None)
    max_length = max(len(action_id) for action_id in matches)
    longest = [action_id for action_id in matches if len(action_id) == max_length]
    if len(longest) != 1:
        return ParsedLLMDecision(None)
    return ParsedLLMDecision(longest[0], rationale)


def _parse_quoted_fields(raw_response: str) -> ParsedLLMDecision:
    action = _quoted_value(raw_response, _QUOTED_ACTION)
    if action is None:
        return ParsedLLMDecision(None)
    return ParsedLLMDecision(action, _quoted_value(raw_response, _QUOTED_RATIONALE))


def _quoted_value(raw_response: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(raw_response)
    if match is None:
        return None
    try:
        value = json.loads(f'"{match.group("value")}"')
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, str) and value else None


__all__ = ["parse_llm_response"]
