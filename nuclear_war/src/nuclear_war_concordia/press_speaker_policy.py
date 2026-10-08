"""Recipient validation policy and failure construction for press speakers."""

from __future__ import annotations

from typing import Any

from nuclear_war_agents import LLMCompletion

from .failure import press_failure
from .types import ParsedPressMessage


def is_complete(
    parsed: ParsedPressMessage, speaker: str, living: list[str], full_press: bool
) -> bool:
    if parsed.is_decline:
        return True
    if parsed.text is None:
        return False
    if parsed.visibility != "private":
        return True
    if not full_press:
        return False
    return parsed.recipient in living and parsed.recipient != speaker


def is_acceptable(parsed: ParsedPressMessage, full_press: bool) -> bool:
    """Whether the final parsed message may be recorded (post-retry gate)."""
    if parsed.is_decline:
        return True
    if parsed.text is None:
        return False
    return full_press or parsed.visibility != "private"


def retry_feedback(
    parsed: ParsedPressMessage, speaker: str, living: list[str], full_press: bool
) -> str | None:
    del speaker, living
    if parsed.visibility == "private" and not full_press:
        return "Whispers are not allowed in this press mode; speak publicly"
    if parsed.text is None and not parsed.is_decline:
        return "Response was neither a message nor a decline"
    return None


def strict_recipient_failure(
    parsed: ParsedPressMessage, speaker: str, living: list[str], full_press: bool
) -> str | None:
    if not full_press:
        return None
    if parsed.visibility != "private" or parsed.recipient is None:
        return None
    if parsed.recipient == speaker:
        return "Cannot whisper to yourself"
    if parsed.recipient not in living:
        return "Whisper recipient is not a living player"
    return None


def speaker_failure(
    message: str,
    *,
    speaker: str,
    round_no: int,
    pass_no: int,
    prior_messages: list[dict[str, Any]],
    scene,
    prompts: list[str],
    raw_responses: list[str],
    completions: list[LLMCompletion],
    validation_errors: list[str],
    parsed: ParsedPressMessage,
    exception: Exception | None = None,
):
    return press_failure(
        message,
        speaker=speaker,
        round_no=round_no,
        audience=parsed.recipient or "public",
        pass_no=pass_no,
        prior_messages=prior_messages,
        scene=scene,
        prompts=prompts,
        raw_responses=raw_responses,
        completions=completions,
        validation_errors=validation_errors,
        parsed=parsed,
        exception=exception,
    )
