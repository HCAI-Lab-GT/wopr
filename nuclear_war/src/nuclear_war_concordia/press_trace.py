"""Trace construction for Concordia press messages."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import LLMCompletion
from nuclear_war_agents import llm_completion as llm_meta

from .provider_metadata import provider_metadata
from .types import ConcordiaScene, ParsedPressMessage


def append_press_trace(
    *,
    press_sink: list[dict[str, Any]] | None,
    round_no: int,
    speaker: str,
    audience: str,
    visibility: str,
    pass_no: int,
    prior_messages: list[dict[str, Any]],
    scene: ConcordiaScene,
    prompts: list[str],
    raw_responses: list[str],
    completions: list[LLMCompletion],
    validation_errors: list[str],
    parsed: ParsedPressMessage,
) -> None:
    if press_sink is None:
        return
    turn = scene.payload.get("turn", round_no)
    record = {
        "message_id": f"press:{turn}:{speaker}:{pass_no}",
        "turn": turn,
        "round": round_no,
        "speaker": speaker,
        "audience": audience,
        "visibility": visibility,
        "pass": pass_no,
        "decision_type": "press",
        "rendered_observation": dict(scene.payload),
        "prior_messages": list(prior_messages),
        "prompt": prompts[-1],
        "prompts": list(prompts),
        "legal_options": list(scene.payload.get("legal_options", [])),
        "raw_response": raw_responses[-1],
        "raw_responses": list(raw_responses),
        "parse_result": {
            "message": parsed.text,
            "rationale": parsed.rationale,
            "declined": parsed.is_decline,
        },
        "text": parsed.text,
        "retries": max(0, len(raw_responses) - 1),
        "recoverable_provider_retries": llm_meta.total_provider_transport_retries(
            completions
        ),
        "validation_errors": list(validation_errors),
        "stated_rationale": parsed.rationale,
        "linked_decision_traces": [],
        **provider_metadata(completions),
    }
    if parsed.recipient is not None:
        record["recipient"] = parsed.recipient
    if parsed.commitment is not None:
        record["commitment"] = dict(parsed.commitment)
    press_sink.append(record)
