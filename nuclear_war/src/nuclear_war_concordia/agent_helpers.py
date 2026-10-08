"""Client stubs and retry helpers for the strict Concordia agent."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from nuclear_war_agents import LLMCompletion, LLMConfigError, LLMHttpError

from .types import ParsedConcordiaDecision

_NO_ACTION_ERROR = "No action_id parsed"


@dataclass
class ScriptedConcordiaClient:
    responses: list[str]
    index: int = 0

    def complete(self, scene_text: str) -> str:
        del scene_text
        if self.index >= len(self.responses):
            raise ValueError("ScriptedConcordiaClient exhausted")
        response = self.responses[self.index]
        self.index += 1
        return response


class FirstLegalConcordiaClient:
    def complete(self, scene_text: str) -> str:
        payload = scene_payload(scene_text)
        action_id = payload["legal_options"][0]["action_id"]
        return json.dumps({"action_id": action_id, "rationale": "first legal action"})


def is_recoverable_client_error(exc: Exception) -> bool:
    if isinstance(exc, LLMConfigError):
        return False
    return isinstance(exc, LLMHttpError | OSError)


def exhaustion_message(
    completions: list[LLMCompletion], last_transient: Exception | None
) -> str:
    if not completions and last_transient is not None:
        return "Concordia decision client failed after exhausting recoverable retries"
    return "No legal Concordia action selected"


def validation_error(parsed: ParsedConcordiaDecision) -> str:
    if parsed.action_id is None:
        return _NO_ACTION_ERROR
    return f"Illegal action_id parsed: {parsed.action_id}"


def scene_payload(scene_text: str) -> dict[str, Any]:
    _, remainder = scene_text.split("Scene JSON:", 1)
    payload, _ = json.JSONDecoder().raw_decode(remainder.lstrip())
    if not isinstance(payload, dict):
        raise ValueError("Concordia scene JSON must be an object")
    return payload
