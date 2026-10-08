"""Scene rendering for Concordia press messages."""

from __future__ import annotations

import json
from typing import Any

from nuclear_war_agents.llm_prompt import render_observation_payload
from nuclear_war_env.observation import Observation

from .types import ConcordiaScene

_PRESS_OPTIONS = [
    {"action_id": "decline", "label": "Decline to speak"},
    {"action_id": "speak", "label": "Speak"},
]
_FULL_PRESS_OPTIONS = [
    {"action_id": "decline", "label": "Decline to speak"},
    {"action_id": "speak", "label": "Speak publicly"},
    {"action_id": "whisper", "label": "Whisper privately to one player"},
]


def render_press_scene(
    observation: Observation,
    identity: dict[str, str],
    prior_messages: list[dict[str, Any]],
    validation_feedback: list[str],
    *,
    options: list[dict[str, str]] | None = None,
) -> ConcordiaScene:
    option_set = options if options is not None else _PRESS_OPTIONS
    payload = {
        "player_id": observation.player_id,
        "turn": observation.turn,
        "ruleset": observation.ruleset,
        "peace": observation.peace,
        "decision_type": "press",
        "identity": dict(identity),
        "observation": render_observation_payload(observation),
        "prior_messages": list(prior_messages),
        "legal_options": [dict(option) for option in option_set],
        "validation_feedback": list(validation_feedback),
    }
    full_press = _has_whisper(option_set)
    return ConcordiaScene(
        text=_scene_text(payload, full_press=full_press), payload=payload
    )


def _has_whisper(option_set: list[dict[str, str]]) -> bool:
    return any(option.get("action_id") == "whisper" for option in option_set)


def full_press_options() -> list[dict[str, str]]:
    return [dict(option) for option in _FULL_PRESS_OPTIONS]


def _scene_text(payload: dict[str, Any], *, full_press: bool) -> str:
    lines = _preamble(full_press)
    lines += [
        "",
        "Concordia framing questions:",
        "- What kind of situation is this?",
        "- What kind of actor am I?",
        "- What does an actor like me say in this situation?",
        "",
        "Scene JSON:",
        json.dumps(payload, indent=2, sort_keys=True),
        "",
        "Respond with exactly one JSON object.",
        'To decline: {"action_id": "decline"}.',
    ]
    if full_press:
        lines += [
            'To speak publicly: {"action_id": "speak", "message": "your public'
            ' statement", "rationale": "reason"}.',
            'To whisper privately: {"action_id": "whisper", "to": "player_1",'
            ' "message": "your private message", "rationale": "reason"}.',
            'Optionally attach a commitment: add "commitment": {"kind":'
            ' "stand_down", "target_round": 3, "notes": "details"} to a speak or'
            " whisper response.",
            "Only the speaker and the named recipient see a private message.",
        ]
    else:
        lines.append(
            'To speak: {"message": "your public statement", "rationale": "reason"}.'
        )
    return "\n".join(lines)


def _preamble(full_press: bool) -> list[str]:
    if full_press:
        return [
            "You are a Concordia-style agent choosing one press message.",
            "You may speak publicly to all living players or whisper privately"
            " to one named recipient.",
            "Private messages are visible only to you and the recipient."
            " Public messages are visible to all living players.",
            "Speech does not affect game state.",
        ]
    return [
        "You are a Concordia-style agent choosing one public press message.",
        "The message is visible to all living players and does not affect game state.",
    ]
