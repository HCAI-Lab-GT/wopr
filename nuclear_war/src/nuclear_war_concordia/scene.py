"""Scene rendering for Concordia-backed WOPR decisions."""

from __future__ import annotations

import json
from typing import Any

from nuclear_war_agents.llm_prompt import (
    render_legal_options,
    render_observation_payload,
)
from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation

from .types import ConcordiaScene


def render_concordia_scene(
    observation: Observation,
    options: list[LegalAction],
    identity: dict[str, str],
    validation_feedback: list[str],
    press_memory: list[dict[str, Any]] | None = None,
) -> ConcordiaScene:
    decision_type = (
        observation.decision.decision_type.value
        if observation.decision is not None
        else "none"
    )
    payload = {
        "player_id": observation.player_id,
        "turn": observation.turn,
        "ruleset": observation.ruleset,
        "peace": observation.peace,
        "decision_type": decision_type,
        "identity": dict(identity),
        "observation": render_observation_payload(observation),
        "legal_options": render_legal_options(options),
        "validation_feedback": list(validation_feedback),
    }
    if press_memory:
        payload["press_memory"] = list(press_memory)
    return ConcordiaScene(text=_scene_text(payload), payload=payload)


def _scene_text(payload: dict[str, Any]) -> str:
    if payload.get("press_memory"):
        press_line = (
            "Prior public press statements from other players appear under"
            " 'press_memory' in the Scene JSON below; weigh them when choosing"
            " your action."
        )
    else:
        press_line = "No press or player communication is available in this run."
    lines = [
        "You are a Concordia-style agent choosing one WOPR Nuclear War action.",
        press_line,
        "",
        "Concordia framing questions:",
        "- What kind of situation is this?",
        "- What kind of actor am I?",
        "- What does an actor like me do in this situation?",
        "",
        "Scene JSON:",
        json.dumps(payload, indent=2, sort_keys=True),
        "",
        "Respond with exactly one legal action_id as JSON.",
        'Allowed response shape: {"action_id": "...", "rationale": "..."}',
    ]
    return "\n".join(lines)
