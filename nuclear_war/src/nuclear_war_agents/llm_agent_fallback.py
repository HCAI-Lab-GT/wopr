"""Fallback and validation helpers for the no-press LLM decision agent."""

from __future__ import annotations

from nuclear_war_env.action_models import LegalAction
from nuclear_war_env.observation import Observation

from .llm_types import ParsedLLMDecision

NO_ACTION_ERROR = "No legal action_id parsed"


def validation_error(parsed: ParsedLLMDecision) -> str:
    if parsed.action_id is None:
        return NO_ACTION_ERROR
    return f"Illegal action_id parsed: {parsed.action_id}"


def fallback_option(options: list[LegalAction], fallback: str) -> LegalAction:
    # Validate the policy name up front so a genuinely unknown policy raises a
    # truthful error, and "pass" is never mistaken for one. The accepted set
    # mirrors the batch config parser (llm_harness_batch_config.FALLBACK_POLICIES).
    if fallback not in ("first", "pass"):
        raise ValueError(f"Unknown LLM fallback policy: {fallback}")
    if fallback == "pass":
        for option in options:
            if option.action_type.value == "pass":
                return option
        # No pass-type option is legal at this decision (e.g. setup_place,
        # intercept, or targeting steps); the "pass" policy degrades to the
        # first legal option rather than aborting the experiment.
    return options[0]


def decision_type(observation: Observation) -> str:
    if observation.decision is None:
        return "none"
    return observation.decision.decision_type.value


__all__ = ["NO_ACTION_ERROR", "decision_type", "fallback_option", "validation_error"]
