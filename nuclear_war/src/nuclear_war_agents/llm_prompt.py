"""Prompt rendering for no-press LLM decision agents."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any

from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation


def render_llm_prompt(
    observation: Observation,
    options: list[LegalAction],
    validation_feedback: list[str] | None = None,
) -> str:
    decision_type = (
        observation.decision.decision_type.value
        if observation.decision is not None
        else "none"
    )
    lines = [
        "You are choosing one Nuclear War no-press action.",
        "Use only the observation and legal options below.",
        "No player communication is available in this game.",
        f"player_id: {observation.player_id}",
        f"ruleset: {observation.ruleset}",
        f"turn: {observation.turn}",
        f"peace: {observation.peace}",
        f"decision_type: {decision_type}",
        "",
        "Observation JSON:",
        _json(render_observation_payload(observation)),
        "",
        "Legal action ids:",
        *_action_id_lines(options),
        "",
        "Legal options JSON:",
        _json(render_legal_options(options)),
    ]
    if validation_feedback:
        lines.extend(
            ["", "Validation feedback:", *_feedback_lines(validation_feedback)]
        )
    lines.extend(
        [
            "",
            "Respond with exactly one legal action_id as JSON.",
            'Allowed response shape: {"action_id": "...", "rationale": "..."}',
        ]
    )
    return "\n".join(lines)


def render_legal_options(options: list[LegalAction]) -> list[dict[str, Any]]:
    return [
        {
            "action_id": option.action_id,
            "player_id": option.player_id,
            "action_type": option.action_type.value,
            "label": option.label,
            "payload": option.payload,
        }
        for option in options
    ]


def render_observation_payload(observation: Observation) -> dict[str, Any]:
    payload = asdict(observation)
    if observation.decision is not None:
        payload["decision"]["decision_type"] = observation.decision.decision_type.value
        payload["decision"]["options"] = render_legal_options(
            observation.decision.options
        )
    return payload


def _feedback_lines(validation_feedback: list[str]) -> list[str]:
    return [f"- {message}" for message in validation_feedback]


def _action_id_lines(options: list[LegalAction]) -> list[str]:
    return [f"- {option.action_id}" for option in options]


def _json(payload: Any) -> str:
    return json.dumps(payload, indent=2, sort_keys=True)


__all__ = ["render_llm_prompt", "render_legal_options", "render_observation_payload"]
