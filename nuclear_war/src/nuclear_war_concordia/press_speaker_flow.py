"""Implementation of one press-speaker turn."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import LLMCompletion
from nuclear_war_agents import llm_completion as llm_meta
from nuclear_war_env.observation import Observation

from .press_response import parse_press_response
from .press_scene import full_press_options, render_press_scene
from .press_speaker_policy import (
    is_acceptable,
    is_complete,
    retry_feedback,
    speaker_failure,
    strict_recipient_failure,
)
from .press_trace import append_press_trace
from .types import ParsedPressMessage

_FULL_PRESS = "full_press"


def run_speaker(
    speaker_agent: Any,
    *,
    speaker: str,
    observation: Observation,
    living: list[str],
    round_no: int,
    pass_no: int,
    prior_messages: list[dict[str, Any]],
) -> dict[str, Any]:
    full_press = speaker_agent.mode == _FULL_PRESS
    options = full_press_options() if full_press else None
    view = speaker_agent._view(speaker, prior_messages)
    prompts: list[str] = []
    raw_responses: list[str] = []
    completions: list[LLMCompletion] = []
    validation_errors: list[str] = []
    parsed = ParsedPressMessage()
    scene = render_press_scene(
        observation=observation,
        identity=speaker_agent.identities[speaker],
        prior_messages=view,
        validation_feedback=validation_errors,
        options=options,
    )
    for attempt in range(speaker_agent.max_retries + 1):
        if attempt:
            scene = render_press_scene(
                observation=observation,
                identity=speaker_agent.identities[speaker],
                prior_messages=view,
                validation_feedback=validation_errors,
                options=options,
            )
        prompts.append(scene.text)
        try:
            completion = llm_meta.normalize_completion(
                speaker_agent.clients[speaker].complete(scene.text)
            )
        except Exception as exc:
            if getattr(exc, "channel_budget_exceeded", False):
                raise
            raise speaker_failure(
                "Concordia press client failed",
                speaker=speaker,
                round_no=round_no,
                pass_no=pass_no,
                prior_messages=view,
                scene=scene,
                prompts=prompts,
                raw_responses=raw_responses,
                completions=completions,
                validation_errors=validation_errors,
                parsed=parsed,
                exception=exc,
            ) from exc
        raw_responses.append(completion.raw_response)
        completions.append(completion)
        parsed = parse_press_response(completion.raw_response)
        failure = strict_recipient_failure(parsed, speaker, living, full_press)
        if failure is not None:
            raise speaker_failure(
                failure,
                speaker=speaker,
                round_no=round_no,
                pass_no=pass_no,
                prior_messages=view,
                scene=scene,
                prompts=prompts,
                raw_responses=raw_responses,
                completions=completions,
                validation_errors=validation_errors,
                parsed=parsed,
            )
        if is_complete(parsed, speaker, living, full_press):
            break
        feedback = retry_feedback(parsed, speaker, living, full_press)
        if feedback is None:
            break
        validation_errors.append(feedback)
    if not is_acceptable(parsed, full_press):
        raise speaker_failure(
            "No valid press message",
            speaker=speaker,
            round_no=round_no,
            pass_no=pass_no,
            prior_messages=view,
            scene=scene,
            prompts=prompts,
            raw_responses=raw_responses,
            completions=completions,
            validation_errors=validation_errors,
            parsed=parsed,
        )
    audience = parsed.recipient or "public"
    append_press_trace(
        press_sink=speaker_agent.press_sink,
        round_no=round_no,
        speaker=speaker,
        audience=audience,
        visibility=parsed.visibility,
        pass_no=pass_no,
        prior_messages=view,
        scene=scene,
        prompts=prompts,
        raw_responses=raw_responses,
        completions=completions,
        validation_errors=validation_errors,
        parsed=parsed,
    )
    entry: dict[str, Any] = {
        "turn": observation.turn,
        "speaker": speaker,
        "text": parsed.text,
        "is_decline": parsed.is_decline,
        "audience": audience,
        "visibility": parsed.visibility,
    }
    if parsed.recipient is not None:
        entry["recipient"] = parsed.recipient
    if parsed.commitment is not None:
        entry["commitment"] = dict(parsed.commitment)
    return entry
